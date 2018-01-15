import json
import unittest
from io import BytesIO

import requests_mock

from response_operations_ui import app

url_get_collection_exercise = f'{app.config["BACKSTAGE_API_URL"]}/collection-exercise/test/000000'
with open('tests/test_data/collection_exercise/collection_exercise_details.json') as json_data:
    collection_exercise_details = json.load(json_data)
url_collection_instrument = f'{app.config["BACKSTAGE_API_URL"]}/collection-instrument/test/000000'


class TestCollectionExercise(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @requests_mock.mock()
    def test_collection_exercise_view(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_collection_instrument, json=[])

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
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_collection_instrument, json=[])
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)

        response = self.app.post("/surveys/test/000000", data=file)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    def test_failed_upload_collection_instrument(self, mock_request):
        file = dict(
            ciFile=(BytesIO(b'data'), 'test.xlsx'),
        )
        mock_request.post(url_collection_instrument, status_code=500)
        mock_request.get(url_collection_instrument, json=[])
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
        mock_request.get(url_collection_instrument, json=[])

        response = self.app.post("/surveys/test/000000", data=file)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    def test_no_upload_collection_instrument_when_no_file(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_collection_instrument, json=[])

        response = self.app.post("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    def test_view_collection_instrument(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_collection_instrument, json=['collection_instrument.xlsx'])

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)

    @requests_mock.mock()
    def test_choose_collection_instrument_when_first(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_collection_instrument, json=[])

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Choose a collection instrument (CI) to load".encode(), response.data)

    @requests_mock.mock()
    def test_add_another_collection_instrument_when_already_uploaded(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_collection_instrument, json=['collection_instrument.xlsx'])

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add another collection instrument (CI)".encode(), response.data)

    @requests_mock.mock()
    def test_failed_get_collection_instruments(self, mock_request):
        mock_request.get(url_get_collection_exercise, json=collection_exercise_details)
        mock_request.get(url_collection_instrument, status_code=500)

        response = self.app.get("/surveys/test/000000")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FAIL".encode(), response.data)
