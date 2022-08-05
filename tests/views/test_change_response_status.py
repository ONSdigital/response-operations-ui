import json
import os
from unittest import TestCase

import requests_mock

from config import TestingConfig
from response_operations_ui import create_app

short_name = "BLOCKS"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
period = "201801"
collection_exercise_id = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
ru_ref = "19000001"
business_party_id = "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c"
case_id = "10b04906-f478-47f9-a985-783400dd8482"
case_group_id = "612f5c34-7e11-4740-8e24-cb321a86a917"
party_id = "cd592e0f-8d07-407b-b75d-e01fbdae8233"

url_get_survey_by_short_name = f"{TestingConfig.SURVEY_URL}/surveys/shortname/{short_name}"
url_get_collection_exercises_by_survey = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey/{survey_id}"
)
url_get_business_by_ru_ref = f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/ref/{ru_ref}"
url_get_available_case_group_statuses = (
    f"{TestingConfig.CASE_URL}" f"/casegroups/transitions/{collection_exercise_id}/{ru_ref}"
)
url_get_case_groups_by_business_party_id = f"{TestingConfig.CASE_URL}/casegroups/partyid/{business_party_id}"
url_update_case_group_status = f"{TestingConfig.CASE_URL}/casegroups/transitions/{collection_exercise_id}/{ru_ref}"
url_post_case_event = f"{TestingConfig.CASE_URL}/cases/{case_id}/events"
url_get_case_by_case_group_id = f"{TestingConfig.CASE_URL}/cases/casegroupid/{case_group_id}"
url_get_case_events = f"{TestingConfig.CASE_URL}/cases/{case_id}/events"
get_respondent_by_id_url = f"{TestingConfig.PARTY_URL}/party-api/v1/respondents/id/{party_id}"
project_root = os.path.dirname(os.path.dirname(__file__))


with open(f"{project_root}/test_data/survey/single_survey.json") as fp:
    survey = json.load(fp)
with open(f"{project_root}/test_data/collection_exercise/collection_exercise_list.json") as fp:
    collection_exercise_list = json.load(fp)
with open(f"{project_root}/test_data/party/get_business_by_ru_ref.json") as fp:
    business_reporting_unit = json.load(fp)
with open(f"{project_root}/test_data/case/case.json") as fp:
    case = json.load(fp)
with open(f"{project_root}/test_data/case/case_groups_list.json") as fp:
    case_groups = json.load(fp)
with open(f"{project_root}/test_data/case/case_groups_list_completed.json") as fp:
    case_groups_completed = json.load(fp)
with open(f"{project_root}/test_data/case/case_events.json") as fp:
    case_events = json.load(fp)
with open(f"{project_root}/test_data/case/case_events_without_metadata.json") as fp:
    case_events_without_metadata = json.load(fp)
with open(f"{project_root}/test_data/case/case_events_without_partyId_in_metadata.json") as fp:
    case_events_without_partyId_in_metadata = json.load(fp)
with open(f"{project_root}/test_data/reporting_units/respondent.json") as json_data:
    respondent = json.load(json_data)
with open(f"{project_root}/test_data/case/case_group_statuses_completed_to_notstarted.json") as fp:
    case_groups_not_started = json.load(fp)
with open(f"{project_root}/test_data/case/case_groups_list_completed_by_phone.json") as fp:
    case_groups_completed_by_phone = json.load(fp)
with open(f"{project_root}/test_data/case/case_groups_list_no_longer_required.json") as fp:
    case_groups_no_longer_required = json.load(fp)


