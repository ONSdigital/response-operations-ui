import logging
import pprint
from datetime import datetime

from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from structlog import wrap_logger
from dateutil import parser

from response_operations_ui.controllers import admin_controller
from response_operations_ui.controllers.admin_controller import get_a_banner, get_all_banners
from response_operations_ui.forms import BannerAdminForm

logger = wrap_logger(logging.getLogger(__name__))

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', template_folder='templates')

INFO_MESSAGES = {
    'survey_changed': "Survey details changed",
    'instrument_linked': "Collection exercise linked to survey successfully"
}


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
    breadcrumbs = [{"text": "Banner Admin", "url": ""}]
    dict_of_alerts = get_all_banners()
    current_banner = admin_controller.current_banner()
    logger.debug("Updating banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    banner = form.banner.data
    logger.debug("Banner update", user=current_username(), banner=banner)
    if banner:
        admin_controller.set_banner_and_time(form.banner.data, datetime.now())
        return redirect(url_for("admin_bp.remove_alert"))
    else:
        response_error = True
    return render_template('banner-admin.html',
                           form=form,
                           list_of_alerts=dict_of_alerts,
                           breadcrumbs=breadcrumbs,
                           current_banner=current_banner,
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


@admin_bp.route('/banner/remove', methods=['POST'])
@login_required
def remove_alert():
    logger.debug("Removing banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    delete = form.delete.data
    if delete:
        flash('The alert has been removed')
        logger.debug("Banner deleted", user=current_username())
        admin_controller.remove_banner()
    return redirect(url_for("admin_bp.banner_admin"))


@admin_bp.route('/banner/edit', methods=['GET'])
@login_required
def edit_alert():
    logger.debug("Editing banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    return render_template('admin-edit.html', form=form)


@admin_bp.route('/banner/manage', methods=['GET'])
@login_required
def manage_alert():
    logger.debug("Managing banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    return render_template('admin-manage.html', form=form)


@admin_bp.route('/banner/create', methods=['GET'])
@login_required
def create_template():
    logger.debug("Creating template", user=current_username())
    form = BannerAdminForm(form=request.form)
    return render_template('admin-create-template.html', form=form)


# Currently datetime.strftime does not support applying suffix's onto the date.
# Reference: https://stackoverflow.com/questions/5891555/display-the-date-like-may-5th-using-pythons-strftime
def set_suffix(today):
    if 4 <= today <= 20 or 24 <= today <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][today % 10 - 1]
    return suffix
