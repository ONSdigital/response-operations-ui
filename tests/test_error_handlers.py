import unittest
from unittest.mock import patch

import fakeredis

from response_operations_ui import create_app


class TestErrorHandlers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )
        self.app = self.app.test_client()

    @patch("requests.post")
    def test_exception_error_page(self, mock_post):
        mock_post.side_effect = Exception("error")
        response = self.app.post(
            "/sign-in", data={"username": "username", "password": "password"}, follow_redirects=True
        )
        self.assertIn(b"Something has gone wrong with the website.", response.data)
