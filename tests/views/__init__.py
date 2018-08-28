from unittest import TestCase

from response_operations_ui import create_app


class ViewTestCase(TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        self.setup_data()

    def setup_data(self):
        raise NotImplementedError
