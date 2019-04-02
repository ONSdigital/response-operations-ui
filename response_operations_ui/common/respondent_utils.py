import logging
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def status_enum_to_string(status):
    enum_lookup = {
        'ACTIVE': 'Active',
        'CREATED': 'Created',
        'SUSPENDED': 'Suspended',
        'LOCKED': 'Locked'
    }
    return enum_lookup.get(status)


def status_enum_to_class(status):
    enum_lookup = {
        'ACTIVE': 'status--success',
        'CREATED': 'status--info',
        'SUSPENDED': 'status--warning',
        'LOCKED': 'status--dead'
    }
    return enum_lookup.get(status)


def filter_respondents(respondents):
    filtered_respondents = []
    for respondent in respondents:
        try:
            filtered_respondents.append({
                'href': '/respondents' + '/respondent-details/' + str(respondent['id']),
                'name': respondent['firstName'] + ' ' + respondent['lastName'],
                'email': respondent['emailAddress'],
                'status': status_enum_to_string(respondent['status']),
                'status_class': status_enum_to_class(respondent['status'])
            })
        except KeyError:
            logger.debug(f'Could not add respondent to retrieved list, as data structure was not that expected.')
    return filtered_respondents
