import json
import os
import unittest

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import case_controller
from response_operations_ui.exceptions.exceptions import ApiError

case_id = "10b04906-f478-47f9-a985-783400dd8482"
project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/case/case_events.json") as fp:
    case_events = json.load(fp)
url_get_case_events = f"{TestingConfig.CASE_URL}/cases/{case_id}/events"
url_get_case_groups = f"{TestingConfig.CASE_URL}/casegroups/partyid/{case_id}"
url_get_cases = f"{TestingConfig.CASE_URL}/cases/partyid/{case_id}"


class TestCaseControllers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    def test_get_case_events_by_case_id_success(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_case_events, json=case_events, status=200, content_type="application/json")
            with self.app.app_context():
                get_case_events = case_controller.get_case_events_by_case_id(case_id)

                self.assertEqual(len(case_events), len(get_case_events))

    def test_get_case_events_by_case_id_fail(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_case_events, status=400)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    case_controller.get_case_events_by_case_id(case_id)

    def test_get_case_events_by_case_id_and_category_success(self):
        categories = ["OFFLINE_RESPONSE_PROCESSED", "SUCCESSFUL_RESPONSE_UPLOAD", "COMPLETED_BY_PHONE"]

        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET,
                url_get_case_events,
                json=[case_events[1], case_events[2]],
                status=200,
                content_type="application/json",
            )
            with self.app.app_context():
                get_case_events = case_controller.get_case_events_by_case_id(case_id, categories)

                self.assertEqual(len(get_case_events), 2)

    def test_get_case_events_by_false_case_id_erturns_404(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_case_events, status=404)
            with self.app.app_context():
                get_case_events = case_controller.get_case_events_by_case_id(case_id)

                self.assertEqual(get_case_events, {})

    def test_get_case_events_by_case_id_and_false_category_returns_400(self):
        category = ["FAKE_CATEGORY"]

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_case_events, status=400, content_type="application/json")
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    case_controller.get_case_events_by_case_id(case_id, category)

    def test_get_case_events_by_case_id_and_one_category_returns_success(self):
        category = "SUCCESSFUL_RESPONSE_UPLOAD"

        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET,
                url_get_case_events,
                json=[case_events[1], case_events[2]],
                status=200,
                content_type="application/json",
            )
            with self.app.app_context():
                get_case_events = case_controller.get_case_events_by_case_id(case_id, category)

                self.assertEqual(len(get_case_events), 2)

    def test_empty_response_if_no_enrolements_case_groups(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_case_groups, json=[], status=204, content_type="application/json")
            with self.app.app_context():
                get_case_events = case_controller.get_case_groups_by_business_party_id(case_id)
                self.assertEqual(get_case_events, [])

    def test_empty_response_if_no_enrolements_cases(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_cases, json=[], status=204, content_type="application/json")
            with self.app.app_context():
                get_case_events = case_controller.get_cases_by_business_party_id(case_id, 12)
                self.assertEqual(get_case_events, [])
