import unittest
from unittest import mock

from response_operations_ui.controllers import collection_exercise_controllers
from response_operations_ui import app


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == f'{app.config["BACKSTAGE_API_URL"]}/collection-exercise/BRES/201801':
        return MockResponse({
            "survey": "survey",
            "collection_exercise": "exercise",
            "collection_instruments": "collection_instruments"
        }, 200)

    return MockResponse(None, 404)


# Our test case class
class TestSurveyControllers(unittest.TestCase):

    # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_fetch(self, mock_get):
        # Assert requests.get calls
        json_data = collection_exercise_controllers.get_collection_exercise("BRES", "201801")
        self.assertEqual(json_data, {
            "survey": "survey",
            "collection_exercise": "exercise",
            "collection_instruments": "collection_instruments"
        })
