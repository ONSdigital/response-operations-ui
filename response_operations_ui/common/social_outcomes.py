from collections import namedtuple


SocialOutcome = namedtuple('SocialOutcome', 'reference_string formatted_string status')


_SOCIAL_OUTCOMES = [
    SocialOutcome('PRIVACY_DATA_CONFIDENTIALITY_CONCERNS', '411 Privacy Concerns/Data security/confidentiality concerns', 'REFUSAL'),  # NOQA
    SocialOutcome('LEGITIMACY_CONCERNS', '412 Legitimacy concerns', 'REFUSAL'),
    SocialOutcome('OTHER_OUTRIGHT_REFUSAL', '413 Other outright refusal (further detail in notes)', 'REFUSAL'),
    SocialOutcome('ILL_AT_HOME', '511 Ill at home during survey period: notified to Head Office', 'OTHERNONRESPONSE'),
    SocialOutcome('IN_HOSPITAL', '521 Away/In hospital throughout field period: notified to Head Office', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('PHYSICALLY_OR_MENTALLY_UNABLE', '531 Physically or mentally unable/incompetent: notified to Head Office', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('LANGUAGE_DIFFICULTIES', '541 Language difficulties: notified to Head Office', 'OTHERNONRESPONSE'),
    SocialOutcome('FULL_INTERVIEW_REQUEST_DATA_DELETED', '561 Full interview achieved but respondent requested data be deleted', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('PARTIAL_INTERVIEW_REQUEST_DATA_DELETED', '562 Partial interview achieved but respondent requested data be deleted', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('FULL_INTERVIEW_REQUEST_DATA_DELETED_INCORRECT', '563 Full interview achieved but respondent requested data be deleted as it is incorrect', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('PARTIAL_INTERVIEW_REQUEST_DATA_DELETED_INCORRECT', '564 Partial interview achieved but respondent requested data be deleted as it is incorrect', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('LACK_OF_COMPUTER_INTERNET_ACCESS', '571 Lack of computer or internet access', 'OTHERNONRESPONSE'),
    SocialOutcome('TOO_BUSY', '572 Too busy', 'OTHERNONRESPONSE'),
    SocialOutcome('OTHER_CIRCUMSTANTIAL_REFUSAL', '573 Other circumstantial refusal (further detail in notes)', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('COMPLY_IN_DIFFERENT_COLLECTION_MODE', '581 Willing to comply in a different collection mode', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('REQUEST_TO_COMPLETE_IN_ALTERNATIVE_FORMAT', '582 Request to complete in an alternative format which is not currently available (e.g. telephone, paper). Refuses available modes', 'OTHERNONRESPONSE'),  # NOQA
    SocialOutcome('NO_TRACE_OF_ADDRESS', '632 No trace of address: returned mail to Head Office', 'UNKNOWNELIGIBILITY'),  # NOQA
    SocialOutcome('WRONG_ADDRESS', '633 Wrong Address', 'UNKNOWNELIGIBILITY'),
    SocialOutcome('VACANT_OR_EMPTY', '730 Vacant/empty', 'NOTELIGIBLE'),
    SocialOutcome('NON_RESIDENTIAL_ADDRESS', '740 Non-residential address', 'NOTELIGIBLE'),
    SocialOutcome('ADDRESS_OCCUPIED_NO_RESIDENT', '750 Address occupied, but no resident household/resident(s)', 'NOTELIGIBLE'),  # NOQA
    SocialOutcome('COMMUNAL_ESTABLISHMENT_INSTITUTION', '760 Communal establishment/institution', 'NOTELIGIBLE'),
    SocialOutcome('DWELLING_OF_FOREIGN_SERVICE_PERSONNEL_DIPLOMATS', '771 Dwelling of foreign service personnel/diplomats', 'NOTELIGIBLE'),  # NOQA
    SocialOutcome('NO_PERSON_IN_ELIGIBLE_AGE_RANGE', '772 No person in eligible age range', 'NOTELIGIBLE'),
    SocialOutcome('DECEASED', '792 Deceased', 'NOTELIGIBLE')
]

SOCIAL_OUTCOMES_MAP = {outcome.reference_string: outcome for outcome in _SOCIAL_OUTCOMES}


def map_social_case_status(case_response_status):
    return {
        'NOTSTARTED': 'Not started',
        'INPROGRESS': 'In progress',
        'COMPLETE': 'Completed',
        'REFUSAL': 'Refusal',
        'OTHERNONRESPONSE': 'Other Non-Response',
        'UNKNOWNELIGIBILITY': 'Unknown Eligibility',
        'NOTELIGIBLE': 'Not Eligible'
    }.get(case_response_status, case_response_status)


def map_social_status_groups(case_response_status):
    return {
        'REFUSAL': '400 Refusal',
        'OTHERNONRESPONSE': '500 Other Non-Response',
        'UNKNOWNELIGIBILITY': '600 Unknown Eligibility',
        'NOTELIGIBLE': '700 Not Eligible'
    }.get(case_response_status, case_response_status)


def get_formatted_social_outcome(social_outcome, default_to_none=False):
    try:
        return SOCIAL_OUTCOMES_MAP[social_outcome].formatted_string
    except KeyError:
        return None if default_to_none else social_outcome


def get_social_status_from_event(social_case_event):
    try:
        return SOCIAL_OUTCOMES_MAP[social_case_event].status
    except KeyError:
        return None
