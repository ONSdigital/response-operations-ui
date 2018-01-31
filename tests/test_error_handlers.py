import unittest
from unittest.mock import patch

from config import TestingConfig
from response_operations_ui import app


class TestErrorHandlers(unittest.TestCase):
    def setUp(self):
        app_config = TestingConfig()
        app.config.from_object(app_config)
        app.login_manager.init_app(app)
        self.app = app.test_client()

    @patch('requests.post')
    def test_exception_error_page(self, mock_post):
        mock_post.side_effect = Exception("error")
        response = self.app.post('/sign-in', data={'username': 'username', 'password': 'password'},
                                 follow_redirects=True)
        self.assertIn(b'Something has gone wrong with the website.', response.data)
