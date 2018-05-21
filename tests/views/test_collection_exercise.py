import json
import unittest
from io import BytesIO

import requests_mock

from config import TestingConfig
from response_operations_ui import app

collection_exercise_id = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
url_get_collection_exercise = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/test/000000'
with open('tests/test_data/collection_exercise/collection_exercise_details.json') as json_data:
    collection_exercise_details = json.load(json_data)
with open('tests/test_data/collection_exercise/collection_exercise_details_no_sample.json') as json_data:
    collection_exercise_details_no_sample = json.load(json_data)
with open('tests/test_data/collection_exercise/collection_exercise_details_failedvalidation.json') as json_data:
    collection_exercise_details_failedvalidation = json.load(json_data)
url_collection_instrument = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/test/000000'
url_collection_instrument_link = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/link/111111/000000'
url_collection_instrument_unlink = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/' \
                                   f'unlink/14fb3e68-4dca-46db-bf49-04b84e07e77c/000000'

url_survey_shortname = f'{app.config["SURVEY_URL"]}/surveys/shortname/test'
url_sample_service_upload = f'{app.config["SAMPLE_URL"]}/samples/B/fileupload'
url_collection_exercise_survey_id = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/survey/' \
                                    'af6ddd8f-7bd0-4c51-b879-ff4b367461c5'
url_collection_exercise_link = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/link/' \
                               '6e65acc4-4192-474b-bd3d-08071c4768e2'

url_upload_sample = f'{app.config["BACKSTAGE_API_URL"]}/v1/sample/test/000000'
url_execute = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/test/000000/execute'
url_update_ce = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/update-collection-exercise-details/' \
                f'{collection_exercise_id}'
url_get_survey_by_short_name = f'{app.config["BACKSTAGE_API_URL"]}/v1/survey/shortname/test'
with open('tests/test_data/survey/edited_survey_ce_details.json') as json_data:
    updated_survey_info = json.load(json_data)
with open('tests/test_data/survey/survey_by_id.json') as fp:
    survey_by_id = json.load(fp)
url_create_collection_exercise = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises'
url_ce_by_survey = f'{app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/survey/' \
                   f'{survey_id}'


