import logging
from json import JSONDecodeError, loads
from pathlib import Path

from flask import Blueprint, jsonify, make_response, session
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))

info_bp = Blueprint("info_bp", __name__, static_folder="static", template_folder="templates")


@info_bp.route("/", methods=["GET"])
def get_info():
    _health_check = {}
    if Path("git_info").exists():
        with open("git_info") as io:
            try:
                _health_check = loads(io.read())
            except JSONDecodeError:
                logger.exception("Failed to decode git_info json")

    info = {
        "name": "response-operations-ui",
        "version": "1.9.1",
    }
    info = {**_health_check, **info}

    return make_response(jsonify(info), 200)


@info_bp.after_request
def clear_session(response):
    # the info endpoint will be hit by CF to confirm app status
    # we don't want lots of sessions in REDIS for this so clear
    # the session after each request
    session.clear()
    return response
