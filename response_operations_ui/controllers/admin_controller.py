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


def current_banner():
    logger.info('Attempting to retrieve the current live banner')
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.info('No banner currently active')
            return {}
        logger.error('Failed to retrieve Banner from api')
        raise ApiError(response)

    logger.info('Successfully retrieved current live banner from api')
    return response.json()


def set_banner(banner_text):
    logger.info('Attempting to set banner text', banner_text=banner_text)
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    response = requests.post(url, json=banner_text)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve Banner from api')
        raise ApiError(response)

    logger.info('Successfully retrieved current live banner from api')
    banner = response.json()
    return banner


def remove_banner():
    logger.info('Attempting to remove banner')
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    response = requests.delete(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to remove Banner')
        raise ApiError(response)

    logger.info('Successfully removed banner from api')


def get_templates():
    logger.info('Attempting to retrieve templates')
    url = f"{app.config['BANNER_SERVICE_URL']}/template"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve templates')
        raise ApiError(response)

    templates = response.json()
    logger.info('Successfully retrieved templates', template_count=len(templates))
    return templates


def get_template(template_id):
    logger.info('Attempting to retrieve template', template_id=template_id)
    url = f"{app.config['BANNER_SERVICE_URL']}/template/{template_id}"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve template from api', template_id=template_id)
        raise ApiError(response)

    template = response.json()
    logger.info('Successfully retrieved template from api', template_id=template_id)
    return template


def create_new_template(template):
    logger.info('Attempting to create a template', template=template)
    url = f"{app.config['BANNER_SERVICE_URL']}/template"
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, template, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to create template', template=template)
        raise ApiError(response)

    banner = response.json()
    logger.info('Successfully created a template', template=template)
    return banner


def edit_template(template):
    logger.info('Attempting to edit the template', template=template)
    url = f"{app.config['BANNER_SERVICE_URL']}/template"
    response = requests.put(url, json=template)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to edit template')
        raise ApiError(response)

    banner = response.json()
    logger.info('Successfully edited the Banner', template=template)
    return banner


def delete_template(template_id):
    logger.info('Attempting to delete template from Datastore', template_id)
    url = f"{app.config['BANNER_SERVICE_URL']}/template/{template_id}"
    response = requests.delete(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to delete template from Datastore', template_id=template_id)
        raise ApiError(response)

    logger.info('Successfully deleted banner', template_id=template_id)
