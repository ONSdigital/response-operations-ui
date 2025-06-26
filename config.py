import os

from response_operations_ui.common.strtobool import strtobool

FDI_LIST = {"AOFDI", "AIFDI", "QIFDI", "QOFDI"}
VACANCIES_LIST = {"VACS2", "VACS3", "VACS4", "VACS5"}


class Config(object):
    DEBUG = os.getenv("DEBUG", False)
    TESTING = False
    PORT = os.getenv("PORT", 8085)
    GOOGLE_TAG_MANAGER = os.getenv("GOOGLE_TAG_MANAGER")
    GOOGLE_TAG_MANAGER_PROP = os.getenv("GOOGLE_TAG_MANAGER_PROP")
    PREFERRED_URL_SCHEME = "https"
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
    RESPONSE_OPERATIONS_UI_SECRET = os.getenv("RESPONSE_OPERATIONS_UI_SECRET", "secret")
    SESSION_TYPE = "redis"
    # WTF_CSRF_TIME_LIMIT this wasn't set causing inconsistenices with sessions
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", 43200))
    WTF_CSRF_TIME_LIMIT = int(os.getenv("WTF_CSRF_TIME_LIMIT", PERMANENT_SESSION_LIFETIME))
    REDIS_SERVICE = os.getenv("REDIS_SERVICE")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_DB = os.getenv("REDIS_DB", 0)
    SECURE_COOKIES = strtobool(os.getenv("SECURE_COOKIES", "True"))
    USE_SESSION_FOR_NEXT = True  # Used by flask-login

    BANNER_SERVICE_HOST = os.getenv("BANNER_API_SERVICE_HOST", "http://localhost")
    BANNER_SERVICE_PORT = os.getenv("BANNER_API_SERVICE_PORT", "8000")
    BANNER_SERVICE_URL = os.getenv("BANNER_SERVICE_URL", f"{BANNER_SERVICE_HOST}:{BANNER_SERVICE_PORT}")

    SECURITY_USER_NAME = os.getenv("SECURITY_USER_NAME")
    SECURITY_USER_PASSWORD = os.getenv("SECURITY_USER_PASSWORD")
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    RESPONSE_OPERATIONS_UI_HOST = os.getenv("RESPONSE_OPERATIONS_UI_HOST", "http://localhost")
    RESPONSE_OPERATIONS_UI_PORT = os.getenv("RESPONSE_OPERATIONS_UI_PORT", "8085")
    RESPONSE_OPERATIONS_UI_URL = os.getenv(
        "RESPONSE_OPERATIONS_UI_URL", f"{RESPONSE_OPERATIONS_UI_HOST}:{RESPONSE_OPERATIONS_UI_PORT}"
    )

    # Service Configs
    CASE_URL = os.getenv("CASE_URL")
    MAX_CASES_RETRIEVED_PER_SURVEY = os.getenv("MAX_CASES_RETRIEVED_PER_SURVEY", 12)

    COLLECTION_EXERCISE_URL = os.getenv("COLLECTION_EXERCISE_URL")
    COLLECTION_INSTRUMENT_URL = os.getenv("COLLECTION_INSTRUMENT_URL")
    DASHBOARD_URL = os.getenv("DASHBOARD_URL")
    IAC_URL = os.getenv("IAC_URL")

    SECURE_MESSAGE_URL = os.getenv("SECURE_MESSAGE_URL")
    SECURE_MESSAGE_JWT_SECRET = os.getenv("SECURE_MESSAGE_JWT_SECRET")

    PARTY_URL = os.getenv("PARTY_URL")
    PARTY_RESPONDENTS_PER_PAGE = os.getenv("PARTY_RESPONDENTS_PER_PAGE", 25)
    PARTY_BUSINESS_RESULTS_PER_PAGE = os.getenv("PARTY_BUSINESS_RESULTS_PER_PAGE", 25)
    PARTY_BUSINESS_RESULTS_TOTAL = os.getenv("PARTY_BUSINESS_RESULTS_TOTAL", 10000)

    AUTH_URL = os.getenv("AUTH_URL")

    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "test-project-id")
    PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "ras-rm-notify-test")
    NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = os.getenv(
        "NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE", "request_password_change_id"
    )
    NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = os.getenv(
        "NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE", "confirm_password_change_id"
    )
    NOTIFY_CREATE_USER_ACCOUNT_TEMPLATE = os.getenv("NOTIFY_CREATE_USER_ACCOUNT_TEMPLATE", "create_user_account_id")
    NOTIFY_UPDATE_ACCOUNT_DETAILS_TEMPLATE = os.getenv(
        "NOTIFY_UPDATE_ACCOUNT_DETAILS_TEMPLATE", "update_account_details_id"
    )
    NOTIFY_UPDATE_EMAIL_TEMPLATE = os.getenv("NOTIFY_UPDATE_EMAIL_TEMPLATE", "update_email_id")
    NOTIFY_UPDATE_ACCOUNT_PASSWORD_CHANGE_TEMPLATE = os.getenv(
        "NOTIFY_UPDATE_ACCOUNT_PASSWORD_CHANGE_TEMPLATE", "update_account_password_id"
    )
    NOTIFY_UPDATE_USER_PERMISSIONS_TEMPLATE = os.getenv(
        "NOTIFY_UPDATE_USER_PERMISSIONS_TEMPLATE", "update_user_permissions_id"
    )
    NOTIFY_DELETE_USER_TEMPLATE = os.getenv("NOTIFY_DELETE_USER_TEMPLATE", "delete_user_id")

    SEND_EMAIL_TO_GOV_NOTIFY = os.getenv("SEND_EMAIL_TO_GOV_NOTIFY", False)

    REPORT_URL = os.getenv("REPORT_URL")
    SAMPLE_URL = os.getenv("SAMPLE_URL")
    SAMPLE_FILE_UPLOADER_URL = os.getenv("SAMPLE_FILE_UPLOADER_URL")
    SURVEY_URL = os.getenv("SURVEY_URL")

    UAA_SERVICE_URL = os.getenv("UAA_SERVICE_URL")
    UAA_CLIENT_ID = os.getenv("UAA_CLIENT_ID")
    UAA_CLIENT_SECRET = os.getenv("UAA_CLIENT_SECRET")

    EMAIL_TOKEN_SALT = os.getenv("EMAIL_TOKEN_SALT", "aardvark")
    # 24 hours in seconds
    EMAIL_TOKEN_EXPIRY = int(os.getenv("EMAIL_TOKEN_EXPIRY", "86400"))
    # 4 weeks in seconds
    CREATE_ACCOUNT_EMAIL_TOKEN_EXPIRY = int(os.getenv("CREATE_ACCOUNT_EMAIL_TOKEN_EXPIRY", "2419200"))
    # 3 days in seconds
    UPDATE_ACCOUNT_EMAIL_TOKEN_EXPIRY = int(os.getenv("UPDATE_ACCOUNT_EMAIL_TOKEN_EXPIRY", "259200"))
    # 48 hours in seconds
    # Grace period for changing the survey status from complete to not started to ensure that when an eQ status is
    # changed, the respondent will be provided with an empty survey
    COMPLETE_TO_NOT_STARTED_WAIT_TIME = int(os.getenv("COMPLETE_TO_NOT_STARTED_WAIT_TIME", "172800"))

    TEST_MODE = strtobool(os.getenv("TEST_MODE", "False"))
    WTF_CSRF_ENABLED = strtobool(os.getenv("WTF_CSRF_ENABLED", "True"))

    OIDC_TOKEN_BACKEND = os.getenv("OIDC_TOKEN_BACKEND", "gcp")
    OIDC_TOKEN_VALIDITY_IN_SECONDS = int(os.getenv("OIDC_TOKEN_VALIDITY_IN_SECONDS", "3600"))
    OIDC_TOKEN_LEEWAY_IN_SECONDS = int(os.getenv("OIDC_TOKEN_LEEWAY_IN_SECONDS", "300"))
    CIR_API_URL = CIR_API_URL = os.getenv("CIR_API_URL", "https://cir.integration.onsdigital.uk")
    CIR_OAUTH2_CLIENT_ID = os.getenv("CIR_OAUTH2_CLIENT_ID", "dummy_client_id")
    CIR_ENABLED = strtobool(os.getenv("CIR_ENABLED", "True"))
    CIR_API_PREFIX = os.getenv("CIR_API_PREFIX", "/v2/ci_metadata")


