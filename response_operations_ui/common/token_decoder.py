import jwt
import logging

from structlog import wrap_logger
from response_operations_ui.common.uaa import get_uaa_public_key

logger = wrap_logger(logging.getLogger(__name__))


def decode_access_token(access_token):
    uaa_public_key = get_uaa_public_key()
    decoded_jwt = jwt.decode(
        access_token,
        key=uaa_public_key,
        audience='response_operations',
        leeway=10
    )
    return decoded_jwt
