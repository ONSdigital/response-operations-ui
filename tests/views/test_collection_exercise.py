import copy
import json
from io import BytesIO
from unittest.mock import patch
from urllib.parse import urlencode, urlparse

import mock
import requests_mock

from config import TestingConfig
from response_operations_ui.controllers.collection_exercise_controllers import \
    get_collection_exercises_with_events_and_samples_by_survey_id
from response_operations_ui.views.collection_exercise import get_existing_sorted_nudge_events
from tests.views import ViewTestCase

ci_selector_id = 'efa868fb-fb80-44c7-9f33-d6800a17c4da'
collection_exercise_event_id = 'b4a36392-a21f-485b-9dc4-d151a8fcd565'
collection_exercise_id = '14fb3e68-4dca-46db-bf49-04b84e07e77c'
collection_instrument_id = 'a32800c5-5dc1-459d-9932-0da6c21d2ed2'
period = '000000'
sample_summary_id = '1a11543f-eb19-41f5-825f-e41aca15e724'
short_name = 'MBS'
survey_id = 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87'
survey_ref = '141'

collex_root = "tests/test_data/collection_exercise/collection_exercise_details"
no_sample = collex_root + "_no_sample.json"
failed_validation = collex_root + "_failedvalidation.json"
collex_details = collex_root + ".json"

"""Load all the necessary test data"""
with open(collex_details) as json_data:
    collection_exercise_details = json.load(json_data)

with open(no_sample) as json_data:
    collection_exercise_details_no_sample = json.load(json_data)

with open(failed_validation) as json_data:
    collection_exercise_details_failedvalidation = json.load(json_data)

with open("tests/test_data/survey/edited_survey_ce_details.json") as json_data:
    updated_survey_info = json.load(json_data)

with open("tests/test_data/survey/survey_by_id.json") as fp:
    survey_by_id = json.load(fp)

with open("tests/test_data/collection_exercise/exercise_data.json") as json_data:
    exercise_data = json.load(json_data)

with open("tests/test_data/collection_exercise/ce_details_new_event.json") as fp:
    ce_details_no_events = json.load(fp)

with open('tests/test_data/survey/classifier_type_selectors.json') as json_data:
    classifier_type_selectors = json.load(json_data)

with open('tests/test_data/survey/classifier_types.json') as json_data:
    classifier_types = json.load(json_data)

with open('tests/test_data/collection_exercise/formatted_collection_exercise_details.json') as fp:
    formatted_collection_exercise_details = json.load(fp)

with open('tests/test_data/collection_exercise/collection_exercise.json') as json_data:
    collection_exercise = json.load(json_data)

with open('tests/test_data/survey/single_survey.json') as json_data:
    survey = json.load(json_data)

with open('tests/test_data/collection_exercise/events.json') as json_data:
    events = json.load(json_data)

with open('tests/test_data/collection_exercise/nudge_events_one.json') as json_data:
    nudge_events_one = json.load(json_data)

with open('tests/test_data/collection_exercise/nudge_events_two.json') as json_data:
    nudge_events_two = json.load(json_data)

with open('tests/test_data/collection_exercise/events_2030.json') as json_data:
    events_2030 = json.load(json_data)

"""Define URLS"""
url_ce_by_id = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/{collection_exercise_id}'
)
url_ce_remove_sample = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/unlink/{collection_exercise_id}'
    f'/sample/{sample_summary_id}'
)
url_ces_by_survey = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey/{survey_id}'
)
url_collection_exercise_link = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/link'
    f'/{collection_exercise_id}'
)
url_collection_instrument = (
    f'{TestingConfig.COLLECTION_INSTRUMENT_URL}'
    f'/collection-instrument-api/1.0.2/upload/{collection_exercise_id}'
)
url_collection_instrument_link = (
    f'{TestingConfig.COLLECTION_INSTRUMENT_URL}'
    f'/collection-instrument-api/1.0.2/link-exercise'
    f'/{collection_instrument_id}/{collection_exercise_id}'
)
url_collection_instrument_unlink = (
    f'{TestingConfig.COLLECTION_INSTRUMENT_URL}'
    f'/collection-instrument-api/1.0.2/unlink-exercise'
    f'/{collection_instrument_id}/{collection_exercise_id}'
)
url_survey_shortname = f'{TestingConfig.SURVEY_URL}/surveys/shortname/{short_name}'
url_sample_service_upload = f'{TestingConfig.SAMPLE_URL}/samples/B/fileupload'
url_collection_exercise_survey_id = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey'
    f'/{survey_id}'
)

