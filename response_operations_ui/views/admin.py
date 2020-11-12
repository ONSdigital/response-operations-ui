import json
import logging
import pprint

from flask import Blueprint, render_template, request, url_for, redirect, jsonify
from flask_login import login_required, current_user
from structlog import wrap_logger

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
    breadcrumbs = [{"text": "Banner Admin", "url": "/banner"},
                   {"text": "Banner Removal"}]
    
    logger.debug("Banner page accessed", user=current_username())
    form = BannerAdminForm(form=request.form)
    dict_of_alerts = get_alert_list()
    current_banner = admin_controller.current_banner()
    if current_banner:
        form.banner.data = current_banner
        logger.debug("Banner set to ", banner=current_banner)
    return render_template('banner-admin.html',
                           current_banner=current_banner,
                           form=form,
                           list_of_alerts=dict_of_alerts,
                           breadcrumbs=breadcrumbs)


def current_username():
    if hasattr(current_user, 'username'):
        return current_user.username
    else:
        return "unknown"


@admin_bp.route('/banner', methods=['POST'])
@login_required
def update_banner():
    breadcrumbs = [{"text": "Banner Admin", "url": "/banner"},
                   {"text": "Banner Removal"}]
    
    logger.debug("Updating banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    banner = form.banner.data

    if form.delete.data or not banner:
        logger.debug("Banner deleted", user=current_username())
        admin_controller.remove_banner()
    else:
        logger.debug("Banner update", user=current_username(), banner=banner)
        admin_controller.set_banner(form.banner.data)
    return redirect(url_for("admin_bp.remove_alert",
                            breadcrumbs=breadcrumbs))


def remove_banner():
    admin_controller.remove_banner()
    return redirect(url_for("admin_bp.banner_admin"))


@admin_bp.route('/banner/remove', methods=['GET'])
@login_required
def publish_alert():
    breadcrumbs = [{"text": "Banner Removal", "url": "/banner/remove"},
                   {"text": "Banner Removal"}]
    
    logger.debug("Deleting alert", user=current_username())
    current_banner = admin_controller.current_banner()
    if request.method == 'GET':
        return render_template('remove-alert.html', 
                               current_banner=current_banner,
                               breadcrumbs=breadcrumbs)


@admin_bp.route('/banner/remove', methods=['POST'])
@login_required
def remove_alert():
    logger.debug("Updating banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    delete = form.delete.data
    banner_removed = form.banner_removed.data

    if delete:
        logger.debug("Banner deleted", user=current_username())
        admin_controller.remove_banner()
    return redirect(url_for("admin_bp.banner_admin",
                            variable=json.dumps(banner_removed)))
