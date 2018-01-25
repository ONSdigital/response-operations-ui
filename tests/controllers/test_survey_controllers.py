import unittest
from unittest import mock

from response_operations_ui.controllers import survey_controllers
from response_operations_ui import app


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == f'{app.config["BACKSTAGE_API_URL"]}/survey/surveys':
        return MockResponse({"survey1": "SURV1", "survey2": "SURV2"}, 200)
    elif args[0] == f'{app.config["BACKSTAGE_API_URL"]}/survey/shortname/BRES':
        return MockResponse({"survey": "BRES", "collection_exercises": "1234"}, 200)

    return MockResponse(None, 404)


# Our test case class
class TestSurveyControllers(unittest.TestCase):

    # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_fetch(self, mock_get):
        # Assert requests.get calls
        print("ABOUT TO DO A THING")
        json_data = survey_controllers.get_surveys_list()
        self.assertEqual(json_data, {"survey1": "SURV1", "survey2": "SURV2"})
        json_data = survey_controllers.get_survey('BRES')
        self.assertEqual(json_data, {"survey": "BRES", "collection_exercises": "1234"})
