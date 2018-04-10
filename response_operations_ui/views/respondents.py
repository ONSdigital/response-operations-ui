import logging

from flask import Blueprint, redirect, render_template, request, url_for
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
    response = None

    if form.validate_on_submit():
        email = request.form.get('query')

        respondent = respondent_controllers.search_respondent_by_email(email)

        if respondent.get('id'):
            return redirect(url_for('respondent_bp.respondent_details', respondent_id=respondent['id']))
        else:
            response = respondent['Response']

    return render_template('search-respondent.html', response=response, form=form, breadcrumbs=breadcrumbs)


@respondent_bp.route('/respondent-details/<respondent_id>', methods=['GET'])
@login_required
def respondent_details(respondent_id):

    respondent = contact_details_controller.get_contact_details(respondent_id)

    breadcrumbs = [
        {
            "title": "Respondents",
            "link": "/respondents"
        },
        {
            "title": f"{respondent['firstName']} {respondent['lastName']}"
        }
    ]

    respondent['status'] = respondent['status'].title()
    return render_template('respondent.html', respondent=respondent, breadcrumbs=breadcrumbs)
