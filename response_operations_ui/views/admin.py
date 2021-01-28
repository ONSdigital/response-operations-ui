import json
import logging

from flask import Blueprint, flash, render_template, request, url_for, redirect, session
from flask_login import login_required, current_user
from structlog import wrap_logger

from response_operations_ui.controllers import admin_controller
from response_operations_ui.controllers.admin_controller import get_template, edit_template, delete_template
from response_operations_ui.controllers.admin_controller import get_templates, create_new_template, Banner
from response_operations_ui.forms import BannerAdminForm, BannerPublishForm
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
    form = BannerAdminForm(form=request.form)
    current_banner = admin_controller.current_banner()
    if current_banner:
        # Display the currently set stuff
        return render_template('admin/admin-remove-alert.html',
                               form=form,
                               current_banner=current_banner,
                               breadcrumbs=breadcrumbs)
    # Display the not currently set stuff
    logger.debug("Banner page accessed", user=current_username())
    form = BannerPublishForm(form=request.form)
    all_banners = get_templates()
    return render_template('admin/banner-admin.html',
                           form=form,
                           list_of_alerts=all_banners,
                           breadcrumbs=breadcrumbs,
                           current_banner=current_banner)


@admin_bp.route('/banner', methods=['POST'])
@login_required
def post_banner():
    form = BannerAdminForm(form=request.form)
    banner_id = form.banner_id.data
    if form.delete.data:
        # Do delete actions
        logger.info("Removing active status from banner", banner_id=banner_id)
        admin_controller.toggle_banner_active_status(banner_id)
        flash('The alert has been removed')
        return redirect(url_for("admin_bp.get_banner_admin"))

    # Validate and redirect to publish confirm screen
    banner_text = form.banner_text.data
    if banner_text:
        session['banner-text'] = banner_text
        return redirect('admin_bp.get_banner_confirm_publish')

    # TODO handle the error if theres no text
    return render_template('admin/banner-admin.html',
                           form=form)


@admin_bp.route('/banner/confirm-publish', methods=['GET'])
@login_required
def get_banner_confirm_publish():
    breadcrumbs = [{"text": "Banner Admin", "url": "/admin/banner"},
                   {"text": "Setting Banner", "url": ""}]

    form = BannerAdminForm(form=request.form)
    form.banner_text = session.pop('banner-text')
    # TODO what happens if there isn't anything in the session?
    return render_template('admin/banner-confirm-publish.html',
                           form=form,
                           breadcrumbs=breadcrumbs)


@admin_bp.route('/banner/confirm-publish', methods=['POST'])
@login_required
def post_banner_confirm_publish():
    form = BannerAdminForm(form=request.form)
    banner_text = form.banner_id.data
    logger.info("Setting an active banner", user=current_username(), banner_text=banner_text)
    if banner_text:
        admin_controller.set_banner(banner_text)
        # TODO handle error if can't set banner live
        return redirect(url_for("surveys_bp.view_surveys", message_key='alert-published'))
    else:
        logger.error("TODO, handle error")
        return redirect(url_for("admin_bp.get_banner_admin"))


# Template management

@admin_bp.route('/banner/manage', methods=['GET'])
@login_required
def manage_alert():
    logger.debug("Managing banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    all_banners = get_templates()
    return render_template('admin/admin-manage.html',
                           form=form,
                           list_of_alerts=all_banners)


@admin_bp.route('/banner/manage', methods=['POST'])
@login_required
def manage_alert_to_edit():
    logger.debug("Managing banner", user=current_username())
    banner_id = request.form['event']
    logger.info("form id", banner=banner_id)
    return redirect(url_for("admin_bp.get_banner_edit", banner_id=banner_id))


# Loads manage page
@admin_bp.route('/banner/create', methods=['GET'])
@login_required
def create_a_new_banner():
    logger.debug("Creating template", user=current_username())
    form = BannerAdminForm(form=request.form)
    return render_template('admin/admin-create-template.html',
                           form=form)


@admin_bp.route('/banner/create', methods=['POST'])
@login_required
def put_new_banner_in_datastore():
    logger.debug("Creating template", user=current_username())
    form = BannerAdminForm(form=request.form)
    title = form.title.data
    banner = form.banner_text.data
    new_banner = Banner(title, banner).to_json()
    create_new_template(new_banner)
    return redirect(url_for("admin_bp.get_banner_admin"))


@admin_bp.route('/banner/edit/<banner_id>', methods=['GET'])
@login_required
def get_banner_edit(banner_id):
    logger.info("searching for banner", id=banner_id)
    banner = get_template(banner_id)
    logger.info("got banner", banner=banner)
    form = BannerAdminForm(form=request.form)
    return render_template('admin/admin-edit.html',
                           form=form,
                           banner=banner)


@admin_bp.route('/banner/edit/<banner_id>', methods=['POST'])
@login_required
def edit_the_chosen_banner(banner_id):
    logger.debug("Editing banner", user=current_username())
    form = BannerAdminForm(form=request.form)
    if form.delete.data:
        logger.debug("Removing banner", user=current_username())
        delete_template(banner_id)
        return redirect(url_for("admin_bp.get_banner_admin"))
    title = form.title.data
    content = form.banner_text.data
    edit_template(json.dumps({"id": banner_id, "title": title, "content": content}))
    return redirect(url_for("admin_bp.get_banner_admin"))


def current_username():
    if hasattr(current_user, 'username'):
        return current_user.username
    else:
        return "unknown"
