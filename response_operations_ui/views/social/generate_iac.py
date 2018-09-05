import logging

from flask import render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import case_controller
from response_operations_ui.views.social.view_social_case_context import build_view_social_case_context

logger = wrap_logger(logging.getLogger(__name__))


@login_required
def generate_iac():
    case_id = request.form['case_id']

    new_iac = case_controller.generate_iac(case_id)
    context = build_view_social_case_context(case_id)
    logger.debug("generate_iac", case_id=case_id, new_iac=new_iac)

    context['new_iac'] = new_iac

    return render_template('social-view-case-details.html', **context)
