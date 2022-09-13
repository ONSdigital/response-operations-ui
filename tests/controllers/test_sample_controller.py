import json
import os
import unittest
from copy import deepcopy

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import sample_controllers
from response_operations_ui.exceptions.exceptions import ApiError

project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/collection_exercise/formatted_collection_exercise_details.json") as fp:
    exercise_details = json.load(fp)

sample_summary_id = "3f469cea-e9af-4d1a-812c-de504ae46fd5"
url_check_sample_units = f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}/check-and-transition-sample-summary-status"

sample_summary_status_complete_json = {"areAllSampleUnitsLoaded": True, "expectedTotal": 10, "currentTotal": 10}


class TestSampleControllers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    def test_sample_summary_state_check_required(self):
        scenarios = [
            ["LIVE", "ACTIVE", False],
            ["READY_FOR_REVIEW", "ACTIVE", False],
            ["READY_FOR_LIVE", "ACTIVE", False],
            ["READY_FOR_LIVE", "ACTIVE", False],
            ["SCHEDULED", "INIT", True],
        ]
        for scenario in scenarios:
            exercise_state = scenario[0]
            sample_state = scenario[1]
            expected_result = scenario[2]

            exercise_details["collection_exercise"]["state"] = exercise_state
            exercise_details["sample_summary"]["state"] = sample_state
            actual = sample_controllers.sample_summary_state_check_required(exercise_details)
            self.assertEqual(expected_result, actual)

    def test_sample_summary_state_check_required_no_sample_loaded(self):
        scenarios = [
            ["SCHEDULED", False],
            ["CREATED", False],
        ]
        copied_exercise_details = deepcopy(exercise_details)
        copied_exercise_details["sample_summary"] = None
        for scenario in scenarios:
            exercise_state = scenario[0]
            expected_result = scenario[1]

            copied_exercise_details["collection_exercise"]["state"] = exercise_state
            actual = sample_controllers.sample_summary_state_check_required(copied_exercise_details)
            self.assertEqual(expected_result, actual)

    def test_check_if_all_sample_units_present_for_sample_summary_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET,
                url_check_sample_units,
                json=sample_summary_status_complete_json,
                status=200,
                content_type="application/json",
            )
            with self.app.app_context():
                output = sample_controllers.check_if_all_sample_units_present_for_sample_summary(sample_summary_id)
                self.assertTrue(output)

    def test_check_if_all_sample_units_present_for_sample_summary_failure(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_check_sample_units, json=sample_summary_status_complete_json, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    sample_controllers.check_if_all_sample_units_present_for_sample_summary(sample_summary_id)
