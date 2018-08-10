import unittest
from unittest.mock import patch
from response_operations_ui import create_app


class TestCreateApp(unittest.TestCase):

    # Check that we can initialise app and access it's config
    def test_create_app(self):
        test_app = create_app('TestingConfig')

        self.assertEqual(test_app.config['REDIS_HOST'], 'localhost')

    @patch('response_operations_ui.cf')
    def test_create_app_with_cf(self, mock_cf):
        mock_cf.redis.return_value = 'REDIS_SERVICE'

        mock_cf.redis_service = {
            'host': 'test_host',
            'port': 'test_port'
        }

        test_app = create_app('CFTestingConfig')

        self.assertEqual(test_app.config['REDIS_HOST'], 'test_host')
        self.assertEqual(test_app.config['REDIS_PORT'], 'test_port')
