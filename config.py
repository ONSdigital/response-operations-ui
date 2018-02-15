import os


class Config(object):
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    PORT = os.getenv('PORT', 8085)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    USE_SESSION_FOR_NEXT = True
    RESPONSE_OPERATIONS_UI_SECRET = os.getenv('RESPONSE_OPERATIONS_UI_SECRET', "secret")
    BACKSTAGE_BASE_URL = os.getenv('BACKSTAGE_BASE_URL')
    BACKSTAGE_API_SEND = '/v1/secure-message/send-message'


class DevelopmentConfig(Config):
    DEBUG = os.getenv('DEBUG', True)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')
    BACKSTAGE_BASE_URL = os.getenv('BACKSTAGE_BASE_URL', 'http://localhost:8001/backstage-api/')


class TestingConfig(DevelopmentConfig):
    DEBUG = False
    TESTING = True
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False
    BACKSTAGE_BASE_URL = os.getenv('BACKSTAGE_BASE_URL', 'http://localhost:8001/backstage-api')
