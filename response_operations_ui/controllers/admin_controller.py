import redis
import logging

from flask import current_app

logger = logging.getLogger(__name__)


def add_banner(banner):
    r = redis.Redis(host=current_app.config['REDIS_HOST'],
                      port=current_app.config['REDIS_PORT'],
                      db=current_app.config['REDIS_DB'])
    r.set('AVAILABILITY_MESSAGE', banner)
    logger.debug(f"Setting availability message {banner}")


def remove_banner():
    r = redis.Redis(host=current_app.config['REDIS_HOST'],
                      port=current_app.config['REDIS_PORT'],
                      db=current_app.config['REDIS_DB'])
    r.delete('AVAILABILITY_MESSAGE')
    logger.debug("Deleting availability message")


def current_banner():
    r = redis.Redis(host=current_app.config['REDIS_HOST'],
                    port=current_app.config['REDIS_PORT'],
                    db=current_app.config['REDIS_DB'])
    banner = r.get('AVAILABILITY_MESSAGE')
    logger.debug(f"Getting availability message {banner}")
    return banner
