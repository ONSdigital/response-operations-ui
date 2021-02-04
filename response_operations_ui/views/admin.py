import json
import logging

from flask import Blueprint, flash, render_template, request, url_for, redirect, session
from flask_login import login_required, current_user
from structlog import wrap_logger

from response_operations_ui.controllers import admin_controller
from response_operations_ui.controllers.admin_controller import get_template, edit_template, delete_template
from response_operations_ui.controllers.admin_controller import get_templates, create_new_template, Template
from response_operations_ui.exceptions.exceptions import ApiError
from response_operations_ui.forms import BannerAdminForm, BannerPublishForm, BannerDeleteForm, BannerManageForm, \
    BannerEditForm, BannerCreateForm
logger = wrap_logger(logging.getLogger(__name__))

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', template_folder='templates')


@admin_bp.route('/banner', methods=['GET'])
@login_required
def get_banner_admin():
    """
    This endpoint, by the design we were given, renders one of two different screens.  Either a 'create' screen if
    there isn't a banner set yet, or a 'remove' screen if there is one.
    """
    breadcrumbs = [{"text": "Banner Admin", "url": ""}]
    current_banner_json = admin_controller.current_banner()
    logger.info("Banner page accessed", user=current_username())
    if current_banner_json:
        # Handle remove scenario
        form = BannerDeleteForm()
        return render_template('admin/admin-remove-alert.html',
                               form=form,
                               current_banner=current_banner_json['content'],
                               breadcrumbs=breadcrumbs)
    # Handle create scenario
    form = BannerPublishForm()
    all_templates = get_templates()
    return render_template('admin/banner-admin.html',
                           form=form,
                           list_of_alerts=all_templates,
                           breadcrumbs=breadcrumbs)


@admin_bp.route('/banner', methods=['POST'])
@login_required
def post_banner():
    if request.form.get('delete'):
        # Handle remove scenario
        logger.info("Removing active status from banner")
        admin_controller.remove_banner()
        flash('The alert has been removed')
        return redirect(url_for("admin_bp.get_banner_admin"))

    # Handle create scenario
    form = BannerPublishForm(form=request.form)
    if form.validate():
        banner_text = form.banner_text.data
        session['banner-text'] = banner_text
        return redirect(url_for('admin_bp.get_banner_confirm_publish'))

    breadcrumbs = [{"text": "Banner Admin", "url": ""}]
    all_templates = get_templates()
    return render_template('admin/banner-admin.html',
                           form=form,
                           list_of_alerts=all_templates,
                           breadcrumbs=breadcrumbs,
                           errors=form.errors.items())


@admin_bp.route('/banner/confirm-publish', methods=['GET'])
@login_required
def get_banner_confirm_publish():
    breadcrumbs = [{"text": "Create an alert", "url": "/admin/banner"},
                   {"text": "Setting Banner", "url": ""}]

    form = BannerPublishForm(form=request.form)
    banner_text = session.pop('banner-text')
    form.banner_text = banner_text
    # TODO what happens if there isn't anything in the session?
    return render_template('admin/banner-confirm-publish.html',
                           current_banner=banner_text,
                           form=form,
                           breadcrumbs=breadcrumbs)


@admin_bp.route('/banner/confirm-publish', methods=['POST'])
@login_required
def post_banner_confirm_publish():
    form = BannerPublishForm(form=request.form)
    banner_text = form.banner_text.data
    logger.info("Setting an active banner", user=current_username(), banner_text=banner_text)
    if banner_text:
        try:
            admin_controller.set_banner(banner_text)
        except ApiError:
            flash("Something went wrong setting the banner")
            return redirect(url_for("admin_bp.get_banner_admin"))
        return redirect(url_for("surveys_bp.view_surveys", message_key='alert_published'))
    else:
        logger.error("Banner text is somehow missing from the form")
        flash("Something went wrong setting the banner")
        return redirect(url_for("admin_bp.get_banner_admin"))


# Template management

@admin_bp.route('/banner/manage', methods=['GET', 'POST'])
@login_required
def manage_alert():
    logger.debug("Managing banner templates", user=current_username())
    form = BannerManageForm(form=request.form)
    if form.validate_on_submit():
        banner_id = form.template_id.data
        logger.info("form id", banner=banner_id)
        return redirect(url_for("admin_bp.edit_the_chosen_banner", banner_id=banner_id))

    all_banners = get_templates()
    return render_template('admin/admin-manage.html',
                           form=form,
                           list_of_alerts=all_banners,
                           errors=form.errors.items())


@admin_bp.route('/banner/create', methods=['GET', 'POST'])
@login_required
def put_new_banner_in_datastore():
    logger.debug("Creating template", user=current_username())
    form = BannerCreateForm(form=request.form)
    if form.validate_on_submit():
        title = form.title.data
        banner = form.banner_text.data
        logger.info(form.banner_text)
        new_banner = Template(title, banner).to_json()
        create_new_template(new_banner)
        return redirect(url_for("admin_bp.get_banner_admin"))
    
    return render_template('admin/admin-create-template.html',                       
                           form=form,
                           errors=form.errors.items())


@admin_bp.route('/banner/edit/<banner_id>', methods=['GET', 'POST'])
@login_required
def edit_the_chosen_banner(banner_id):
    logger.info("Editing template", user=current_username(), banner_id=banner_id)
    form = BannerEditForm(form=request.form)
    if form.validate_on_submit():
        if form.delete.data:
            logger.debug("Removing banner", user=current_username())
            delete_template(banner_id)
            return redirect(url_for("admin_bp.get_banner_admin"))

        edit_template({"id": banner_id,
                       "title": form.title.data,
                       "content": form.banner.data})
        return redirect(url_for("admin_bp.get_banner_admin"))

    banner = get_template(banner_id)
    return render_template('admin/admin-edit.html',
                           form=form,
                           banner=banner,
                           errors=form.errors.items())


def current_username():
    if hasattr(current_user, 'username'):
        return current_user.username
    else:
        return "unknown"
