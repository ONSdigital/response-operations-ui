import json
from urllib.parse import urlparse

import requests_mock

from config import TestingConfig
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
with open('tests/test_data/collection_exercise/nudge_events_two.json') as json_data:
    nudge_events_two = json.load(json_data)
with open('tests/test_data/collection_exercise/events_2030.json') as json_data:
    events_2030 = json.load(json_data)
url_put_update_event_date = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises'
    f'/{collection_exercise_id}/events/{tag}'
)
url_put_update_nudge_event_date = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises'
    f'/{collection_exercise_id}/events/nudge_email_4'
)
url_delete_event = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises'
    f'/{collection_exercise_id}/events/nudge_email_0'
)
url_survey_shortname = f'{TestingConfig.SURVEY_URL}/surveys/shortname/{survey_short_name}'
url_collection_exercise_survey_id = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey'
    f'/{survey_id}'
)
url_get_collection_exercise_events = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}'
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
            "year": "2030",
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

        self.past_update_event_form = {
            "day": "01",
            "month": "01",
            "year": "2018",
            "hour": "01",
            "minute": "00"
        }

        self.delete_nudge_email_form = {
            "day": "01",
            "month": "01",
            "year": "2030",
            "hour": "01",
            "minute": "00",
            "checkbox": "True"
        }

    @requests_mock.mock()
    def test_update_event_date_view(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.get(f"/surveys/{survey_short_name}/{period}/event/go_live")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Go Live".encode(), response.data)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00".encode(), response.data)
        self.assertIn("Must be before Return by Thursday 11 Oct 2018 23:00".encode(), response.data)

    @requests_mock.mock()
    def test_update_event_no_collection_exercise(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[])

        response = self.client.get(f"/surveys/{survey_short_name}/{period}/event/go_live")

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_event_date_service_fail(self, mock_request):
        mock_request.get(url_survey_shortname, status_code=500)

        response = self.client.get(f"/surveys/{survey_short_name}/{period}/event/go_live", follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_put_update_event_date(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.put(url_put_update_event_date, status_code=201)

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                    data=self.update_event_form)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, f'/surveys/{survey_short_name}/{period}')

    @requests_mock.mock()
    def test_put_update_event_date_no_collection_exercise(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[])

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                    data=self.update_event_form, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_put_update_event_date_invalid_form(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                    data=self.invalid_update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00".encode(), response.data)
        self.assertIn("Error updating Go Live date".encode(), response.data)

    @requests_mock.mock()
    def test_delete_nudge_email_form(self, mock_request):
        mock_request.post(url_delete_event, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events_2030)

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/nudge_email_0",
                                    data=self.delete_nudge_email_form)

        self.assertEqual(response.status_code, 302)

    @requests_mock.mock()
    def test_nudge_email_event_date_invalid_form(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=nudge_events_two)
        create_ce_event_form = {
            "day": "15",
            "month": "10",
            "year": "2018",
            "hour": "01",
            "minute": "00"
        }

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/nudge_email_4",
                                    data=create_ce_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Maximum of five nudge email allowed".encode(), response.data)
        self.assertIn("Must be after Go Live Thursday 11 Oct 2018 23:00".encode(), response.data)
        self.assertIn("Must be before Return by Tuesday 30 Oct 2018 22:00".encode(), response.data)

    @requests_mock.mock()
    def test_remove_event_is_not_present(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.get(f"/surveys/{survey_short_name}/{period}/event/go_live")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Remove Event".encode(), response.data)

    @requests_mock.mock()
    def test_remove_event_is_present(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events_2030)

        response = self.client.get(f"/surveys/{survey_short_name}/{period}/event/nudge_email_0",
                                   data=self.delete_nudge_email_form)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Remove Event".encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date_update_bad_request(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=400, text='{"error":{"code":"BAD_REQUEST","timestamp":'
                                                                          ' "20190328133054682","message":'
                                                                          '"Collection exercise events must be set '
                                                                          'sequentially"}}')
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                    data=self.update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Collection exercise events must be set sequentially'.encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date_update_service_fail(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.put(url_put_update_event_date, status_code=500)

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                    data=self.update_event_form, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_put_update_event_date_in_past(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/go_live",
                                    data=self.past_update_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Selected date can not be in the past".encode(), response.data)
        self.assertIn("Error updating Go Live date".encode(), response.data)
