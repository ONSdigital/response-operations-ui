import datetime
import json
import os
import unittest

import requests_mock
import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import collection_exercise_controllers
from response_operations_ui.exceptions.exceptions import ApiError

ce_id = "4a084bc0-130f-4aee-ae48-1a9f9e50178f"
sample_summary_id = "1a11543f-eb19-41f5-825f-e41aca15e724"
survey_id = "02b9c366-7397-42f7-942a-76dc5876d86d"

url_get_sample_summary = f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}"
url_ce_by_survey = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey/{survey_id}"
ce_events_by_id_url = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/{ce_id}/events"
ce_nudge_events_by_id_url = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/{ce_id}/events/nudge"

project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/collection_exercise/ce_events_by_id.json") as fp:
    ce_events = json.load(fp)

with open(f"{project_root}/test_data/survey/survey_02b9c366.json") as fp:
    bres_survey = json.load(fp)


class TestCollectionExerciseController(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    def test_get_ce_events_by_id_all_events(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, ce_events_by_id_url, json=ce_events, status=200, content_type="applicaton/json")

            with self.app.app_context():
                collection_exercise = collection_exercise_controllers.get_collection_exercise_events_by_id(ce_id)

            self.assertIn("mps", collection_exercise[0]["tag"], "MPS not in collection exercise events")
            self.assertIn("go_live", collection_exercise[1]["tag"], "Go live not in collection exercise events")
            self.assertIn("return_by", collection_exercise[2]["tag"], "Return by not in collection exercise events")
            self.assertIn(
                "exercise_end", collection_exercise[3]["tag"], "Exercise end not in collection exercise events"
            )

    def test_get_ce_events_by_id_no_events(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, ce_events_by_id_url, json=[], status=200, content_type="applicaton/json")

            with self.app.app_context():
                collection_exercise = collection_exercise_controllers.get_collection_exercise_events_by_id(ce_id)

            self.assertEqual(len(collection_exercise), 0, "Unexpected collection exercise event returned.")

    def test_get_ce_events_by_id_http_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, ce_events_by_id_url, status=400)

            with self.app.app_context():
                self.assertRaises(ApiError, collection_exercise_controllers.get_collection_exercise_events_by_id, ce_id)

    def test_create_ce_event_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ce_events_by_id_url, status=200)

            timestamp = datetime.datetime.strptime(
                "".join("2020-01-27 07:00:00+00:00".rsplit(":", 1)), "%Y-%m-%d %H:%M:%S%z"
            )

            with self.app.app_context():
                self.assertFalse(
                    collection_exercise_controllers.create_collection_exercise_event(ce_id, "mps", timestamp)
                )

    def test_delete_ce_event_accepted(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ce_nudge_events_by_id_url, status=200)

            with self.app.app_context():
                self.assertFalse(collection_exercise_controllers.delete_event(ce_id, "nudge"))

    def test_create_ce_event_bad_request_return_false(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ce_events_by_id_url, body='{"error":{"message": "some message"}}', status=400)

            timestamp = datetime.datetime.strptime(
                "".join("2020-01-27 07:00:00+00:00".rsplit(":", 1)), "%Y-%m-%d %H:%M:%S%z"
            )

            with self.app.app_context():
                self.assertTrue(
                    collection_exercise_controllers.create_collection_exercise_event(ce_id, "mps", timestamp)
                )

    @requests_mock.mock()
    def test_get_collection_exercises_with_events_and_samples_by_survey_id(self, mock_request):
        collection_exercise_id = "14fb3e68-4dca-46db-bf49-04b84e07e77c"

        collection_exercises = [
            {
                "id": collection_exercise_id,
                "name": "201601",
                "scheduledExecutionDateTime": "2017-05-15T00:00:00Z",
                "state": "PUBLISHED",
                "exerciseRef": "000000",
                "events": [
                    {
                        "collectionExerciseId": "14fb3e68-4dca-46db-bf49-04b84e07e77c",
                        "eventStatus": "PROCESSED",
                        "id": "b4a36392-a21f-485b-9dc4-d151a8fcd565",
                        "tag": "mps",
                        "timestamp": "2018-03-16T00:00:00.000Z",
                    }
                ],
            }
        ]
        mock_request.get(url_ce_by_survey, json=collection_exercises)
        with self.app.app_context():
            ce_list = collection_exercise_controllers.get_collection_exercises_with_samples_by_survey_id(
                bres_survey["id"]
            )

        self.assertEqual(ce_list, collection_exercises)