class TestCollectionExercise(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()
        self.headers = {
            'Authorization': 'test_jwt',
            'Content-Type': 'application/json',
        }
        self.collection_exercises = [
            {
                "id": "c6467711-21eb-4e78-804c-1db8392f93fb",
                "exerciseRef": "201601",
                "scheduledExecutionDateTime": "2017-05-15T00:00:00Z"
            }
        ]

    @requests_mock.mock()
    def test_collection_exercise_view(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment Survey".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_fail(self, mock_request):
        mock_request.get(url_get_collection_exercise, status_code=500)

        response = self.app.get("/surveys/test/000000", follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_upload_collection_instrument(self, mock_request):
        post_data = {
            'ciFile': (BytesIO(b'data'), '064_201803_0001.xlsx'),
            'load-ci': '',
        }
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    def test_select_collection_instrument(self, mock_request):
        post_data = {
            'checkbox-answer': ['111111'],
            'ce_id': '000000',
            'select-ci': ''
        }
        mock_request.post(url_collection_instrument_link, status_code=200)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instruments added".encode(), response.data)

    @requests_mock.mock()
    def test_failed_select_collection_instrument(self, mock_request):
        post_data = {
            'checkbox-answer': ['111111'],
            'ce_id': '000000',
            'select-ci': ''
        }
        mock_request.post(url_collection_instrument_link, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to add collection instrument(s)".encode(), response.data)

    @requests_mock.mock()
    def test_failed_no_selected_collection_instrument(self, mock_request):
        post_data = {
            'checkbox-answer': [],
            'ce_id': '000000',
            'select-ci': ''
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: No collection instruments selected".encode(), response.data)

    @requests_mock.mock()
    def test_view_collection_instrument_after_upload(self, mock_request):
        post_data = {
            'ciFile': (BytesIO(b'data'), '064_201803_0001.xlsx'),
            'load-ci': '',
        }
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)

    @requests_mock.mock()
    def test_failed_upload_collection_instrument(self, mock_request):
        post_data = {
            'ciFile': (BytesIO(b'data'), '064_201803_0001.xlsx'),
            'load-ci': '',
        }
        mock_request.post(url_collection_instrument, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_bad_extension(self, mock_request):
        post_data = {
            'ciFile': (BytesIO(b'data'), '064_201803_0001.html'),
            'load-ci': '',
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: wrong file type for collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_bad_form_type_format(self, mock_request):
        post_data = {
            'ciFile': (BytesIO(b'data'), '064_201803_xxxxx.xlsx'),
            'load-ci': '',
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_bad_file_name_format(self, mock_request):
        post_data = {
            'ciFile': (BytesIO(b'data'), '064201803_xxxxx.xlsx'),
            'load-ci': '',
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_form_type_not_integer(self, mock_request):
        post_data = {
            'ciFile': (BytesIO(b'data'), '064_201803_123E.xlsx'),
            'load-ci': '',
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: invalid file name format for collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_no_file(self, mock_request):
        post_data = {
            'load-ci': '',
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: No collection instrument supplied".encode(), response.data)

    @requests_mock.mock()
    def test_view_collection_instrument(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)

    @requests_mock.mock()
    def test_choose_collection_instrument_when_first(self, mock_request):
        with open('tests/test_data/collection_exercise/collection_exercise_details_no_ci.json') as collection_exercise:
            mock_request.get(url_get_collection_exercise, json=json.load(collection_exercise))

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add a collection instrument. Must be XLSX".encode(), response.data)

    @requests_mock.mock()
    def test_add_another_collection_instrument_when_already_uploaded(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add another collection instrument. Must be XLSX".encode(), response.data)

    @requests_mock.mock()
    def test_upload_sample(self, mock_request):
        post_data = {
            "sampleFile": (BytesIO(b'data'), 'test.csv'),
            "load-sample": "",
        }

        json_date = {
            "sampleSummaryPK": 1,
            "id": "d7d13200-34a1-4a66-9f3b-ea0af4bc023d",
            "state": "ACTIVE",
            "ingestDateTime": "2017-11-06T14:02:24.203+0000"
        }

        survey_data = {
            "id": "af6ddd8f-7bd0-4c51-b879-ff4b367461c5"
        }

        exercise_data = [{
            'id': '6e65acc4-4192-474b-bd3d-08071c4768e2',
            'surveyId': '0b1f8376-28e9-4884-bea5-acf9d709464e',
            'name': 'Monthly Business Sur',
            'scheduledExecutionDateTime': '2018-06-19T00:00:00.000Z',
            'scheduledStartDateTime': '2018-06-19T00:00:00.000Z',
            'periodStartDateTime': '2018-06-19T00:00:00.000Z',
            'periodEndDateTime': '2020-08-31T00:00:00.000Z',
            'scheduledReturnDateTime': '2018-07-07T00:00:00.000Z',
            'scheduledEndDateTime': '2020-08-31T00:00:00.000Z',
            'state': 'SCHEDULED',
            'caseTypes': [],
            'exerciseRef': '000000'
        }]

        sample_data = {
            "id": "d29489a0-1044-4c33-9d0d-02aeb57ce82d"
        }

        collection_exercise_link = {
            "id": ""
        }

        mock_request.post(url_upload_sample, status_code=201, json=json_date)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_survey_shortname, status_code=200, json=survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=200, json=sample_data)
        mock_request.put(url_collection_exercise_link, status_code=200, json=collection_exercise_link)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Loaded sample summary".encode(), response.data)
        self.assertIn('2\n'.encode(), response.data)
        self.assertIn('5\n'.encode(), response.data)

    @requests_mock.mock()
    def test_failed_upload_sample(self, mock_request):
        data = {
            "sampleFile": (BytesIO(b'data'), 'test.csv'),
            "load-sample": ""
        }

        mock_request.post(url_upload_sample, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=data, follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_sample_when_bad_extension(self, mock_request):
        data = {
            "sampleFile": (BytesIO(b'data'), 'test.html'),
            "load-sample": ""
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details_no_sample)

        response = self.app.post("/surveys/test/000000", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_sample_when_no_file(self, mock_request):
        data = {"load-sample": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details_no_sample)

        response = self.app.post("/surveys/test/000000", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live(self, mock_request):
        post_data = {'ready-for-live': ''}
        mock_request.post(url_execute, status_code=200)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post('/surveys/test/000000', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Sample loaded successfully'.encode(), response.data)
        self.assertIn('Collection exercise executed'.encode(), response.data)
        self.assertIn('Processing collection exercise'.encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live_failed(self, mock_request):
        post_data = {'ready-for-live': ''}
        mock_request.post(url_execute, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post('/surveys/test/000000', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Sample loaded successfully'.encode(), response.data)
        self.assertNotIn('Collection exercise executed'.encode(), response.data)
        self.assertIn('Failed to execute Collection Exercise'.encode(), response.data)

    @requests_mock.mock()
    def test_get_processing(self, mock_request):
        collection_exercise_details['collection_exercise']['state'] = 'EXECUTION_STARTED'
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get('/surveys/test/000000')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing collection exercise'.encode(), response.data)

    @requests_mock.mock()
    def test_failed_execution(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details_failedvalidation)

        response = self.app.get('/surveys/test/000000')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Ready for review'.encode(), response.data)
        self.assertIn('Error processing collection exercise'.encode(), response.data)
        self.assertIn('Check collection instruments'.encode(), response.data)

    @requests_mock.mock()
    def test_update_collection_exercise_details_success(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": '14fb3e68-4dca-46db-bf49-04b84e07e77c',
            "user_description": '16th June 2019',
            "period": '201906',
            "hidden_survey_id": survey_id
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.put(url_update_ce)
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        response = self.app.post(f"/surveys/test/000000/edit-collection-exercise-details",
                                 data=changed_ce_details, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('16th June 2019'.encode(), response.data)
        self.assertIn('201906'.encode(), response.data)

    @requests_mock.mock()
    def test_update_collection_exercise_details_fail(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": '14fb3e68-4dca-46db-bf49-04b84e07e77c',
            "user_description": '16th June 2019',
            "period": '201906',
            "hidden_survey_id": survey_id
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.put(url_update_ce, status_code=500)

        response = self.app.post(f"/surveys/test/000000/edit-collection-exercise-details",
                                 data=changed_ce_details, follow_redirects=True)

        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_get_ce_details(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        response = self.app.get(f"/surveys/test/000000/edit-collection-exercise-details",
                                follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("14fb3e68-4dca-46db-bf49-04b84e07e77c".encode(), response.data)

    @requests_mock.mock()
    def test_unlink_collection_instrument(self, mock_request):
        post_data = {
            'ci_id': '14fb3e68-4dca-46db-bf49-04b84e07e77c',
            'ce_id': '000000',
            'unselect-ci': ''
        }

        mock_request.put(url_collection_instrument_unlink, status_code=200)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument removed".encode(), response.data)

    @requests_mock.mock()
    def test_failed_unlink_collection_instrument(self, mock_request):
        post_data = {
            'ci_id': '14fb3e68-4dca-46db-bf49-04b84e07e77c',
            'ce_id': '000000',
            'unselect-ci': ''
        }

        mock_request.put(url_collection_instrument_unlink, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_success(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": 'BRES',
            "hidden_survey_id": survey_id,
            "user_description": 'New collection exercise',
            "period": '123456'
        }
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.app.post(f"/surveys/141-test/create-collection-exercise", data=new_collection_exercise_details,
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('123456'.encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_failure(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": 'BRES',
            "hidden_survey_id": survey_id,
            "user_description": 'New collection exercise',
            "period": '123456'
        }
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        mock_request.post(url_create_collection_exercise, status_code=500)

        response = self.app.post(f"/surveys/141-test/create-collection-exercise", data=new_collection_exercise_details,
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_get_create_ce_form(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        response = self.app.get(f"/surveys/141-test/create-collection-exercise",
                                follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Create collection exercise".encode(), response.data)

    @requests_mock.mock()
    def test_failed_create_ce_validation_period_exists(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": 'BRES',
            "hidden_survey_id": survey_id,
            "user_description": 'New collection exercise',
            "period": '201601'
        }
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.app.post(f"/surveys/141-test/create-collection-exercise", data=new_collection_exercise_details,
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please use a period that is not in use by any collection exercise for this survey".encode(),
                      response.data)

    @requests_mock.mock()
    def test_failed_create_ce_letters_fails_in_period_validation(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": 'BRES',
            "hidden_survey_id": survey_id,
            "user_description": 'New collection exercise',
            "period": 'hello'
        }
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.app.post(f"/surveys/141-test/create-collection-exercise", data=new_collection_exercise_details,
                                 follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)

    @requests_mock.mock()
    def test_failed_edit_ce_validation_period_exists(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": '14fb3e68-4dca-46db-bf49-04b84e07e77c',
            "user_description": '16th June 2019',
            "period": '201601',
            "hidden_survey_id": survey_id
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.put(url_update_ce)
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        response = self.app.post(f"/surveys/test/000000/edit-collection-exercise-details",
                                 data=changed_ce_details, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please use a period that is not in use by any collection exercise for this survey".encode(),
                      response.data)

    @requests_mock.mock()
    def test_failed_edit_ce_validation_letters_in_period_fails_validation(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": '14fb3e68-4dca-46db-bf49-04b84e07e77c',
            "user_description": '16th June 2019',
            "period": 'hello',
            "hidden_survey_id": survey_id
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.put(url_update_ce)
        mock_request.get(url_ce_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        response = self.app.post(f"/surveys/test/000000/edit-collection-exercise-details",
                                 data=changed_ce_details, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)
