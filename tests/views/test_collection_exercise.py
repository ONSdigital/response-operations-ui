import json
import os
from collections import namedtuple
from io import BytesIO
from unittest.mock import patch
from urllib.parse import urlencode, urlparse

import fakeredis
import jwt
import mock
import requests_mock
from mock import Mock

from config import TestingConfig
from response_operations_ui.controllers import collection_instrument_controllers
from response_operations_ui.exceptions.error_codes import ErrorCode
from response_operations_ui.exceptions.exceptions import ApiError, ExternalApiError
from response_operations_ui.views.collection_exercise import (
    CIR_ERROR_MESSAGES,
    _build_collection_instruments_details,
    get_collection_exercise_and_survey_details,
    get_sample_summary,
    validate_file_extension_is_correct,
    validate_ru_specific_collection_instrument,
)
from tests.views import ViewTestCase
from tests.views.test_admin import url_permission_url, url_sign_in_data

fake_response = namedtuple("Response", "url status_code text")

collection_exercise_event_id = "b4a36392-a21f-485b-9dc4-d151a8fcd565"
collection_exercise_id = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
collection_instrument_id = "a32800c5-5dc1-459d-9932-0da6c21d2ed2"
period = "221_201712"
sample_summary_id = "1a11543f-eb19-41f5-825f-e41aca15e724"
short_name = "MBS"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
survey_ref = "141"
form_type = "0001"

project_root = os.path.dirname(os.path.dirname(__file__))

collex_root = f"{project_root}/test_data/collection_exercise/collection_exercise_details"
collex_details = collex_root + ".json"

"""Load all the necessary test data"""
with open(collex_details) as json_data:
    collection_exercise_details = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/seft_collection_exercise_details.json") as seft:
    seft_collection_exercise_details = json.load(seft)

with open(f"{project_root}/test_data/collection_exercise/collection_exercise.json") as json_data:
    collection_exercise = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/nudge_events.json") as json_data:
    nudge_events = json.load(json_data)

with open(f"{project_root}/test_data/collection_exercise/events_2030.json") as json_data:
    events_2030 = json.load(json_data)

with open(f"{project_root}/test_data/cir/cir_metadata.json") as fp:
    cir_metadata = json.load(fp)

user_permission_surveys_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "surveys.edit", "type": "DIRECT"}],
}

user_permission_messages_edit_json = {
    "id": "5902656c-c41c-4b38-a294-0359e6aabe59",
    "groups": [{"value": "f385f89e-928f-4a0f-96a0-4c48d9007cc3", "display": "messages.edit", "type": "DIRECT"}],
}

"""Define URLS"""
collection_exercise_root = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises"
url_ce_by_id = f"{collection_exercise_root}/{collection_exercise_id}"
url_ce_remove_sample = f"{collection_exercise_root}/unlink/{collection_exercise_id}/sample/{sample_summary_id}"
url_ces_by_survey = f"{collection_exercise_root}/survey/{survey_id}"
url_collection_exercise_link = f"{collection_exercise_root}/link/{collection_exercise_id}"
url_get_collection_exercises_link = f"{collection_exercise_root}/link/{collection_exercise_id}"
url_link_sample = f"{collection_exercise_root}/link/{collection_exercise_id}"
url_collection_exercise_survey_id = f"{collection_exercise_root}/survey/{survey_id}"
url_update_ce_user_details = f"{collection_exercise_root}/{collection_exercise_id}/userDescription"
url_create_collection_exercise = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises"
url_execute = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexerciseexecution/{collection_exercise_id}"
url_get_by_survey_with_ref_end_date = f"{collection_exercise_root}/survey/{short_name}/{period}/event/ref_period_end?"

collection_instrument_root = f"{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2"
url_collection_instrument = f"{collection_instrument_root}/upload/{collection_exercise_id}"
url_collection_instrument_unlink = (
    f"{collection_instrument_root}/unlink-exercise/{collection_instrument_id}/{collection_exercise_id}"
)
url_collection_instrument_multi_select = f"{collection_instrument_root}/update-eq-instruments/{collection_exercise_id}"

url_post_instrument_link = f"{TestingConfig.COLLECTION_INSTRUMENT_URL}/collection-instrument-api/1.0.2/upload"
url_get_collection_instrument = f"{collection_instrument_root}/collectioninstrument"
url_delete_collection_instrument = f"{collection_instrument_root}/delete/{collection_instrument_id}"

url_survey_shortname = f"{TestingConfig.SURVEY_URL}/surveys/shortname/{short_name}"
url_get_survey_by_short_name = f"{TestingConfig.SURVEY_URL}/surveys/shortname/{short_name}"

url_sample_service_upload = f"{TestingConfig.SAMPLE_FILE_UPLOADER_URL}/samples/fileupload"

url_get_sample_summary = f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}"
url_get_sample_summary_status = (
    f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/"
    f"{sample_summary_id}/check-and-transition-sample-summary-status"
)
url_delete_sample_summary = f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}"
url_check_if_all_sample_units_present_for_sample_summary = (
    f"{TestingConfig.SAMPLE_URL}/samples/samplesummary/{sample_summary_id}/check-and-transition-sample-summary-status"
)

url_get_by_survey_with_ref_start_date = (
    f"{collection_exercise_root}/survey/{short_name}/{period}/event/ref_period_start?"
)

url_party_delete_attributes = (
    f"{TestingConfig.PARTY_URL}/party-api/v1/businesses/attributes/sample-summary/{sample_summary_id}"
)

url_cir_get_metadata = f"http://test.domain/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}"

ci_search_string = urlencode(
    {"searchString": json.dumps({"SURVEY_ID": survey_id, "COLLECTION_EXERCISE": collection_exercise_id})}
)

ci_type_search_string_eq = urlencode({"searchString": json.dumps({"SURVEY_ID": survey_id, "TYPE": "EQ"})})
ci_type_search_string_seft = urlencode({"searchString": json.dumps({"SURVEY_ID": survey_id, "TYPE": "SEFT"})})


def sign_in_with_permission(self, mock_request, permission):
    mock_request.post(url_sign_in_data, json={"access_token": self.access_token}, status_code=201)
    mock_request.get(url_permission_url, json=permission, status_code=200)
    self.client.post("/sign-in", follow_redirects=True, data={"username": "user", "password": "pass"})


class File:
    """Used to imitate a file being uploaded"""

    pass


MOCK_GET_COLLECTION_EXERCISE_AND_SURVEY_DETAILS = (
    "response_operations_ui.views.collection_exercise.get_collection_exercise_and_survey_details"
)
MOCK_BUILD_COLLECTION_INSTRUMENTS_DETAILS = (
    "response_operations_ui.views.collection_exercise._build_collection_instruments_details"
)
MOCK_GET_SAMPLE_SUMMARY = "response_operations_ui.views.collection_exercise.get_sample_summary"
MOCK_GET_COLLECTION_EXERCISE_EVENTS_BY_ID = (
    "response_operations_ui.views.collection_exercise."
    "collection_exercise_controllers."
    "get_collection_exercise_events_by_id"
)

