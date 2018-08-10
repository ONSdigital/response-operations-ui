import logging

from flask import Blueprint, render_template, request
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers.case_controller import get_cases_by_sample_unit_id
from response_operations_ui.controllers.sample_controllers import search_samples_by_postcode
from response_operations_ui.forms import SearchForm

logger = wrap_logger(logging.getLogger(__name__))
social_bp = Blueprint('social_bp', __name__,
                      static_folder='static', template_folder='templates')


@login_required
@social_bp.route('/', methods=['GET', 'POST'])
def social_case_search():
    form = SearchForm()

    if form.validate_on_submit():

        postcode = request.form.get('query')
        logger.info("Now retrieving cases for postcode", postcode=postcode)

        results = get_cases_by_postcode(postcode)
        return render_template('social.html',
                               results=results,
                               postcode=postcode,
                               form=form)

    return render_template('social.html',
                           results=None,
                           form=form)


def get_cases_by_postcode(postcode):
    sample_units = search_samples_by_postcode(postcode)

    if not sample_units:
        return {}

    sample_unit_ids = [sample_unit['id'] for sample_unit in sample_units]

    cases = get_cases_by_sample_unit_id(sample_unit_ids)

    case_attributes = []
    for case in cases:
        for sample_unit in sample_units:
            if sample_unit['id'] == case['sampleUnitId']:
                case_attributes.append({
                    'case': case,
                    'attributes': sample_unit['sampleAttributes']['attributes']
                })

    return case_attributes
