import logging

from flask import Blueprint, render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import admin_controller
from response_operations_ui.forms import BannerAdminForm


logger = wrap_logger(logging.getLogger(__name__))

admin_bp = Blueprint('admin_pd', __name__,
                       static_folder='static', template_folder='templates')

INFO_MESSAGES = {
    'survey_changed': "Survey details changed",
    'survey_created': "Survey created successfully",
    'instrument_linked': "Collection exercise linked to survey successfully"
}


@admin_bp.route('/banner', methods=['GET'])
@login_required
def banner_admin():
    form = BannerAdminForm(form=request.form)

    current_banner = admin_controller.current_banner()
        
    form.banner.data = current_banner
    
    return render_template('banner-admin.html', current_banner=current_banner, form=form)


@admin_bp.route('/banner', methods=['POST'])
@login_required
def create_banner():
    form = BannerAdminForm(form=request.form)

    admin_controller.add_banner(form.banner.data)

    return render_template('banner-admin.html', form=form)

