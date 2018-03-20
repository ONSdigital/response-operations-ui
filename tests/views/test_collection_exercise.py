import json
import unittest
from io import BytesIO

import requests_mock

from config import TestingConfig
from response_operations_ui import app


url_get_collection_exercise = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/test/000000'
with open('tests/test_data/collection_exercise/collection_exercise_details.json') as json_data:
    collection_exercise_details = json.load(json_data)
with open('tests/test_data/collection_exercise/collection_exercise_details_no_sample.json') as json_data:
    collection_exercise_details_no_sample = json.load(json_data)
with open('tests/test_data/collection_exercise/collection_exercise_details_failedvalidation.json') as json_data:
    collection_exercise_details_failedvalidation = json.load(json_data)
url_collection_instrument = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/test/000000'
url_collection_instrument_link = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-instrument/link/111111/000000'
url_upload_sample = f'{app.config["BACKSTAGE_API_URL"]}/v1/sample/test/000000'
url_execute = f'{app.config["BACKSTAGE_API_URL"]}/v1/collection-exercise/test/000000/execute'


class TestCollectionExercise(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

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
            "state": "INIT",
            "ingestDateTime": "2017-11-06T14:02:24.203+0000"
        }

        mock_request.post(url_upload_sample, status_code=201, json=json_date)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample successfully loaded".encode(), response.data)
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
        self.assertNotIn("Sample successfully loaded".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_sample_when_no_file(self, mock_request):
        data = {"load-sample": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details_no_sample)

        response = self.app.post("/surveys/test/000000", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample successfully loaded".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live(self, mock_request):
        post_data = {'ready-for-live': ''}
        mock_request.post(url_execute, status_code=200)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post('/surveys/test/000000', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Sample successfully loaded'.encode(), response.data)
        self.assertIn('Collection exercise executed'.encode(), response.data)
        self.assertIn('Processing collection exercise'.encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live_failed(self, mock_request):
        post_data = {'ready-for-live': ''}
        mock_request.post(url_execute, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post('/surveys/test/000000', data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Sample successfully loaded'.encode(), response.data)
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
