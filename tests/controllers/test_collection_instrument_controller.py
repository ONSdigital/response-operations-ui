import unittest

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers.collection_instrument_controllers import (
    get_registry_instruments_by_exercise_id,
    link_collection_instrument,
    link_collection_instrument_to_survey,
    upload_collection_instrument,
    upload_ru_specific_collection_instrument,
)
from response_operations_ui.exceptions.exceptions import ApiError

survey_uuid = "b2dd0330-09c7-408f-a7c4-fa1a2bb3bfdd"
eq_id = "vacancies"
form_type = "0001"
collection_exercise_id = "e76e8c11-88c5-4d4b-a2c8-2ba923806e3c"
collection_instrument_id = "02ef3fde-919a-4b36-8c38-066336a6a3a4"
ru_ref = "12345678901"

collection_instrument_url_base = f"{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2"

ci_link_to_survey_url = (
    f"{collection_instrument_url_base}/upload?survey_id={survey_uuid}"
    f"&classifiers=%7B%22form_type%22%3A%22{form_type}%22%2C%22eq_id%22%3A%22{eq_id}%22%7D"
)
ci_link_url = f"{collection_instrument_url_base}/link-exercise/{collection_instrument_id}/{collection_exercise_id}"
ci_bres_upload_url = f"{collection_instrument_url_base}/upload/{collection_exercise_id}/{ru_ref}"
ci_upload_url = f"{collection_instrument_url_base}/upload/{collection_exercise_id}"


class File:
    """Used to imitate a file being uploaded"""

    pass


class TestCollectionInstrumentController(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    @staticmethod
    def create_test_file():
        file = File()
        file.filename = "filename"
        file.stream = "stream"
        file.mimetype = "mimetype"
        return file

    def test_link_collection_instrument_to_survey_success(self):
        """Tests on success (200) nothing is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_link_to_survey_url, status=200)
            with self.app.app_context():
                self.assertIsNone(link_collection_instrument_to_survey(survey_uuid, eq_id, form_type))

    def test_link_collection_instrument_to_survey_unauthorised(self):
        """Tests on unauthorised (401) an APIError is raised"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_link_to_survey_url, status=401)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    link_collection_instrument_to_survey(survey_uuid, eq_id, form_type)

    def test_upload_ru_specific_collection_instrument(self):
        """Tests on success (200) True is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_bres_upload_url, status=200)
            with self.app.app_context():
                file = self.create_test_file()
                success, error_text = upload_ru_specific_collection_instrument(collection_exercise_id, file, ru_ref)
                self.assertTrue(success)
                self.assertIsNone(error_text)

    def test_upload_ru_specific_collection_instrument_validation_failure(self):
        """Tests on validation failure (400) False is returned"""
        with responses.RequestsMock() as rsps:
            error = "Reporting unit 12345678901 already has an instrument uploaded for this collection exercise"
            rsps.add(rsps.POST, ci_bres_upload_url, status=500, json={"errors": [error]})
            with self.app.app_context():
                file = self.create_test_file()
                success, error_text = upload_ru_specific_collection_instrument(collection_exercise_id, file, ru_ref)
                self.assertFalse(success)
                self.assertEqual(error_text, error)

    def test_upload_ru_specific_collection_instrument_unauthorised(self):
        """Tests on unauthorised (401) False is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_bres_upload_url, status=401)
            with self.app.app_context():
                file = self.create_test_file()
                success, error_text = upload_ru_specific_collection_instrument(collection_exercise_id, file, ru_ref)
                self.assertFalse(success)
                self.assertIsNone(error_text)

    def test_upload_ru_specific_collection_instrument_failure(self):
        """Tests on failure (500) False is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_bres_upload_url, status=500, json={"errors": ["Failed to publish upload message"]})
            with self.app.app_context():
                file = self.create_test_file()
                success, error_text = upload_ru_specific_collection_instrument(collection_exercise_id, file, ru_ref)
                self.assertFalse(success)
                self.assertEqual(error_text, "Failed to publish upload message")

    def test_upload_collection_instrument(self):
        """Tests on success (200) True is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_upload_url, status=200)
            with self.app.app_context():
                file = self.create_test_file()
                self.assertTrue(upload_collection_instrument(collection_exercise_id, file))

    def test_upload_collection_instrument_unauthorised(self):
        """Tests on unauthorised (401) False is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_upload_url, status=401)
            with self.app.app_context():
                file = self.create_test_file()
                upload_success, error_text = upload_collection_instrument(collection_exercise_id, file)
                self.assertFalse(upload_success)
                self.assertEqual(error_text, None)

    def test_upload_collection_instrument_failure(self):
        """Tests on failure (500) False is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_upload_url, status=500, json={"errors": ["Failed to publish upload message"]})
            with self.app.app_context():
                file = self.create_test_file()
                upload_success, error_text = upload_collection_instrument(collection_exercise_id, file)
                self.assertFalse(upload_success)
                self.assertEqual(error_text, "Failed to publish upload message")

    def test_link_collection_instrument(self):
        """Tests on success (200) True is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_link_url, status=200)
            with self.app.app_context():
                self.assertTrue(link_collection_instrument(collection_exercise_id, collection_instrument_id))

    def test_link_collection_instrument_unauthorised(self):
        """Tests on unauthorised (401) False is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_link_url, status=401)
            with self.app.app_context():
                self.assertFalse(link_collection_instrument(collection_exercise_id, collection_instrument_id))

    def test_link_collection_instrument_failure(self):
        """Tests on failure (500) False is returned"""
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, ci_link_url, status=500, json={"errors": ["Failed to publish upload message"]})
            with self.app.app_context():
                self.assertFalse(link_collection_instrument(collection_exercise_id, collection_instrument_id))

    def test_get_registry_instruments_by_exercise_id_success(self):
        """Tests successful retrieval (200) returns JSON data"""
        exercise_id = collection_exercise_id
        url = (
            f"{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2/registry-instrument"
            f"/exercise-id/{exercise_id}"
        )

        sample_response = [{"id": "1", "classifier_value": "0001"}, {"id": "2", "classifier_value": "0002"}]

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url, json=sample_response, status=200)
            with self.app.app_context():
                result = get_registry_instruments_by_exercise_id(exercise_id)
                self.assertEqual(result, sample_response)

    def test_get_registry_instruments_by_exercise_id_not_found(self):
        """Tests when the registry instruments are not found (404), None is returned"""
        exercise_id = collection_exercise_id
        url = (
            f"{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2/registry-instrument"
            f"/exercise-id/{exercise_id}"
        )

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url, status=404)
            with self.app.app_context():
                result = get_registry_instruments_by_exercise_id(exercise_id)
                self.assertIsNone(result)
