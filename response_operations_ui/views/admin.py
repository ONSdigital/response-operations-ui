import logging
from datetime import datetime
from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from structlog import wrap_logger
from dateutil import parser
import json

from response_operations_ui.controllers import admin_controller
from response_operations_ui.controllers.admin_controller import get_all_banners, create_new_banner, Banner, get_a_banner, edit_banner, delete_banner
from response_operations_ui.forms import BannerAdminForm, BannerManageForm

logger = wrap_logger(logging.getLogger(__name__))

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', template_folder='templates')

INFO_MESSAGES = {
    'survey_changed': "Survey details changed",
    'instrument_linked': "Collection exercise linked to survey successfully"
}
title_to_edit = ""


@admin_bp.route('/banner', methods=['GET'])
@login_required
def banner_admin():
    breadcrumbs = [{"text": "Banner Admin", "url": ""}]
    current_banner = admin_controller.current_banner()
    logger.debug("Banner page accessed", user=current_username())
    form = BannerAdminForm(form=request.form)
    dict_of_alerts = get_all_banners()
    return render_template('banner-admin.html',
                           form=form,
                           list_of_alerts=dict_of_alerts,
                           breadcrumbs=breadcrumbs,
                           current_banner=current_banner)


def current_username():
    if hasattr(current_user, 'username'):
        return current_user.username
    else:
        return "unknown"


@admin_bp.route('/banner', methods=['POST'])
@login_required
def update_banner():
    form = BannerAdminForm(form=request.form)
    banner_id = form.banner_id.data
    logger.info("Setting an active banner", user=current_username(), banner_id=banner_id)
    if banner_id:
        admin_controller.set_live_banner(banner_id)
        return redirect(url_for("admin_bp.banner_admin"))
    else:
        response_error = True
    return render_template('banner-admin.html',
                           form=form,
                           list_of_alerts=get_all_banners(),
                           breadcrumbs=[{"text": "Banner Admin", "url": ""}],
                           current_banner=admin_controller.current_banner(),
                           response_error=response_error)


# Parser.parse allows the string returned from redis to be converted into a datetime object from string
@admin_bp.route('/banner/remove', methods=['GET'])
@login_required
def view_and_remove_current_banner():
    breadcrumbs = [{"text": "Banner Admin", "url": "/admin/banner"},
                   {"text": "Setting Banner", "url": ""}]
    logger.debug("Deleting alert", user=current_username())
    form = BannerAdminForm(form=request.form)
    current_banner = admin_controller.current_banner()
    time_banner_set = admin_controller.banner_time_get()
    time_banner_set = parser.parse(time_banner_set) \
        .strftime('%d' + set_suffix(datetime.today().day) + ' %B ' + '%Y ' + 'at %H' + ':%M')
    if current_banner:
        return render_template('admin-remove-alert.html',
                               form=form,
                               current_banner=current_banner,
                               breadcrumbs=breadcrumbs,
                               time_banner_set=time_banner_set)
    else:
        return redirect(url_for("admin_bp.banner_admin"))


def remove_alert(banner_id):
    logger.debug("Removing banner", user=current_username())
    delete_banner(banner_id)
    return redirect(url_for("admin_bp.banner_admin"))


@admin_bp.route('/banner/manage', methods=['GET'])
@login_required
def manage_alert():
    logger.debug("Managing banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    list_of_alerts = get_all_banners()
    return render_template('admin-manage.html',
                           form=form,
                           list_of_alerts=list_of_alerts)


# Nothing is being posted to this endpoint. I believe its something to do with the Radio buttons and setting
# the "name" variable to "title" at the wrong point in admin-manage.html
@admin_bp.route('/banner/manage', methods=['POST'])
@login_required
def manage_alert_to_edit():
    logger.debug("Managing banner", user=current_username())
    id = request.form['event']
    logger.info("form id", banner=id)
    return redirect(url_for("admin_bp.get_banner_edit", banner_id=id))

@admin_bp.route('/banner/edit/<banner_id>', methods=['GET'])
@login_required
def get_banner_edit(banner_id):
    logger.info("searching for banner", id=banner_id)
    banner = get_a_banner(banner_id)
    logger.info("got banner", banner=banner)
    form = BannerAdminForm(form=request.form)
    return render_template('admin-edit.html',
                           form=form,
                           banner=banner)

@admin_bp.route('/banner/edit/<banner_id>', methods=['POST'])
@login_required
def edit_the_chosen_banner(banner_id):
    logger.debug("Editing banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    if form.delete.data:
        return remove_alert(banner_id)
    title = form.title.data
    content = form.banner.data
    banner = edit_banner(json.dumps({ "id": banner_id, "title": title, "content": content}))
    return redirect(url_for("admin_bp.banner_admin"))


# Loads manage page
@admin_bp.route('/banner/create', methods=['GET'])
@login_required
def create_a_new_banner():
    logger.debug("Creating template", user=current_username())
    form = BannerAdminForm(form=request.form)
    return render_template('admin-create-template.html',
                           form=form)


@admin_bp.route('/banner/create', methods=['POST'])
@login_required
def put_new_banner_in_datastore():
    logger.debug("Creating template", user=current_username())
    form = BannerAdminForm(form=request.form)
    title = form.title.data
    banner = form.banner.data
    new_banner = Banner(title, banner)
    new_banner = new_banner.to_json()
    try:
        create_new_banner(new_banner)
        return redirect(url_for("admin_bp.banner_admin"))
    except ValueError:
        raise ValueError


# Currently datetime.strftime does not support applying suffix's onto the date.
# Reference: https://stackoverflow.com/questions/5891555/display-the-date-like-may-5th-using-pythons-strftime
def set_suffix(today):
    if 4 <= today <= 20 or 24 <= today <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][today % 10 - 1]
    return suffix
