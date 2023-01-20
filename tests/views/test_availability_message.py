from unittest import TestCase
from unittest.mock import patch

import fakeredis
import requests_mock

from config import TestingConfig
from response_operations_ui import create_app

TESTMSG = b"RESPONSE UI TEST MESSAGE"

url_surveys = f"{TestingConfig.SURVEY_URL}/surveys/surveytype/Business"

surveys_list_json = [
    {
        "id": "75b19ea0-69a4-4c58-8d7f-4458c8f43f5c",
        "legalBasis": "Statistics of Trade Act 1947",
        "longName": "Monthly Business Survey - Retail Sales Index",
        "shortName": "RSI",
        "surveyRef": "023",
    }
]


class TestAvailabilityMessage(TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )

    @patch("redis.StrictRedis")
    @requests_mock.mock()
    def test_message_does_not_show_if_redis_flag_not_set(self, mock_redis, mock_request):
        mock_request.get(url_surveys, json=surveys_list_json, status_code=200)
        mock_redis.get.return_value = b""
        mock_redis.keys.return_value = []
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TESTMSG in response.data)

    @patch("redis.StrictRedis")
    @requests_mock.mock()
    def test_message_shows_correct_message_if_redis_flag_set(self, mock_redis, mock_request):
        mock_request.get(url_surveys, json=surveys_list_json, status_code=200)
        mock_redis.get.return_value = TESTMSG
        mock_redis.keys.return_value = ["AVAILABILITY_MESSAGE_RES_OPS"]
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TESTMSG in response.data)
