from datetime import datetime

import redis
import logging
import json

from flask import current_app
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def _get_redis():
    r = redis.Redis(host=current_app.config['REDIS_HOST'],
                    port=current_app.config['REDIS_PORT'],
                    db=current_app.config['REDIS_DB'],
                    decode_responses=True)
    return r


def set_banner_and_time(banner, time=datetime.now()):
    try:
        r = _get_redis()
        r.set('AVAILABILITY_MESSAGE', banner)
        r.set('AVAILABILITY_MESSAGE_TIME_SET', time)
        logger.debug("Setting availability message", banner=banner)
    except redis.RedisError:
        logger.exception("Unable to update banner and time")
        logger.exception('Ensure time parameter is correct structure if not '
                         'default. e.g. strftime does not work on string')


def remove_banner():
    try:
        r = _get_redis()
        r.delete('AVAILABILITY_MESSAGE')
        logger.debug("Deleting availability message")
    except redis.RedisError:
        logger.exception("Unable to remove banner")


def current_banner():
    try:
        r = _get_redis()
        banner = r.get('AVAILABILITY_MESSAGE')
        logger.debug("Getting availability message", banner=banner)
        return banner
    except redis.RedisError:
        logger.exception("Unable to retrieve current banners")


def banner_time_get():
    try:
        r = _get_redis()
        banner = r.get('AVAILABILITY_MESSAGE_TIME_SET')
        logger.debug("Getting time availability message was set", banner=banner)
        return banner
    except redis.RedisError:
        logger.exception("Unable to retrieve current banners")


def get_alert_list():
    my_dict = {}
    try:
        with open('response_operations_ui/templates/banner-admin-json.json', 'r') as f:
            alert_list = json.load(f)
    except (OSError, IOError) as e:
        logger.exception(e, 'error opening JSON file containing the alert templates')
    for i in alert_list:
        my_dict.update(i)
    return my_dict