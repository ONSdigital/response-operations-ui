import json
import os
import unittest
from pathlib import Path

from response_operations_ui import app


class TestInfo(unittest.TestCase):

    @staticmethod
    def delete_git_info():
        if Path('git_info').exists():
            os.remove('git_info')

    def setUp(self):
        self.app = app.test_client()
        self.delete_git_info()

    def tearDown(self):
        self.delete_git_info()

    def test_info_no_git_info(self):
        response = self.app.get("/info")

        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "response-operations-ui"'.encode(), response.data)
        self.assertNotIn('"test": "test"'.encode(), response.data)

    def test_info_with_git_info(self):
        with open('git_info', 'w') as outfile:
            json.dump({"test": "test"}, outfile)

        response = self.app.get("/info")

        self.assertEqual(response.status_code, 200)
        self.assertIn('"name": "response-operations-ui"'.encode(), response.data)
        self.assertIn('"test": "test"'.encode(), response.data)
