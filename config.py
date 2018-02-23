import os


class Config(object):
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    PORT = os.getenv('PORT', 8085)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    USE_SESSION_FOR_NEXT = True
    RESPONSE_OPERATIONS_UI_SECRET = os.getenv('RESPONSE_OPERATIONS_UI_SECRET', "secret")
    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL')
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DB = os.getenv('REDIS_DB', 3)


class DevelopmentConfig(Config):
    DEBUG = os.getenv('DEBUG', True)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')
    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL', 'http://localhost:8001/backstage-api')
    REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
    REDIS_PORT = os.getenv('REDIS_PORT', 7379)
    REDIS_DB = os.getenv('REDIS_DB', 3)


class TestingConfig(DevelopmentConfig):
    DEBUG = False
    TESTING = True
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False
