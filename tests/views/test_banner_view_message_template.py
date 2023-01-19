import fakeredis
import requests_mock

from config import TestingConfig
from tests.controllers.test_admin_controller import templates_response
from tests.views import ViewTestCase

url_template = f"{TestingConfig.BANNER_SERVICE_URL}/template"
url_view_template = "/admin/banner/message-template"


class TestBannerViewMessageTemplate(ViewTestCase):
    def setup_data(self):
        self.headers = {"Authorization": "test_jwt", "Content-Type": "application/json"}
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )
    @requests_mock.mock()
    def test_collection_exercise_view(self, mock_request):
        mock_request.get(url_template, json=templates_response, status_code=200)
        response = self.client.get(url_view_template)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Banner title 1".encode(), response.data)
        self.assertIn("Banner content 1".encode(), response.data)
        self.assertIn("Banner content 2".encode(), response.data)
        self.assertIn("Banner content 2".encode(), response.data)
