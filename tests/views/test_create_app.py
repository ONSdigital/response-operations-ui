import os

import unittest
from unittest.mock import patch
from response_operations_ui import create_app
from flask import app


class TestCreateApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        os.environ['APP_SETTINGS'] = 'TestingConfig'

    # Check that we can initialise app and access it's config
    def test_create_app(self):
        test_app = create_app('TestingConfig')
        self.assertEqual(test_app.config['REDIS_HOST'], 'localhost')

    @patch('response_operations_ui.cf')
    def test_create_app_with_cf(self, mock_cf):
        mock_cf.detected.return_value = False
        mock_cf.redis.credentials = {
            'host': 'test_host',
            'port': 'test_port'
        }

        test_app = create_app()
        self.assertEqual(test_app.config['REDIS_HOST'], 'test_host')
        self.assertEqual(test_app.config['REDIS_PORT'], 'test_port')
