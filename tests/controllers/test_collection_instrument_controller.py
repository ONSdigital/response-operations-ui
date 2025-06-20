import unittest
from unittest.mock import patch

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers.collection_instrument_controllers import (
    get_cis_and_cir_version,
    get_linked_cis_and_cir_version,
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

    @patch(
        "response_operations_ui.controllers.collection_instrument_controllers.get_collection_instruments_by_classifier"
    )
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service")
    def test_get_cis_and_cir_version(self, get_response_json_from_service, get_collection_instruments_by_classifier):
        get_response_json_from_service.return_value = [
            {
                "ci_version": 1,
                "classifier_type": "form_type",
                "classifier_value": "0001",
                "exercise_id": collection_exercise_id,
                "guid": "c046861a-0df7-443a-a963-d9aa3bddf328",
                "instrument_id": "efc3ddd7-3e79-4c6b-a8f8-1fa184cdd06b",
                "published_at": "2025-12-31T00:00:00",
                "survey_id": "0b1f8376-28e9-4884-bea5-acf9d709464e",
            }
        ]
        get_collection_instruments_by_classifier.return_value = [
            {"classifiers": {"form_type": "0001"}},
            {"classifiers": {"form_type": "0002"}},
        ]
        with self.app.app_context():
            cis = get_cis_and_cir_version(collection_exercise_id)

        self.assertEqual(cis, [{"form_type": "0001", "ci_version": 1}, {"form_type": "0002", "ci_version": None}])

    @patch(
        "response_operations_ui.controllers.collection_instrument_controllers.get_collection_instruments_by_classifier"
    )
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service")
    def test_get_cis_and_cir_version_no_registry_instruments(
        self, get_response_json_from_service, get_collection_instruments_by_classifier
    ):
        get_response_json_from_service.return_value = []
        get_collection_instruments_by_classifier.return_value = [{"classifiers": {"form_type": "0001"}}]
        with self.app.app_context():
            cis = get_cis_and_cir_version(collection_exercise_id)

        self.assertEqual(cis, [{"form_type": "0001", "ci_version": None}])

    @patch(
        "response_operations_ui.controllers.collection_instrument_controllers.get_collection_instruments_by_classifier"
    )
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service")
    def test_get_cis_and_cir_version_no_collection_instruments(
        self, get_response_json_from_service, get_collection_instruments_by_classifier
    ):
        get_response_json_from_service.return_value = []
        get_collection_instruments_by_classifier.return_value = []
        with self.app.app_context():
            cis = get_cis_and_cir_version(collection_exercise_id)

        self.assertEqual(cis, [])

    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service")
    def test_get_linked_cis_and_cir_version(self, get_response_json_from_service):
        ci_id_01 = collection_instrument_id
        ci_id_02 = "efc3ddd7-3e79-4c6b-a8f8-1fa184cdd06b"
        ci_id_03 = "c046861a-0df7-443a-a963-d9aa3bddf328"
        get_response_json_from_service.return_value = [
            {"classifier_type": "form_type", "classifier_value": "0001", "ci_version": 1},
            {"classifier_type": "form_type", "classifier_value": "0002", "ci_version": 2},
        ]

        ci_linked = [
            {"classifiers": {"form_type": "0001"}},
            {"classifiers": {"form_type": "0003"}},
        ]

        all_cis = [
            {"id": ci_id_01, "classifiers": {"form_type": "0001"}},
            {"id": ci_id_02, "classifiers": {"form_type": "0002"}},
            {"id": ci_id_03, "classifiers": {"form_type": "0003"}},
        ]

        with self.app.app_context():
            result = get_linked_cis_and_cir_version(collection_exercise_id, ci_linked, all_cis)

        expected = [
            {"id": ci_id_01, "form_type": "0001", "checked": "true", "ci_version": 1},
            {"id": ci_id_02, "form_type": "0002", "checked": "false", "ci_version": 2},
            {"id": ci_id_03, "form_type": "0003", "checked": "true", "ci_version": None},
        ]

        self.assertEqual(result, expected)
