import logging

from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required
from flask_paginate import Pagination
from requests import HTTPError
from structlog import wrap_logger
from werkzeug.exceptions import abort

from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.controllers.uaa_controller import (
    add_group_membership,
    delete_user,
    get_filter_query,
    get_groups,
    get_user_by_id,
    get_users_list,
    remove_group_membership,
    user_has_permission,
)
from response_operations_ui.exceptions.exceptions import NotifyError
from response_operations_ui.forms import EditUserPermissionsForm, UserSearchForm
from response_operations_ui.views.admin import admin_bp

logger = wrap_logger(logging.getLogger(__name__))


@admin_bp.route("/manage-user-accounts", methods=["GET", "POST"])
@login_required
def manage_user_accounts():
    """
    This endpoint, by design is only accessible to ROPs admin user.
    This endpoint lists all current user in the system.
    """
    _verify_user_admin_permission()
    page = request.values.get("page", "1")
    user_with_email = request.values.get("user_with_email", None)
    limit = 20
    offset = (int(page) - 1) * limit
    query = None
    form = UserSearchForm()
    search_email = None
    if user_with_email is not None:
        query = get_filter_query("starts with", user_with_email, "emails.value")
    if form.validate_on_submit():
        search_email = form.user_search.data
        query = get_filter_query("equal", search_email, "emails.value")
    if form.errors:
        flash(form.errors["user_search"][0], "error")

    uaa_user_list = get_users_list(start_index=offset, max_count=limit, query=query)
    user_list = _get_refine_user_list(uaa_user_list["resources"])
    pagination = Pagination(
        page=int(page),
        per_page=limit,
        total=uaa_user_list["totalResults"],
        record_name="Users",
        prev_label="Previous",
        next_label="Next",
        outer_window=0,
        format_total=True,
        format_number=True,
        show_single_page=False,
    )
    return render_template(
        "admin/manage-user-accounts.html",
        user_list=user_list,
        pagination=pagination,
        show_pagination=bool(uaa_user_list["totalResults"] > limit),
        form=form,
        search_email=search_email,
    )


@admin_bp.route("/manage-account/<user_id>", methods=["GET"])
@login_required
def manage_account(user_id):
    _verify_user_admin_permission()

    logger.info("Attempting to get user by id", user_id=user_id)
    uaa_user = get_user_by_id(user_id)
    if uaa_user is None:
        # Something went wrong when trying to retrieve them from UAA
        flash("Selected user could not be found", "error")
        return redirect(url_for("admin_bp.manage_user_accounts"))

    if uaa_user["id"] == session["user_id"]:
        flash("You cannot modify your own user account", "error")
        logger.error("User tried to modify their own account", user_id=uaa_user["id"])
        return redirect(url_for("admin_bp.manage_user_accounts"))

    name = uaa_user["name"]["givenName"] + " " + uaa_user["name"]["familyName"]
    permissions = {g["display"]: "y" for g in uaa_user["groups"]}

    return render_template("admin/manage-account.html", name=name, permissions=permissions, user_id=uaa_user["id"])


