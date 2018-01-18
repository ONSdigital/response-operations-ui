import json
import logging
from pathlib import Path

from flask import Blueprint, make_response, jsonify
from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))

info_bp = Blueprint('info_bp', __name__, static_folder='static', template_folder='templates')


_health_check = {}
if Path('git_info').exists():
    with open('git_info') as io:
        _health_check = json.loads(io.read())


@info_bp.route('/', methods=['GET'])
def get_info():
    info = {
        "name": "response-operations-ui",
        "version": "0.0.1",
    }
    info = dict(_health_check, **info)

    return make_response(jsonify(info), 200)