class TestChangeResponseStatus(TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        self.setup_data()

    def setup_data(self):
        self.statuses = {
            "COLLECTION_INSTRUMENT_DOWNLOADED": "INPROGRESS",
            "EQ_LAUNCH": "INPROGRESS",
            "SUCCESSFUL_RESPONSE_UPLOAD": "COMPLETE",
            "COMPLETED_BY_PHONE": "COMPLETEDBYPHONE",
            "RESPONDENT_ENROLED": "NOTSTARTED",
            "ACCESS_CODE_AUTHENTICATION_ATTEMPT": "NOTSTARTED",
            "NO_LONGER_REQUIRED": "NOLONGERREQUIRED",
            "COMPLETED_TO_NOTSTARTED": "NOTSTARTED",
        }

    @requests_mock.mock()
    def test_get_available_status(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, json=case_groups)
        mock_request.get(url_get_case_events, json=case_events)
        mock_request.get(url_get_case_by_case_group_id, json=[case])

        response = self.client.get(f"/case/{ru_ref}/response-status?survey={short_name}&period={period}")

        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"19000001", data)
        self.assertIn(b"Bolts and Ratchets", data)
        self.assertIn(b"221 BLOCKS", data)
        self.assertIn(b"Not started", data)
        self.assertIn(b"Completed by phone", data)
        self.assertIn(b"No longer required", data)

        # Test that events that end up in the NOTSTARTED state don't get a radio button
        self.assertNotIn(b"ACCESS_CODE_AUTHENTICATION_ATTEMPT", data)
        self.assertNotIn(b"RESPONDENT_ENROLED", data)

    @requests_mock.mock()
    def test_get_available_status_failures(self, mock_request):
        """
        Tests how the response status page will act if various API calls fail.
        """
        response_status_url = f"/case/{ru_ref}/response-status?survey={short_name}&period={period}"
        # Survey fail
        mock_request.get(url_get_survey_by_short_name, status_code=500)
        response = self.client.get(response_status_url, follow_redirects=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

        # Collection exercise fail
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, status_code=500)
        response = self.client.get(response_status_url, follow_redirects=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

        # Party fail
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, status_code=500)
        response = self.client.get(response_status_url, follow_redirects=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

        # Case fail
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, status_code=500)
        response = self.client.get(response_status_url, follow_redirects=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

        # Case group fail
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, status_code=500)
        response = self.client.get(response_status_url, follow_redirects=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_update_case_group_status(self, mock_request):
        mock_request.get(url_get_case_by_case_group_id, json=[case])
        mock_request.post(url_post_case_event)

        response = self.client.post(
            f"/case/{ru_ref}/response-status" f"?survey={short_name}&period={period}&case_group_id={case_group_id}",
            data={"event": "COMPLETEDBYPHONE"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(f"reporting-units/{ru_ref}", response.location)

    @requests_mock.mock()
    def test_update_case_group_status_get_case_fail(self, mock_request):
        mock_request.get(url_get_case_by_case_group_id, json=[case], status_code=500)

        response = self.client.post(
            f"/case/{ru_ref}/response-status?survey={short_name}&period={period}&case_group_id={case_group_id}",
            data={"event": "COMPLETEDBYPHONE"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_update_case_group_status_post_event_fail(self, mock_request):
        mock_request.get(url_get_case_by_case_group_id, json=[case])
        mock_request.post(url_post_case_event, status_code=500)

        response = self.client.post(
            f"/case/{ru_ref}/response-status?survey={short_name}&period={period}&case_group_id={case_group_id}",
            data={"event": "COMPLETEDBYPHONE"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_update_case_group_status_no_event(self, mock_request):
        mock_request.get(url_get_case_by_case_group_id, json=[case])

        response = self.client.post(
            f"/case/{ru_ref}/response-status?survey={short_name}&period={period}&case_group_id={case_group_id}"
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(f"case/{ru_ref}", response.location)

    @requests_mock.mock()
    def test_update_case_group_status_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.put(url_update_case_group_status, status_code=500)

        response = self.client.post(
            f"/case/{ru_ref}/response-status?survey={short_name}&period={period}",
            data={"event": "COMPLETEDBYPHONE"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("Server error (Error 500)".encode(), response.data)

    @requests_mock.mock()
    def test_get_timestamp_for_completed_case_event(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, json=case_groups_completed)
        mock_request.get(url_get_case_by_case_group_id, json=[case])
        mock_request.get(url_get_case_events, json=case_events)
        mock_request.get(get_respondent_by_id_url, json=respondent)

        response = self.client.get(f"/case/{ru_ref}/response-status?survey={short_name}&period={period}")

        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"19000001", data)
        self.assertIn(b"Bolts and Ratchets", data)
        self.assertIn(b"221 BLOCKS", data)
        self.assertIn(b"Completed", data)

    @requests_mock.mock()
    def test_get_respondent_name_for_completed_case_event(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, json=case_groups_completed)
        mock_request.get(url_get_case_by_case_group_id, json=[case])
        mock_request.get(url_get_case_events, json=case_events)
        mock_request.get(get_respondent_by_id_url, json=respondent)

        response = self.client.get(f"/case/{ru_ref}/response-status?survey={short_name}&period={period}")
        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"19000001", data)
        self.assertIn(b"Bolts and Ratchets", data)
        self.assertIn(b"221 BLOCKS", data)
        self.assertIn(b"Completed", data)
        self.assertIn(b"Jacky Turner", data)

    @requests_mock.mock()
    def test_respondent_name_unavailable_for_completed_case_event(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, json=case_groups_completed)
        mock_request.get(url_get_case_by_case_group_id, json=[case])
        mock_request.get(url_get_case_events, json=case_events_without_metadata)
        mock_request.get(get_respondent_by_id_url, json=respondent)

        response = self.client.get(f"/case/{ru_ref}/response-status?survey={short_name}&period={period}")
        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"19000001", data)
        self.assertIn(b"Bolts and Ratchets", data)
        self.assertIn(b"221 BLOCKS", data)
        self.assertIn(b"Completed", data)
        self.assertNotIn(b"Jacky Turner", data)

    @requests_mock.mock()
    def test_respondent_name_not_in_metadata_for_completed_case_event(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, json=case_groups_completed)
        mock_request.get(url_get_case_by_case_group_id, json=[case])
        mock_request.get(url_get_case_events, json=case_events_without_partyId_in_metadata)
        mock_request.get(get_respondent_by_id_url, json=respondent)

        response = self.client.get(f"/case/{ru_ref}/response-status?survey={short_name}&period={period}")
        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"19000001", data)
        self.assertIn(b"Bolts and Ratchets", data)
        self.assertIn(b"221 BLOCKS", data)
        self.assertIn(b"Completed", data)
        self.assertNotIn(b"Jacky Turner", data)

    @requests_mock.mock()
    def test_not_started_status_is_present_for_completed_by_phone(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, json=case_groups_completed_by_phone)
        mock_request.get(url_get_case_events, json=case_events)
        mock_request.get(url_update_case_group_status, json=case_groups_not_started)
        mock_request.get(url_get_case_by_case_group_id, json=[case])

        response = self.client.get(f"/case/{ru_ref}/response-status?survey={short_name}&period={period}")

        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"19000001", data)
        self.assertIn(b"Bolts and Ratchets", data)
        self.assertIn(b"221 BLOCKS", data)
        self.assertIn(b"Completed by phone", data)
        self.assertIn(b"Not started", data)

    @requests_mock.mock()
    def test_not_started_status_is_present_for_no_longer_required(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=survey)
        mock_request.get(url_get_collection_exercises_by_survey, json=collection_exercise_list)
        mock_request.get(url_get_business_by_ru_ref, json=business_reporting_unit)
        mock_request.get(url_get_available_case_group_statuses, json=self.statuses)
        mock_request.get(url_get_case_groups_by_business_party_id, json=case_groups_no_longer_required)
        mock_request.get(url_get_case_events, json=case_events)
        mock_request.get(url_update_case_group_status, json=case_groups_not_started)
        mock_request.get(url_get_case_by_case_group_id, json=[case])

        response = self.client.get(f"/case/{ru_ref}/response-status?survey={short_name}&period={period}")

        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"19000001", data)
        self.assertIn(b"Bolts and Ratchets", data)
        self.assertIn(b"221 BLOCKS", data)
        self.assertIn(b"No longer required", data)
        self.assertIn(b"Not started", data)
