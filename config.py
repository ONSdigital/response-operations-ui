import os


class Config(object):
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    PORT = os.getenv('PORT', 8085)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL', 'http://localhost:8001/backstage-api/v2')
    RESPONSE_OPERATIONS_UI_SECRET = os.getenv('RESPONSE_OPERATIONS_UI_SECRET', "secret")


class DevelopmentConfig(Config):
    DEBUG = os.getenv('DEBUG', True)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')


class TestingConfig(DevelopmentConfig):
    DEBUG = False
    TESTING = True
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False
