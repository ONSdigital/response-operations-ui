def status_enum_to_string(status):
    dict = {
        'ACTIVE': 'Active',
        'CREATED': 'Created',
        'SUSPENDED': 'Suspended',
        'LOCKED': 'Locked'
    }
    return dict.get(status, None)


def status_enum_to_class(status):
    dict = {
        'ACTIVE': 'status--success',
        'CREATED': 'status--info',
        'SUSPENDED': 'status--warning',
        'LOCKED': 'status--dead'
    }
    return dict.get(status, None)


def filter_respondents(respondents):
    filtered_respondents = []
    for respondent in respondents:
        try:
            filtered_respondents.append({
                'href': '/respondent-details/' + str(respondent['id']),
                'name': respondent['firstName'] + ' ' + respondent['lastName'],
                'email': respondent['emailAddress'],
                'status': status_enum_to_string(respondent['status']),
                'status_class': status_enum_to_class(respondent['status'])
            })
        except KeyError:
            logger.debug(f'Could not add respondent to retrieved list, as data structure was not that expected.', respondent)
    return filtered_respondents
