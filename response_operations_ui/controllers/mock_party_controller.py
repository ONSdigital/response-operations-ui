import json

from flask import current_app as app


def mock_search_respondents(first_name, last_name, email_address, page=1):
    with open('response_operations_ui/data/mock_search_respondents_data.json', 'r') as json_data:
        data = json.load(json_data)
        limit = app.config['PARTY_RESPONDENTS_PER_PAGE']

        chunk_range = range((len(data) + limit - 1) // limit)
        data_by_surname = sorted(data, key=lambda dict: dict["lastName"].lower())
        sorted_data = filter_json_by_passed_parameters(data_by_surname, first_name, last_name, email_address)
        data_chunks = [sorted_data[i * limit:(i + 1) * limit] for i in chunk_range]

        return {
            'data': data_chunks[int(page) - 1],
            'total': len(sorted_data)
        }


def filter_json_by_passed_parameters(sorted_data, first_name='', last_name='', email_address=''):
    if first_name:
        sorted_data = [a for a in sorted_data if a['firstName'].lower().startswith(first_name.lower())]

    if last_name:
        sorted_data = [a for a in sorted_data if a['lastName'].lower().startswith(last_name.lower())]

    if email_address:
        sorted_data = [a for a in sorted_data if email_address.lower() in a['emailAddress']]

    return sorted_data
