import logging

from structlog import wrap_logger

from response_operations_ui.common.social_outcomes import map_social_case_status, get_formatted_social_outcome, \
    get_social_status_from_event
from response_operations_ui.controllers import case_controller, sample_controllers
from response_operations_ui.controllers.case_controller import is_allowed_change_social_status

logger = wrap_logger(logging.getLogger(__name__))


def build_view_social_case_context(case_id):
    social_case = case_controller.get_case_by_id(case_id)
    case_events = case_controller.get_case_events_by_case_id(case_id)
    case_status = map_social_case_status(social_case['caseGroup']['caseGroupStatus'])

    context = dict()

    context['attributes'] = sample_controllers.get_sample_attributes(social_case['sampleUnitId'])['attributes']
    context['status'] = case_status
    context['case_id'] = case_id
    context['iac_count'] = case_controller.get_iac_count_for_case(case_id)
    context['displayed_attributes'] = ['ADDRESS_LINE1', 'ADDRESS_LINE2', 'LOCALITY', 'TOWN_NAME', 'POSTCODE']
    context['case_reference'] = social_case['caseGroup']['sampleUnitRef']
    context['can_change_status'] = any(map(case_controller.is_allowed_change_social_status,
                                           case_controller.get_available_case_group_statuses_direct(
                                               social_case['caseGroup']['collectionExerciseId'],
                                               social_case['caseGroup']['sampleUnitRef']
                                           ).values()))

    if is_allowed_change_social_status(social_case['caseGroup']['caseGroupStatus']):
        event_description = get_case_event_description(social_case['caseGroup']['caseGroupStatus'], case_events)
        if event_description is None:
            logger.error('Failed to find case event description', case_id=case_id, case_status=case_status)
        else:
            context['case_event_description'] = event_description

    return context


def get_case_event_description(case_status, case_events):
    try:
        last_matching_event = [case_event for case_event in case_events
                               if get_social_status_from_event(case_event.get('category')) == case_status][0]
        return get_formatted_social_outcome(last_matching_event.get('category'), default_to_none=True)
    except IndexError:
        return None
