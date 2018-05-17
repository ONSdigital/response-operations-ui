import os
from distutils.util import strtobool


class Config(object):
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    PORT = os.getenv('PORT', 8085)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    RESPONSE_OPERATIONS_UI_SECRET = os.getenv('RESPONSE_OPERATIONS_UI_SECRET', "secret")
    SESSION_TYPE = "redis"
    PERMANENT_SESSION_LIFETIME = os.getenv('PERMANENT_SESSION_LIFETIME', 43200)
    REDIS_SERVICE = os.getenv('REDIS_SERVICE')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DB = os.getenv('REDIS_DB', 0)
    SECURE_COOKIES = strtobool(os.getenv('SECURE_COOKIES', 'True'))
    EDIT_EVENT_DATES_ENABLED = strtobool(os.getenv('EDIT_EVENT_DATES_ENABLED', 'False'))
    USE_SESSION_FOR_NEXT = True

    # Service Configs
    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL')

    CASE_URL = os.getenv('CASE_URL')
    CASE_USERNAME = os.getenv('CASE_USERNAME')
    CASE_PASSWORD = os.getenv('CASE_PASSWORD')
    CASE_AUTH = (CASE_USERNAME, CASE_PASSWORD)

    COLLECTION_EXERCISE_URL = os.getenv('COLLECTION_EXERCISE_URL')
    COLLECTION_EXERCISE_USERNAME = os.getenv('COLLECTION_EXERCISE_USERNAME')
    COLLECTION_EXERCISE_PASSWORD = os.getenv('COLLECTION_EXERCISE_PASSWORD')
    COLLECTION_EXERCISE_AUTH = (COLLECTION_EXERCISE_USERNAME, COLLECTION_EXERCISE_PASSWORD)

    IAC_URL = os.getenv('IAC_URL')
    IAC_USERNAME = os.getenv('IAC_USERNAME')
    IAC_PASSWORD = os.getenv('IAC_PASSWORD')
    IAC_AUTH = (IAC_USERNAME, IAC_PASSWORD)

    SECURE_MESSAGE_URL = os.getenv('SECURE_MESSAGE_URL')
    RAS_SECURE_MESSAGING_JWT_SECRET = os.getenv('RAS_SECURE_MESSAGING_JWT_SECRET')

    PARTY_URL = os.getenv('PARTY_URL')
    PARTY_USERNAME = os.getenv('PARTY_USERNAME')
    PARTY_PASSWORD = os.getenv('PARTY_PASSWORD')
    PARTY_AUTH = (PARTY_USERNAME, PARTY_PASSWORD)

    SAMPLE_URL = os.getenv('SAMPLE_URL')
    SAMPLE_USERNAME = os.getenv('SAMPLE_USERNAME')
    SAMPLE_PASSWORD = os.getenv('SAMPLE_PASSWORD')
    SAMPLE_AUTH = (SAMPLE_USERNAME, SAMPLE_PASSWORD)

    SURVEY_URL = os.getenv('SURVEY_URL')
    SURVEY_USERNAME = os.getenv('SURVEY_USERNAME')
    SURVEY_PASSWORD = os.getenv('SURVEY_PASSWORD')
    SURVEY_AUTH = (SURVEY_USERNAME, SURVEY_PASSWORD)

    UAA_SERVICE_URL = os.getenv('UAA_SERVICE_URL')


class DevelopmentConfig(Config):
    DEBUG = os.getenv('DEBUG', True)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')
    REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
    REDIS_PORT = os.getenv('REDIS_PORT', 7379)
    REDIS_DB = os.getenv('REDIS_DB', 0)
    SECURE_COOKIES = strtobool(os.getenv('SECURE_COOKIES', 'False'))
    EDIT_EVENT_DATES_ENABLED = True

    # Service Config
    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL', 'http://localhost:8001/backstage-api')

    CASE_URL = os.getenv('CASE_URL', 'http://localhost:8171')
    CASE_USERNAME = os.getenv('CASE_USERNAME', 'admin')
    CASE_PASSWORD = os.getenv('CASE_PASSWORD', 'secret')
    CASE_AUTH = (CASE_USERNAME, CASE_PASSWORD)

    COLLECTION_EXERCISE_URL = os.getenv('COLLECTION_EXERCISE_URL', 'http://localhost:8145')
    COLLECTION_EXERCISE_USERNAME = os.getenv('COLLECTION_EXERCISE_USERNAME', 'admin')
    COLLECTION_EXERCISE_PASSWORD = os.getenv('COLLECTION_EXERCISE_PASSWORD', 'secret')
    COLLECTION_EXERCISE_AUTH = (COLLECTION_EXERCISE_USERNAME, COLLECTION_EXERCISE_PASSWORD)

    IAC_URL = os.getenv('IAC_URL', 'http://localhost:8121')
    IAC_USERNAME = os.getenv('IAC_USERNAME', 'admin')
    IAC_PASSWORD = os.getenv('IAC_PASSWORD', 'secret')
    IAC_AUTH = (IAC_USERNAME, IAC_PASSWORD)

    SECURE_MESSAGE_URL = os.getenv('SECURE_MESSAGE_URL', 'http://localhost:5050')
    RAS_SECURE_MESSAGING_JWT_SECRET = os.getenv('RAS_SECURE_MESSAGING_JWT_SECRET', 'testsecret')

    PARTY_URL = os.getenv('PARTY_URL', 'http://localhost:8081')
    PARTY_USERNAME = os.getenv('PARTY_USERNAME', 'admin')
    PARTY_PASSWORD = os.getenv('PARTY_PASSWORD', 'secret')
    PARTY_AUTH = (PARTY_USERNAME, PARTY_PASSWORD)

    SAMPLE_URL = os.getenv('SAMPLE_URL', 'http://localhost:8125')
    SAMPLE_USERNAME = os.getenv('SAMPLE_USERNAME', 'admin')
    SAMPLE_PASSWORD = os.getenv('SAMPLE_PASSWORD', 'secret')
    SAMPLE_AUTH = (SAMPLE_USERNAME, SAMPLE_PASSWORD)

    SURVEY_URL = os.getenv('SURVEY_URL', 'http://localhost:8080')
    SURVEY_USERNAME = os.getenv('SURVEY_USERNAME', 'admin')
    SURVEY_PASSWORD = os.getenv('SURVEY_PASSWORD', 'secret')
    SURVEY_AUTH = (SURVEY_USERNAME, SURVEY_PASSWORD)

    UAA_SERVICE_URL = os.getenv('UAA_SERVICE_URL', 'http://localhost:9080')


class TestingConfig(DevelopmentConfig):
    DEBUG = False
    TESTING = True
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
