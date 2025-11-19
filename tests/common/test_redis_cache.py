import json
import os
import unittest
from unittest.mock import patch

import fakeredis
import responses
from redis import RedisError

from response_operations_ui import create_app
from response_operations_ui.common.redis_cache import RedisCache

short_name = "MBS"
survey_id = "427d40e6-f54a-4512-a8ba-e4dea54ea3dc"
form_type = "0001"
ci_version = "ci_version': 1"

project_root = os.path.dirname(os.path.dirname(__file__))

with open(f"{project_root}/test_data/survey/redis_survey_list.json") as data:
    redis_survey_list = data.read().encode("utf8").splitlines()

with open(f"{project_root}/test_data/survey/survey_list.json") as json_data:
    survey_list = json.load(json_data)


class TestRedisCache(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        self.app.config["SESSION_REDIS"] = fakeredis.FakeStrictRedis(
            host=self.app.config["REDIS_HOST"], port=self.app.config["FAKE_REDIS_PORT"], db=self.app.config["REDIS_DB"]
        )

    @patch("redis.StrictRedis.get")
    def test_get_survey_by_shortname_in_cache(self, mock_redis_get):
        with self.app.app_context():
            cache = RedisCache()
            mock_redis_get.return_value = b'{"survey_ref": "427d40e6-f54a-4512-a8ba-e4dea54ea3dc"}'
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

    @patch("redis.StrictRedis.get")
    def test_get_cir_metadata_in_cache(self, mock_redis_get):
        with self.app.app_context():
            cir_metadata = open(f"{project_root}/test_data/cir/cir_metadata.json")
            cache = RedisCache()
            mock_redis_get.return_value = cir_metadata.read().encode("utf-8")
            result = cache.get_cir_metadata(short_name, formtype=form_type)
            self.assertIn(survey_id, str(result))
            self.assertIn(form_type, str(result))
            self.assertIn(ci_version, str(result))

    @patch("redis.StrictRedis.get")
    def test_get_cir_metadata_not_in_cache(self, mock_redis_get):
        cir_metadata = open(f"{project_root}/test_data/cir/cir_metadata.json")
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET,
                f"http://localhost:3030/v2/ci_metadata?classifier_type=form_type&classifier_value={form_type}"
                f"&language=en&survey_id={short_name}",
                json=json.load(cir_metadata),
                status=200,
                content_type="application/json",
            )
            with self.app.app_context():
                cache = RedisCache()
                mock_redis_get.return_value = b""
                result = cache.get_cir_metadata(short_name, formtype=form_type)
                self.assertIn(survey_id, str(result))
                self.assertIn(form_type, str(result))
                self.assertIn(ci_version, str(result))

    @patch("redis.StrictRedis.hvals")
    def test_get_survey_list_in_cache(self, mock_redis_hvals):
        with self.app.app_context():
            cache = RedisCache()
            mock_redis_hvals.return_value = redis_survey_list
            result = cache.get_survey_list()
            self.assertEqual(survey_list, result)

    @patch("redis.StrictRedis.hvals")
    @patch("response_operations_ui.common.redis_cache.RedisCache.refresh_survey_list")
    def test_get_survey_list_not_in_cache(self, mock_refresh_survey_list_cache, mock_redis_hvals):
        with self.app.app_context():
            with self.assertLogs(level="INFO") as log:
                cache = RedisCache()
                mock_redis_hvals.return_value = []
                mock_refresh_survey_list_cache.return_value = survey_list
                result = cache.get_survey_list()
                log_message = "Key not in cache, getting values from survey service"
                redis_key = "response-operations-ui:survey-list"
                self.assertEqual(survey_list, result)
                self.assertIn(log_message, log.output[0])
                self.assertIn(redis_key, log.output[0])
                mock_refresh_survey_list_cache.assert_called_once()

    @patch("redis.StrictRedis.hvals")
    @patch("response_operations_ui.common.redis_cache.RedisCache.refresh_survey_list")
    def test_get_survey_list_redis_error(self, mock_refresh_survey_list_cache, mock_redis_hvals):
        with self.app.app_context():
            with self.assertLogs(level="ERROR") as log:
                cache = RedisCache()
                mock_redis_hvals.side_effect = RedisError
                mock_refresh_survey_list_cache.return_value = survey_list
                cache.get_survey_list()
                log_message = "Error getting value from cache, please investigate"
                redis_key = "response-operations-ui:survey-list"
                self.assertIn(log_message, log.output[0])
                self.assertIn(redis_key, log.output[0])
                mock_refresh_survey_list_cache.assert_called_once()

    def test_refresh_survey_list_cache(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET,
                "http://localhost:8080/surveys/surveytype/Business",
                json=survey_list,
                status=200,
                content_type="application/json",
            )

            with self.app.app_context():
                with self.assertLogs(level="INFO") as log:
                    cache = RedisCache()
                    cache.refresh_survey_list()
                    log_message = "Refreshing cached survey list"
                    redis_key = "response-operations-ui:survey-list"
                    self.assertEqual(600, self.app.redis.ttl(redis_key))
                    self.assertIn(cache.get_survey_list()[0], survey_list)
                    self.assertIn(log_message, log.output[0])
                    self.assertIn(redis_key, log.output[0])
