from flask import Blueprint, request, render_template, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from response_operations_ui.common.mappers import map_ce_response_status
from response_operations_ui.controllers import case_controller
from response_operations_ui.forms import ChangeGroupStatusForm

case_bp = Blueprint('case_bp', __name__, static_folder='static', template_folder='templates')


@case_bp.route('/<ru_ref>/change-response-status', methods=['GET'])
@login_required
def get_response_statuses(ru_ref):
    short_name = request.args.get('survey')
    collection_exercise_period = request.args.get('period')
    statuses = case_controller.get_available_case_group_statuses(short_name, collection_exercise_period, ru_ref)
    statuses['available_statuses'] = {event: map_ce_response_status(status)
                                      for event, status in statuses['available_statuses'].items()}
    return render_template('change-response-status.html', ru_ref=statuses['ru_ref'], trading_as=statuses['trading_as'],
                           survey_short_name=short_name, survey_id=statuses['survey_id'],
                           ce_period=collection_exercise_period,
                           case_group_status=map_ce_response_status(statuses['current_status']),
                           statuses=statuses['available_statuses'])


@case_bp.route('/<ru_ref>/change-response-status', methods=['POST'])
@login_required
def update_response_status(ru_ref):
    short_name = request.args.get('survey')
    collection_exercise_period = request.args.get('period')
    form = ChangeGroupStatusForm(request.form)
    if form.event.data:
        case_controller.update_case_group_statuses(short_name, collection_exercise_period, ru_ref, form.event.data)
        return redirect(url_for('reporting_unit_bp.view_reporting_unit', ru_ref=ru_ref,
                        survey=short_name, period=collection_exercise_period))

    statuses = case_controller.get_available_case_group_statuses(short_name, collection_exercise_period, ru_ref)
    statuses['available_statuses'] = {event: map_ce_response_status(status)
                                      for event, status in statuses['available_statuses'].items()}
    return render_template('change-response-status.html', ru_ref=statuses['ru_ref'], trading_as=statuses['trading_as'],
                           survey_short_name=short_name, survey_id=statuses['survey_id'],
                           ce_period=collection_exercise_period,
                           case_group_status=map_ce_response_status(statuses['current_status']),
                           statuses=statuses['available_statuses'],
                           error="Please select one of these options.")
