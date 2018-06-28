import json
from unittest.mock import patch

import requests_mock

from response_operations_ui import app
from tests.views import ViewTestCase


collection_exercise_id = '14fb3e68-4dca-46db-bf49-04b84e07e77c'
survey_id = 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87'
survey_short_name = 'BRES'
period = '201801'
tag = 'go_live'

with open('tests/test_data/collection_exercise/collection_exercise.json') as json_data:
    collection_exercise = json.load(json_data)
with open('tests/test_data/collection_exercise/collection_exercise_details.json') as json_data:
    collection_exercise_details = json.load(json_data)
with open('tests/test_data/survey/single_survey.json') as json_data:
    survey = json.load(json_data)
with open('tests/test_data/collection_exercise/events.json') as json_data:
    events = json.load(json_data)
url_get_collection_exercise = (
    f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise'
    f'/{survey_short_name}/{period}'
)
url_put_update_event_date = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises'
    f'/{collection_exercise_id}/events/{tag}'
)
url_survey_shortname = f'{app.config["SURVEY_URL"]}/surveys/shortname/{survey_short_name}'
url_collection_exercise_survey_id = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/survey'
    f'/{survey_id}'
)
url_get_collection_exercise_events = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}'
    f'/collectionexercises/{collection_exercise_id}/events'
)


class TestUpdateEventDate(ViewTestCase):

    def setup_data(self):
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
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.app.get(f"/surveys/{survey_short_name}/{period}/event/go_live")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Go Live".encode(), response.data)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00 GMT".encode(), response.data)
        self.assertIn("Must be before Return by Thursday 11 Oct 2018 23:00 GMT".encode(), response.data)

    @requests_mock.mock()
    def test_update_event_no_collection_exercise(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.app.get(f"/surveys/{survey_short_name}/{period}/event/go_live")

        self.assertEqual(response.status_code, 404)

    @requests_mock.mock()
    def test_update_event_date_service_fail(self, mock_request):
        mock_request.get(url_survey_shortname, status_code=500)

        self.app.get(f"/surveys/{survey_short_name}/{period}/event/go_live", follow_redirects=True)

        self.assertApiError(url_survey_shortname, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_put_update_event_date(self, mock_request, mock_details):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_details.return_value = collection_exercise

        response = self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                 data=self.update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_put_update_event_date_no_collection_exercise(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                 data=self.update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 404)

    @requests_mock.mock()
    def test_put_update_event_date_invalid_form(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                 data=self.invalid_update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00 GMT".encode(), response.data)
        self.assertIn("Error updating Go Live date".encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date_update_bad_request(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=400)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                 data=self.update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00 GMT".encode(), response.data)
        self.assertIn("Error updating Go Live date".encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date_update_service_fail(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)
        mock_request.put(url_put_update_event_date, status_code=500)

        self.app.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                      data=self.update_event_form, follow_redirects=True)

        self.assertApiError(url_put_update_event_date, 500)
