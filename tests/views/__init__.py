from unittest import TestCase
from unittest.mock import MagicMock

from flask import Response

from config import TestingConfig
from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError


class ViewTestCase(TestCase):

    def setUp(self):
        app.config.from_object(TestingConfig)
        app.login_manager.init_app(app)
        self._create_apierror_handler_mock()
        self.app = app.test_client()
        self.init_data()

    def init_data(self):
        raise NotImplementedError

    def tearDown(self):
        self._reset_apierror_handler_mock()

    def _reset_apierror_handler_mock(self):
        # NB: each of test cases use the same app object.
        app._error_handlers[None][ApiError] = self._old_handler

    def _create_apierror_handler_mock(self, mock=None):
        """
        This mocks the Flask error handler so we can validate that an ApiError was raised.
        """
        self._mocked_handler = mock or MagicMock(return_value=Response(''))
        self._old_handler = app._error_handlers[None][ApiError]
        app._error_handlers[None][ApiError] = self._mocked_handler

    def assertApiError(self, url, status_code):
        """
        Helper method for asserting the cause of an ApiError.
        """
        self._mocked_handler.assert_called()
        self.assertEqual(self._mocked_handler.call_args[0][0].status_code, status_code)
        self.assertEqual(self._mocked_handler.call_args[0][0].url, url)
