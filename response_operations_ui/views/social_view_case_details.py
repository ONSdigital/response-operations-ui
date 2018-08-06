import json
import logging
from flask import Blueprint, render_template
from flask_login import login_required
from structlog import wrap_logger
from response_operations_ui.controllers import case_controller, sample_controllers
from response_operations_ui.common.mappers import map_social_case_status
from response_operations_ui.forms import SearchForm

logger = wrap_logger(logging.getLogger(__name__))
social_bp = Blueprint('social_bp', __name__,
                      static_folder='static', template_folder='templates')


@social_bp.route('/case/<case_id>', methods=['GET'])
@login_required
def view_social_case_details(case_id):
    form = SearchForm()  # TODO Remove banner before committing

    # with open('tests/test_data/case/social_case.json') as fp:
    #     mocked_case = json.load(fp)
    # with open('tests/test_data/sample/sample_attributes.json') as fp:
    #     mocked_attributes = json.load(fp)
    # mocked_case_id = case_id['id']
    # mocked_sample_unit_id = social_case['sampleUnitId']
    # mocked_case_status = social_case['caseGroup']['caseGroupStatus']

    social_case = case_controller.get_case_by_id(case_id)
    sample_attributes = sample_controllers.get_sample_attributes(social_case['sampleUnitId'])

    social_case['caseGroup']['caseGroupStatus'] = map_social_case_status(social_case['caseGroup']['caseGroupStatus'])

    return render_template('social-view-case-details.html', attributes=sample_attributes['attributes'],
                           status=social_case['caseGroup'], form=form)
