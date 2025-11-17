import json
import logging

from flask import current_app
from redis.exceptions import RedisError
from structlog import wrap_logger

from response_operations_ui.controllers.cir_controller import get_cir_metadata
from response_operations_ui.controllers.survey_controllers import (
    get_survey_by_shortname,
    get_surveys_list,
)

logger = wrap_logger(logging.getLogger(__name__))


class RedisCache:
    EXPIRY = 600  # 10 mins
    APPLICATION_KEY = "response-operations-ui"

    def get_cir_metadata(self, survey_ref: str, formtype: str) -> dict:
        """
        Gets the cir_metadata from redis or the cir service

        :param survey_ref: str: the qualifying part of the redis key
                                (response-operations-ui:survey:<SURVEY_REF>:<FORMTYPE>)
        :param formtype: str: the formtype of the instrument
        :return: Result from either the cache or the CIR service
        """
        redis_key = f"{self.APPLICATION_KEY}:cir:{survey_ref}:{formtype}"
        try:
            result = current_app.redis.get(redis_key)
        except RedisError:
            logger.error("Error getting value from cache", key=redis_key, exc_info=True)
            result = None

        if not result:
            logger.info("Key not in cache, getting value from CIR service", key=redis_key)
            result = get_cir_metadata(survey_ref, formtype)
            self.set(redis_key, json.dumps(result), self.EXPIRY)
            return result

        return json.loads(result.decode("utf-8"))

    def get_survey_by_shortname(self, short_name: str) -> dict:
        """
        Gets the survey from redis or the survey service

        :param short_name: str: the qualifying part of the redis key (response-operations-ui:survey:<SURVEY_SHORT_NAME>)
        :return: Result from either the cache or survey service
        """
        redis_key = f"{self.APPLICATION_KEY}:survey:{short_name}"
        try:
            result = current_app.redis.get(redis_key)
        except RedisError:
            logger.error("Error getting value from cache, please investigate", key=redis_key, exc_info=True)
            result = None

        if not result:
            logger.info("Key not in cache, getting value from survey service", key=redis_key)
            result = get_survey_by_shortname(short_name)
            self.set(redis_key, json.dumps(result), self.EXPIRY)
            return result

        return json.loads(result.decode("utf-8"))

    def refresh_survey_list(self) -> dict:
        """
        Refreshes the survey list cached in redis by retrieving it from the survey service
        """
        redis_key = f"{self.APPLICATION_KEY}:survey-list"
        logger.info("Refreshing cached survey list", redis_key=redis_key)
        current_app.redis.delete(redis_key)
        result = get_surveys_list()
        redis_hash_mapping = {}

        for survey in result:
            redis_hash_mapping[f'{survey["id"]}:{survey["shortName"]}:{survey["surveyRef"]}'] = json.dumps(survey)

        current_app.redis.hset(redis_key, mapping=redis_hash_mapping)
        current_app.redis.expire(redis_key, self.EXPIRY)

        return result

    def get_survey_list(self) -> dict:
        """
        Gets the survey list from redis or the survey service
        """
        redis_key = f"{self.APPLICATION_KEY}:survey-list"
        try:
            result = [json.loads(survey) for survey in current_app.redis.hvals(redis_key)]
        except RedisError:
            logger.error("Error getting value from cache, please investigate", redis_key=redis_key)
            result = None

        if not result:
            logger.info("Key not in cache, getting values from survey service", redis_key=redis_key)
            result = self.refresh_survey_list()

        return result

    def set(self, key, value, expiry):
        if not expiry:
            logger.error("Expiry must be provided")
            raise ValueError("Expiry must be provided")
        try:
            current_app.redis.set(key, value, ex=expiry)
        except RedisError:
            # Not throwing an exception as the cache isn't fatal
            logger.error("Error setting key, please investigate", key=key, exc_info=True)
