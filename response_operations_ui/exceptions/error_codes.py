from enum import Enum


class ErrorCode(Enum):
    """
    E0001 to E0006 relate to API Error Codes
    """

    API_CONNECTION_ERROR = "E0001"
    API_AUTHENTICATION_ERROR = "E0002"
    API_UNEXPECTED_STATUS_CODE = "E0003"
    API_UNEXPECTED_CONTENT_TYPE = "E0004"
    API_UNEXPECTED_CONTENT = "E0005"
    API_OIDC_CREDENTIALS_ERROR = "E0006"
    API_TIMEOUT_ERROR = "E0007"
    
    # HTTP Error Codes
    NO_RESULTS_FOUND = "404"


def get_error_code_message(error_code):
    error_code_messages = {
        ErrorCode.API_CONNECTION_ERROR: "Unable to connect to CIR",
        ErrorCode.API_TIMEOUT_ERROR: "The request to the service timed out",
        ErrorCode.API_AUTHENTICATION_ERROR: "An error occurred authenticating with the service",
        ErrorCode.API_UNEXPECTED_STATUS_CODE: "The service returned an unexpected status code",
        ErrorCode.API_UNEXPECTED_CONTENT_TYPE: "The service returned an unexpected content type",
        ErrorCode.API_UNEXPECTED_CONTENT: "The service returned unexpected content",
        ErrorCode.API_OIDC_CREDENTIALS_ERROR: "An error occurred preparing to authenticate with the service",
        ErrorCode.NO_RESULTS_FOUND: "No CIR data retrieved"
    }
    return error_code_messages.get(error_code, "An unknown error occurred")