EQ_CI = {
    "EQ": [
        {
            "classifiers": {
                "COLLECTION_EXERCISE": ["e33daf0e-6a27-40cd-98dc-c6231f50e84a"],
                "RU_REF": [],
                "SURVEY_ID": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
                "eq_id": "a32800c5-5dc1-459d-9932-0da6c21d2ed2",
                "form_type": "0001",
            },
            "file_name": "0001",
            "id": collection_instrument_id,
            "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
        }
    ]
}

SEFT_CI = {
    "SEFT": [
        {
            "classifiers": {
                "COLLECTION_EXERCISE": ["e33daf0e-6a27-40cd-98dc-c6231f50e84a"],
                "RU_REF": [],
                "SURVEY_ID": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
            },
            "file_name": "collection_instrument.xlsx",
            "id": "f732afbe-c710-4c95-a8d3-6644833195a7",
            "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
            "type": "SEFT",
        }
    ]
}

SEFT_AND_EQ_CI = SEFT_CI.copy()
SEFT_AND_EQ_CI.update(EQ_CI)

CE = {
    "id": collection_exercise_id,
    "name": "201601",
    "scheduledExecutionDateTime": "2017-05-15T00:00:00Z",
    "state": "READY_FOR_REVIEW",
    "exerciseRef": "221_201712",
    "userDescription": "exercise description",
    "events": [],
}

CE_PREPROP = CE.copy()
CE_PREPROP["supplementaryDatasetEntity"] = {
    "survey_id": "139",
    "period_id": "202201",
    "form_types": ["0001", "0002", "0003"],
    "title": "QBS",
    "sds_published_at": "2023-08-24T11:55:00Z",
    "total_reporting_units": 1,
    "schema_version": "v1.0.0",
    "sds_dataset_version": 2,
    "filename": "eccb61ad-4eb3-4714-8afd-8c8426960b43.json",
    "dataset_id": "eccb61ad-4eb3-4714-8afd-8c8426960b43",
}

CE_INIT = CE.copy()
CE_INIT["state"] = "INIT"

CE_EX_STARTED = CE.copy()
CE_EX_STARTED["state"] = "EXECUTION_STARTED"

CE_FAILED = CE.copy()
CE_FAILED["state"] = "FAILEDVALIDATION"

CE_READY = CE.copy()
CE_READY["state"] = "READY_FOR_REVIEW"

CE_VALIDATED = CE.copy()
CE_VALIDATED["state"] = "VALIDATED"

CE_EXECUTED = CE.copy()
CE_EXECUTED["state"] = "EXECUTED"

CE_ENDED = CE.copy()
CE_ENDED["state"] = "ENDED"

EQ_CI_SELECTORS = [
    {
        "classifiers": {
            "COLLECTION_EXERCISE": [collection_exercise_id],
            "RU_REF": [],
            "SURVEY_ID": survey_id,
            "form_type": "0001",
        },
        "file_name": None,
        "id": collection_instrument_id,
        "surveyId": survey_id,
        "type": "EQ",
    }
]

EQ_SURVEY = {
    "id": survey_id,
    "longName": "Monthly Survey of Building Materials Bricks",
    "shortName": "MBS",
    "surveyRef": "009",
    "eqVersion": "",
    "surveyMode": "EQ",
}

EQ_AND_SEFT_SURVEY = {
    "id": survey_id,
    "longName": "Monthly Survey of Building Materials Bricks",
    "shortName": "MBS",
    "surveyRef": "009",
    "eqVersion": "",
    "surveyMode": "EQ_AND_SEFT",
}

SEFT_SURVEY = {
    "id": survey_id,
    "longName": "Business Register and Employment Survey",
    "shortName": "BRES",
    "surveyRef": "221_201712",
    "eqVersion": "",
    "surveyMode": "SEFT",
}
CE_LINK = [sample_summary_id]
SAMPLE_SUMMARY = {
    "id": sample_summary_id,
    "effectiveStartDateTime": "",
    "effectiveEndDateTime": "",
    "surveyRef": "",
    "ingestDateTime": "2018-03-14T14:29:51.325Z",
    "state": "ACTIVE",
    "totalSampleUnits": 8,
    "expectedCollectionInstruments": 1,
    "areAllSampleUnitsLoaded": True,
}

SAMPLE_SUMMARY_INIT = SAMPLE_SUMMARY.copy()
SAMPLE_SUMMARY_INIT["state"] = "INIT"