class DevelopmentConfig(Config):
    DEBUG = os.getenv("DEBUG", True)
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
    PREFERRED_URL_SCHEME = "http"
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_DB = os.getenv("REDIS_DB", 0)
    SECURE_COOKIES = strtobool(os.getenv("SECURE_COOKIES", "False"))

    SECURITY_USER_NAME = os.getenv("SECURITY_USER_NAME", "admin")
    SECURITY_USER_PASSWORD = os.getenv("SECURITY_USER_PASSWORD", "secret")
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    # Service Config
    CASE_URL = os.getenv("CASE_URL", "http://localhost:8171")
    COLLECTION_EXERCISE_URL = os.getenv("COLLECTION_EXERCISE_URL", "http://localhost:8145")
    COLLECTION_INSTRUMENT_URL = os.getenv("COLLECTION_INSTRUMENT_URL", "http://localhost:8002")
    DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8078")
    IAC_URL = os.getenv("IAC_URL", "http://localhost:8121")

    SECURE_MESSAGE_URL = os.getenv("SECURE_MESSAGE_URL", "http://localhost:5050")
    SECURE_MESSAGE_JWT_SECRET = os.getenv("SECURE_MESSAGE_JWT_SECRET", "testsecret")

    REPORT_URL = os.getenv("REPORT_URL", "http://localhost:8084")
    PARTY_URL = os.getenv("PARTY_URL", "http://localhost:8081")
    SAMPLE_URL = os.getenv("SAMPLE_URL", "http://localhost:8125")
    SAMPLE_FILE_UPLOADER_URL = os.getenv("SAMPLE_FILE_UPLOADER_URL", "http://localhost:8083")
    SURVEY_URL = os.getenv("SURVEY_URL", "http://localhost:8080")
    AUTH_URL = os.getenv("AUTH_URL", "http://localhost:8041")

    UAA_SERVICE_URL = os.getenv("UAA_SERVICE_URL", "http://localhost:9080")
    UAA_CLIENT_ID = os.getenv("UAA_CLIENT_ID", "response_operations")
    UAA_CLIENT_SECRET = os.getenv("UAA_CLIENT_SECRET", "response.operations.dummy.secret")

    EMAIL_TOKEN_SALT = os.getenv("EMAIL_TOKEN_SALT", "aardvark")
    # 24 hours in seconds
    EMAIL_TOKEN_EXPIRY = int(os.getenv("EMAIL_TOKEN_EXPIRY", "86400"))
    # 4 weeks in seconds
    CREATE_ACCOUNT_EMAIL_TOKEN_EXPIRY = int(os.getenv("CREATE_ACCOUNT_EMAIL_TOKEN_EXPIRY", "2419200"))
    # 3 days in seconds
    UPDATE_ACCOUNT_EMAIL_TOKEN_EXPIRY = int(os.getenv("UPDATE_ACCOUNT_EMAIL_TOKEN_EXPIRY", "259200"))
    WTF_CSRF_ENABLED = strtobool(os.getenv("WTF_CSRF_ENABLED", "False"))
    # 5 minutes in seconds
    COMPLETE_TO_NOT_STARTED_WAIT_TIME = int(os.getenv("COMPLETE_TO_NOT_STARTED_WAIT_TIME", "300"))

    OIDC_TOKEN_BACKEND = os.getenv("OIDC_TOKEN_BACKEND", "local")
    OIDC_TOKEN_VALIDITY_IN_SECONDS = int(os.getenv("OIDC_TOKEN_VALIDITY_IN_SECONDS", "3600"))
    OIDC_TOKEN_LEEWAY_IN_SECONDS = int(os.getenv("OIDC_TOKEN_LEEWAY_IN_SECONDS", "300"))
    CIR_API_URL = CIR_API_URL = os.getenv("CIR_API_URL", "http://localhost:3030")
    CIR_OAUTH2_CLIENT_ID = os.getenv("CIR_OAUTH2_CLIENT_ID", "dummy_client_id")
    CIR_ENABLED = strtobool(os.getenv("CIR_ENABLED", "True"))
    CIR_API_PREFIX = os.getenv("CIR_API_PREFIX", "/v2/ci_metadata")


