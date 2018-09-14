import logging
from collections import OrderedDict

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.common.mappers import map_social_case_status, map_social_case_event, \
    map_social_case_status_groups
from response_operations_ui.controllers import case_controller
from response_operations_ui.forms import ChangeGroupStatusForm
from response_operations_ui.views.social.social_case_context import build_view_social_case_context

logger = wrap_logger(logging.getLogger(__name__))


@login_required
def view_social_case_details(case_id):
    context = build_view_social_case_context(case_id)
    logger.debug("view_social_case_details", case_id=case_id, status=context.get('status'))

    return render_template('social-view-case-details.html', **context)


@login_required
def change_case_response_status(case_id):
    social_case = case_controller.get_case_by_id(case_id)
    current_status = map_social_case_status(social_case['caseGroup']['caseGroupStatus'])
    sample_unit_reference = social_case['caseGroup']['sampleUnitRef']
    collection_exercise_id = social_case['caseGroup']['collectionExerciseId']

    statuses = case_controller.get_available_case_group_statuses_direct(collection_exercise_id, sample_unit_reference)
    available_events = filter_to_available_events(statuses)

    grouped_events = group_and_order_events(available_events, statuses)

    return render_template('social-change-response-status.html', current_status=current_status,
                           reference=sample_unit_reference, statuses=grouped_events)


def filter_to_available_events(statuses):
    available_events = {event: map_social_case_event(event)
                        for event, status in sorted(statuses.items())
                        if case_controller.is_allowed_social_status(status)}
    return available_events


def group_and_order_events(available_events, statuses):
    grouped_events = OrderedDict()
    for event, formatted_event in sorted(available_events.items(), key=lambda pair: pair[1]):
        if not grouped_events.get(map_social_case_status_groups(statuses[event])):
            grouped_events[map_social_case_status_groups(statuses[event])] = OrderedDict()
        grouped_events[map_social_case_status_groups(statuses[event])][event] = formatted_event
    return grouped_events


@login_required
def update_case_response_status(case_id):
    form = ChangeGroupStatusForm(request.form)

    social_case = case_controller.get_case_by_id(case_id)
    ru_ref = social_case['caseGroup']['sampleUnitRef']
    collection_exercise_id = social_case['caseGroup']['collectionExerciseId']

    case_controller.update_case_group_status(collection_exercise_id, ru_ref, form.event.data)
    flash('Status changed successfully', 'success')
    return redirect(url_for('social_bp.view_social_case_details', case_id=case_id,
                            status_updated=True,
                            updated_status=form.event.data))
