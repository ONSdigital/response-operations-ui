import logging

from flask import render_template, request, redirect, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.forms import ChangeGroupStatusForm
from response_operations_ui.common.mappers import map_social_case_status, map_social_case_event
from response_operations_ui.controllers import case_controller, sample_controllers

logger = wrap_logger(logging.getLogger(__name__))


@login_required
def view_social_case_details(case_id):
    social_case = case_controller.get_case_by_id(case_id)
    sample_attributes = sample_controllers.get_sample_attributes(social_case['sampleUnitId'])

    mapped_status = map_social_case_status(social_case['caseGroup']['caseGroupStatus'])
    sample_unit_reference = social_case['caseGroup']['sampleUnitRef']

    return render_template('social-view-case-details.html', attributes=sample_attributes['attributes'],
                           displayed_attributes=['ADDRESS_LINE1', 'ADDRESS_LINE2', 'LOCALITY', 'TOWN_NAME', 'POSTCODE'],
                           status=mapped_status, case_reference=sample_unit_reference, case_id=social_case)


@login_required
def get_case_response_statuses(case_id):
    social_case = case_controller.get_case_by_id(case_id)
    current_status = map_social_case_status(social_case['caseGroup']['caseGroupStatus'])
    sample_unit_reference = social_case['caseGroup']['sampleUnitRef']
    collection_exercise_id = social_case['caseGroup']['collectionExerciseId']

    statuses = case_controller.get_available_case_group_statuses_direct(collection_exercise_id, sample_unit_reference)
    available_statuses = {event: map_social_case_event(event)
                          for event, status in statuses.items()
                          if case_controller.is_allowed_social_status(status)}

    return render_template('social-change-response-status.html', current_status=current_status,
                           reference=sample_unit_reference, statuses=available_statuses)


@login_required
def update_case_response_status(case_id):
    info_message = 'Status changed successfully'
    form = ChangeGroupStatusForm(request.form)

    social_case = case_controller.get_case_by_id(case_id)
    ru_ref = social_case['caseGroup']['sampleUnitRef']
    collection_exercise_id = social_case['caseGroup']['collectionExerciseId']

    case_controller.update_case_group_status(collection_exercise_id, ru_ref, form.event.data)

    return redirect(url_for('social_bp.view_social_case_details', case_id=case_id, info_message=info_message))