@admin_bp.route("/manage-account/<user_id>", methods=["POST"])
@login_required
def update_account_permissions(user_id):
    _verify_user_admin_permission()

    if user_id == session["user_id"]:
        flash("You cannot modify your own user account", "error")
        logger.error("User tried to modify their own account", user_id=user_id)
        return redirect(url_for("admin_bp.manage_user_accounts"))

    # Get user from uaa, so we have a fresh set of permissions to look at
    user = get_user_by_id(user_id)
    if user is None:
        flash("User does not exist", "error")
        return redirect(url_for("admin_bp.manage_user_accounts"))

    try:
        groups = get_groups()
    except HTTPError:
        flash("Failed to get groups, please try again", "error")
        return redirect(url_for("admin_bp.manage_user_accounts"))

    form = EditUserPermissionsForm(request.form)
    user_groups = [group["display"] for group in user["groups"]]

    translated_permissions = {
        "surveys_edit": "surveys.edit",
        "reporting_units_edit": "reportingunits.edit",
        "respondents_edit": "respondents.edit",
        "respondents_delete": "respondents.delete",
        "messages_edit": "messages.edit",
        "uaa_admin": "uaa.admin",
    }

    # Because we can't add or remove in a batch, if one of them fail then we can leave the user in a state that wasn't
    # intended.  Though it can be easily fixed by trying again.

    was_permission_changed = False
    for permission, is_ticked in form.data.items():
        # Translate the permission, so we have the uaa form of it
        translated_permission = translated_permissions[permission]
        group_details = next(item for item in groups["resources"] if item["displayName"] == translated_permission)
        group_id = group_details["id"]
        if is_ticked:
            if translated_permission in user_groups:
                continue  # Nothing to do, already part of the group
            try:
                add_group_membership(user_id, group_id)  # Ticked and not in group, need to add it
            except HTTPError:
                flash(f"Failed add [{permission}] to the user, please try again", "error")
                return redirect(url_for("admin_bp.manage_account", user=user["emails"][0]["value"]))
            was_permission_changed = True

        if translated_permission in user_groups:
            try:
                remove_group_membership(user_id, group_id)  # Not ticked but in group, need to remove it
            except HTTPError:
                flash(f"Failed remove [{permission}] to the user, please try again", "error")
                return redirect(url_for("admin_bp.manage_account", user=user["emails"][0]["value"]))
            was_permission_changed = True
        continue  # Nothing to do, already not in the group

    if was_permission_changed:
        try:
            NotifyController().request_to_notify(
                email=user["emails"][0]["value"],
                template_name="update_user_permissions",
                personalisation={},
            )
        except NotifyError as e:
            logger.error("failed to send email", msg=e.description, exc_info=True)
            flash("Failed to send email, please try again", "error")
            return redirect(url_for("admin_bp.manage_account", user=user["emails"][0]["value"]))

        flash("User account has been successfully changed. An email to inform the user has been sent.")

    return redirect(url_for("admin_bp.manage_user_accounts"))


@admin_bp.route("/manage-account/<user_id>/delete", methods=["GET"])
@login_required
def get_delete_uaa_user(user_id):
    _verify_user_admin_permission()

    if user_id == session["user_id"]:
        flash("You cannot delete your own user account", "error")
        logger.error("User tried to delete themselves", user_id=user_id)
        return redirect(url_for("admin_bp.manage_user_accounts"))

    user = get_user_by_id(user_id)
    if user is None:
        flash("User does not exist", "error")
        return redirect(url_for("admin_bp.manage_user_accounts"))

    name = user["name"]["givenName"] + " " + user["name"]["familyName"]
    email = user["emails"][0]["value"]
    return render_template("admin/user-delete.html", name=name, email=email)


@admin_bp.route("/manage-account/<user_id>/delete", methods=["POST"])
@login_required
def post_delete_uaa_user(user_id):
    _verify_user_admin_permission()

    if user_id == session["user_id"]:
        flash("You cannot delete your own user account", "error")
        logger.error("User tried to delete themselves", user_id=user_id)
        return redirect(url_for("admin_bp.manage_user_accounts"))

    user = get_user_by_id(user_id)
    if user is None:
        flash("User does not exist", "error")
        return redirect(url_for("admin_bp.manage_user_accounts"))

    try:
        NotifyController().request_to_notify(
            email=user["emails"][0]["value"],
            template_name="delete_user",
            personalisation={},
        )
        delete_user(user_id)
    except (NotifyError, HTTPError):
        logger.error("Failed to complete user deletion process", user_id=user_id, exc_info=True)
        flash("Failed to delete user, please try again", "error")
        return redirect(url_for("admin_bp.get_delete_uaa_user", user_id=user_id))

    logger.info("Just before the flash")
    flash("User account has been successfully deleted. An email to inform the user has been sent.")
    return redirect(url_for("admin_bp.manage_user_accounts"))


def _verify_user_admin_permission():
    """
    Checks if the user has 'users.admin' permission and aborts with a 401 status code if the user
    doesn't have permission.
    """
    if not user_has_permission("users.admin"):
        logger.exception("Manage User Account request requested but unauthorised.")
        abort(401)


def _get_refine_user_list(users: list) -> list[dict]:
    user_list = []
    for user in users:
        user_list.append(
            {
                "email": user["emails"][0]["value"],
                "name": user["name"]["givenName"],
                "lastname": user["name"]["familyName"],
                "id": user["id"],
                "show_edit_button": user["id"] != session["user_id"],
            }
        )
    return user_list
