import json
import logging

from flask import current_app
from redis.exceptions import RedisError
from structlog import wrap_logger

from response_operations_ui.controllers.cir_controller import get_cir_metadata
from response_operations_ui.controllers.survey_controllers import (
    get_survey_by_shortname,
)

logger = wrap_logger(logging.getLogger(__name__))


class RedisCache:
    SURVEY_EXPIRY = 600  # 10 mins

    def get_cir_metadata(self, survey_ref: str, formtype: str) -> dict:
        """
        Gets the cir_metadata from redis or the cir service

        :param short_name: str: the qualifying part of the redis key
                                (response-operations-ui:survey:<SURVEY_REF>:<FORMTYPE>)
        :return: Result from either the cache or the CIR service
        """
        redis_key = f"response-operations-ui:cir:{survey_ref}:{formtype}"
        try:
            result = current_app.redis.get(redis_key)
        except RedisError:
            logger.error("Error getting value from cache", key=redis_key, exc_info=True)
            result = None

        if not result:
            logger.info("Key not in cache, getting value from CIR service", key=redis_key)
            result = get_cir_metadata(survey_ref, formtype)
            self.set(redis_key, json.dumps(result), self.SURVEY_EXPIRY)
            return result

        return json.loads(result.decode("utf-8"))

    def get_survey_by_shortname(self, short_name: str) -> dict:
        """
        Gets the survey from redis or the survey service

        :param short_name: str: the qualifying part of the redis key (response-operations-ui:survey:<SURVEY_SHORT_NAME>)
        :return: Result from either the cache or survey service
        """
        redis_key = f"response-operations-ui:survey:{short_name}"
        try:
            result = current_app.redis.get(redis_key)
        except RedisError:
            logger.error("Error getting value from cache, please investigate", key=redis_key, exc_info=True)
            result = None

        if not result:
            logger.info("Key not in cache, getting value from survey service", key=redis_key)
            result = get_survey_by_shortname(short_name)
            self.set(redis_key, json.dumps(result), self.SURVEY_EXPIRY)
            return result

        return json.loads(result.decode("utf-8"))

    def set(self, key, value, expiry):
        if not expiry:
            logger.error("Expiry must be provided")
            raise ValueError("Expiry must be provided")
        try:
            current_app.redis.set(key, value, ex=expiry)
        except RedisError:
            # Not throwing an exception as the cache isn't fatal
            logger.error("Error setting key, please investigate", key=key, exc_info=True)
