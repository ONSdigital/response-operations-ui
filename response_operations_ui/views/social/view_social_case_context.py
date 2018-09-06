import logging

from structlog import wrap_logger

from response_operations_ui.common.mappers import map_social_case_status
from response_operations_ui.controllers import case_controller, sample_controllers

logger = wrap_logger(logging.getLogger(__name__))


def build_view_social_case_context(case_id):
    social_case = case_controller.get_case_by_id(case_id)
    context = dict()

    context['attributes'] = sample_controllers.get_sample_attributes(social_case['sampleUnitId'])['attributes']
    context['status'] = map_social_case_status(social_case['caseGroup']['caseGroupStatus'])
    context['case_id'] = case_id
    context['iac_count'] = case_controller.get_iac_count_for_case(case_id)
    context['displayed_attributes'] = ['ADDRESS_LINE1', 'ADDRESS_LINE2', 'LOCALITY', 'TOWN_NAME', 'POSTCODE']
    context['case_reference'] = social_case['caseGroup']['sampleUnitRef']

    return context
