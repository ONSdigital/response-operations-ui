import pprint

import redis
import logging
import json
import requests

from flask import current_app as app
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def _get_redis():
    r = redis.Redis(host=app.config['REDIS_HOST'],
                    port=app.config['REDIS_PORT'],
                    db=app.config['REDIS_DB'],
                    decode_responses=True)
    return r


def set_banner_and_time(banner, time):
    try:
        r = _get_redis()
        r.set('AVAILABILITY_MESSAGE', banner)
        r.set('AVAILABILITY_MESSAGE_TIME_SET', time)
        logger.debug("Setting availability message", banner=banner)
    except redis.RedisError:
        logger.exception("Unable to update banner and time. Ensure time parameter is correct structure if not\
                         default. e.g. strftime does not work on string")


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


'''
Unused code
'''


# def get_alert_list():
#     my_dict = {}
#     try:
#         with open('response_operations_ui/templates/banner-admin-json.json', 'r') as f:
#             alert_list = json.load(f)
#     except (OSError, IOError) as e:
#         logger.exception(e, 'error opening JSON file containing the alert templates')
#     for i in alert_list:
#         my_dict.update(i)
#     return my_dict


def get_all_banners():
    logger.info('Attempting to retrieve banners from Datastore')
    url = f"{app.config['RAS_RM_BANNER_SERVICE_URL']}/banner"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banners from Datastore')
        raise ApiError(response)

    logger.info('Successfully retrieved banners from Datastore')
    list_of_banners = response.json()
    # if collection_exercise['events']:
    #     collection_exercise['events'] = convert_events_to_new_format(collection_exercise['events'])
    return list_of_banners


def get_a_banner(banner):
    logger.info('Attempting to retrieve banners from Datastore')
    url = f"{app.config['RAS_RM_BANNER_SERVICE_URL']}/banner/{banner}"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banners from Datastore')
        raise ApiError(response)

    logger.info('Successfully retrieved banners from Datastore')
    banner = response.json()
    # if collection_exercise['events']:
    #     collection_exercise['events'] = convert_events_to_new_format(collection_exercise['events'])
    return banner


def create_new_banner(banner):
    logger.info('Attempting to retrieve banners from Datastore')
    url = f"{app.config['RAS_RM_BANNER_SERVICE_URL']}/banner/{banner}"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banners from Datastore')
        raise ApiError(response)

    logger.info('Successfully retrieved banners from Datastore')
    banner = response.json()
    # if collection_exercise['events']:
    #     collection_exercise['events'] = convert_events_to_new_format(collection_exercise['events'])
    return banner


def delete_a_banner(banner):
    logger.info('Attempting to retrieve banners from Datastore')
    url = f"{app.config['RAS_RM_BANNER_SERVICE_URL']}/banner/{banner}"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banners from Datastore')
        raise ApiError(response)

    logger.info('Successfully retrieved banners from Datastore')
    banner = response.json()
    # if collection_exercise['events']:
    #     collection_exercise['events'] = convert_events_to_new_format(collection_exercise['events'])
    return banner
