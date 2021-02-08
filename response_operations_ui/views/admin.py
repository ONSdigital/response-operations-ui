import logging

from flask import Blueprint, flash, render_template, request, url_for, redirect, session
from flask_login import login_required, current_user
from structlog import wrap_logger

from response_operations_ui.controllers import admin_controller
from response_operations_ui.controllers.admin_controller import get_template, edit_template, delete_template
from response_operations_ui.controllers.admin_controller import get_templates, create_new_template, Template
from response_operations_ui.forms import BannerPublishForm, BannerDeleteForm, BannerManageForm, \
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
        return render_template('admin/banner-remove.html',
                               form=form,
                               current_banner=current_banner_json['content'],
                               breadcrumbs=breadcrumbs)
    # Handle create scenario
    form = BannerPublishForm()
    all_templates = get_templates()
    return render_template('admin/banner-manage.html',
                           form=form,
                           list_of_templates=all_templates,
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
    return render_template('admin/banner-manage.html',
                           form=form,
                           list_of_templates=all_templates,
                           breadcrumbs=breadcrumbs,
                           errors=form.errors.items())


@admin_bp.route('/banner/confirm-publish', methods=['GET'])
@login_required
def get_banner_confirm_publish():
    logger.info("About to confirm banner text to publish", user=current_username())
    breadcrumbs = [{"text": "Create an alert", "url": "/admin/banner"},
                   {"text": "Setting Banner", "url": ""}]

    form = BannerPublishForm(form=request.form)
    try:
        banner_text = session.pop('banner-text')
    except KeyError:
        flash("Something went wrong setting the banner")
        return redirect(url_for("admin_bp.get_banner_admin"))

    form.banner_text = banner_text
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
        admin_controller.set_banner(banner_text)
        return redirect(url_for("surveys_bp.view_surveys", message_key='alert_published'))
    else:
        logger.error("Banner text is somehow missing from the form")
        flash("Banner text somehow not found on publish.  Please try again.")
        return redirect(url_for("admin_bp.get_banner_admin"))


# Template management

@admin_bp.route('/banner/manage', methods=['GET', 'POST'])
@login_required
def manage_alert():
    logger.info("Managing banner templates", user=current_username())
    form = BannerManageForm(form=request.form)
    if form.validate_on_submit():
        template_id = form.template_id.data
        return redirect(url_for("admin_bp.get_post_edit_template", banner_id=template_id))

    all_templates = get_templates()
    return render_template('admin/template-manage.html',
                           form=form,
                           list_of_templates=all_templates,
                           errors=form.errors.items())


@admin_bp.route('/banner/create', methods=['GET', 'POST'])
@login_required
def put_new_banner_in_datastore():
    logger.info("Creating template", user=current_username())
    breadcrumbs = [{"text": "Manage templates", "url": "/admin/banner/manage"},
                   {"text": "Create alert template", "url": ""}]
    form = BannerCreateForm(form=request.form)
    if form.validate_on_submit():
        template = Template(form.title.data,
                            form.banner_text.data).to_json()
        create_new_template(template)
        return redirect(url_for("admin_bp.get_banner_admin"))

    return render_template('admin/template-create.html',
                           breadcrumbs=breadcrumbs,
                           form=form,
                           errors=form.errors.items())


@admin_bp.route('/banner/edit/<banner_id>', methods=['GET', 'POST'])
@login_required
def get_post_edit_template(banner_id):
    logger.info("Editing template", user=current_username(), banner_id=banner_id)
    breadcrumbs = [{"text": "Manage templates", "url": "/admin/banner/manage"},
                   {"text": "Create alert template", "url": ""}]
    form = BannerEditForm(form=request.form)
    if form.validate_on_submit():
        if form.delete.data:
            logger.info("Deleting template", user=current_username(), banner_id=banner_id)
            delete_template(banner_id)
            return redirect(url_for("admin_bp.get_banner_admin"))

        logger.info("Editing template", user=current_username(), banner_id=banner_id)
        edit_template({"id": banner_id,
                       "title": form.title.data,
                       "content": form.banner.data})
        return redirect(url_for("admin_bp.get_banner_admin"))

    banner = get_template(banner_id)
    return render_template('admin/template-edit.html',
                           breadcrumbs=breadcrumbs,
                           form=form,
                           banner=banner,
                           errors=form.errors.items())


def current_username():
    if hasattr(current_user, 'username'):
        return current_user.username
    else:
        return "unknown"
