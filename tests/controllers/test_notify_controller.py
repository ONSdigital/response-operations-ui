import unittest
from unittest.mock import MagicMock

from response_operations_ui import create_app
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.exceptions.exceptions import NotifyError


class TestNotifyController(unittest.TestCase):
    """
    Tests that the notify controller is working as expected
    """

    def setUp(self):
        self.app = create_app("TestingConfig")

    def test_an_invalid_template_id(self):
        with self.app.app_context():
            with self.assertRaises(KeyError):
                notify = NotifyController()
                notify._get_template_id(template_name="invalid_template")

    def test_a_successful_send_to_pub_sub(self):
        with self.app.app_context():
            publisher = MagicMock()
            publisher.topic_path.return_value = "projects/test-project-id/topics/ras-rm-notify-test"
            notify = NotifyController()
            notify.publisher = publisher
            result = notify.request_to_notify(
                email="test@test.test", template_name="request_password_change", personalisation=None
            )
            data = (
                b'{"notify": {"email_address": "test@test.test", '
                b'"template_id": "request_password_change_id", "personalisation": {}}}'
            )

            publisher.publish.assert_called()
            publisher.publish.assert_called_with("projects/test-project-id/topics/ras-rm-notify-test", data=data)
            self.assertIsNone(result)

    def test_a_successful_send_to_pub_sub_with_personalisation(self):
        with self.app.app_context():
            publisher = MagicMock()
            publisher.topic_path.return_value = "projects/test-project-id/topics/ras-rm-notify-test"
            notify = NotifyController()
            notify.publisher = publisher
            personalisation = {"first_name": "firstname", "last_name": "surname"}
            result = notify.request_to_notify(
                email="test@test.test", template_name="request_password_change", personalisation=personalisation
            )
            data = (
                b'{"notify": {"email_address": "test@test.test", '
                b'"template_id": "request_password_change_id", "personalisation": {"first_name": "firstname", '
                b'"last_name": "surname"}}}'
            )

            publisher.publish.assert_called()
            publisher.publish.assert_called_with("projects/test-project-id/topics/ras-rm-notify-test", data=data)
            self.assertIsNone(result)

    def test_a_unsuccessful_send_to_pub_sub(self):
        with self.app.app_context():
            future = MagicMock()
            future.result.side_effect = TimeoutError("bad")
            publisher = MagicMock()
            publisher.publish.return_value = future
            notify = NotifyController()
            notify.publisher = publisher
            with self.assertRaises(NotifyError):
                notify.request_to_notify(
                    email="test@test.test", template_name="request_password_change", personalisation=None
                )

    def test_a_unsuccessful_send_to_pub_sub_with_exception(self):
        with self.app.app_context():
            future = MagicMock()
            future.result.side_effect = Exception("bad")
            publisher = MagicMock()
            publisher.publish.return_value = future
            notify = NotifyController()
            notify.publisher = publisher
            with self.assertRaises(NotifyError):
                notify.request_to_notify(
                    email="test@test.test", template_name="request_password_change", personalisation=None
                )
