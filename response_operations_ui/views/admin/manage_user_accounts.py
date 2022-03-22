import logging

from flask import flash, render_template, request
from flask_login import login_required
from flask_paginate import Pagination
from structlog import wrap_logger
from werkzeug.exceptions import abort

from response_operations_ui.controllers.uaa_controller import (
    get_filter_query,
    get_users_list,
    user_has_permission,
)
from response_operations_ui.forms import UserSearchForm
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
        logger.exception("Manage User Account request requested but unauthorised. ")
        abort(401)
    page = request.values.get("page", "1")
    user_with_email = request.values.get("user_with_email", None)
    limit = 20
    offset = (int(page) - 1) * limit
    query = None
    form = UserSearchForm()
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
    )


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
