from flask import Blueprint, request, render_template, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from response_operations_ui.common.mappers import format_short_name, map_ce_response_status
from response_operations_ui.controllers import case_controller, collection_exercise_controllers, \
    party_controller, survey_controllers
from response_operations_ui.forms import ChangeGroupStatusForm

case_bp = Blueprint('case_bp', __name__, static_folder='static', template_folder='templates')


@case_bp.route('/<ru_ref>/change-response-status', methods=['GET'])
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
    current_status = case_controller.get_case_group_status_by_collection_exercise(case_groups, exercise['id'])

    return render_template('change-response-status.html',
                           ru_ref=ru_ref, ru_name=reporting_unit['name'], trading_as=reporting_unit['trading_as'],
                           survey_short_name=format_short_name(survey['shortName']), survey_ref=survey['surveyRef'],
                           ce_period=period,
                           statuses=available_statuses, case_group_status=map_ce_response_status(current_status),
                           error=error)


@case_bp.route('/<ru_ref>/change-response-status', methods=['POST'])
@login_required
def update_response_status(ru_ref):
    short_name = request.args.get('survey')
    period = request.args.get('period')
    form = ChangeGroupStatusForm(request.form)

    if not form.event.data:
        return redirect(url_for('case_bp.get_response_statuses',
                                ru_ref=ru_ref, survey=short_name, period=period,
                                error="Please select one of these options"))

    # Retrieve the correct collection exercise and update case group status
    survey = survey_controllers.get_survey_by_shortname(short_name)
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])
    exercise = collection_exercise_controllers.get_collection_exercise_from_list(exercises, period)
    case_controller.update_case_group_status(exercise['id'], ru_ref, form.event.data)

    return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref,
                    survey=short_name, period=period))
