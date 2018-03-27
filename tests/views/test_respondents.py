import unittest

from config import TestingConfig
from response_operations_ui import app


class TestRespondents(unittest.TestCase):

    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

    def test_search_respondent_get(self):
        response = self.app.get("/respondents")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Respondents".encode(), response.data)
