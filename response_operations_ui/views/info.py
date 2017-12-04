import json
from pathlib import Path

from flask import make_response, jsonify

from response_operations_ui import app


@app.route('/info', methods=['GET'])
def get_info():

    _health_check = {}
    if Path('git_info').exists():
        with open('git_info') as io:
            _health_check = json.loads(io.read())

    info = {
        "name": 'response-operations-ui',
        "version": '0.0.1',
    }
    info = {**_health_check, **info}

    return make_response(jsonify(info), 200)
