import re
from datetime import datetime, timezone

import iso8601

from response_operations_ui.common.dates import localise_datetime


def format_short_name(short_name):
    """
    This regex function returns a short name value without spaces
    e.g. Sand & Gravel -> Sand&Gravel
    """
    return re.sub('(&)', r' \1 ', short_name)


def convert_events_to_new_format(events):
    formatted_events = {}
    for event in events:
        date_time_utc = iso8601.parse_date(event['timestamp'])
        localised_datetime = localise_datetime(date_time_utc)
        formatted_events[event['tag']] = {
            "day": localised_datetime.strftime('%A'),
            "date": localised_datetime.strftime('%d %b %Y'),
            "month": localised_datetime.strftime('%m'),
            "time": localised_datetime.strftime('%H:%M'),
            "is_in_future": date_time_utc > iso8601.parse_date(datetime.now(timezone.utc).isoformat())
        }
    return formatted_events


def map_collection_exercise_state(ce_state):
    return {
        'CREATED': 'Created',
        'SCHEDULED': 'Scheduled',
        'READY_FOR_REVIEW': 'Ready for review',
        'FAILEDVALIDATION': 'Ready for review',
        'EXECUTION_STARTED': 'Setting ready for live',
        'VALIDATED': 'Setting ready for live',
        'EXECUTED': 'Setting ready for live',
        'READY_FOR_LIVE': 'Ready for live',
        'LIVE': 'Live',
    }.get(ce_state, ce_state)


def map_ce_response_status(ce_response_status):
    return {
        'NOTSTARTED': "Not started",
        'INPROGRESS': "In progress",
        'COMPLETE': "Completed",
        'COMPLETEDBYPHONE': 'Completed by phone',
        'NOLONGERREQUIRED': 'No longer required',
    }.get(ce_response_status, ce_response_status)


def map_social_case_status(case_response_status):
    return {
        'NOTSTARTED': "Not started",
        'INPROGRESS': "In progress",
        'COMPLETE': "Completed",
        'REOPENED': 'Reopened',
        'REFUSAL': 'Refusal',
        'OTHERNONRESPONSE': 'Other Non-Response',
        'UNKNOWNELIGIBILITY': 'Unknown Eligibility',
        'NOTELIGIBLE': 'Not Eligible'
    }.get(case_response_status, case_response_status)


def map_social_case_status_by_number(case_response_status):
    return {
        'REFUSAL': '400 Refusal',
        'OTHERNONRESPONSE': '500 Other Non-Response',
        'UNKNOWNELIGIBILITY': '600 Unknown Eligibility',
        'NOTELIGIBLE': '700 Not Eligible'
    }.get(case_response_status, case_response_status)


def map_social_case_event(case_response_status, default_to_none=False):
    return {
        'PRIVACY_DATA_CONFIDENTIALITY_CONCERNS': '411 Privacy Concerns/Data security/confidentiality concerns',
        'LEGITIMACY_CONCERNS': '412 Legitimacy concerns',
        'OTHER_OUTRIGHT_REFUSAL': '413 Other outright refusal (further detail in notes)',
        'ILL_AT_HOME': '511 Ill at home during survey period: notified to Head Office',
        'IN_HOSPITAL': '521 Away/In hospital throughout field period: notified to Head Office',
        'PHYSICALLY_OR_MENTALLY_UNABLE': '531 Physically or mentally unable/incompetent: notified to Head Office',
        'LANGUAGE_DIFFICULTIES': '541 Language difficulties: notified to Head Office',
        'FULL_INTERVIEW_REQUEST_DATA_DELETED': '561 Full interview achieved but respondent requested data be deleted',
        'PARTIAL_INTERVIEW_REQUEST_DATA_DELETED': '562 Partial interview achieved but respondent requested data be deleted',  # NOQA
        'FULL_INTERVIEW_REQUEST_DATA_DELETED_INCORRECT': '563 Full interview achieved but respondent requested data be deleted as it is incorrect',  # NOQA
        'PARTIAL_INTERVIEW_REQUEST_DATA_DELETED_INCORRECT': '564 Partial interview achieved but respondent requested data be deleted as it is incorrect',  # NOQA
        'LACK_OF_COMPUTER_INTERNET_ACCESS': '571 Lack of computer or internet access',
        'TOO_BUSY': '572 Too busy',
        'OTHER_CIRCUMSTANTIAL_REFUSAL': '573 Other circumstantial refusal (Further detail to be provided in the notes field)',  # NOQA
        'COMPLY_IN_DIFFERENT_COLLECTION_MODE': '581 Willing to comply in a different collection mode',
        'REQUEST_TO_COMPLETE_IN_ALTERNATIVE_FORMAT': '582 Request to complete in an alternative format which is not currently available (e.g. telephone, paper). Refuses available modes',  # NOQA
        'NO_TRACE_OF_ADDRESS': '632 No trace of address: returned mail to Head Office',
        'WRONG_ADDRESS': '633 Wrong Address',
        'VACANT_OR_EMPTY': '730 Vacant/empty',
        'NON_RESIDENTIAL_ADDRESS': '740 Non-residential address',
        'ADDRESS_OCCUPIED_NO_RESIDENT': '750 Address occupied, but no resident household/resident(s)',
        'COMMUNAL_ESTABLISHMENT_INSTITUTION': '760 Communal establishment/institution',
        'DWELLING_OF_FOREIGN_SERVICE_PERSONNEL_DIPLOMATS': '771 Dwelling of foreign service personnel/diplomats',
        'NO_PERSON_IN_ELIGIBLE_AGE_RANGE': '772 No person in eligible age range',
        'DECEASED': '792 Deceased'
    }.get(case_response_status, None if default_to_none else case_response_status)


def map_region(region):
    return "NI" if region == "YY" else "GB"
