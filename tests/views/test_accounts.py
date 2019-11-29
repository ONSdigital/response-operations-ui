import unittest

from config import TestingConfig
from response_operations_ui import create_app

class TestAccounts(unittest.TestCase):

    def setUp(self):
        app = create_app('TestingConfig')
        self.client = app.test_client()
  
    def test_request_account_page(self):
        response = self.client.get('/request-new-account')
        self.assertIn(b'ONS email address', response.data)
        self.assertIn(b'admin password', response.data)
        self.assertEqual(response.status_code, 200)
