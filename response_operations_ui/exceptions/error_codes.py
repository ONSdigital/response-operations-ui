from enum import Enum


class ErrorCode(Enum):
    """
    E0001 to E0006 relate to API Error Codes
    """

    CONNECTION_ERROR = "E0001"
    AUTHENTICATION_ERROR = "E0002"
    UNEXPECTED_STATUS_CODE = "E0003"
    UNEXPECTED_CONTENT_TYPE = "E0004"
    UNEXPECTED_CONTENT = "E0005"
    OIDC_CREDENTIALS_ERROR = "E0006"


def get_error_code_message(error_code):
    error_code_messages = {
        ErrorCode.CONNECTION_ERROR: "An error occurred trying to connect to the service",
        ErrorCode.AUTHENTICATION_ERROR: "An error occurred authenticating with the service",
        ErrorCode.UNEXPECTED_STATUS_CODE: "The service returned an unexpected status code",
        ErrorCode.UNEXPECTED_CONTENT_TYPE: "The service returned an unexpected content type",
        ErrorCode.UNEXPECTED_CONTENT: "The service returned unexpected content",
        ErrorCode.OIDC_CREDENTIALS_ERROR: "An error occurred preparing to authenticate with the service",
    }
    return error_code_messages.get(error_code, "An unknown error occurred")