url_update_ce_user_details = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises'
    f'/{collection_exercise_id}/userDescription'
)
url_update_ce_period = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises'
    f'/{collection_exercise_id}/exerciseRef'
)

url_execute = f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexerciseexecution/{collection_exercise_id}'
url_create_collection_exercise = f'{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises'
url_get_classifier_type_selectors = (
    f'{TestingConfig.SURVEY_URL}/surveys/{survey_id}/classifiertypeselectors'
)
url_get_classifier_type = (
    f'{TestingConfig.SURVEY_URL}'
    f'/surveys/{survey_id}/classifiertypeselectors/{ci_selector_id}'
)
url_get_collection_exercise_events = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}'
    f'/collectionexercises/{collection_exercise_id}/events'
)
url_get_collection_instrument = (
    f'{TestingConfig.COLLECTION_INSTRUMENT_URL}'
    f'/collection-instrument-api/1.0.2/collectioninstrument'
)
url_get_sample_summary = (
    f'{TestingConfig.SAMPLE_URL}'
    f'/samples/samplesummary/{sample_summary_id}'
)
url_get_survey_by_short_name = f'{TestingConfig.SURVEY_URL}/surveys/shortname/{short_name}'
url_link_sample = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}'
    f'/collectionexercises/link/{collection_exercise_id}'
)
url_get_collection_exercises_link = (
    f'{TestingConfig.COLLECTION_EXERCISE_URL}'
    f'/collectionexercises/link/{collection_exercise_id}'
)

ci_search_string = urlencode({'searchString': json.dumps({
    "SURVEY_ID": survey_id,
    "COLLECTION_EXERCISE": collection_exercise_id
})})

ci_type_search_string = urlencode({'searchString': json.dumps({
    "SURVEY_ID": survey_id,
    "TYPE": "EQ"
})})


