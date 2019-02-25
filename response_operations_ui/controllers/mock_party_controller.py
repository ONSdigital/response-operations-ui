import json


def mock_search_respondents(first_name, last_name, email_address, page=1):
    with open('response_operations_ui/data/mock_search_respondents_data.json', 'r') as json_data:
        data = json.load(json_data)
        data_chunks = [data[i * 25:(i + 1) * 25] for i in range((len(data) + 25 - 1) // 25)]

        return {
            'data': data_chunks[int(page) - 1],
            'total': len(data)
        }
