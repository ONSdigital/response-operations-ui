import json
import unittest
from io import BytesIO
from unittest.mock import MagicMock

from requests import RequestException
import requests_mock

from response_operations_ui import app


url_get_survey_list = f'{app.config["BACKSTAGE_API_URL"]}/survey/surveys'
with open('tests/test_data/survey/survey_list.json') as json_data:
    survey_list = json.load(json_data)
url_get_survey_by_short_name = f'{app.config["BACKSTAGE_API_URL"]}/survey/shortname/bres'
with open('tests/test_data/survey/survey.json') as json_data:
    survey_info = json.load(json_data)
url_get_collection_exercise = f'{app.config["BACKSTAGE_API_URL"]}/collection-exercise/test/000000'
with open('tests/test_data/collection_exercise/collection_exercise_details.json') as json_data:
    collection_exercise_details = json.load(json_data)
url_upload_collection_instrument = f'{app.config["BACKSTAGE_API_URL"]}/collection-instrument/test/000000'
url_upload_sample = f'{app.config["BACKSTAGE_API_URL"]}/sample/upload/14fb3e68-4dca-46db-bf49-04b84e07e77c'


class TestSurvey(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @requests_mock.mock()
    def test_survey_list(self, mock_request):
        mock_request.get(url_get_survey_list, json=survey_list)

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("BRES".encode(), response.data)
        self.assertIn("BRUS".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_fail(self, mock_request):
        mock_request.get(url_get_survey_list, status_code=500)

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

    @requests_mock.mock()
    def test_survey_list_connection_error(self, mock_request):
        mock_request.get(url_get_survey_list, exc=RequestException(request=MagicMock()))

        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

    @requests_mock.mock()
    def test_survey_view(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey_info)

        response = self.app.get("/surveys/bres")

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_survey_view_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, status_code=500)

        response = self.app.get("/surveys/bres")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

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

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

    @requests_mock.mock()
    def test_upload_collection_instrument(self, mock_request):
        file = dict(
            ciFile=(BytesIO(b'data'), 'test.xlsx'),
        )
        mock_request.post(url_upload_collection_instrument, status_code=201)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=file)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    def test_failed_upload_collection_instrument(self, mock_request):
        file = dict(
            ciFile=(BytesIO(b'data'), 'test.xlsx'),
        )
        mock_request.post(url_upload_collection_instrument, status_code=500)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=file)

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

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
    def test_upload_sample(self, mock_request):
        data = {
            "sampleFile": (BytesIO(b'data'), 'test.csv'),
            "load-sample": "",
            "sample-businesses": "5",
            "sample-collection-instruments": "2"
        }

        mock_request.post(url_upload_sample, status_code=201)
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample loaded".encode(), response.data)
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

        response = self.app.post("/surveys/test/000000", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_sample_when_bad_extension(self, mock_request):
        data = {
            "sampleFile": (BytesIO(b'data'), 'test.html'),
            "load-sample": ""
        }
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_sample_when_no_file(self, mock_request):
        data = {"load-sample": ""}
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)