class TestingConfig(DevelopmentConfig):
    """Configuration used for testing.  The uaa public and private keys in this block are used ONLY for
    the unit tests when testing the jwt and aren't used at all for anything else.
    """

    FAKE_REDIS_PORT = os.getenv("FAKE_REDIS_PORT", 6380)

    DEBUG = False
    TESTING = True
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SEND_EMAIL_TO_GOV_NOTIFY = True
    UAA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFswDQYJKoZIhvcNAQEBBQADSgAwRwJAeeLysb2I2n86Ya+W3vqCxUM1j5sRdlFN
U9yf2b38ppt3rf2xHJYTfjSvezXOMEJusFbhH9LeH4V8kr4k4ZmdewIDAQAB
-----END PUBLIC KEY-----"""
    UAA_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIBOQIBAAJAeeLysb2I2n86Ya+W3vqCxUM1j5sRdlFNU9yf2b38ppt3rf2xHJYT
fjSvezXOMEJusFbhH9LeH4V8kr4k4ZmdewIDAQABAkBmg8QeTEybgWDIIpghaM+u
PC4DX6hbPFxuiWSFDe8+7N/dWO6xV3zDjzM6L8lXb5J2woEZ0JUVeS/BQB1xykOh
AiEAvdS9ocmimlGUTHaH+t0N92ZJBuGc5RdrQjdVMc5bZ0sCIQCkX0qHKjzxBC8S
IYBrirWvgd/bEXbV/81BprpF6p7UkQIhAJ0mNu5urAuwqWI7ZgrJYTyEEsR9lZMZ
thOVFxQqTwTNAiAFBhCODwFr0Ffr8vAs2UFySsLfvCnoonfQgNsClggisQIgIGEJ
Z5VVFymXN2n+A6UeWAnuO8/E1inhk99dBzKEGdw=
-----END RSA PRIVATE KEY-----"""
    SECRET_KEY = "sekrit!"
    SECURITY_USER_NAME = "admin"
    SECURITY_USER_PASSWORD = "secret"
    # 5 minutes in seconds
    COMPLETE_TO_NOT_STARTED_WAIT_TIME = int(os.getenv("COMPLETE_TO_NOT_STARTED_WAIT_TIME", "300"))

    OIDC_TOKEN_BACKEND = os.getenv("OIDC_TOKEN_BACKEND", "local")
    OIDC_TOKEN_VALIDITY_IN_SECONDS = int(os.getenv("OIDC_TOKEN_VALIDITY_IN_SECONDS", "3600"))
    OIDC_TOKEN_LEEWAY_IN_SECONDS = int(os.getenv("OIDC_TOKEN_LEEWAY_IN_SECONDS", "300"))
    CIR_API_URL = CIR_API_URL = os.getenv("CIR_API_URL", "http://localhost:3030")
    CIR_OAUTH2_CLIENT_ID = os.getenv("CIR_OAUTH2_CLIENT_ID", "dummy_client_id")
    CIR_ENABLED = True
    CIR_API_PREFIX = os.getenv("CIR_API_PREFIX", "/v2/ci_metadata")