CE_EVENTS = [
    {"tag": "mps", "timestamp": "2018-10-11T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "go_live", "timestamp": "2018-10-11T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "return_by", "timestamp": "2018-10-30T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "reminder", "timestamp": "2018-10-12T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "exercise_end", "timestamp": "2018-10-13T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "nudge_email_0", "timestamp": "2018-10-14T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "nudge_email_1", "timestamp": "2018-10-14T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "nudge_email_2", "timestamp": "2018-10-15T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "nudge_email_3", "timestamp": "2018-10-16T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "ref_period_start", "timestamp": "2018-10-11T22:00:00.000+0000", "eventStatus": "PROCESSED"},
    {"tag": "ref_period_end", "timestamp": "2019-10-11T22:00:00.000+0000", "eventStatus": "PROCESSED"},
]


class TestCollectionExercise(ViewTestCase):

    @staticmethod
    def mock_decorator(ce=None, survey=None, ci=None, sample_summary=None, ce_events=None):
        def decorator(func):
            def wrapper(self, *args):
                if ce and survey:
                    patch(MOCK_GET_COLLECTION_EXERCISE_AND_SURVEY_DETAILS, return_value=(ce, survey)).start()
                if ci:
                    patch(MOCK_BUILD_COLLECTION_INSTRUMENTS_DETAILS, return_value=ci).start()
                if sample_summary:
                    patch(MOCK_GET_SAMPLE_SUMMARY, return_value=sample_summary).start()
                if ce_events:
                    patch(MOCK_GET_COLLECTION_EXERCISE_EVENTS_BY_ID, return_value=ce_events).start()

                func(self, *args)

            return wrapper

        return decorator

    def setup_data(self):
        self.headers = {"Authorization": "test_jwt", "Content-Type": "application/json"}
        payload = {"user_id": "test-id", "aud": "response_operations"}
        self.access_token = jwt.encode(payload, TestingConfig.UAA_PRIVATE_KEY, algorithm="RS256")
        self.survey_data = {"id": survey_id}
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )

    @mock_decorator(CE_READY, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    def test_set_live_button(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE_READY, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, {})
    def test_set_live_button_invalid(self):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE_READY, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service")
    def test_cir_count_valid(self, mock_request, registry_instrument_count):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        self.app.config["CIR_ENABLED"] = True
        registry_instrument_count.return_value = {"registry_instrument_count": 1}

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE_READY, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service")
    def test_cir_count_invalid(self, registry_instrument_count):
        self.app.config["CIR_ENABLED"] = True
        registry_instrument_count.return_value = {"registry_instrument_count": 0}

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertNotIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE_PREPROP, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_collection_exercise_view_with_pre_population(self):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Pre-Populated data is available for this sample".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_seft_collection_exercise(self):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment Survey".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_eq_collection_exercise_and_instrument(self):
        # Given I have an eQ collection exercise with a collection instrument linked

        # When I call the collection exercise period endpoint
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        # Then I can view eQ collection instruments but not SEFT
        self.assertEqual(response.status_code, 200)
        self.assertIn("EQ formtypes".encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-eq">View</a>'.encode(), response.data)
        self.assertNotIn("SEFT collection instruments".encode(), response.data)
        self.assertNotIn('id="view-choose-upload-ci-seft">View</a>'.encode(), response.data)
        self.assertNotIn("CIR version".encode(), response.data)  # to be removed when CIR is live

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_response_json_from_service")
    def test_collection_exercise_view_cir(self, registry_instrument_count):
        # Given I have an eQ collection exercise with a collection instrument linked and CIR_ENABLED
        self.app.config["CIR_ENABLED"] = True
        registry_instrument_count.return_value = {"registry_instrument_count": 1}

        # When I call the collection exercise period endpoint
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        # Then I can view eQ collection instruments and get a cir
        self.assertEqual(response.status_code, 200)
        self.assertIn("EQ formtypes".encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-eq">View</a>'.encode(), response.data)
        self.assertIn("CIR version".encode(), response.data)

    @mock_decorator(CE, EQ_AND_SEFT_SURVEY, SEFT_AND_EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_eq_and_seft_collection_exercise(self):
        # Given I have an eQ and SEFT collection exercise with collection instruments for both

        # When I call the collection exercise period endpoint
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        # Then I can view eQ and SEFT collection instruments for both
        self.assertEqual(response.status_code, 200)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn("EQ formtypes".encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-eq">View</a>'.encode(), response.data)
        self.assertIn('id="view-choose-upload-ci-seft">View</a>'.encode(), response.data)

    @mock_decorator(CE_READY, SEFT_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_collection_exercise_ready_for_live(self):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ready for live".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE_EX_STARTED, SEFT_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_collection_exercise_execution_started(self):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE_VALIDATED, SEFT_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_collection_exercise_validated(self):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE_EXECUTED, SEFT_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_collection_exercise_executed(self):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Setting ready for live".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE_ENDED, SEFT_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_collection_exercise_ended(self):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ended".encode(), response.data)

    @mock_decorator(CE_READY, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @patch("response_operations_ui.controllers.sample_controllers.sample_summary_state_check_required")
    @patch("response_operations_ui.controllers.sample_controllers.check_if_all_sample_units_present_for_sample_summary")
    def test_collection_exercise_sample_check_count(
        self, check_if_all_sample_units_present_for_sample_summary, sample_summary_state_check_required
    ):
        sample_summary_state_check_required.return_value = True
        check_if_all_sample_units_present_for_sample_summary.return_value = {
            "areAllSampleUnitsLoaded": True,
            "expectedTotal": 10,
            "currentTotal": 10,
        }

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ready for live".encode(), response.data)
        self.assertIn("Sample loaded: ".encode(), response.data)

    @mock_decorator(CE_INIT, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY_INIT, CE_EVENTS)
    @patch("response_operations_ui.controllers.sample_controllers.sample_summary_state_check_required")
    @patch("response_operations_ui.controllers.sample_controllers.check_if_all_sample_units_present_for_sample_summary")
    def test_collection_exercise_sample_check_count_incorrect(
        self, check_if_all_sample_units_present_for_sample_summary, sample_summary_state_check_required
    ):
        sample_summary_state_check_required.return_value = True
        check_if_all_sample_units_present_for_sample_summary.return_value = {
            "areAllSampleUnitsLoaded": False,
            "expectedTotal": 10,
            "currentTotal": 5,
        }

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Loading (5 / 10 loaded) …".encode(), response.data)
        self.assertIn("Refresh to see progress".encode(), response.data)

    @patch("response_operations_ui.controllers.sample_controllers.sample_summary_state_check_required")
    @patch("response_operations_ui.controllers.sample_controllers.check_if_all_sample_units_present_for_sample_summary")
    @patch("response_operations_ui.views.collection_exercise.flash")
    @mock_decorator(CE_INIT, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY_INIT, CE_EVENTS)
    def test_collection_exercise_sample_check_failed(
        self, flash, check_if_all_sample_units_present_for_sample_summary, sample_summary_state_check_required
    ):
        sample_summary_state_check_required.return_value = True
        exception = ApiError(fake_response(url="", status_code=400, text="sample check failed"))
        check_if_all_sample_units_present_for_sample_summary.side_effect = exception

        self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        flash.assert_called_once_with("Sample summary check failed.  Refresh page to try again", category="error")

    @requests_mock.mock()
    @mock_decorator(CE, EQ_SURVEY)
    def test_upload_seft_collection_instrument(self, mock_request):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-seft-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers."
        "get_collection_instruments_by_classifier"
    )
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers."
        "update_collection_exercise_eq_instruments"
    )
    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_failed_add_eq_collection_instrument(
        self,
        mock_request,
        update_collection_exercise_eq_instruments,
        mock_collective_cis,
        mock_get_linked_cis_and_cir_version,
    ):
        update_collection_exercise_eq_instruments.return_value = (
            500,
            "Collection exercise collection instrument update successful",
        )
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"checkbox-answer": [collection_instrument_id], "ce_id": collection_exercise_id, "select-eq-ci": ""}
        eq_ci_to_add = {"id": collection_instrument_id, "form_type": "0001", "checked": "true", "ci_version": None}
        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]
        mock_collective_cis.return_value = eq_ci_to_add

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to add and remove collection instrument(s)".encode(), response.data)

    @patch("response_operations_ui.views.collection_exercise._redirect_with_error")
    def test_cir_no_ci_selected(self, redirect_with_error):
        self.app.config["CIR_ENABLED"] = True
        post_data = {"ce_id": collection_exercise_id, "select-eq-ci": ""}

        self.client.post(f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=False)

        redirect_with_error.assert_called_once_with("Choose one or more EQ formtypes to continue.", "221_201712", "MBS")

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_upload_seft_collection_instrument_upload_validation(self):
        # Bad file extension
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.html"), "load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Wrong file type for collection instrument".encode(), response.data)

        # Bad form type format
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_xxxxx.xlsx"), "load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

        # Bad file name format
        post_data = {"ciFile": (BytesIO(b"data"), "064201803_xxxxx.xlsx"), "load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

        # Formtype isn't an integer
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_123E.xlsx"), "load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

        # No file supplied
        post_data = {"load-seft-ci": ""}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: No collection instrument supplied".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, SEFT_CI)
    def test_view_collection_instrument(self):
        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, SEFT_CI)
    def test_load_collection_instruments_seft_already_uploaded_no_permission(self):
        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("1 SEFT collection instruments uploaded".encode(), response.data, response.data)
        self.assertNotIn("Remove SEFT file".encode(), response.data, response.data)
        self.assertNotIn("Add another collection instrument. Must be XLSX".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    def test_upload_sample(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv")}
        sample_data = {"id": sample_summary_id}

        collection_exercise_link = {"id": ""}
        mock_request.post(url_sample_service_upload, json=sample_data)
        mock_request.put(url_collection_exercise_link, json=collection_exercise_link)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/upload-sample-file", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Sample summary".encode(), response.data)
        self.assertIn("8\n".encode(), response.data)
        self.assertIn("1\n".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.flash")
    def test_no_upload_sample_when_bad_extension(self, mock_request, flash):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        data = {"sampleFile": (BytesIO(b"data"), "test.html")}

        self.client.post(
            f"/surveys/{short_name}/{period}/upload-sample-file",
            data=data,
        )

        flash.assert_called_once_with("Invalid file format", "error")

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise.flash")
    def test_no_upload_sample_when_no_file(self, mock_request, flash):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        data = {"load-sample": ""}

        self.client.post(f"/surveys/{short_name}/{period}/upload-sample-file", data=data)
        flash.assert_called_once_with("No file uploaded", "error")

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.sample_controllers.upload_sample")
    @patch("response_operations_ui.views.collection_exercise.flash")
    def test_upload_sample_csv_too_few_columns(self, mock_request, flash, upload_sample):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv")}
        exception = ApiError(fake_response(url="", status_code=400, text="Too few columns in CSV file"))
        upload_sample.side_effect = exception

        self.client.post(f"/surveys/{short_name}/{period}/upload-sample-file", data=post_data)

        flash.assert_called_once_with("Too few columns in CSV file", "error")

    @mock_decorator(CE_EX_STARTED, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @patch("response_operations_ui.controllers.collection_exercise_controllers.execute_collection_exercise")
    def test_post_ready_for_live(self, execute_collection_exercise):
        post_data = {"ready-for-live": ""}
        execute_collection_exercise.return_value = 200

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    def test_post_ready_for_live_failed(self, mock_request):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=500)

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Error: Failed to execute Collection Exercise".encode(), response.data)

    @mock_decorator(CE_EX_STARTED, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_get_processing(self):
        response = self.client.get(f"/surveys/{short_name}/{period}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @mock_decorator(CE_FAILED, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    def test_failed_execution(
        self,
    ):
        response = self.client.get(f"/surveys/{short_name}/{period}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ready for review".encode(), response.data)
        self.assertIn("Error processing collection exercise".encode(), response.data)
        self.assertNotIn("Incorrect file type. Please choose a file type XLSX".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_exercise_controllers.update_collection_exercise_period")
    def test_edit_collection_exercise_period_id(self, mock_request, update_collection_exercise_period):
        update_collection_exercise_period.return_value = None
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        new_period_id = "201907"
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "user description",
            "period": new_period_id,
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=[CE])
        mock_request.put(url_update_ce_user_details)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id",
            data=changed_ce_details,
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, f"/surveys/{short_name}/{new_period_id}")

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    def test_update_collection_exercise_user_description_success(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "new description",
            "period": "201906",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=[CE])
        mock_request.put(url_update_ce_user_details)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-description",
            data=changed_ce_details,
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, f"/surveys/{short_name}/{period}")

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    def test_get_exercise_user_description(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        response = self.client.get(f"/surveys/{short_name}/{period}/edit-collection-exercise-period-description")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Edit collection exercise details".encode(), response.data)

    @mock_decorator(CE_FAILED, SEFT_SURVEY, SEFT_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    def test_edit_collection_exercise_period_description_invalid(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        invalid_user_description = 12345
        mock_request.get(url_ces_by_survey, json=[CE])
        mock_request.put(url_update_ce_user_details)

        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": invalid_user_description,
            "period": "period",
        }

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-description",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Error processing collection exercise".encode(),
            response.data,
        )

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    def test_get_ce_details(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=SEFT_SURVEY)
        mock_request.get(url_ces_by_survey, json=SEFT_SURVEY)
        response = self.client.get(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(collection_exercise_id.encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, {})
    @requests_mock.mock()
    def test_delete_seft_collection_instrument(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {
            "ci_id": collection_instrument_id,
            "delete-ci": "",
        }

        mock_request.delete(url_delete_collection_instrument, status_code=200)
        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument removed".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, {})
    @requests_mock.mock()
    def test_delete_seft_collection_instrument_failure(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {
            "ci_id": collection_instrument_id,
            "delete-ci": "",
        }
        mock_request.delete(url_delete_collection_instrument, status_code=404)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_get_create_collection_exercise(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_ces_by_survey, json=CE)
        response = self.client.get(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Create collection exercise".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, SEFT_CI, ce_events=CE_EVENTS)
    @requests_mock.mock()
    def test_create_collection_exercise(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        new_collection_exercise_details = {
            "user_description": "New collection exercise",
            "period": period,
        }
        mock_request.register_uri(
            "GET",
            url_ces_by_survey,
            [{"json": {}, "status_code": 200}, {"json": CE, "status_code": 200}],
        )
        mock_request.get(url_get_survey_by_short_name, json=SEFT_SURVEY)
        mock_request.get(url_get_collection_exercises_link, json=CE_LINK)
        mock_request.get(url_get_sample_summary, json=SAMPLE_SUMMARY)
        mock_request.post(url_create_collection_exercise, status_code=200)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=EQ_CI, complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=EQ_CI_SELECTORS, complete_qs=True
        )

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment Survey".encode(), response.data)
        self.assertIn(period.encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_period_already_exists(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        new_collection_exercise_details = {
            "user_description": "New collection exercise",
            "period": "221_201712",
        }
        mock_request.get(url_ces_by_survey, json=[CE])
        mock_request.get(url_get_survey_by_short_name, json=SEFT_SURVEY)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Use a period that is not in use by any collection exercise for this survey".encode(),
            response.data,
        )

    @requests_mock.mock()
    def test_create_collection_exercise_invalid_period(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        new_collection_exercise_details = {
            "user_description": "New collection exercise",
            "period": "invalid",
        }
        mock_request.get(url_survey_shortname, status_code=200, json=SEFT_SURVEY)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise", data=new_collection_exercise_details
        )

        self.assertIn("Error creating collection exercise".encode(), response.data)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @mock_decorator(CE_FAILED, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    @patch("response_operations_ui.forms.collection_exercise_controllers.get_collection_exercises_by_survey")
    def test_failed_edit_ce_validation_period_exists(self, mock_request, get_collection_exercises_by_survey):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        taken_period = "12345"
        get_collection_exercises_by_survey.return_value = [{"exerciseRef": taken_period, "id": survey_id}]

        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": taken_period,
            "hidden_survey_id": survey_id,
        }

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Use a period that is not in use by any collection exercise for this survey".encode(),
            response.data,
        )

    @mock_decorator(CE_FAILED, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    @patch("response_operations_ui.forms.collection_exercise_controllers.get_collection_exercises_by_survey")
    def test_failed_edit_ce_validation_letters_in_period_fails_validation(
        self, mock_request, get_collection_exercises_by_survey
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        taken_period = "12345"
        get_collection_exercises_by_survey.return_value = [{"exerciseRef": taken_period, "id": survey_id}]

        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "period",
            "hidden_survey_id": survey_id,
        }

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-period-id",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Please enter numbers only for the period".encode(),
            response.data,
        )

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    def test_remove_loaded_sample_success(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=200)
        mock_request.delete(url_delete_sample_summary, status_code=204)
        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample removed".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    def test_remove_loaded_sample_failed_on_party(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        mock_request.delete(url_party_delete_attributes, status_code=500)

        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove sample".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, sample_summary=SAMPLE_SUMMARY)
    @requests_mock.mock()
    def test_remove_loaded_sample_failed_on_unlink(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=500)

        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove sample".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, sample_summary=SAMPLE_SUMMARY)
    @requests_mock.mock()
    def test_remove_loaded_sample_failed_on_sample(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=200)
        mock_request.delete(url_delete_sample_summary, status_code=500)
        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # If the sample deletion fails, then there shouldn't be an error message
        self.assertNotIn("Error: Failed to remove sample".encode(), response.data)

    def test_get_confirm_remove_sample(self):
        response = self.client.get("/surveys/test/221_201712/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Remove sample from test 221_201712".encode(), response.data)

    @mock_decorator(CE_EVENTS)
    @requests_mock.mock()
    def test_get_create_ce_event_form_success(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_survey_shortname, json=SEFT_SURVEY)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])

        response = self.client.get(
            f"/surveys/MBS/201801/{collection_exercise_id}/confirm-create-event/mps", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("MBS".encode(), response.data)
        self.assertIn("Main print selection".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, SEFT_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event")
    def test_create_collection_exercise_event_success(self, mock_request, create_collection_exercise_event):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        create_ce_event_form = {"day": "01", "month": "01", "year": "2030", "hour": "01", "minute": "00"}

        create_collection_exercise_event.return_value = None

        response = self.client.post(
            f"/surveys/MBS/201901/{collection_exercise_id}/create-event/mps",
            data=create_ce_event_form,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Event date added.".encode(), response.data)

    @mock_decorator(CE_EVENTS)
    @requests_mock.mock()
    def test_create_collection_exercise_invalid_form(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_survey_shortname, json=SEFT_SURVEY)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])

        create_ce_event_form = {"day": "50", "month": "01", "year": "2018", "hour": "01", "minute": "00"}

        response = self.client.post(
            f"/surveys/MBS/201801/{collection_exercise_id}/create-event/mps",
            data=create_ce_event_form,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

    @mock_decorator(CE_EVENTS)
    @requests_mock.mock()
    def test_create_collection_exercise_date_in_past(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_survey_shortname, json=SEFT_SURVEY)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])

        create_ce_event_form = {"day": "01", "month": "01", "year": "2018", "hour": "01", "minute": "00"}
        response = self.client.post(
            f"/surveys/MBS/201801/{collection_exercise_id}/create-event/mps",
            data=create_ce_event_form,
            follow_redirects=True,
        )

        self.assertIn("Selected date can not be in the past".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @mock_decorator(CE, EQ_SURVEY)
    @requests_mock.mock()
    @mock.patch("response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event")
    def test_create_collection_events_not_set_sequentially(self, mock_request, mock_ce_event):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_ce_event.return_value = "Collection exercise events must be set sequentially"

        create_ce_event_form = {"day": "01", "month": "01", "year": "2029", "hour": "01", "minute": "00"}

        response = self.client.post(
            f"/surveys/MBS/201801/{collection_exercise_id}/create-event/reminder2",
            data=create_ce_event_form,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection exercise events must be set sequentially".encode(), response.data)

    @mock_decorator(CE_INIT, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    def test_schedule_nudge_email_option_not_present(self, mock_request):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Schedule nudge email".encode(), response.data)

    @mock_decorator(CE_READY, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    def test_schedule_nudge_email_option_present(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add nudge email".encode(), response.data)

    @requests_mock.mock()
    def test_can_create_up_to_five_nudge_email(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=SEFT_SURVEY)
        mock_request.get(url_ces_by_survey, json=CE)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=SAMPLE_SUMMARY)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=EQ_CI, complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=EQ_CI_SELECTORS, complete_qs=True
        )

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add nudge email".encode(), response.data)

        @requests_mock.mock()
        @mock.patch(
            "response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event"
        )
        def test_create_collection_events_not_set_sequentially(self, mock_request, mock_ce_event):
            mock_request.get(url_survey_shortname, json=SEFT_SURVEY)
            mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
            mock_ce_event.return_value = "Collection exercise events must be set sequentially"

            create_ce_event_form = {"day": "15", "month": "10", "year": "2018", "hour": "01", "minute": "00"}

            res = self.client.post(
                f"/surveys/MBS/201801/{collection_exercise_id}/create-event/nudge_email_4",
                data=create_ce_event_form,
                follow_redirects=True,
            )

            self.assertEqual(res.status_code, 200)
            self.assertIn("Nudge email must be set sequentially".encode(), res.data)

    @staticmethod
    def create_test_file():
        file = File()
        file.filename = "12345678901.xlsx"
        file.stream = "stream"
        file.mimetype = "mimetype"
        return file

    def test_validate_file_extension(self):
        """Test validation returns None when file extension is valid and an error dict when invalid"""
        file = self.create_test_file()
        self.assertIsNone(validate_file_extension_is_correct(file))

        file.filename = "12345678901.badext"
        error = validate_file_extension_is_correct(file)
        self.assertEqual(error["section"], "ciFile")
        self.assertEqual(error["header"], "Error: Wrong file type for collection instrument")
        self.assertEqual(error["message"], "Please use XLSX file only")

    def test_validate_ru_specific_collection_instrument(self):
        """Test validation returns None when file is correct and error dict if ru ref is not 11 digits"""
        file = self.create_test_file()
        self.assertIsNone(validate_ru_specific_collection_instrument(file, "12345678901"))

        file.filename = "1234567890.xlsx"
        error = validate_ru_specific_collection_instrument(file, "1234567890")
        self.assertEqual(error["section"], "ciFile")
        self.assertEqual(error["header"], "Error: Invalid file name format for ru specific collection instrument")
        self.assertEqual(error["message"], "Please provide a file with a valid 11 digit ru ref in the file name")

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    def test_replace_sample_is_present(
        self,
        mock_request,
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        mock_request.get(url_get_survey_by_short_name, json=SEFT_SURVEY)
        mock_request.get(url_ces_by_survey, json=SEFT_SURVEY)
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Replace sample file".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY)
    @requests_mock.mock()
    def test_load_seft_collection_instruments_is_not_present(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        mock_request.get(url_get_survey_by_short_name, json=SEFT_SURVEY)
        mock_request.get(url_ces_by_survey, json=SEFT_SURVEY)
        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Upload SEFT collection instrument".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, SEFT_CI)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.upload_collection_instrument")
    def test_seft_upload_and_view_collection_instrument(self, mock_request, upload_collection_instrument):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        upload_collection_instrument.return_value = (True, "")
        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)
        self.assertIn("1 SEFT collection instruments uploaded".encode(), response.data)
        self.assertIn("Remove".encode(), response.data)

    @mock_decorator(CE, EQ_AND_SEFT_SURVEY, SEFT_AND_EQ_CI)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.upload_collection_instrument")
    def test_eq_and_seft_upload_collection_instrument_supports_xls(self, mock_request, upload_collection_instrument):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xls"), "load-ci": ""}
        upload_collection_instrument.return_value = (True, "")
        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("collection_instrument.xlsx".encode(), response.data)
        self.assertIn("1 SEFT collection instruments uploaded".encode(), response.data)
        self.assertIn("Remove".encode(), response.data)

    @mock_decorator(CE_EX_STARTED, EQ_SURVEY, EQ_CI)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.upload_collection_instrument")
    def test_seft_failed_upload_collection_instrument_with_error_message(self, mock_request, mock_upload_ci):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_upload_ci.return_value = (False, "Error message passed")
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)
        self.assertIn("Error message passed".encode(), response.data)

    @mock_decorator(CE_EX_STARTED, EQ_SURVEY, EQ_CI)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.upload_collection_instrument")
    def test_seft_failed_upload_collection_instrument_without_error_message(self, mock_request, mock_upload_ci):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_upload_ci.return_value = (False, None)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)
        self.assertIn("Please try again".encode(), response.data)

    @mock_decorator(CE, SEFT_SURVEY, SEFT_CI)
    @requests_mock.mock()
    def test_no_upload_seft_collection_instrument_when_bad_extension(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.html"), "load-ci": ""}

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Wrong file type for collection instrument".encode(), response.data)

    @mock_decorator(CE_EX_STARTED, SEFT_SURVEY, SEFT_CI)
    @requests_mock.mock()
    def test_no_upload_seft_collection_instrument_when_bad_form_type_format(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_xxxxx.xlsx"), "load-ci": ""}

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @mock_decorator(CE_EX_STARTED, SEFT_SURVEY, SEFT_CI)
    @requests_mock.mock()
    def test_no_upload_seft_collection_instrument_bad_file_name_format(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064201803_xxxxx.xlsx"), "load-ci": ""}

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @mock_decorator(CE_EX_STARTED, SEFT_SURVEY, SEFT_CI)
    @requests_mock.mock()
    def test_no_upload_seft_collection_instrument_form_type_not_integer(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_123E.xlsx"), "load-ci": ""}

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: Invalid file name format for collection instrument".encode(), response.data)

    @mock_decorator(CE_EX_STARTED, SEFT_SURVEY, SEFT_CI)
    @requests_mock.mock()
    def test_no_upload_seft_collection_instrument_when_no_file(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"load-ci": ""}

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: No collection instrument supplied".encode(), response.data)

    @mock_decorator(CE_EVENTS)
    @requests_mock.mock()
    def test_survey_edit_permission_collection_exercise(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=EQ_SURVEY)
        mock_request.get(url_ces_by_survey, json=CE)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=SAMPLE_SUMMARY)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=EQ_CI, complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=EQ_CI_SELECTORS, complete_qs=True
        )

        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertIn("Add".encode(), response.data)
        self.assertIn("Edit".encode(), response.data)
        self.assertIn("Add reminder".encode(), response.data)
        self.assertIn("Add nudge email".encode(), response.data)
        self.assertIn("Replace sample file".encode(), response.data)
        self.assertIn("Choose".encode(), response.data)

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, {}, CE_EVENTS)
    @patch(
        "response_operations_ui.controllers.collection_instrument_controllers.update_collection_exercise_eq_instruments"
    )
    def test_cir_post_select_eq_ci(self, update_collection_exercise_eq_instruments):
        self.app.config["CIR_ENABLED"] = True

        update_collection_exercise_eq_instruments.return_value = (
            200,
            "Collection exercise collection instrument update successful",
        )
        post_data = {
            "checkbox-answer": [collection_instrument_id],
            "ce_id": collection_exercise_id,
            "select-eq-ci": "",
        }
        response = self.client.post(f"/surveys/{short_name}/{period}/view-sample-ci", data=post_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(response.headers["Location"], f"/surveys/{short_name}/{period}/view-sample-ci/summary")

    @mock_decorator(CE_READY, SEFT_SURVEY, SEFT_CI)
    @requests_mock.mock()
    def test_seft_loaded_load_collection_instruments_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments")

        self.assertEqual(200, response.status_code)
        self.assertIn("SEFT collection instruments".encode(), response.data)
        self.assertIn("Upload SEFT collection instrument".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @mock_decorator(CE_EVENTS)
    @requests_mock.mock()
    def test_seft_loaded_load_collection_instrument_page_no_survey_permission(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=SEFT_SURVEY)
        mock_request.get(url_ces_by_survey, json=CE)
        mock_request.get(url_ce_by_id, json=collection_exercise_details["collection_exercise"])
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=SEFT_CI,
            complete_qs=True,
        )
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=EQ_CI_SELECTORS, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=SAMPLE_SUMMARY)

        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments")

        self.assertEqual(200, response.status_code)
        self.assertIn("SEFT collection instruments uploaded".encode(), response.data)
        self.assertNotIn("Remove SEFT file".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @mock_decorator(CE_EVENTS)
    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_linked_ci_eq_view_sample_ci_page_survey_permission(
        self, mock_request, mock_get_linked_cis_and_cir_version
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]
        mock_request.get(url_get_survey_by_short_name, json=EQ_SURVEY)
        mock_request.get(url_ces_by_survey, json=CE)
        mock_request.get(url_ce_by_id, json=CE)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=EQ_CI, complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=EQ_CI_SELECTORS, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=SAMPLE_SUMMARY)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=CE)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=CE)

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ")

        self.assertEqual(200, response.status_code)
        self.assertIn("Select EQ collection instruments".encode(), response.data)
        self.assertIn("btn-add-ci".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @mock_decorator(CE_READY, EQ_SURVEY, ce_events=CE_EVENTS)
    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_linked_ci_eq_view_sample_ci_page_no_survey_permission(
        self, mock_request, mock_get_linked_cis_and_cir_version
    ):
        mock_request.get(url_ce_by_id, json=CE)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=EQ_CI, complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=EQ_CI_SELECTORS, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=SAMPLE_SUMMARY)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=CE)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=CE)

        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ")

        self.assertEqual(200, response.status_code)
        self.assertIn("1 EQ collection instrument selected".encode(), response.data)
        self.assertNotIn("form-unselect-eq-ci-1".encode(), response.data)

    @mock_decorator(CE_EVENTS)
    @requests_mock.mock()
    def test_loaded_sample_upload_sample_page_survey_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=EQ_SURVEY)
        mock_request.get(url_ces_by_survey, json=CE)
        mock_request.get(url_ce_by_id, json=CE)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=EQ_CI, complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=EQ_CI_SELECTORS, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=SAMPLE_SUMMARY)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=CE)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=CE)

        response = self.client.get(f"/surveys/{short_name}/{period}/upload-sample-file")

        self.assertEqual(200, response.status_code)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertIn("Total businesses".encode(), response.data)
        self.assertIn("Collection instruments".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @mock_decorator(CE_EVENTS)
    @requests_mock.mock()
    def test_upload_sample_page_no_survey_permission(self, mock_request):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        mock_request.get(url_get_survey_by_short_name, json=EQ_SURVEY)
        mock_request.get(url_ces_by_survey, json=CE)
        mock_request.get(url_ce_by_id, json=CE)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=EQ_CI, complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=EQ_CI_SELECTORS, complete_qs=True
        )
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=SAMPLE_SUMMARY)

        mock_request.get(url_get_by_survey_with_ref_start_date, json=CE)
        mock_request.get(url_get_by_survey_with_ref_end_date, json=CE)

        response = self.client.get(f"/surveys/{short_name}/{period}/upload-sample-file")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have permission to access this page. "
            "If you believe this is a mistake, contact your SDC champion.".encode(),
            response.data,
        )

    @mock_decorator(CE_READY, EQ_SURVEY)
    @requests_mock.mock()
    def test_upload_sample_no_survey_permission(self, mock_request):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv")}
        sample_data = {"id": sample_summary_id}
        collection_exercise_link = {"id": ""}

        mock_request.post(url_sample_service_upload, json=sample_data)
        mock_request.put(url_collection_exercise_link, json=collection_exercise_link)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/upload-sample-file", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have permission to access this page. "
            "If you believe this is a mistake, contact your SDC champion.".encode(),
            response.data,
        )

    @mock_decorator(CE_READY, EQ_SURVEY)
    @requests_mock.mock()
    def test_remove_loaded_sample_no_survey_permission(self, mock_request):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)

        mock_request.delete(url_party_delete_attributes, status_code=204)
        mock_request.delete(url_ce_remove_sample, status_code=200)
        mock_request.delete(url_delete_sample_summary, status_code=204)
        response = self.client.post(f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have permission to access this page. "
            "If you believe this is a mistake, contact your SDC champion.".encode(),
            response.data,
        )

    @mock_decorator(CE_READY, EQ_SURVEY)
    def test_loaded_ci_load_collection_instrument_no_page_survey_permission(self):
        response = self.client.get(f"/surveys/{short_name}/{period}/load-collection-instruments", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Upload".encode(), response.data)
        self.assertNotIn("Choose file".encode(), response.data)
        self.assertIn("1 SEFT collection instruments uploaded".encode(), response.data)
        self.assertIn("Done".encode(), response.data)

    @mock_decorator(CE_READY, EQ_SURVEY)
    @requests_mock.mock()
    def test_load_ci_load_collection_instrument_page_no_survey_permission(self, mock_request):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have permission to access this page. "
            "If you believe this is a mistake, contact your SDC champion.".encode(),
            response.data,
        )

    @mock_decorator(CE_READY, EQ_SURVEY)
    @requests_mock.mock()
    def test_remove_ci_load_collection_instrument_page_no_survey_permission(self, mock_request):
        # Sign in without correct permissions
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        post_data = {
            "ci_id": collection_instrument_id,
            "ce_id": collection_exercise_id,
            "unselect-eq-ci": "",
        }

        response = self.client.post(
            f"/surveys/{short_name}/{period}/load-collection-instruments", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have permission to access this page. "
            "If you believe this is a mistake, contact your SDC champion.".encode(),
            response.data,
        )

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    def test_collection_exercise_no_survey_edit_permission(self, mock_request):
        response = self.client.get(f"/surveys/{short_name}/{period}", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Monthly Survey of Building Materials Bricks".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)
        self.assertNotIn("Add".encode(), response.data)
        self.assertNotIn("Edit".encode(), response.data)
        self.assertNotIn("Add nudge email".encode(), response.data)
        self.assertNotIn("Add reminder".encode(), response.data)
        self.assertIn("Sample loaded".encode(), response.data)
        self.assertNotIn("Set as ready for live".encode(), response.data)

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_add_collection_instrument_success(self, mock_request, mock_get_linked_cis_and_cir_version):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)

        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]

        post_data = {"formtype": "0001", "add-eq-ci": ""}

        mock_request.get(url_survey_shortname, json=EQ_SURVEY)
        mock_request.post(
            f"{url_post_instrument_link}?survey_id={survey_id}&classifiers=%7B%22form_type%22%3A%220001%22%2C%22eq_id"
            f"%22%3A%22mbs%22%7D",
            status_code=200,
        )
        mock_request.get(f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=[], complete_qs=True)
        mock_request.get(f"{url_get_collection_instrument}?{ci_search_string}", json=[], complete_qs=True)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ",
            data=post_data,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(collection_instrument_id.encode(), response.data)

    @mock_decorator(CE, EQ_SURVEY, EQ_CI, SAMPLE_SUMMARY, CE_EVENTS)
    @requests_mock.mock()
    @patch(
        "response_operations_ui.views.collection_exercise.collection_instrument_controllers"
        ".get_linked_cis_and_cir_version"
    )
    def test_add_collection_instrument_duplicate(self, mock_request, mock_get_linked_cis_and_cir_version):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"formtype": "0001", "add-eq-ci": ""}

        mock_get_linked_cis_and_cir_version.return_value = [
            {
                "id": collection_instrument_id,
                "form_type": "0001",
                "checked": "true",
                "ci_version": None,
            }
        ]
        mock_request.get(url_survey_shortname, json=EQ_SURVEY)

        mock_request.post(
            f"{url_post_instrument_link}?survey_id={survey_id}&classifiers=%7B%22form_type%22%3A%220001%22%2C%22eq_id"
            f"%22%3A%22mbs%22%7D",
            status_code=400,
            content=b'{"errors":["Failed to link collection instrument to survey"]}',
        )
        mock_request.get(f"{url_get_collection_instrument}?{ci_type_search_string_eq}", json=[], complete_qs=True)
        mock_request.get(
            f"{url_get_collection_instrument}?{ci_search_string}",
            json=EQ_CI,
            complete_qs=True,
        )
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci?survey_mode=EQ", data=post_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("There is a problem with this page".encode(), response.data)

    @mock_decorator(CE, EQ_SURVEY)
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_cis_and_cir_version")
    def test_view_sample_ci_summary(self, get_cis_and_cir_version):
        get_cis_and_cir_version.return_value = [
            {"form_type": "0001", "ci_version": "12"},
            {"form_type": "0002", "ci_version": None},
        ]

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f"/surveys/{short_name}/{period}/view-sample-ci/summary/0001".encode(),
            response.data,
        )
        self.assertIn("Choose a version".encode(), response.data)
        self.assertIn("Edit version".encode(), response.data)
        self.assertIn("Version 12".encode(), response.data)

    @mock_decorator(CE, EQ_SURVEY)
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_cis_and_cir_version")
    def test_view_sample_ci_summary_no_cis(self, get_cis_and_cir_version):
        get_cis_and_cir_version.return_value = []

        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Choose a version".encode(), response.data)
        self.assertNotIn("Edit version".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_registry_instrument")
    @patch("response_operations_ui.controllers.collection_exercise_controllers.get_collection_exercises_by_survey")
    @patch("response_operations_ui.common.redis_cache.get_survey_by_shortname")
    @patch("response_operations_ui.common.redis_cache.get_cir_metadata")
    def test_view_ci_versions_metadata_returned(
        self, mock_request, mock_cir_details, mock_get_shortname, mock_get_collection_exercises_by_survey, mock_registry
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        mock_get_collection_exercises_by_survey.return_value = [CE]
        mock_get_shortname.return_value = {"short_name": {"survey_ref": survey_id}}
        mock_cir_details.return_value = cir_metadata
        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(form_type.encode(), response.data)
        self.assertIn("Back to CIR versions".encode(), response.data)
        self.assertIn("Choose CIR version for EQ formtype".encode(), response.data)
        self.assertIn("Version 1".encode(), response.data)
        self.assertIn("Published: 16/07/2024 at 14:26:44".encode(), response.data)
        self.assertIn("Save".encode(), response.data)

    @mock_decorator(CE, EQ_SURVEY, EQ_CI)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.save_registry_instrument")
    @patch("response_operations_ui.common.redis_cache.get_cir_metadata")
    def test_save_ci_versions(
        self,
        mock_request,
        mock_cir_details,
        mock_save_registry_instrument,
    ):
        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"formtype": "0001", "ci-versions": "427d40e6-f54a-4512-a8ba-e4dea54ea3dc"}

        mock_cir_details.return_value = cir_metadata
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci/summary/0001", data=post_data, follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/surveys/{short_name}/{period}".encode(), response.data)

        mock_save_registry_instrument.assert_called_once_with(
            "14fb3e68-4dca-46db-bf49-04b84e07e77c",
            "0001",
            1,
            "427d40e6-f54a-4512-a8ba-e4dea54ea3dc",
            "a32800c5-5dc1-459d-9932-0da6c21d2ed2",
            "2024-07-16T14:26:44.609010Z",
            "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
        )

    @mock_decorator(CE, EQ_SURVEY, EQ_CI)
    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.delete_registry_instruments")
    @patch(
        "response_operations_ui.views.collection_exercise."
        "collection_exercise_controllers.get_collection_exercises_by_survey"
    )
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_cis_and_cir_version")
    def test_delete_ci_versions(
        self,
        mock_request,
        mock_collection_instrument,
        mock_collection_exercise,
        mock_delete_registry_instruments,
    ):
        mock_collection_exercise.return_value = CE
        mock_delete_registry_instruments.return_value = {"status_code": 200}
        mock_collection_instrument.return_value = [{"form_type": "0001", "ci_version": None}]

        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        post_data = {"formtype": "0001", "ci-versions": "nothing-selected", "period": period}
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci/summary/0001", data=post_data, follow_redirects=True
        )
        self.assertIn(f"/surveys/{short_name}/{period}/view-sample-ci/summary".encode(), response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instruments step 2 of 2".encode(), response.data)
        self.assertIn(form_type.encode(), response.data)
        self.assertIn("Nothing selected".encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.controllers.collection_instrument_controllers.get_registry_instrument")
    @patch("response_operations_ui.common.redis_cache.get_survey_by_shortname")
    @patch("response_operations_ui.controllers.collection_exercise_controllers.get_collection_exercises_by_survey")
    @patch("response_operations_ui.common.redis_cache.get_cir_metadata")
    def test_view_ci_versions_no_metadata(
        self,
        mock_request,
        mock_cir_details,
        mock_get_collection_exercises_by_survey,
        mock_redis,
        mock_response,
    ):
        mock_cir_details.side_effect = ExternalApiError(mock_response, ErrorCode.NOT_FOUND)
        mock_get_collection_exercises_by_survey.return_value = [CE]
        mock_response = mock_response.return_value
        mock_response.url.return_value = url_cir_get_metadata
        mock_response.status_code.return_value = "404"
        mock_response.message.return_value = "No results found"
        mock_redis.return_value = {"short_name": {"survey_ref": survey_id}}

        sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Choose CIR version for EQ formtype".encode(), response.data)
        self.assertIn(CIR_ERROR_MESSAGES[ErrorCode.NOT_FOUND].encode(), response.data)

    @requests_mock.mock()
    @patch("response_operations_ui.common.redis_cache.get_survey_by_shortname")
    @patch("response_operations_ui.controllers.collection_exercise_controllers.get_collection_exercises_by_survey")
    def test_view_ci_versions_unable_to_connect_to_cir(
        self, mock_request, mock_get_collection_exercises_by_survey, mock_redis
    ):
        collection_instrument_controllers.get_registry_instrument = Mock()
        mock_get_collection_exercises_by_survey.return_value = [CE]
        mock_response = Mock()
        mock_response.url.return_value = url_cir_get_metadata
        mock_response.status_code.return_value = "E0001"
        mock_response.message.return_value = "Unable to connect to CIR"
        mock_redis.return_value = {"short_name": {"survey_ref": survey_id}}
        with patch(
            "response_operations_ui.common.redis_cache.get_cir_metadata",
            Mock(side_effect=ExternalApiError(mock_response, ErrorCode.API_CONNECTION_ERROR)),
        ):
            sign_in_with_permission(self, mock_request, user_permission_surveys_edit_json)
            response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Choose CIR version for EQ formtype".encode(), response.data)
            self.assertIn(CIR_ERROR_MESSAGES[ErrorCode.API_CONNECTION_ERROR].encode(), response.data)

    @requests_mock.mock()
    def test_post_cir_version_no_permission(self, mock_request):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        response = self.client.post(
            f"/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You do not have permission to access this page. "
            "If you believe this is a mistake, contact your SDC champion.".encode(),
            response.data,
        )

    @requests_mock.mock()
    @patch("response_operations_ui.views.collection_exercise._build_cir_metadata")
    @patch("response_operations_ui.common.redis_cache.get_survey_by_shortname")
    def test_get_cir_version_no_permission(self, mock_request, mock_get_shortname, build_cir_metadata):
        sign_in_with_permission(self, mock_request, user_permission_messages_edit_json)
        build_cir_metadata.return_value = cir_metadata, ""
        mock_get_shortname.return_value = {"short_name": {"survey_ref": survey_id}}
        response = self.client.get(f"/surveys/{short_name}/{period}/view-sample-ci/summary/{form_type}")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Save".encode(), response.data)

    @patch("response_operations_ui.controllers.collection_exercise_controllers.get_linked_sample_summary_id")
    @patch("response_operations_ui.controllers.sample_controllers.get_sample_summary")
    def test_get_sample_summary(self, sample_summary, linked_sample_summary_id):
        sample_summary.return_value = SAMPLE_SUMMARY
        linked_sample_summary_id.return_value = sample_summary_id
        sample_summary = get_sample_summary(collection_exercise_id)

        self.assertEqual(sample_summary, SAMPLE_SUMMARY)

    @patch("response_operations_ui.controllers.survey_controllers.get_survey_by_shortname")
    @patch("response_operations_ui.controllers.collection_exercise_controllers.get_collection_exercises_by_survey")
    def test_get_collection_exercise_and_survey_details(self, collection_exercises_by_survey, survey_by_shortname):
        collection_exercises_by_survey.return_value = [CE]
        survey_by_shortname.return_value = SEFT_SURVEY
        exercise, survey = get_collection_exercise_and_survey_details("MBS", period)

        self.assertEqual(exercise, CE)
        self.assertEqual(survey, SEFT_SURVEY)

    @patch(
        "response_operations_ui.controllers.collection_instrument_controllers.get_collection_instruments_by_classifier"
    )
    def test_build_collection_instruments_details(self, collection_instruments_by_classifier):
        collection_instruments_by_classifier.return_value = SEFT_CI["SEFT"]
        collection_instruments = _build_collection_instruments_details(collection_exercise_id, survey_id)
        self.assertEqual(collection_instruments, SEFT_CI)
