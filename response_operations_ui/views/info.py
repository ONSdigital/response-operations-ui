from json import JSONDecodeError, loads
import logging
from pathlib import Path

from flask import Blueprint, make_response, jsonify, g
from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))

info_bp = Blueprint('info_bp', __name__, static_folder='static', template_folder='templates')


@info_bp.route('/', methods=['GET'])
def get_info():

    _health_check = {}
    if Path('git_info').exists():
        with open('git_info') as io:
            try:
                _health_check = loads(io.read())
            except JSONDecodeError:
                logger.exception('Failed to decode git_info json')

    info = {
        "name": 'response-operations-ui',
        "version": '0.0.1',
    }
    info = {**_health_check, **info}

    setattr(g, "info", True)
    return make_response(jsonify(info), 200)
