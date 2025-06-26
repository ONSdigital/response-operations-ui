import json
import logging

import requests
from flask import current_app as app
from requests import Session
from structlog import wrap_logger

from response_operations_ui.exceptions.error_codes import (
    ErrorCode,
    get_error_code_message,
)
from response_operations_ui.exceptions.exceptions import ExternalApiError

logger = wrap_logger(logging.getLogger(__name__))


def get_response_json_from_service(request_url: str, target_service: str, session: Session = None) -> json:
    try:
        response = session.get(request_url) if session else requests.get(request_url, auth=app.config["BASIC_AUTH"])

    except (requests.ConnectionError, requests.exceptions.Timeout) as e:
        error_code = (
            ErrorCode.API_CONNECTION_ERROR if isinstance(e, requests.ConnectionError) else ErrorCode.API_TIMEOUT_ERROR
        )
        logger.error(
            get_error_code_message(error_code),
            error=str(e),
            request_url=request_url,
            target_service=target_service,
        )

        raise ExternalApiError(None, error_code, target_service) from e
    if response.status_code != 200:
        if response.status_code == 404:
            logger.error(
                get_error_code_message(ErrorCode.NOT_FOUND),
                status_code=str(response.status_code),
                request_url=request_url,
                target_service=target_service,
            )
            raise ExternalApiError(response, ErrorCode.NOT_FOUND, target_service)
        else:
            logger.error(
                get_error_code_message(ErrorCode.API_UNEXPECTED_STATUS_CODE),
                status_code=str(response.status_code),
                request_url=request_url,
                target_service=target_service,
            )
            raise ExternalApiError(response, ErrorCode.API_UNEXPECTED_STATUS_CODE, target_service)

    if response.headers.get("content-type") != "application/json":
        logger.error(
            get_error_code_message(ErrorCode.API_UNEXPECTED_CONTENT_TYPE),
            content_type=response.headers.get("content-type"),
            request_url=request_url,
            target_service=target_service,
        )
        raise ExternalApiError(response, ErrorCode.API_UNEXPECTED_CONTENT_TYPE, target_service)
    else:
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            logger.error(
                get_error_code_message(ErrorCode.API_UNEXPECTED_CONTENT),
                error=str(e),
                request_url=request_url,
                target_service=target_service,
            )
            raise ExternalApiError(response, ErrorCode.API_UNEXPECTED_CONTENT, target_service) from e
