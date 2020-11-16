import logging

from flask import Blueprint, render_template, request, url_for, redirect, session
from flask_login import login_required, current_user
from structlog import wrap_logger
from datetime import datetime

from response_operations_ui.controllers import admin_controller
from response_operations_ui.controllers.admin_controller import get_alert_list
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
    dict_of_alerts = get_alert_list()
    banner_removed = False
    if 'banner_removed' in session:
        session.pop('banner_removed')
        banner_removed = True
    return render_template('banner-admin.html',
                           form=form,
                           list_of_alerts=dict_of_alerts,
                           breadcrumbs=breadcrumbs,
                           banner_removed=banner_removed,
                           current_banner=current_banner)


def current_username():
    if hasattr(current_user, 'username'):
        return current_user.username
    else:
        return "unknown"


@admin_bp.route('/banner', methods=['POST'])
@login_required
def update_banner():
    logger.debug("Updating banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    banner = form.banner.data
    time_set = datetime.now().strftime('%d' + set_suffix(datetime.today().day) + ' %B ' + '%Y ' + 'at %H' + ':%M')
    logger.debug("Banner update", user=current_username(), banner=banner)
    admin_controller.set_banner_and_time(form.banner.data, time_set)
    return redirect(url_for("admin_bp.remove_alert"))


@admin_bp.route('/banner/remove', methods=['GET'])
@login_required
def publish_alert():
    breadcrumbs = [{"text": "Banner Admin", "url": "/admin/banner"},
                   {"text": "Setting Banner", "url": ""}]
    logger.debug("Deleting alert", user=current_username())
    current_banner = admin_controller.current_banner()
    time_banner_set = admin_controller.banner_time_get()
    if current_banner:
        return render_template('remove-alert.html',
                               current_banner=current_banner,
                               breadcrumbs=breadcrumbs,
                               time_banner_set=time_banner_set)
    else:
        return redirect(url_for("admin_bp.banner_admin"))


@admin_bp.route('/banner/remove', methods=['POST'])
@login_required
def remove_alert():
    logger.debug("Updating banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    banner_removed = ''
    delete = form.delete.data
    if delete:
        session['banner_removed'] = banner_removed
        logger.debug("Banner deleted", user=current_username())
        admin_controller.remove_banner()
    return redirect(url_for("admin_bp.banner_admin"))


def set_suffix(today):
    if 4 <= today <= 20 or 24 <= today <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][today % 10 - 1]
    return suffix
