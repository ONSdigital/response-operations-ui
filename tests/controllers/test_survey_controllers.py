import json
import os
import unittest

import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers import survey_controllers
from response_operations_ui.exceptions.exceptions import ApiError

project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/survey/survey_list.json") as json_data:
    survey_list = json.load(json_data)

url_get_surveys_list = f"{TestingConfig.SURVEY_URL}/surveys/surveytype/Business"


class TestCaseControllers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    def test_convert_specific_surveys_to_specific_shortnames(self):
        inputs = ["AOFDI", "QOFDI", "VACS2", "VACS4", "ASHE", "MBS"]
        expected_outputs = ["FDI", "FDI", "Vacancies", "Vacancies", "ASHE", "MBS"]

        for item, expected in zip(inputs, expected_outputs):
            output = survey_controllers.convert_specific_surveys_to_specific_shortnames(item)
            self.assertEqual(output, expected)

    def test_get_business_survey_shortname_list(self):
        expected = ["AIFDI", "AOFDI", "ASHE", "BRES", "BRUS", "Bricks", "QIFDI", "QOFDI"]

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_surveys_list, json=survey_list)
            with self.app.app_context():
                output = survey_controllers.get_business_survey_shortname_list()
                self.assertEqual(output, expected)

    def test_get_business_survey_shortname_list_failure(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_surveys_list, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    survey_controllers.get_business_survey_shortname_list()

    def test_get_grouped_surveys_list(self):
        expected = ["ASHE", "BRES", "BRUS", "Bricks", "FDI"]

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_surveys_list, json=survey_list)
            with self.app.app_context():
                output = survey_controllers.get_grouped_surveys_list()
                self.assertEqual(output, expected)

    def test_get_grouped_surveys_list_failure(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_surveys_list, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    survey_controllers.get_grouped_surveys_list()

    def test_get_surveys_dictionary(self):
        expected = {
            "6aa8896f-ced5-4694-800c-6cd661b0c8b2": {"shortName": "ASHE", "surveyRef": "141"},
            "AIFDI_id": {"shortName": "FDI", "surveyRef": "062"},
            "AOFDI_id": {"shortName": "FDI", "surveyRef": "063"},
            "QIFDI_id": {"shortName": "FDI", "surveyRef": "064"},
            "QOFDI_id": {"shortName": "FDI", "surveyRef": "065"},
            "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87": {"shortName": "BRES", "surveyRef": "221"},
            "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88": {"shortName": "BRUS", "surveyRef": "222"},
            "cb8accda-6118-4d3b-85a3-149e28960c54": {"shortName": "Bricks", "surveyRef": "074"},
        }

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_surveys_list, json=survey_list)
            with self.app.app_context():
                output = survey_controllers.get_surveys_dictionary()
                self.assertEqual(output, expected)

    def test_get_surveys_dictionary_failure(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_surveys_list, status=500)
            with self.app.app_context():
                with self.assertRaises(ApiError):
                    survey_controllers.get_surveys_dictionary()

    def test_check_cache(self):
        expected = {
            "6aa8896f-ced5-4694-800c-6cd661b0c8b2": {"shortName": "ASHE", "surveyRef": "141"},
            "AIFDI_id": {"shortName": "FDI", "surveyRef": "062"},
            "AOFDI_id": {"shortName": "FDI", "surveyRef": "063"},
            "QIFDI_id": {"shortName": "FDI", "surveyRef": "064"},
            "QOFDI_id": {"shortName": "FDI", "surveyRef": "065"},
            "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87": {"shortName": "BRES", "surveyRef": "221"},
            "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88": {"shortName": "BRUS", "surveyRef": "222"},
            "cb8accda-6118-4d3b-85a3-149e28960c54": {"shortName": "Bricks", "surveyRef": "074"},
        }
        try:
            self.failIf(self.app.surveys_dict)
        except AttributeError:
            # we're expecting it not to be there
            pass

        try:
            self.failIf(self.app.surveys_dict_time)
        except AttributeError:
            # we're expecting it not to be there
            pass

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_surveys_list, json=survey_list)
            with self.app.app_context():
                survey_controllers.check_cache()
                self.assertIsNotNone(self.app.surveys_dict)
                self.assertIsNotNone(self.app.surveys_dict_time)
                self.assertEqual(expected, self.app.surveys_dict)

    def test_refresh_cache(self):
        expected = {
            "6aa8896f-ced5-4694-800c-6cd661b0c8b2": {"shortName": "ASHE", "surveyRef": "141"},
            "AIFDI_id": {"shortName": "FDI", "surveyRef": "062"},
            "AOFDI_id": {"shortName": "FDI", "surveyRef": "063"},
            "QIFDI_id": {"shortName": "FDI", "surveyRef": "064"},
            "QOFDI_id": {"shortName": "FDI", "surveyRef": "065"},
            "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87": {"shortName": "BRES", "surveyRef": "221"},
            "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88": {"shortName": "BRUS", "surveyRef": "222"},
            "cb8accda-6118-4d3b-85a3-149e28960c54": {"shortName": "Bricks", "surveyRef": "074"},
        }

        try:
            self.failIf(self.app.surveys_dict)
        except AttributeError:
            # we're expecting it not to be there
            pass

        try:
            self.failIf(self.app.surveys_dict_time)
        except AttributeError:
            # we're expecting it not to be there
            pass

        with responses.RequestsMock() as rsps:
            rsps.add(rsps.GET, url_get_surveys_list, json=survey_list)
            with self.app.app_context():
                survey_controllers.refresh_cache()
                self.assertIsNotNone(self.app.surveys_dict)
                self.assertIsNotNone(self.app.surveys_dict_time)
                self.assertEqual(expected, self.app.surveys_dict)
