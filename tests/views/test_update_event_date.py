import json
import unittest

import requests_mock

from config import TestingConfig
from response_operations_ui import app


survey_short_name = 'BRES'
period = '201801'

url_get_update_event_date = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise' \
                            f'/{survey_short_name}/{period}/update-events'
with open('tests/test_data/collection_exercise/collection_exercise_details.json') as json_data:
    collection_exercise = json.load(json_data)
with open('tests/test_data/survey/survey.json') as json_data:
    survey = json.load(json_data)
with open('tests/test_data/collection_exercise/events.json') as json_data:
    events = json.load(json_data)
url_put_update_event_date = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise' \
                            f'/{survey_short_name}/{period}/update-events/go_live'
url_get_collection_exercise = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{survey_short_name}/{period}'


class TestUpdateEventDate(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()
        self.get_update_event_data = {
            "collection_exercise": collection_exercise,
            "survey": survey,
            "events": events
        }
        self.update_event_form = {
            "day": "01",
            "month": "01",
            "year": "2018",
            "hour": "01",
            "minute": "00"
        }
        self.invalid_update_event_form = {
            "day": "50",
            "month": "01",
            "year": "2018",
            "hour": "01",
            "minute": "00"
        }

    @requests_mock.mock()
    def test_update_event_date_view(self, mock_request):
        mock_request.get(url_get_update_event_date, json=self.get_update_event_data)

        response = self.app.get(f"/surveys/{survey_short_name}/{period}/event/go_live")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Go Live".encode(), response.data)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00 GMT".encode(), response.data)
        self.assertIn("Must be before Return by Thursday 11 Oct 2018 23:00 GMT".encode(), response.data)

    @requests_mock.mock()
    def test_update_event_date_view_fail(self, mock_request):
        mock_request.get(url_get_update_event_date, status_code=500)

        response = self.app.get(f"/surveys/{survey_short_name}/{period}/event/go_live", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_get_collection_exercise, json=collection_exercise)

        response = self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                 data=self.update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_put_update_event_date_invalid_form(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_get_update_event_date, json=self.get_update_event_data)

        response = self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                 data=self.invalid_update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00 GMT".encode(), response.data)
        self.assertIn("Error updating Go Live date".encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date_update_bad_request(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=400)
        mock_request.get(url_get_update_event_date, json=self.get_update_event_data)

        response = self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                 data=self.update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00 GMT".encode(), response.data)
        self.assertIn("Error updating Go Live date".encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date_update_fail(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=500)

        response = self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                 data=self.update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)
