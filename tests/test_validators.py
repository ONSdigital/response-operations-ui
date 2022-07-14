import json
import os
import unittest
from datetime import datetime

import requests_mock
from wtforms import ValidationError

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.common.validators import valid_date_for_event
from response_operations_ui.controllers.collection_exercise_controllers import (
    update_event,
)
from response_operations_ui.exceptions.exceptions import ApiError
from response_operations_ui.forms import EventDateForm
from tests.views import ViewTestCase

collection_exercise_id = "14fb3e68-4dca-46db-bf49-04b84e07e77c"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
survey_short_name = "BRES"
period = "201801"
tag = "go_live"
project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/tests/test_data/collection_exercise/collection_exercise.json") as json_data:
    collection_exercise = json.load(json_data)
with open(f"{project_root}/tests/test_data/collection_exercise/collection_exercise_details.json") as json_data:
    collection_exercise_details = json.load(json_data)
with open(f"{project_root}/tests/test_data/survey/single_survey.json") as json_data:
    survey = json.load(json_data)
with open(f"{project_root}/tests/test_data/collection_exercise/events.json") as json_data:
    events = json.load(json_data)
url_put_update_event_date = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/{collection_exercise_id}/events/{tag}"
)
url_survey_shortname = f"{TestingConfig.SURVEY_URL}/surveys/shortname/{survey_short_name}"
url_collection_exercise_survey_id = f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey/{survey_id}"

url_get_collection_exercise_events = (
    f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/{collection_exercise_id}/events"
)


class TestValidators(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")

    def test_date_can_be_past_for_reference_period_end_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event("ref_period_end", form), None)

    def test_date_can_be_past_for_reference_period_start_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event("ref_period_start", form), None)

    def test_date_can_be_past_for_employment_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            self.assertEqual(valid_date_for_event("employment", form), None)

    def test_date_can_not_be_past_for_mps_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            with self.assertRaises(ValidationError) as exc:
                valid_date_for_event("mps", form)
            exception = exc.exception
            self.assertEqual(exception.args[0], "Selected date can not be in the past")

    def test_date_can_not_be_past_for_go_live_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            with self.assertRaises(ValidationError) as exc:
                valid_date_for_event("go_live", form)
            exception = exc.exception
            self.assertEqual(exception.args[0], "Selected date can not be in the past")

    def test_date_can_not_be_past_for_reminder_tag(self):
        with self.app.app_context():
            form = self._create_form_with_past_date()
            with self.assertRaises(ValidationError) as exc:
                valid_date_for_event("reminder", form)
            exception = exc.exception
            self.assertEqual(exception.args[0], "Selected date can not be in the past")

    @staticmethod
    def _create_form_with_past_date():
        form = EventDateForm()
        form.year.data = "2017"
        form.month.data = "01"
        form.day.data = "01"
        form.hour.data = "01"
        form.minute.data = "00"

        return form


class TestValidationErrorMessages(ViewTestCase):
    def setup_data(self):
        self.reminder1_after_reminder2 = {
            "error": {
                "code": "BAD_REQUEST",
                "timestamp": "20190321131255986",
                "message": "Collection exercise events must be set sequentially",
            }
        }

    @requests_mock.mock()
    def test_update_event_error_when_reminder1_after_reminder2(self, mock_request):
        with self.app.app_context():
            mock_request.put(url_put_update_event_date, status_code=400, json=self.reminder1_after_reminder2)

            error_expected = update_event(collection_exercise_id, tag, datetime.utcnow())

            self.assertIn("Collection exercise events must be set sequentially", error_expected["error"]["message"])

    @requests_mock.mock()
    def test_update_event_HTTPerror_not_400(self, mock_request):
        with self.app.app_context():
            mock_request.put(url_put_update_event_date, status_code=500)

            with self.assertRaises(ApiError):
                update_event(collection_exercise_id, tag, datetime.utcnow())
