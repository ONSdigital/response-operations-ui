import unittest

from response_operations_ui import app


class TestInfo(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_info_no_git_info(self):
        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
