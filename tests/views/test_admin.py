from unittest import TestCase
from unittest.mock import patch
from response_operations_ui import create_app

TESTMSG = b'RESPONSE UI TEST MESSAGE'


class TestAdmin(TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

    @patch('redis.Redis.get')
    def test_message_does_not_show_if_not_set(self, mock_redis):
        mock_redis.get.return_value = b''
        response = self.client.get('/admin/banner', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TESTMSG in response.data)

    @patch('redis.Redis.get')
    def test_message_shows_correct_message_if__set(self, mock_redis):
        mock_redis.return_value = TESTMSG
        response = self.client.get('/admin/banner', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        mock_redis.assert_called
        self.assertTrue(TESTMSG in response.data)

    @patch('redis.Redis.get')
    @patch('redis.Redis.set')
    def test_message_is_set(self, mock_redis_set, mock_redis_get):
        mock_redis_get.return_value = TESTMSG
        response = self.client.post('/admin/banner', data=dict(
            delete="false",
            banner=TESTMSG,
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        mock_redis_set.set.assert_called
        mock_redis_get.get.assert_called
        self.assertTrue(TESTMSG in response.data)

    @patch('redis.Redis.delete')
    @patch('redis.Redis.get')
    def test_message_is_deleted(self, mock_redis_delete, mock_redis_get):
        response = self.client.post('/admin/banner', data=dict(
            delete="true",
            banner="",
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        mock_redis_delete.set.assert_called
        mock_redis_get.get.assert_called
        self.assertFalse(TESTMSG in response.data)
