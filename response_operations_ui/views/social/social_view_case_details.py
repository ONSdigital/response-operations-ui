import logging

from flask import render_template
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.views.social.view_social_case_context import build_view_social_case_context

logger = wrap_logger(logging.getLogger(__name__))


@login_required
def view_social_case_details(case_id):
    context = build_view_social_case_context(case_id)

    logger.debug("view_social_case_details", case_id=case_id, status=context.get('status'))

    return render_template('social-view-case-details.html', **context)
