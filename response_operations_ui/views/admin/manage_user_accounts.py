import logging

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_paginate import Pagination
from structlog import wrap_logger
from werkzeug.exceptions import abort

from response_operations_ui.controllers.uaa_controller import (
    add_group_membership,
    get_filter_query,
    get_groups,
    get_user_by_email,
    get_user_by_id,
    get_users_list,
    remove_group_membership,
    user_has_permission,
)
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
    if not user_has_permission("users.admin"):
        logger.exception("Manage User Account request requested but unauthorised.")
        abort(401)
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


@admin_bp.route("/manage-account", methods=["GET"])
@login_required
def manage_account():
    if not user_has_permission("users.admin"):
        logger.exception("Manage User Account request requested but unauthorised.")
        abort(401)
    user_requested = request.values.get("user", None)
    if user_requested is None:
        # Someone has gotten here directly without passing a parameter in, send them back to the main page
        flash("No user was selected to edit", "error")
        return redirect(url_for("admin_bp.manage_user_accounts"))

    logger.info("Attempting to get user " + user_requested)
    uaa_user = get_user_by_email(user_requested)
    if uaa_user is None or len(uaa_user["resources"]) == 0:
        # Something went wrong when trying to retrieve them from UAA
        flash("Selected user could not be found", "error")
        return redirect(url_for("admin_bp.manage_user_accounts"))

    name = uaa_user["resources"][0]["name"]["givenName"] + " " + uaa_user["resources"][0]["name"]["familyName"]
    permissions = {g["display"]: "y" for g in uaa_user["resources"][0]["groups"]}

    # TODO the checkboxes in a table didn't seem to get posted, had to take them out of the table to get them working.
    #  will fix that after we get the functionality sorted
    return render_template(
        "admin/manage-account.html", name=name, permissions=permissions, user_id=uaa_user["resources"][0]["id"]
    )


@admin_bp.route("/manage-account", methods=["POST"])
@login_required
def update_account_permissions():
    if not user_has_permission("users.admin"):
        logger.exception("Manage User Account request requested but unauthorised.")
        abort(401)

    user_id = request.form.get("user_id")
    user = get_user_by_id(user_id)
    groups = get_groups()
    # Get user from uaa (so we have a fresh set of permissions to look at)
    form = EditUserPermissionsForm(request.form)
    user_groups = [group["display"] for group in user["groups"]]

    # TODO need to figure out how to get from surveys_edit to surveys.edit (the group name in uaa)
    translated_permissions = {
        "surveys_edit": "surveys.edit",
        "reporting_units_edit": "reportingunits.edit",
        "respondents_edit": "respondents.edit",
        "respondents_delete": "respondents.delete",
        "messages_edit": "messages.edit",
    }

    for permission, ticked in form.data.items():
        # Translate the permission, so we have the uaa form of it
        translated_permission = translated_permissions[permission]
        group_details = next(item for item in groups["resources"] if item["displayName"] == translated_permission)
        group_id = group_details["id"]
        if ticked:
            if translated_permission in user_groups:
                continue  # Nothing to do, already part of the group
            add_group_membership(user_id, group_id)

        if translated_permission in user_groups:
            remove_group_membership(user_id, group_id)
        continue  # Nothing to do, already not in the group

    # TODO do we flash?  What do we flash? Where do we redirect to after we do this?
    return redirect(url_for("admin_bp.manage_user_accounts"))


def _get_refine_user_list(users: list):
    user_list = []
    for user in users:
        user_list.append(
            {
                "email": user["emails"][0]["value"],
                "name": user["name"]["givenName"],
                "lastname": user["name"]["familyName"],
                "id": user["id"],
            }
        )
    return user_list
