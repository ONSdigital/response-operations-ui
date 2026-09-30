import unittest

from response_operations_ui import create_app
from response_operations_ui.common.cir_enabled_for_survey import (
    is_cir_enabled_for_survey,
)


class TestCirEnabledForSurvey(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_is_cir_enabled_for_survey_when_enabled(self):
        self.app.config["CIR_ENABLED"] = True
        self.app.config["CIR_SURVEY_EXCLUSIONS"] = []

        self.assertTrue(is_cir_enabled_for_survey("test_survey"))

    def test_is_cir_disabled_for_excluded_survey(self):
        self.app.config["CIR_ENABLED"] = True
        self.app.config["CIR_SURVEY_EXCLUSIONS"] = ["test_survey"]

        self.assertFalse(is_cir_enabled_for_survey("test_survey"))

    def test_is_cir_disabled_when_globally_disabled(self):
        self.app.config["CIR_ENABLED"] = False
        self.app.config["CIR_SURVEY_EXCLUSIONS"] = []

        self.assertFalse(is_cir_enabled_for_survey("test_survey"))
