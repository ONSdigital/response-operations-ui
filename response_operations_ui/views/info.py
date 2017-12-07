from json import JSONDecodeError, loads
import logging
from pathlib import Path

from flask import make_response, jsonify
from structlog import wrap_logger

from response_operations_ui import app


logger = wrap_logger(logging.getLogger(__name__))


@app.route('/info', methods=['GET'])
def get_info():

    _health_check = {}
    if Path('git_info').exists():
        with open('git_info') as io:
            try:
                _health_check = loads(io.read())
            except JSONDecodeError as e:
                logger.error('Failed to decode git_info json', exc_info=e)

    info = {
        "name": 'response-operations-ui',
        "version": '0.0.1',
    }
    info = {**_health_check, **info}

    return make_response(jsonify(info), 200)
