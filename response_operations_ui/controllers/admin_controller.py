import logging
import json
import requests

from flask import current_app as app
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


class Banner:
    def __init__(self, title, content, active=False):
        self.title = title
        self.content = content
        self.active = active

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def toggle_banner_active_status(banner_id):
    logger.info('Attempting to set banner to active', banner_id=banner_id)
    url = f"{app.config['BANNER_SERVICE_URL']}/banner/{banner_id}/active"
    response = requests.patch(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banner from api')
        raise ApiError(response)

    logger.info('Successfully retrieved current live banner from api')
    banner = response.json()
    return banner


def remove_banner(banner_id):
    logger.info('Attempting to remove banner', banner_id=banner_id)
    url = f"{app.config['BANNER_SERVICE_URL']}/banner/{banner_id}"
    response = requests.delete(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to remove Banner', banner_id=banner_id)
        raise ApiError(response)

    logger.info('Successfully removed banner from api', banner_id=banner_id)


def current_banner():
    logger.info('Attempting to retrieve the current live banner')
    url = f"{app.config['BANNER_SERVICE_URL']}/banner/active"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banner from api')
        raise ApiError(response)

    logger.info('Successfully retrieved current live banner from api')
    if response.status_code == 204:
        return {}
    banner = response.json()
    return banner


def get_all_banners():
    logger.info('Attempting to retrieve banners')
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banners')
        raise ApiError(response)

    list_of_banners = response.json()
    logger.info('Successfully retrieved banners', banners=list_of_banners)
    return list_of_banners


def get_a_banner(banner_id):
    logger.info('Attempting to retrieve banner', banner_id=banner_id)
    url = f"{app.config['BANNER_SERVICE_URL']}/banner/{banner_id}"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banner from api')
        raise ApiError(response)

    banner = response.json()
    logger.info('Successfully retrieved banner from api', banner=banner)
    return banner


def create_new_banner(banner):
    logger.info('Attempting to store a banner banner', banner=banner)
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, banner, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to create Banner')
        raise ApiError(response)

    banner = response.json()
    logger.info('Successfully created the new Banner', banner=banner)
    return banner


def edit_banner(banner):
    logger.info('Attempting to edit the banner', banner=banner)
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    headers = {'Content-type': 'application/json'}
    response = requests.put(url, banner, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to edit banner via banner-api')
        raise ApiError(response)

    banner = response.json()
    logger.info('Successfully edited the Banner', banner=banner)
    return banner


def delete_banner(banner_id):
    logger.info('Attempting to delete banner from Datastore')
    url = f"{app.config['BANNER_SERVICE_URL']}/banner/{banner_id}"
    response = requests.delete(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to delete Banners from Datastore')
        raise ApiError(response)

    logger.info('Successfully deleted banner', banner_id=banner_id)
