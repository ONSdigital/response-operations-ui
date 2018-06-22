import json
import unittest
from io import BytesIO

import requests_mock

from config import TestingConfig
from response_operations_ui import app

collection_exercise_event_id = 'b4a36392-a21f-485b-9dc4-d151a8fcd565'
collection_exercise_id = '14fb3e68-4dca-46db-bf49-04b84e07e77c'
collection_instrument_id = 'a32800c5-5dc1-459d-9932-0da6c21d2ed2'
period = '000000'
sample_summary_id = '1a11543f-eb19-41f5-825f-e41aca15e724'
short_name = 'ashortname'
survey_id = 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87'
survey_ref = '141'

collex_root = "tests/test_data/collection_exercise/collection_exercise_details"
no_sample = collex_root + "_no_sample.json"
failed_validation = collex_root + "_failedvalidation.json"
collex_details = collex_root + ".json"

"""Load all the necessary test data"""
with open(collex_details) as json_data:
    collection_exercise_details = json.load(json_data)

with open(no_sample) as json_data:
    collection_exercise_details_no_sample = json.load(json_data)

with open(failed_validation) as json_data:
    collection_exercise_details_failedvalidation = json.load(json_data)

with open("tests/test_data/survey/edited_survey_ce_details.json") as json_data:
    updated_survey_info = json.load(json_data)

with open("tests/test_data/survey/survey_by_id.json") as fp:
    survey_by_id = json.load(fp)

with open("tests/test_data/collection_exercise/exercise_data.json") as json_data:
    exercise_data = json.load(json_data)

"""Define URLS"""

url_get_collection_exercise = (
    f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/{short_name}/{period}'
)
url_collection_instrument = (
    f'{app.config["COLLECTION_INSTRUMENT_URL"]}'
    f'/collection-instrument-api/1.0.2/upload/{collection_exercise_id}'
)
url_collection_instrument_link = (
    f'{app.config["COLLECTION_INSTRUMENT_URL"]}'
    f'/collection-instrument-api/1.0.2/link-exercise'
    f'/{collection_instrument_id}/{collection_exercise_id}'
)
url_collection_instrument_unlink = (
    f'{app.config["COLLECTION_INSTRUMENT_URL"]}'
    f'/collection-instrument-api/1.0.2/unlink-exercise'
    f'/{collection_instrument_id}/{collection_exercise_id}'
)
url_survey_shortname = f'{app.config["SURVEY_URL"]}/surveys/shortname/{short_name}'
url_sample_service_upload = f'{app.config["SAMPLE_URL"]}/samples/B/fileupload'
url_collection_exercise_survey_id = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/survey'
    f'/{survey_id}'
)
url_collection_exercise_link = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/link'
    f'/{collection_exercise_id}'
)
url_upload_sample = f'{app.config["BACKSTAGE_API_URL"]}/v1/sample/{short_name}/{period}'
url_execute = (
    f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise'
    f'/{short_name}/{period}/execute'
)
url_update_ce = (
    f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/update-collection-exercise-details'
    f'/{collection_exercise_id}'
)
url_get_survey_by_short_name = f'{app.config["SURVEY_URL"]}/surveys/shortname/{short_name}'
url_create_collection_exercise = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises'
url_ce_remove_sample = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/unlink/{collection_exercise_id}'
    f'/sample/{sample_summary_id}'
)
url_get_collection_exercises = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}'
    f'/collectionexercises/survey/{survey_id}'
)
url_get_collection_exercise_events = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}'
    f'/collectionexercises/{collection_exercise_id}/events'
)
url_get_collection_exercises_link = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}'
    f'/collectionexercises/link/{collection_exercise_id}'
)
url_get_sample_summary = (
    f'{app.config["SAMPLE_URL"]}'
    f'/samples/samplesummary/{sample_summary_id}'
)
url_ce_by_survey = (
    f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/survey/{survey_id}'
)


