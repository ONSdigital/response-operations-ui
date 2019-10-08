import unittest
import responses

from config import TestingConfig
from response_operations_ui import create_app
from response_operations_ui.controllers.notify_controller import NotifyController
from response_operations_ui.exceptions.exceptions import NotifyError

url_send_notify = f'{TestingConfig().NOTIFY_SERVICE_URL}{TestingConfig().NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE}'


class TestNotifyController(unittest.TestCase):
    '''
    Tests that the notify controller is working as expected
    '''
    def setUp(self):
        self.app = create_app('TestingConfig')

    def test_an_invalid_template_id(self):
        with self.app.app_context():
            with self.assertRaises(KeyError):
                NotifyController().request_to_notify(email='test@test.test', template_name='fake-template-name')

    def test_a_successful_send(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, url_send_notify, json={'emailAddress': 'test@test.test'}, status=201)
            with self.app.app_context():
                try:
                    NotifyController().request_to_notify(email='test@test.test',
                                                         template_name='request_password_change')
                except NotifyError:
                    self.fail('NotifyController didnt properly handle a 201')
                except KeyError:
                    self.fail('NotifyController couldnt find the template ID request_password_change')

    def test_an_unsuccessful_send(self):
        with responses.RequestsMock() as rsps:
            rsps.add(rsps.POST, url_send_notify, json={'emailAddress': 'test@test.test'}, status=500)
            with self.app.app_context():
                with self.assertRaises(NotifyError):
                    NotifyController().request_to_notify(email='test@test.test',
                                                         template_name='request_password_change')
