import json
import os
from urllib.parse import urlparse

import fakeredis
import requests_mock

from config import TestingConfig
from response_operations_ui.views.update_event_date import (
    is_viewed_reminder_last_in_sequence,
)
from tests.views import ViewTestCase

collection_exercise_id = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
survey_short_name = "BRES"
period = "201801"
tag = "go_live"
project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/collection_exercise/collection_exercise.json") as json_data:
    collection_exercise = json.load(json_data)
with open(f"{project_root}/test_data/collection_exercise/collection_exercise_details.json") as json_data:
    collection_exercise_details = json.load(json_data)
with open(f"{project_root}/test_data/survey/single_survey.json") as json_data:
    survey = json.load(json_data)
with open(f"{project_root}/test_data/collection_exercise/events.json") as json_data:
    events = json.load(json_data)
with open(f"{project_root}/test_data/collection_exercise/nudge_events.json") as json_data:
    nudge_events = json.load(json_data)
with open(f"{project_root}/test_data/collection_exercise/events_2030.json") as json_data:
    events_2030 = json.load(json_data)
url_put_update_event_date = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises" f"/{collection_exercise_id}/events/{tag}"
)
url_put_update_nudge_event_date = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises" f"/{collection_exercise_id}/events/nudge_email_4"
)
url_delete_event = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises" f"/{collection_exercise_id}/events/nudge_email_0"
)
url_survey_shortname = f"{TestingConfig.SURVEY_URL}/surveys/shortname/{survey_short_name}"
url_collection_exercise_survey_id = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey" f"/{survey_id}"
)
url_get_collection_exercise_events = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}" f"/collectionexercises/{collection_exercise_id}/events"
)


