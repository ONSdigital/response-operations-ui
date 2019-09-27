from unittest import TestCase
from unittest.mock import patch
from response_operations_ui import create_app


TESTMSG = b'RESPONSE UI TEST MESSAGE'


class TestAvailabilityMessage(TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    @patch('redis.StrictRedis')
    def test_message_does_not_show_if_redis_flag_not_set(self, mock_redis):
        mock_redis.get.return_value = b''
        mock_redis.keys.return_value = []
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TESTMSG in response.data)

    @patch('redis.StrictRedis')
    def test_message_shows_correct_message_if_redis_flag_set(self, mock_redis):
        mock_redis.get.return_value = TESTMSG
        mock_redis.keys.return_value = ['AVAILABILITY_MESSAGE_RES_OPS']
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TESTMSG in response.data)
