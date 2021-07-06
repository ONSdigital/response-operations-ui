import os
import unittest

from flask import app

from response_operations_ui import create_app


class TestCreateApp(unittest.TestCase):
    def setUp(self):
        app.testing = True
        os.environ["APP_SETTINGS"] = "TestingConfig"

    # Check that we can initialise app and access it's config
    def test_create_app(self):
        test_app = create_app("TestingConfig")
        self.assertEqual(test_app.config["REDIS_HOST"], "localhost")
