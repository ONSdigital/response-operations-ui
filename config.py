import os
from distutils.util import strtobool


class Config(object):
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    PORT = os.getenv('PORT', 8085)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    USE_SESSION_FOR_NEXT = True
    RESPONSE_OPERATIONS_UI_SECRET = os.getenv('RESPONSE_OPERATIONS_UI_SECRET', "secret")
    SESSION_TYPE = "redis"
    PERMANENT_SESSION_LIFETIME = os.getenv('PERMANENT_SESSION_LIFETIME', 43200)
    REDIS_SERVICE = os.getenv('REDIS_SERVICE')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DB = os.getenv('REDIS_DB', 0)
    SECURE_COOKIES = strtobool(os.getenv('SECURE_COOKIES', 'True'))

    # Service Configs
    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL')

    COLLECTION_EXERCISE_URL = os.getenv('COLLECTION_EXERCISE_URL')
    COLLECTION_EXERCISE_USERNAME = os.getenv('COLLECTION_EXERCISE_USERNAME')
    COLLECTION_EXERCISE_PASSWORD = os.getenv('COLLECTION_EXERCISE_PASSWORD')
    COLLECTION_EXERCISE_AUTH = (COLLECTION_EXERCISE_USERNAME, COLLECTION_EXERCISE_PASSWORD)

    PARTY_URL = os.getenv('PARTY_URL')
    PARTY_USERNAME = os.getenv('PARTY_USERNAME')
    PARTY_PASSWORD = os.getenv('PARTY_PASSWORD')
    PARTY_AUTH = (PARTY_USERNAME, PARTY_PASSWORD)

    SECURE_MESSAGE_URL = os.getenv('SECURE_MESSAGE_URL')
    RAS_SECURE_MESSAGING_JWT_SECRET = os.getenv('RAS_SECURE_MESSAGING_JWT_SECRET')

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

    # Service Config
    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL', 'http://localhost:8001/backstage-api')

    COLLECTION_EXERCISE_URL = os.getenv('COLLECTION_EXERCISE_URL', 'http://localhost:8145')
    COLLECTION_EXERCISE_USERNAME = os.getenv('COLLECTION_EXERCISE_USERNAME', 'admin')
    COLLECTION_EXERCISE_PASSWORD = os.getenv('COLLECTION_EXERCISE_PASSWORD', 'secret')
    COLLECTION_EXERCISE_AUTH = (COLLECTION_EXERCISE_USERNAME, COLLECTION_EXERCISE_PASSWORD)

    PARTY_URL = os.getenv('PARTY_URL', 'http://localhost:8081')
    PARTY_USERNAME = os.getenv('PARTY_USERNAME', 'admin')
    PARTY_PASSWORD = os.getenv('PARTY_PASSWORD', 'secret')
    PARTY_AUTH = (PARTY_USERNAME, PARTY_PASSWORD)

    SECURE_MESSAGE_URL = os.getenv('SECURE_MESSAGE_URL', 'http://localhost:5050')
    RAS_SECURE_MESSAGING_JWT_SECRET = os.getenv('RAS_SECURE_MESSAGING_JWT_SECRET', 'testsecret')

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