class TestUpdateEventDate(ViewTestCase):
    def setup_data(self):
        self.get_update_event_data = {"collection_exercise": collection_exercise, "survey": survey, "events": events}
        self.update_event_form = {"day": "01", "month": "01", "year": "2030", "hour": "01", "minute": "00"}
        self.invalid_update_event_form = {"day": "50", "month": "01", "year": "2018", "hour": "01", "minute": "00"}

        self.past_update_event_form = {"day": "01", "month": "01", "year": "2018", "hour": "01", "minute": "00"}

        self.delete_nudge_email_form = {
            "day": "01",
            "month": "01",
            "year": "2030",
            "hour": "01",
            "minute": "00",
            "checkbox": "True",
        }

        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )

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
        event = {
            "event": {
                "id": "528424f3-aa43-48e9-b7ba-a4c59fde9984",
                "eventPK": 18,
                "tag": "return_by",
                "timestamp": "2020-06-12T11:00:00.000Z",
                "collectionExercise": {
                    "id": "658a305b-1947-40f7-abf1-f99399be36e6",
                    "exercisePK": 7,
                    "actualExecutionDateTime": None,
                    "scheduledExecutionDateTime": "2020-06-10T06:00:00.000Z",
                    "scheduledStartDateTime": "2020-06-10T06:00:00.000Z",
                    "actualPublishDateTime": None,
                    "periodStartDateTime": "2020-06-10T06:00:00.000Z",
                    "periodEndDateTime": None,
                    "scheduledReturnDateTime": "2020-06-12T11:00:00.000Z",
                    "scheduledEndDateTime": None,
                    "executedBy": None,
                    "state": "CREATED",
                    "sampleSize": None,
                    "exerciseRef": "011",
                    "userDescription": "May 2020",
                    "created": "2020-06-05T13:21:31.361Z",
                    "updated": "2020-06-05T21:39:21.073Z",
                    "deleted": None,
                    "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d",
                },
                "created": "2020-06-05T13:22:31.448Z",
                "updated": None,
                "deleted": False,
                "messageSent": None,
            },
            "info": "This is a test",
        }
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.put(url_put_update_event_date, status_code=200, json=event)

        response = self.client.post(f"/surveys/{survey_short_name}/{period}/event/go_live", data=self.update_event_form)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, f"/surveys/{survey_short_name}/{period}")

    @requests_mock.mock()
    def test_put_update_event_date_no_collection_exercise(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[])

        response = self.client.post(
            f"/surveys/{survey_short_name}/{period}/event/go_live", data=self.update_event_form, follow_redirects=True
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_put_update_event_date_invalid_form(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.post(
            f"/surveys/{survey_short_name}/{period}/event/go_live",
            data=self.invalid_update_event_form,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Must be after MPS Thursday 11 Oct 2018 23:00".encode(), response.data)

    @requests_mock.mock()
    def test_delete_nudge_email_form(self, mock_request):
        mock_request.post(url_delete_event, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events_2030)

        response = self.client.post(
            f"/surveys/{survey_short_name}/{period}/event/nudge_email_0", data=self.delete_nudge_email_form
        )

        self.assertEqual(response.status_code, 302)

    @requests_mock.mock()
    def test_nudge_email_event_date_invalid_form(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=nudge_events)
        create_ce_event_form = {"day": "15", "month": "10", "year": "2018", "hour": "01", "minute": "00"}

        response = self.client.post(
            f"/surveys/{survey_short_name}/{period}/event/nudge_email_4",
            data=create_ce_event_form,
            follow_redirects=True,
        )

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
        self.assertNotIn("Yes".encode(), response.data)

    @requests_mock.mock()
    def test_remove_event_is_present_for_nudge_email(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events_2030)

        response = self.client.get(
            f"/surveys/{survey_short_name}/{period}/event/nudge_email_0", data=self.delete_nudge_email_form
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Yes".encode(), response.data)

    @requests_mock.mock()
    def test_remove_event_is_present_for_reminder_email(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events_2030)

        response = self.client.get(
            f"/surveys/{survey_short_name}/{period}/event/reminder2", data=self.delete_nudge_email_form
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Yes".encode(), response.data)

    @requests_mock.mock()
    def test_remove_event_is_disabled_for_reminder_email(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events_2030)

        response = self.client.get(
            f"/surveys/{survey_short_name}/{period}/event/reminder", data=self.delete_nudge_email_form
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("To remove this event, delete more recent reminders first.".encode(), response.data)
        self.assertIn("Disabled".encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date_update_bad_request(self, mock_request):
        mock_request.put(
            url_put_update_event_date,
            status_code=400,
            text='{"error":{"code":"BAD_REQUEST","timestamp":'
            ' "20190328133054682","message":'
            '"Collection exercise events must be set '
            'sequentially"}}',
        )
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.post(
            f"/surveys/{survey_short_name}/{period}/event/go_live", data=self.update_event_form, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection exercise events must be set sequentially".encode(), response.data)

    @requests_mock.mock()
    def test_put_update_event_date_update_service_fail(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.put(url_put_update_event_date, status_code=500)

        response = self.client.post(
            f"/surveys/{survey_short_name}/{period}/event/go_live", data=self.update_event_form, follow_redirects=True
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_put_update_event_date_in_past(self, mock_request):
        mock_request.put(url_put_update_event_date, status_code=201)
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.post(
            f"/surveys/{survey_short_name}/{period}/event/go_live",
            data=self.past_update_event_form,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Selected date can not be in the past".encode(), response.data)

    def test_get_reminder_del_visibility_for_non_reminder_tag(self):
        existing_events = [
            {
                "id": "1edcb763-608d-4c18-bf07-85cf09e9d0a6",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "mps",
                "timestamp": "2020-08-01T06:00:00.000Z",
            },
            {
                "id": "90df0b3f-cbd0-4107-90b1-30f351fec0af",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "go_live",
                "timestamp": "2020-08-02T06:00:00.000Z",
            },
            {
                "id": "116db676-9b4a-417b-90f2-8d44e2f78b77",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "return_by",
                "timestamp": "2020-08-30T06:00:00.000Z",
            },
        ]
        res = is_viewed_reminder_last_in_sequence(existing_events, "mps")
        self.assertEqual(res, None)

    def test_get_reminder_del_visibility_for_reminder_tag_when_reminder2_exists(self):
        existing_events = [
            {
                "id": "1edcb763-608d-4c18-bf07-85cf09e9d0a6",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "mps",
                "timestamp": "2020-08-01T06:00:00.000Z",
            },
            {
                "id": "90df0b3f-cbd0-4107-90b1-30f351fec0af",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "go_live",
                "timestamp": "2020-08-02T06:00:00.000Z",
            },
            {
                "id": "116db676-9b4a-417b-90f2-8d44e2f78b77",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "return_by",
                "timestamp": "2020-08-30T06:00:00.000Z",
            },
            {
                "id": "29f16e05-c275-4563-8a89-01393448e0c8",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "reminder",
                "timestamp": "2020-08-30T06:00:00.000Z",
            },
            {
                "id": "b15964d5-10e7-4ddc-a95a-a97d76ed3836",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "reminder2",
                "timestamp": "2020-09-01T06:00:00.000Z",
            },
        ]
        res = is_viewed_reminder_last_in_sequence(existing_events, "reminder")
        self.assertEqual(res, False)

    def test_get_reminder_del_visibility_for_reminder2_tag_when_reminder_exists(self):
        existing_events = [
            {
                "id": "1edcb763-608d-4c18-bf07-85cf09e9d0a6",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "mps",
                "timestamp": "2020-08-01T06:00:00.000Z",
            },
            {
                "id": "90df0b3f-cbd0-4107-90b1-30f351fec0af",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "go_live",
                "timestamp": "2020-08-02T06:00:00.000Z",
            },
            {
                "id": "116db676-9b4a-417b-90f2-8d44e2f78b77",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "return_by",
                "timestamp": "2020-08-30T06:00:00.000Z",
            },
            {
                "id": "29f16e05-c275-4563-8a89-01393448e0c8",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "reminder",
                "timestamp": "2020-08-30T06:00:00.000Z",
            },
            {
                "id": "b15964d5-10e7-4ddc-a95a-a97d76ed3836",
                "collectionExerciseId": "d46b1fb1-da30-4624-aee1-2fe51eb87d08",
                "tag": "reminder2",
                "timestamp": "2020-09-01T06:00:00.000Z",
            },
        ]
        res = is_viewed_reminder_last_in_sequence(existing_events, "reminder2")
        self.assertEqual(res, True)