class TestCollectionExercise(ViewTestCase):

    def setup_data(self):
        self.headers = {"Authorization": "test_jwt", "Content-Type": "application/json"}
        self.survey_data = {"id": survey_id}
        self.survey = {
            "id": survey_id,
            "longName": "Business Register and Employment Survey",
            "shortName": "BRES",
            "surveyRef": "221"
        }
        self.collection_exercises = [
            {
                "id": collection_exercise_id,
                "name": "201601",
                "scheduledExecutionDateTime": "2017-05-15T00:00:00Z",
                "state": "PUBLISHED",
                "exerciseRef": "000000"
            }
        ]
        self.collection_exercise_events = [
            {
                "id": collection_exercise_event_id,
                "collectionExerciseId": collection_exercise_id,
                "tag": "mps",
                "timestamp": "2018-03-16T00:00:00.000Z"
            }
        ]
        self.collection_exercises_link = [sample_summary_id]
        self.collection_instruments = [
            {
                "classifiers": {
                    "COLLECTION_EXERCISE": [
                        collection_exercise_id,
                    ],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                },
                "file_name": "file",
                "id": collection_instrument_id,
                "surveyId": survey_id
            }
        ]
        self.eq_ci_selectors = [
            {
                "classifiers": {
                    "COLLECTION_EXERCISE": [
                    ],
                    "RU_REF": [],
                    "SURVEY_ID": survey_id,
                },
                "file_name": None,
                "id": collection_instrument_id,
                "surveyId": survey_id
            }
        ]
        self.linked_sample = {
            "collectionExerciseId": collection_exercise_id,
            "sampleSummaryIds": [
                sample_summary_id,
            ]
        }
        self.sample_summary = {
            "id": sample_summary_id,
            "effectiveStartDateTime": "",
            "effectiveEndDateTime": "",
            "surveyRef": "",
            "ingestDateTime": "2018-03-14T14:29:51.325Z",
            "state": "ACTIVE",
            "totalSampleUnits": 5,
            "expectedCollectionInstruments": 1
        }

    @requests_mock.mock()
    def test_collection_exercise_view(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', json=self.collection_instruments,
                         complete_qs=True)
        mock_request.get(f'{url_get_collection_instrument}?{ci_type_search_string}', json=self.eq_ci_selectors,
                         complete_qs=True)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_classifier_type_selectors, json=classifier_type_selectors)
        mock_request.get(url_get_classifier_type, json=classifier_types)

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Business Register and Employment Survey".encode(), response.data)
        self.assertIn("221_201712".encode(), response.data)

    @requests_mock.mock()
    def test_collection_exercise_view_404(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=[])

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_empty_list(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, status_code=204)

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_404_no_match(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=[
            {
                "exerciseRef": "111111"
            }
        ])

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_service_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, status_code=500)

        response = self.client.get(f'/surveys/{short_name}/{period}')

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 1)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_ci_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', status_code=400)

        response = self.client.get(f'/surveys/{short_name}/{period}')

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_classifiers_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', json=self.collection_instruments,
                         complete_qs=True)
        mock_request.get(f'{url_get_collection_instrument}?{ci_type_search_string}', json=self.eq_ci_selectors,
                         complete_qs=True)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_classifier_type_selectors, json=classifier_type_selectors)
        mock_request.get(url_get_classifier_type, status_code=400)

        response = self.client.get(f'/surveys/{short_name}/{period}')

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 10)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_classifiers_204(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', json=self.collection_instruments,
                         complete_qs=True)
        mock_request.get(f'{url_get_collection_instrument}?{ci_type_search_string}', json=self.eq_ci_selectors,
                         complete_qs=True)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_classifier_type_selectors, status_code=204)

        response = self.client.get(f'/surveys/{short_name}/{period}')

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 9)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_collection_exercise_view_selectors_fail(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', json=self.collection_instruments,
                         complete_qs=True)
        mock_request.get(f'{url_get_collection_instrument}?{ci_type_search_string}', json=self.eq_ci_selectors,
                         complete_qs=True)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_classifier_type_selectors, status_code=400)

        response = self.client.get(f'/surveys/{short_name}/{period}')

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 9)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_upload_collection_instrument(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_ces_by_survey, json=exercise_data)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument loaded".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_select_collection_instrument(self, mock_request, mock_details):
        post_data = {
            "checkbox-answer": [collection_instrument_id],
            "ce_id": collection_exercise_id,
            "select-ci": ""
        }
        mock_request.post(url_collection_instrument_link, status_code=200)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instruments added".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_failed_select_collection_instrument(self, mock_request, mock_details):
        post_data = {"checkbox-answer": [collection_instrument_id], "ce_id": collection_exercise_id, "select-ci": ""}
        mock_request.post(url_collection_instrument_link, status_code=500)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to add collection instrument(s)".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_failed_no_selected_collection_instrument(self, mock_request, mock_details):
        post_data = {"checkbox-answer": [], "ce_id": "000000", "select-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: No collection instruments selected".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_view_collection_instrument_after_upload(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=201)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_collection_instrument.xlxs".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_failed_upload_collection_instrument(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.xlsx"), "load-ci": ""}
        mock_request.post(url_collection_instrument, status_code=500)
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to upload collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_no_upload_collection_instrument_when_bad_extension(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_0001.html"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: wrong file type for collection instrument".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_no_upload_collection_instrument_when_bad_form_type_format(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_xxxxx.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn(
            "Error: invalid file name format for collection instrument".encode(), response.data
        )

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_no_upload_collection_instrument_bad_file_name_format(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064201803_xxxxx.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn(
            "Error: invalid file name format for collection instrument".encode(), response.data
        )

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_no_upload_collection_instrument_form_type_not_integer(self, mock_request, mock_details):
        post_data = {"ciFile": (BytesIO(b"data"), "064_201803_123E.xlsx"), "load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn(
            "Error: invalid file name format for collection instrument".encode(), response.data
        )

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_no_upload_collection_instrument_when_no_file(self, mock_request, mock_details):
        post_data = {"load-ci": ""}
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Collection instrument loaded".encode(), response.data)
        self.assertIn("Error: No collection instrument supplied".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_view_collection_instrument(self, mock_request, mock_details):
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("test_collection_instrument.xlxs".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_choose_collection_instrument_when_first(self, mock_request, mock_details):
        with open(
                "tests/test_data/collection_exercise/formatted_collection_exercise_details_no_ci.json"
        ) as collection_exercise:
            mock_details.return_value = json.load(collection_exercise)

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add a collection instrument. Must be XLSX".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_add_another_collection_instrument_when_already_uploaded(self, mock_request, mock_details):
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Add another collection instrument. Must be XLSX".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_upload_sample(self, mock_request, mock_details):
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

        sample_data = {
            "id": sample_summary_id
        }

        collection_exercise_link = {"id": ""}

        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey_data)
        mock_request.get(
            url_ces_by_survey, json=exercise_data
        )
        mock_request.post(url_sample_service_upload, json=sample_data)
        mock_request.put(
            url_collection_exercise_link, json=collection_exercise_link
        )

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Loaded sample summary".encode(), response.data)
        self.assertIn("8\n".encode(), response.data)
        self.assertIn("1\n".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_upload_sample_link_failure(self, mock_request, mock_details):
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}
        sample_data = {"id": sample_summary_id}
        collection_exercise_link = {"id": ""}

        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=200, json=sample_data)
        mock_request.put(url_collection_exercise_link, status_code=500, json=collection_exercise_link)

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 4)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_upload_sample_exception(self, mock_request, mock_details):
        post_data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}
        sample_data = {"id": sample_summary_id}

        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=500, json=sample_data)

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_failed_upload_sample(self, mock_request, mock_details):
        data = {"sampleFile": (BytesIO(b"data"), "test.csv"), "load-sample": ""}

        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(url_ces_by_survey, status_code=200, json=exercise_data)
        mock_request.post(url_sample_service_upload, status_code=500)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=data)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_no_upload_sample_when_bad_extension(self, mock_request, mock_details):
        data = {"sampleFile": (BytesIO(b"data"), "test.html"), "load-sample": ""}
        with open(
                "tests/test_data/collection_exercise/formatted_collection_exercise_details_no_sample.json"
        ) as collection_exercise:
            mock_details.return_value = json.load(collection_exercise)
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(
            url_ces_by_survey, status_code=200, json=exercise_data
        )

        response = self.client.post(f'/surveys/{short_name}/{period}', data=data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_no_upload_sample_when_no_file(self, mock_request, mock_details):
        data = {"load-sample": ""}
        with open(
                "tests/test_data/collection_exercise/formatted_collection_exercise_details_no_sample.json"
        ) as collection_exercise:
            mock_details.return_value = json.load(collection_exercise)
        mock_request.get(url_get_survey_by_short_name, status_code=200, json=self.survey_data)
        mock_request.get(
            url_ces_by_survey, status_code=200, json=exercise_data
        )
        response = self.client.post(
            f'/surveys/{short_name}/{period}', data=data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Loaded sample summary".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_post_ready_for_live(self, mock_request, mock_details):
        post_data = {"ready-for-live": ""}
        details = formatted_collection_exercise_details.copy()
        details['collection_exercise']['state'] = 'EXECUTION_STARTED'
        mock_request.post(url_execute, status_code=200)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_details.return_value = details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_post_ready_for_live_404(self, mock_request, mock_details):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=404)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Error: Failed to execute Collection Exercise".encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live_empty(self, mock_request):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=404)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 5)  # Redirect calls mocked requests 2 additional times
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_post_ready_for_live_failed(self, mock_request, mock_details):
        post_data = {"ready-for-live": ""}
        mock_request.post(url_execute, status_code=500)
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=200, json=exercise_data)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Sample loaded successfully".encode(), response.data)
        self.assertNotIn("Collection exercise executed".encode(), response.data)
        self.assertIn("Error: Failed to execute Collection Exercise".encode(), response.data)

    @requests_mock.mock()
    def test_post_ready_for_live_service_fail(self, mock_request):
        post_data = {"ready-for-live": ""}
        mock_request.get(url_survey_shortname, status_code=200, json=self.survey_data)
        mock_request.get(url_collection_exercise_survey_id, status_code=500)

        response = self.client.post(f'/surveys/{short_name}/{period}', data=post_data, follow_redirects=True)

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_get_processing(self, mock_request, mock_details):
        details = formatted_collection_exercise_details.copy()
        details["collection_exercise"]["state"] = "EXECUTION_STARTED"
        mock_details.return_value = details

        response = self.client.get(f'/surveys/{short_name}/{period}')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Processing collection exercise".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_failed_execution(self, mock_request, mock_details):
        with open(
                "tests/test_data/collection_exercise/formatted_collection_exercise_details_failedvalidation.json"
        ) as collection_exercise:
            mock_details.return_value = json.load(collection_exercise)

        response = self.client.get(f'/surveys/{short_name}/{period}')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ready for review".encode(), response.data)
        self.assertIn("Error processing collection exercise".encode(), response.data)
        self.assertIn("Incorrect file type. Please choose a file type XLSX".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_update_collection_exercise_details_success(self, mock_request, mock_details):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201907",
            "hidden_survey_id": survey_id,
        }
        # update survey
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.put(url_update_ce_user_details)
        mock_request.put(url_update_ce_period)
        # redirect to survey details
        mock_request.get(url_ces_by_survey, json=updated_survey_info['collection_exercises'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("16th June 2019".encode(), response.data)
        self.assertIn("201906".encode(), response.data)

    @requests_mock.mock()
    def test_update_collection_exercise_userdescription_success(self, mock_request):
        test_description = '16th June 2019'
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": test_description,
            "period": "201906",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info['collection_exercises'])
        mock_request.put(url_update_ce_user_details)

        response = self.client.post(
            f"/surveys/{short_name}/201906/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, f'/surveys/{short_name}')

    @requests_mock.mock()
    def test_update_collection_exercise_details_fail(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201906",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info['collection_exercises'])
        mock_request.put(url_update_ce_user_details, status_code=500)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_collection_exercise_details_404(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201906",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info['collection_exercises'])
        mock_request.put(url_update_ce_user_details, status_code=404)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_collection_exercise_period_fail(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201907",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info['collection_exercises'])
        mock_request.put(url_update_ce_user_details, status_code=200)
        mock_request.put(url_update_ce_period, status_code=500)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_update_collection_exercise_period_404(self, mock_request):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "201907",
            "hidden_survey_id": survey_id,
        }
        mock_request.get(url_ces_by_survey, json=updated_survey_info['collection_exercises'])
        mock_request.put(url_update_ce_user_details, status_code=200)
        mock_request.put(url_update_ce_period, status_code=404)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 3)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_get_ce_details(self, mock_request, mock_details):
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.get(url_ces_by_survey, json=updated_survey_info['collection_exercises'])
        response = self.client.get(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(collection_exercise_id.encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_unlink_collection_instrument(self, mock_request, mock_details):
        post_data = {
            "ci_id": collection_instrument_id,
            "ce_id": collection_exercise_id,
            "unselect-ci": "",
        }

        mock_request.put(url_collection_instrument_unlink, status_code=200)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection instrument removed".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_failed_unlink_collection_instrument(self, mock_request, mock_details):
        post_data = {
            "ci_id": collection_instrument_id,
            "ce_id": collection_exercise_id,
            "unselect-ci": "",
        }

        mock_request.put(url_collection_instrument_unlink, status_code=500)
        mock_details.return_value = formatted_collection_exercise_details

        response = self.client.post(f"/surveys/{short_name}/{period}", data=post_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Error: Failed to remove collection instrument".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_success(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "123456",
        }
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("123456".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_failure(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "123456",
        }
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.post(url_create_collection_exercise, status_code=500)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details
        )

        request_history = mock_request.request_history
        self.assertEqual(len(request_history), 2)
        self.assertEqual(response.status_code, 500)

    @requests_mock.mock()
    def test_get_create_ce_form(self, mock_request):
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        response = self.client.get(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Create collection exercise".encode(), response.data)

    @requests_mock.mock()
    def test_failed_create_ce_validation_period_exists(self, mock_request):
        taken_period = '12345'
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": taken_period,
        }
        ces = self.collection_exercises
        ces[0]['exerciseRef'] = taken_period
        mock_request.get(url_ces_by_survey, json=ces)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Please use a period that is not in use by any collection exercise for this survey".encode(),
            response.data,
        )

    @requests_mock.mock()
    def test_failed_create_ce_letters_fails_in_period_validation(self, mock_request):
        new_collection_exercise_details = {
            "hidden_survey_name": "BRES",
            "hidden_survey_id": survey_id,
            "user_description": "New collection exercise",
            "period": "hello",
        }
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info)
        mock_request.post(url_create_collection_exercise, status_code=200)

        response = self.client.post(
            f"/surveys/{survey_ref}/{short_name}/create-collection-exercise",
            data=new_collection_exercise_details,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_failed_edit_ce_validation_period_exists(self, mock_request, mock_details):
        taken_period = '12345'
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": taken_period,
            "hidden_survey_id": survey_id,
        }

        # update survey
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.put(url_update_ce_user_details)

        # failed validation
        ces = self.collection_exercises
        ces.append(ces[0])
        ces[1]['id'] = survey_id  # new id
        ces[1]['exerciseRef'] = taken_period
        mock_request.get(url_ces_by_survey, json=ces)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Please use a period that is not in use by any collection exercise for this survey".encode(),
            response.data,
        )

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_failed_edit_ce_validation_letters_in_period_fails_validation(self, mock_request, mock_details):
        changed_ce_details = {
            "collection_exercise_id": collection_exercise_id,
            "user_description": "16th June 2019",
            "period": "hello",
            "hidden_survey_id": survey_id,
        }
        # update survey
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.get(url_get_survey_by_short_name, json=updated_survey_info['survey'])
        mock_request.put(url_update_ce_user_details)

        # failed validation
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(url_get_collection_exercises_link, json=self.collection_exercises_link)
        mock_request.get(url_get_sample_summary, json=self.sample_summary)

        response = self.client.post(
            f"/surveys/{short_name}/{period}/edit-collection-exercise-details",
            data=changed_ce_details,
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter numbers only for the period".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_remove_loaded_sample_success(self, mock_request, mock_details):
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.delete(url_ce_remove_sample, status_code=200)
        response = self.client.post(
            f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample removed".encode(), response.data)

    @requests_mock.mock()
    @patch('response_operations_ui.views.collection_exercise.build_collection_exercise_details')
    def test_remove_loaded_sample_failed(self, mock_request, mock_details):
        mock_details.return_value = formatted_collection_exercise_details
        mock_request.delete(url_ce_remove_sample, status_code=500)
        response = self.client.post(
            f"/surveys/{short_name}/{period}/confirm-remove-sample", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Error: Failed to remove sample'.encode(), response.data)

    def test_get_confirm_remove_sample(self):
        response = self.client.get("/surveys/test/000000/confirm-remove-sample",
                                   follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Remove sample from test 000000".encode(), response.data)

    @requests_mock.mock()
    def test_get_create_ce_event_form_success(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        response = self.client.get(f"/surveys/MBS/201801/{collection_exercise_id}/confirm-create-event/mps",
                                   follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("MBS".encode(), response.data)
        self.assertIn("Main print selection".encode(), response.data)

    @mock.patch("response_operations_ui.views.collection_exercise.build_collection_exercise_details")
    @mock.patch("response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event")
    def test_create_collection_exercise_event_success(self, mock_ce_events, mock_get_ce_details):
        with open(
                "tests/test_data/collection_exercise/formatted_collection_exercise_details_no_events.json"
        ) as collection_exercise:
            mock_get_ce_details.return_value = json.load(collection_exercise)
            mock_ce_events.return_value = None
        create_ce_event_form = {
            "day": "01",
            "month": "01",
            "year": "2030",
            "hour": "01",
            "minute": "00"
        }

        response = self.client.post(f"/surveys/MBS/201901/{collection_exercise_id}/create-event/mps",
                                    data=create_ce_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Event date added.".encode(), response.data)

    @requests_mock.mock()
    def test_create_collection_exercise_invalid_form(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        create_ce_event_form = {
            "day": "50",
            "month": "01",
            "year": "2018",
            "hour": "01",
            "minute": "00"
        }

        response = self.client.post(f"/surveys/MBS/201801/{collection_exercise_id}/create-event/mps",
                                    data=create_ce_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_create_collection_exercise_date_in_past(self, mock_request):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events)

        create_ce_event_form = {
            "day": "01",
            "month": "01",
            "year": "2018",
            "hour": "01",
            "minute": "00"
        }

        response = self.client.post(f"/surveys/MBS/201801/{collection_exercise_id}/create-event/mps",
                                    data=create_ce_event_form, follow_redirects=True)

        self.assertIn("Selected date can not be in the past".encode(), response.data)
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    @mock.patch("response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event")
    def test_create_collection_events_not_set_sequentially(self, mock_request, mock_ce_event):
        mock_request.get(url_survey_shortname, json=survey)
        mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
        mock_request.get(url_get_collection_exercise_events, json=events_2030)
        mock_ce_event.return_value = 'Collection exercise events must be set sequentially'

        create_ce_event_form = {
            "day": "01",
            "month": "01",
            "year": "2029",
            "hour": "01",
            "minute": "00"
        }

        response = self.client.post(f"/surveys/MBS/201801/{collection_exercise_id}/create-event/reminder2",
                                    data=create_ce_event_form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Collection exercise events must be set sequentially".encode(), response.data)

    def test_get_collection_exercises_with_events_and_samples_by_survey_id(self):
        name_space = 'response_operations_ui.controllers.collection_exercise_controllers.'
        with mock.patch(
                name_space + "get_collection_exercises_by_survey", return_value=self.collection_exercises), \
             mock.patch(
                 name_space + "get_collection_exercise_events_by_id", return_value=self.collection_exercise_events), \
             mock.patch(
                 name_space + "get_linked_sample_summary_id", return_value=self.sample_summary['id']), \
             mock.patch(
                 name_space + "get_sample_summary", return_value=self.sample_summary):
            ce_list = get_collection_exercises_with_events_and_samples_by_survey_id(self.survey['id'])

        expected_ce_list = copy.deepcopy(self.collection_exercises)
        expected_ce_list[0]['events'] = self.collection_exercise_events
        expected_ce_list[0]['sample_summary'] = self.sample_summary
        self.assertEqual(ce_list, expected_ce_list)

    @requests_mock.mock()
    def test_schedule_nudge_email_option_not_present(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=self.collection_exercise_events)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', json=self.collection_instruments,
                         complete_qs=True)
        mock_request.get(f'{url_get_collection_instrument}?{ci_type_search_string}', json=self.eq_ci_selectors,
                         complete_qs=True)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_classifier_type_selectors, json=classifier_type_selectors)
        mock_request.get(url_get_classifier_type, json=classifier_types)

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Schedule nudge email".encode(), response.data)

    @requests_mock.mock()
    def test_schedule_nudge_email_option_present(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=events)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', json=self.collection_instruments,
                         complete_qs=True)
        mock_request.get(f'{url_get_collection_instrument}?{ci_type_search_string}', json=self.eq_ci_selectors,
                         complete_qs=True)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_classifier_type_selectors, json=classifier_type_selectors)
        mock_request.get(url_get_classifier_type, json=classifier_types)

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Schedule nudge email".encode(), response.data)

    @requests_mock.mock()
    def test_you_cannot_schedule_any_new_nudge_emails_info_pannel(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=nudge_events_one)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', json=self.collection_instruments,
                         complete_qs=True)
        mock_request.get(f'{url_get_collection_instrument}?{ci_type_search_string}', json=self.eq_ci_selectors,
                         complete_qs=True)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_classifier_type_selectors, json=classifier_type_selectors)
        mock_request.get(url_get_classifier_type, json=classifier_types)

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("You cannot schedule any new nudge emails".encode(), response.data)
        self.assertNotIn("Schedule nudge email".encode(), response.data)

    @requests_mock.mock()
    def test_can_create_up_to_five_nudge_email(self, mock_request):
        mock_request.get(url_get_survey_by_short_name, json=self.survey)
        mock_request.get(url_ces_by_survey, json=self.collection_exercises)
        mock_request.get(url_ce_by_id, json=collection_exercise_details['collection_exercise'])
        mock_request.get(url_get_collection_exercise_events, json=nudge_events_two)
        mock_request.get(f'{url_get_collection_instrument}?{ci_search_string}', json=self.collection_instruments,
                         complete_qs=True)
        mock_request.get(f'{url_get_collection_instrument}?{ci_type_search_string}', json=self.eq_ci_selectors,
                         complete_qs=True)
        mock_request.get(url_link_sample, json=[sample_summary_id])
        mock_request.get(url_get_sample_summary, json=self.sample_summary)
        mock_request.get(url_get_classifier_type_selectors, json=classifier_type_selectors)
        mock_request.get(url_get_classifier_type, json=classifier_types)

        response = self.client.get(f'/surveys/{short_name}/{period}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("You cannot schedule any new nudge emails".encode(), response.data)
        self.assertIn("Schedule nudge email".encode(), response.data)

        @requests_mock.mock()
        @mock.patch(
            "response_operations_ui.controllers.collection_exercise_controllers.create_collection_exercise_event")
        def test_create_collection_events_not_set_sequentially(self, mock_request, mock_ce_event):
            mock_request.get(url_survey_shortname, json=survey)
            mock_request.get(url_collection_exercise_survey_id, json=[collection_exercise])
            mock_request.get(url_get_collection_exercise_events, json=nudge_events_two)
            mock_ce_event.return_value = 'Collection exercise events must be set sequentially'

            create_ce_event_form = {
                "day": "15",
                "month": "10",
                "year": "2018",
                "hour": "01",
                "minute": "00"
            }

            res = self.client.post(f"/surveys/MBS/201801/{collection_exercise_id}/create-event/nudge_email_4",
                                   data=create_ce_event_form, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Nudge email must be set sequentially".encode(), res.data)

    def test_get_existing_sorted_nudge_events_for_no_nudge(self):
        res = get_existing_sorted_nudge_events([])
        self.assertEqual(res, [])

    def test_get_existing_sorted_nudge_events_for_sequential_nudge(self):
        nudge = {'nudge_email_0': {
            'day': 'Saturday',
            'date': '06 Jun 2020',
            'month': '06',
            'time': '11:00',
            'is_in_future': True
        },
            'nudge_email_3': {
                'day': 'Saturday',
                'date': '06 Jun 2020',
                'month': '06',
                'time': '08:00',
                'is_in_future': True
        },
            'nudge_email_4': {
                'day': 'Saturday',
                'date': '06 Jun 2019',
                'month': '06',
                'time': '08:00',
                'is_in_future': True
        }}
        res = get_existing_sorted_nudge_events(nudge)
        self.assertEqual(res, ['nudge_email_4', 'nudge_email_3', 'nudge_email_0'])
