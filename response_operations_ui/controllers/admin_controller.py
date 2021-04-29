import logging
import json
import requests

from flask import current_app as app
from structlog import wrap_logger

from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


class Template:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def current_banner():
    """
    Gets the current banner, if it exists.

    :return: A dict with the current text of the banner. Will be empty if there isn't one set
    :rtype dict
    :raises ApiError: Raised on any non-404 failure status code returned from the banner-api
    """
    logger.info('Attempting to retrieve the current live banner')
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            logger.info('No banner currently active')
            return {}
        logger.error('Failed to retrieve current live banner')
        raise ApiError(response)

    logger.info('Successfully retrieved current live banner')
    return response.json()


def set_banner(banner_text: str):
    """
    Sets the text of the banner.  If there was a banner already active then this will overwrite the text
    that was previously there.

    :param banner_text: The text the banner will display
    :type banner_text: str
    :return: A copy of what the banner-api has saved to the database
    :rtype: dict
    :raises ApiError: Raised on any 4XX or 5XX returned from the banner-api
    """
    logger.info('Attempting to set banner text', banner_text=banner_text)
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    response = requests.post(url, json={'content': banner_text})
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to set banner text')
        raise ApiError(response)

    logger.info('Successfully set banner text')
    banner = response.json()
    return banner


def remove_banner():
    """
    Deletes the banner, if it exists.  If there was no active banner then a success is reported regardless.

    :rtype: None
    :raises ApiError: Raised on any 4XX or 5XX returned from the banner-api
    """
    logger.info('Attempting to remove banner')
    url = f"{app.config['BANNER_SERVICE_URL']}/banner"
    response = requests.delete(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to remove Banner')
        raise ApiError(response)

    logger.info('Successfully removed banner')


def get_templates():
    """
    Gets all the templates stored in the banner-api service.

    :return: A list of dicts containing the templates stored
    :rtype: list of dict
    :raises ApiError: Raised on any 4XX or 5XX returned from the banner-api
    """
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


def get_template(template_id: str) -> dict:
    """
    Get a specific template, by id, from the banner-api service.

    :param template_id: A string representation of the template_id
    :return: A dict containing the data stored for the template
    :raises ApiError: Raised on any 4XX or 5XX returned from the banner-api
    """
    logger.info('Attempting to retrieve template', template_id=template_id)
    url = f"{app.config['BANNER_SERVICE_URL']}/template/{template_id}"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to retrieve template', template_id=template_id)
        raise ApiError(response)

    template = response.json()
    logger.info('Successfully retrieved template', template_id=template_id)
    return template


def create_new_template(template: dict) -> dict:
    """
    Creates a new template.

    :param template: A dictionary containing all the data required for a new template
    :return: A copy of what the banner-api has saved to the database
    :raises ApiError: Raised on any 4XX or 5XX returned from the banner-api
    """
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


def edit_template(template: dict) -> dict:
    """
    Edits an existing template. The template that is provided will overwrite everything that was there
    previously.

    :param template: A dict containing all the fields for the template
    :return: A copy of what the banner-api has saved to the database
    :raises ApiError: Raised on any 4XX or 5XX returned from the banner-api
    """
    logger.info('Attempting to edit the template', template=template)
    url = f"{app.config['BANNER_SERVICE_URL']}/template"
    response = requests.put(url, json=template)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to edit the template')
        raise ApiError(response)

    banner = response.json()
    logger.info('Successfully edited the template', template=template)
    return banner


def delete_template(template_id: str):
    """
    Deletes a template, if it exists.  Will report success even if it didn't exist.

    :param template_id: A string representation of the template_id
    :rtype: None
    :raises ApiError: Raised on any 4XX or 5XX returned from the banner-api
    """
    logger.info('Attempting to delete template', template_id=template_id)
    url = f"{app.config['BANNER_SERVICE_URL']}/template/{template_id}"
    response = requests.delete(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.error('Failed to delete template', template_id=template_id)
        raise ApiError(response)

    logger.info('Successfully deleted template', template_id=template_id)
