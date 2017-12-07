import json
import logging

from flask import render_template
import requests
from structlog import wrap_logger

from response_operations_ui import app


logger = wrap_logger(logging.getLogger(__name__))


@app.route('/', methods=['GET'])
def view_surveys():
    return render_template('surveys.html')


def get_surveys_list():
    logger.debug('Retrieving surveys list')
    url = '{}/{}'.format(app.config['BACKSTAGE_API_URL'], 'surveys')

    response = requests.get(url)
    if response.status_code != 200:
        logger.error('Failed to retrieve surveys list')
        raise Exception

    logger.debug('Successfully retrieved surveys list')
    return json.loads(response.text)
