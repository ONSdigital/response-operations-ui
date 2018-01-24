import os


class Config(object):
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    PORT = os.getenv('PORT', 8085)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL', 'http://localhost:8001/backstage-api/v1')

    PASSWORD_MATCH_ERROR_TEXT = 'Your passwords do not match'
    PASSWORD_CRITERIA_ERROR_TEXT = 'Your password doesn\'t meet the requirements'
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 160


class DevelopmentConfig(Config):
    DEBUG = os.getenv('DEBUG', True)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')


class TestingConfig(DevelopmentConfig):
    DEBUG = False
    TESTING = True
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False

    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL', 'http://localhost:8001/backstage-api/v1')
