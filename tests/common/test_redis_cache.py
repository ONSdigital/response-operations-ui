import unittest
from unittest.mock import patch

import responses
from redis import RedisError

from response_operations_ui import create_app
from response_operations_ui.common.redis_cache import RedisCache

short_name = "MBS"
survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"


class TestRedisCache(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()

    @patch("redis.StrictRedis.get")
    def test_get_survey_by_shortname_in_cache(self, mock_redis_get):
        with self.app.app_context():
            cache = RedisCache()
            mock_redis_get.return_value = b'{"survey_ref": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"}'
            result = cache.get_survey_by_shortname(short_name)
            self.assertIn(survey_id, str(result))

    @patch("redis.StrictRedis.get")
    def test_get_survey_by_shortname_not_in_cache(self, mock_redis_get):
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET,
                f"http://localhost:8080/surveys/shortname/{short_name}",
                json={"survey_ref": survey_id},
                status=200,
                content_type="application/json",
            )
            with self.app.app_context():
                cache = RedisCache()
                mock_redis_get.return_value = b""
                result = cache.get_survey_by_shortname(short_name)
                self.assertIn(survey_id, str(result))

    @patch("redis.StrictRedis.get")
    def test_get_survey_by_shortname_logs_error(self, mock_redis_get):
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET,
                f"http://localhost:8080/surveys/shortname/{short_name}",
                json={"survey_ref": survey_id},
                status=200,
                content_type="application/json",
            )
            with self.app.app_context():
                with self.assertLogs(level="ERROR") as log:
                    cache = RedisCache()
                    mock_redis_get.side_effect = RedisError
                    result = cache.get_survey_by_shortname(short_name)
                    error_message = "Error getting value from cache, please investigate"
                    redis_key = f"response-operations-ui:survey:{short_name}"
                    self.assertIn(error_message, log.output[0])
                    self.assertIn(redis_key, log.output[0])
                    self.assertIn(survey_id, str(result))
