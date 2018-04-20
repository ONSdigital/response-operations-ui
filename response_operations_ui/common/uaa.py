import logging
from json import JSONDecodeError

import requests
from flask import current_app
from requests import HTTPError

logger = logging.getLogger(__name__)


def request_uaa_public_key(app):
    headers = {
        'Accept': 'application/json',
    }

    public_key_url = f'{app.config["UAA_SERVICE_URL"]}/token_key'

    try:
        response = requests.get(public_key_url, headers=headers)
        response.raise_for_status()
        res_json = response.json()
        return res_json['value']
    except requests.RequestException:
        logger.exception(f"Error during request to get public key from {public_key_url}")
    except KeyError:
        logger.exception(f"No public key returned by UAA {public_key_url}")
    except (JSONDecodeError, ValueError):
        logger.exception(f"Unable to decode response from UAA {public_key_url}")
    except HTTPError:
        logger.exception(f"Error while retrieving public key from UAA at {public_key_url}")
    return None


def get_uaa_public_key():
    if not current_app.config.get('UAA_PUBLIC_KEY'):
        current_app.config['UAA_PUBLIC_KEY'] = request_uaa_public_key(current_app)
    return current_app.config['UAA_PUBLIC_KEY']
