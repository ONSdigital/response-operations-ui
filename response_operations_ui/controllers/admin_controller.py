import redis
import logging

from flask import current_app
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def _get_redis():
    r = redis.Redis(host=current_app.config['REDIS_HOST'],
                    port=current_app.config['REDIS_PORT'],
                    db=current_app.config['REDIS_DB'],
                    decode_responses=True)
    return r


def set_banner(banner):
    try:
        r = _get_redis()
        r.set('AVAILABILITY_MESSAGE', banner)
        logger.debug("Setting availability message", banner=banner)
    except redis.RedisError:
        logger.exception("Unable to updated banner")


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
