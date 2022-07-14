import logging

import jwt
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from structlog import wrap_logger
from werkzeug.exceptions import InternalServerError

from response_operations_ui.common.uaa import get_uaa_public_key

logger = wrap_logger(logging.getLogger(__name__))


def decode_access_token(access_token):
    """Decodes the access token provided by uaa.  It's important to note that this JWT is
    using RS256 as it's what uaa uses whereas other parts of the application use HS256.
    """
    uaa_public_key = get_uaa_public_key()
    decoded_jwt = jwt.decode(
        access_token, key=uaa_public_key, algorithms=["RS256"], audience="response_operations", leeway=10
    )
    return decoded_jwt


def generate_token(data):
    """
    Creates a token based on data provided

    :param data: Some data that we wish to create a token for
    :return: A serialised string containing the data
    """
    secret_key = current_app.config["SECRET_KEY"]
    email_token_salt = current_app.config["EMAIL_TOKEN_SALT"]

    # Double checking config items are set as they need to be set up correctly
    if secret_key is None or email_token_salt is None:
        msg = "SECRET_KEY or EMAIL_TOKEN_SALT are not configured."
        logger.error(msg)
        raise InternalServerError(msg)

    timed_serializer = URLSafeTimedSerializer(secret_key)
    return timed_serializer.dumps(data, salt=email_token_salt)


def decode_email_token(token, duration=None):
    """Decodes a token and returns the result

    :param token: A serialised string
    :param duration: The amount of time in seconds the token is valid for.  If the token is older
    then this number, an exception will be thrown. Default is None.
    :return: The contents of the deserialised token
    """
    logger.info("Decoding email verification token", token=token)

    timed_serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    email_token_salt = current_app.config["EMAIL_TOKEN_SALT"]

    result = timed_serializer.loads(token, salt=email_token_salt, max_age=duration)
    logger.info("Successfully decoded email verification token", token=token)
    return result
