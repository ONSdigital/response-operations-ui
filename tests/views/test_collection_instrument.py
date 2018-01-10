import unittest
from io import BytesIO

from response_operations_ui import app


class TestSurvey(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_upload_collection_instrument(self,):
        response = self.app.post("/surveys/bres/201801", data=dict(
            ciFile=(BytesIO(b'data'), 'test.xlsx'),
        ))

        self.assertEqual(response.status_code, 200)
