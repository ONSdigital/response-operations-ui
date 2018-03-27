import logging

from flask import Blueprint, render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import contact_details_controller, respondent_controllers
from response_operations_ui.forms import SearchForm


logger = wrap_logger(logging.getLogger(__name__))
respondent_bp = Blueprint('respondent_bp', __name__,
                          static_folder='static', template_folder='templates')


@respondent_bp.route('/', methods=['GET', 'POST'])
@login_required
def respondent_search():
    form = SearchForm()
    breadcrumbs = [{"title": "Respondents"}]
    respondent = None

    if form.validate_on_submit():
        email = request.form.get('email')

        respondent = respondent_controllers.search_respondent_by_email(email)

    if request.args.get('respondent_id'):
        respondent_id = request.args['respondent_id']

        respondent = contact_details_controller.get_contact_details(respondent_id)

    return render_template('search_respondent.html', respondent=respondent, form=form, breadcrumbs=breadcrumbs)