class TestCollectionExercise(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()
        self.headers = {"Authorization": "test_jwt", "Content-Type": "application/json"}
        self.survey_data = {"id": survey_id}
        self.survey = {
            "id": survey_id,
            "longName": "Business Register and Employment Survey",
            "shortName": "BRES",
            "surveyRef": "221"
        }
        self.collection_exercises = [
            {
                "id": collection_exercise_id,
                "name": "201601",
                "exerciseRef": "201601",
                "scheduledExecutionDateTime": "2017-05-15T00:00:00Z",
                "state": "PUBLISHED",
                "exerciseRef": "000000"
            }
        ]
        self.collection_exercises_events = [
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "mps",
                "timestamp": "2018-03-16T00:00:00.000Z"
            }
        ]
        self.collection_exercises_link = [sample_summary_id]
        self.sample_summary = {
            "id": sample_summary_id,
            "effectiveStartDateTime": "",
            "effectiveEndDateTime": "",
            "surveyRef": "",
            "ingestDateTime": "2018-03-14T14:29:51.325Z",
            "state": "ACTIVE",
            "totalSampleUnits": 5,
            "expectedCollectionInstruments": 1
        }

    @requests_mock.mock()
    def test_collection_exercise_view(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get(f'/surveys/{short_name}/{period}')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment Survey".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_fail(self, mock_request):
        mock_request.get(url_get_collection_exercise, status_code=500)

        response = self.app.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_upload_collection_instrument(self, mock_request):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    def test_select_collection_instrument(self, mock_request):
        post_data = {
            "checkbox-answer": [collection_instrument_id],
            "ce_id": collection_exercise_id,
            "select-ci": ""
        }
        mock_request.post(url_collection_instrument_link, status_code=200)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f"/surveys/{short_name}/{period}", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instruments added".encode(), response.data)

    @requests_mock.mock()
    def test_failed_select_collection_instrument(self, mock_request):
        post_data = {"checkbox-answer": [collection_instrument_id], "ce_id": collection_exercise_id, "select-ci": ""}
        mock_request.post(url_collection_instrument_link, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f"/surveys/{short_name}/{period}", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to add collection instrument(s)".encode(), response.data)

    @requests_mock.mock()
    def test_failed_no_selected_collection_instrument(self, mock_request):
        post_data = {"checkbox-answer": [], "ce_id": "000000", "select-ci": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: No collection instruments selected".encode(), response.data)

    @requests_mock.mock()
    def test_view_collection_instrument_after_upload(self, mock_request):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)

    @requests_mock.mock()
    def test_failed_upload_collection_instrument(self, mock_request):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=500)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_bad_extension(self, mock_request):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.html"), "load-ci": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: wrong file type for collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_bad_form_type_format(self, mock_request):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_xxxxx.xlsx"), "load-ci": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn(
            "Error: invalid file name format for collection instrument".encode(), response.data
        )

    @requests_mock.mock()
    def test_no_upload_collection_instrument_bad_file_name_format(self, mock_request):
        post_data = {"ciFile": (BytesIO(b"data"), "064201803_xxxxx.xlsx"), "load-ci": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn(
            "Error: invalid file name format for collection instrument".encode(), response.data
        )

    @requests_mock.mock()
    def test_no_upload_collection_instrument_form_type_not_integer(self, mock_request):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_123E.xlsx"), "load-ci": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn(
            "Error: invalid file name format for collection instrument".encode(), response.data
        )

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_no_file(self, mock_request):
        post_data = {"load-ci": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: No collection instrument supplied".encode(), response.data)

    @requests_mock.mock()
    def test_view_collection_instrument(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get(f'/surveys/{short_name}/{period}')

        self.assertEqual(response.status_code, 200)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)

    @requests_mock.mock()
    def test_choose_collection_instrument_when_first(self, mock_request):
        with open(
            "tests/test_data/collection_exercise/collection_exercise_details_no_ci.json"
        ) as collection_exercise:
            mock_request.get(url_get_collection_exercise, json=json.load(collection_exercise))

        response = self.app.get(f'/surveys/{short_name}/{period}')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add a collection instrument. Must be XLSX".encode(), response.data)

    @requests_mock.mock()
    def test_add_another_collection_instrument_when_already_uploaded(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get(f'/surveys/{short_name}/{period}')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add another collection instrument. Must be XLSX".encode(), response.data)

    @requests_mock.mock()
    def test_upload_sample(self, mock_request):
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

        sample_data = {
            "id": sample_summary_id
        }

        collection_exercise_link = {"id": ""}

        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(
            url_collection_exercise_survey_id, status_code=200, json=exercise_data
        )
        mock_request.post(url_sample_service_upload, status_code=200, json=sample_data)
        mock_request.put(
            url_collection_exercise_link, status_code=200, json=collection_exercise_link
        )

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Loaded sample summary".encode(), response.data)
        self.assertIn("2\n".encode(), response.data)
        self.assertIn("5\n".encode(), response.data)

    @requests_mock.mock()
    def test_upload_sample_link_failure(self, mock_request):
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

        sample_data = {
            "id": sample_summary_id
        }

        collection_exercise_link = {"id": ""}

        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(
            url_collection_exercise_survey_id, status_code=200, json=exercise_data
        )
        mock_request.post(url_sample_service_upload, status_code=200, json=sample_data)
        mock_request.put(
            url_collection_exercise_link, status_code=500, json=collection_exercise_link
        )

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_upload_sample_exception(self, mock_request):
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

        sample_data = {
            "id": sample_summary_id
        }

        collection_exercise_link = {"id": ""}

        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=500, json=sample_data)
        mock_request.put(
            url_collection_exercise_link, status_code=200, json=collection_exercise_link
        )

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_failed_upload_sample(self, mock_request):
        data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

        mock_request.post(url_upload_sample, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=data, follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_sample_when_bad_extension(self, mock_request):
        data = {"sampleFile": (BytesIO(b"data"), "test.html"), "load-sample": ""}
        mock_request.get(
            url_get_collection_exercise, json=collection_exercise_details_no_sample
        )
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(
            url_collection_exercise_survey_id, status_code=200, json=exercise_data
        )

        response = self.app.post(f'/surveys/{short_name}/{period}', data=data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_sample_when_no_file(self, mock_request):
        data = {"load-sample": ""}

        mock_request.get(
            url_get_collection_exercise, json=collection_exercise_details_no_sample
        )
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(
            url_collection_exercise_survey_id, status_code=200, json=exercise_data
        )
        response = self.app.post(
            f'/surveys/{short_name}/{period}', data=data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live(self, mock_request):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=200)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live_failed(self, mock_request):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f'/surveys/{short_name}/{period}', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Failed to execute Collection Exercise".encode(), response.data)

    @requests_mock.mock()
    def test_get_processing(self, mock_request):
        collection_exercise_details["collection_exercise"]["state"] = "EXECUTION_STARTED"
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get(f'/surveys/{short_name}/{period}')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @requests_mock.mock()
    def test_failed_execution(self, mock_request):
        mock_request.get(
            url_get_collection_exercise, json=collection_exercise_details_failedvalidation
        )

        response = self.app.get(f'/surveys/{short_name}/{period}')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ready for review".encode(), response.data)
        self.assertIn("Error processing collection exercise".encode(), response.data)
        self.assertIn("Check collection instruments".encode(), response.data)

    @requests_mock.mock()
    def test_update_collection_exercise_details_success(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201907",  # NB: slight difference in value to avoid validation error
            "hidden_survey_id": survey_id,
        }
        # update survey
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.put(url_update_ce)
        # redirect to survey details
        mock_request.get(url_get_collection_exercises, json=updated_survey_info['collection_exercises'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.app.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("16th June 2019".encode(), response.data)
        self.assertIn("201906".encode(), response.data)

    @requests_mock.mock()
    def test_update_collection_exercise_details_fail(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201906",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.put(url_update_ce, status_code=500)

        response = self.app.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_get_ce_details(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.get(url_get_collection_exercises, json=updated_survey_info['collection_exercises'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        response = self.app.get(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(collection_exercise_id.encode(), response.data)

    @requests_mock.mock()
    def test_unlink_collection_instrument(self, mock_request):
        post_data = {
            "ci_id": collection_instrument_id,
            "ce_id": collection_exercise_id,
            "unselect-ci": "",
        }

        mock_request.put(url_collection_instrument_unlink, status_code=200)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f"/surveys/{short_name}/{period}", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument removed".encode(), response.data)

    @requests_mock.mock()
    def test_failed_unlink_collection_instrument(self, mock_request):
        post_data = {
            "ci_id": collection_instrument_id,
            "ce_id": collection_exercise_id,
            "unselect-ci": "",
        }

        mock_request.put(url_collection_instrument_unlink, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post(f"/surveys/{short_name}/{period}", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_success(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "123456",
        }
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.app.post(
            f"/surveys/{survey_ref}-{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("123456".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_failure(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "123456",
        }
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        mock_request.post(url_create_collection_exercise, status_code=500)

        response = self.app.post(
            f"/surveys/{survey_ref}-{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_get_create_ce_form(self, mock_request):
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        response = self.app.get(
            f"/surveys/{survey_ref}-{short_name}/create-collection-exercise", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Create collection exercise".encode(), response.data)

    @requests_mock.mock()
    def test_failed_create_ce_validation_period_exists(self, mock_request):
        taken_period = '12345'
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": taken_period,
        }
        ces = self.collection_exercises
        ces[0]['exerciseRef'] = taken_period
        mock_request.get(url_ce_by_survey, json=ces)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.app.post(
            f"/surveys/{survey_ref}-{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Please use a period that is not in use by any collection exercise for this survey".encode(),
            response.data,
        )

    @requests_mock.mock()
    def test_failed_create_ce_letters_fails_in_period_validation(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "hello",
        }
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.app.post(
            f"/surveys/{survey_ref}-{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)

    @requests_mock.mock()
    def test_failed_edit_ce_validation_period_exists(self, mock_request):
        taken_period = '12345'
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": taken_period,
            "hidden_survey_id": survey_id,
        }

        # update survey
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.put(url_update_ce)

        # failed validation
        ces = self.collection_exercises
        ces[0]['exerciseRef'] = taken_period
        mock_request.get(url_get_collection_exercises, json=ces)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.app.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Please use a period that is not in use by any collection exercise for this survey".encode(),
            response.data,
        )

    @requests_mock.mock()
    def test_failed_edit_ce_validation_letters_in_period_fails_validation(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "hello",
            "hidden_survey_id": survey_id,
        }
        # update survey
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.put(url_update_ce)

        # failed validation
        mock_request.get(url_get_collection_exercises, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercises_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.app.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)

    @requests_mock.mock()
    def test_remove_loaded_sample_success(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.delete(url_ce_remove_sample, status_code=200)
        response = self.app.post(
            f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True
        )

        self.assertEquals(response.status_code, 200)
        self.assertIn("Sample removed".encode(), response.data)

    @requests_mock.mock()
    def test_remove_loaded_sample_failed(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.delete(url_ce_remove_sample, status_code=500)
        response = self.app.post(
            f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True
        )

        self.assertEquals(response.status_code, 200)
        self.assertIn("Error failed to remove sample".encode(), response.data)

    @requests_mock.mock()
    def test_get_confirm_remove_sample(self, mock_request):
        response = self.app.get(
            f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Remove sample from {short_name} {period}".encode(), response.data)
