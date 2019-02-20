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
        'ACTIVE': 'Active',
        'CREATED': 'Created',
        'SUSPENDED': 'Suspended',
        'LOCKED': 'Locked'
    }
    return dict.get(status, None)


def get_controller_args_from_request(request):
    try:
        values = request.values
    except AttributeError:
        return False

    return {
        'email_address': values.get('email_address', ''),
        'first_name': values.get('email_address', ''),
        'last_name': values.get('email_address', '')
    }


def filter_respondents(respondents):
    filtered_respondents = []
    for respondent in respondents:
        try:
            filtered_respondents.append({
                'href': '/respondent-details/' + respondent['id'],
                'name': respondent['firstName'] + ' ' + respondent['lastName'],
                'email': respondent['emailAddress'],
                'status': status_enum_to_string(respondent['status']),
                'status_class': status_enum_to_class(respondent['status'])
            })
        except KeyError:
            return []
    return filtered_respondents
