from flask import Blueprint, request, render_template, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from response_operations_ui.common.dates import get_formatted_date
from response_operations_ui.common.mappers import format_short_name, map_ce_response_status
from response_operations_ui.controllers import case_controller, collection_exercise_controllers, \
    party_controller, survey_controllers
from response_operations_ui.controllers.case_controller import get_case_events_by_case_id, \
    get_case_by_case_group_id
from response_operations_ui.forms import ChangeGroupStatusForm

COMPLETE_STATE = ['COMPLETEDBYPHONE', 'COMPLETE']
COMPLETED_CASE_EVENTS = ['OFFLINE_RESPONSE_PROCESSED', 'SUCCESSFUL_RESPONSE_UPLOAD', 'COMPLETED_BY_PHONE']
case_bp = Blueprint('case_bp', __name__, static_folder='static', template_folder='templates')


@case_bp.route('/<ru_ref>/response-status', methods=['GET'])
@login_required
def get_response_statuses(ru_ref, error=None):
    short_name = request.args.get('survey')
    period = request.args.get('period')

    survey = survey_controllers.get_survey_by_shortname(short_name)

    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])
    exercise = collection_exercise_controllers.get_collection_exercise_from_list(exercises, period)

    reporting_unit = party_controller.get_party_by_ru_ref(ru_ref)

    statuses = case_controller.get_available_case_group_statuses_direct(exercise['id'], ru_ref)
    available_statuses = {event: map_ce_response_status(status)
                          for event, status in statuses.items()
                          if case_controller.is_allowed_status(status)}

    case_groups = case_controller.get_case_groups_by_business_party_id(reporting_unit['id'])
    case_group = case_controller.get_case_group_by_collection_exercise(case_groups, exercise['id'])
    case_group_status = case_group['caseGroupStatus']
    case_id = get_case_by_case_group_id(case_group['id']).get('id')
    is_complete = case_group_status in COMPLETE_STATE
    completed_timestamp = get_timestamp_for_completed_case_event(case_id) if is_complete else None

    return render_template('response-status.html',
                           ru_ref=ru_ref, ru_name=reporting_unit['name'], trading_as=reporting_unit['trading_as'],
                           survey_short_name=format_short_name(survey['shortName']), survey_ref=survey['surveyRef'],
                           ce_period=period,
                           statuses=available_statuses,
                           case_group_status=map_ce_response_status(case_group_status),
                           case_group_id=case_group['id'],
                           error=error,
                           is_complete=is_complete,
                           completed_timestamp=completed_timestamp)


@case_bp.route('/<ru_ref>/response-status', methods=['POST'])
@login_required
def update_response_status(ru_ref):
    short_name = request.args.get('survey')
    period = request.args.get('period')
    case_group_id = request.args['case_group_id']
    form = ChangeGroupStatusForm(request.form)

    if not form.event.data:
        return redirect(url_for('case_bp.get_response_statuses',
                                ru_ref=ru_ref, survey=short_name, period=period,
                                error="Please select one of these options"))

    # Retrieve the correct collection exercise and update case group status
    case = case_controller.get_case_by_case_group_id(case_group_id)
    case_controller.post_case_event(case['id'], form.event.data, "Transition case group status")

    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref,
                    survey=short_name, period=period))


def get_timestamp_for_completed_case_event(case_id):
    case_events = get_case_events_by_case_id(case_id, COMPLETED_CASE_EVENTS)
    timestamp = case_events[0]['createdDateTime'].replace("T", " ").split('.')[0]

    return get_formatted_date(timestamp)
