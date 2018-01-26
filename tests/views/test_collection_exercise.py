import json
import unittest
from io import BytesIO

import requests_mock

from config import TestingConfig
from response_operations_ui import app

url_get_collection_exercise = f'{app.config["BACKSTAGE_API_URL"]}/collection-exercise/test/000000'
with open('tests/test_data/collection_exercise/collection_exercise_details.json') as json_data:
    collection_exercise_details = json.load(json_data)
with open('tests/test_data/collection_exercise/collection_exercise_details_no_sample.json') as json_data:
    collection_exercise_details_no_sample = json.load(json_data)
url_collection_instrument = f'{app.config["BACKSTAGE_API_URL"]}/collection-instrument/test/000000'
url_upload_sample = f'{app.config["BACKSTAGE_API_URL"]}/sample/test/000000'


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
        file = dict(
            ciFile=(BytesIO(b'data'), 'test.xlsx'),
        )
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=file)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    def test_view_collection_instrument_after_upload(self, mock_request):
        file = dict(
            ciFile=(BytesIO(b'data'), 'collection_instrument.xlsx'),
        )
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=file)

        self.assertEqual(response.status_code, 200)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)

    @requests_mock.mock()
    def test_failed_upload_collection_instrument(self, mock_request):
        file = dict(
            ciFile=(BytesIO(b'data'), 'test.xlsx'),
        )
        mock_request.post(url_collection_instrument, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=file, follow_redirects=True)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error 500 - Server error".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_bad_extension(self, mock_request):
        file = dict(
            ciFile=(BytesIO(b'data'), 'test.html'),
        )
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=file)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_no_file(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)

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
        self.assertIn("Choose a collection instrument (CI) to load".encode(), response.data)

    @requests_mock.mock()
    def test_add_another_collection_instrument_when_already_uploaded(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add another collection instrument (CI)".encode(), response.data)

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
