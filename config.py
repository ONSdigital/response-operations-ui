import os


class Config(object):
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    PORT = os.getenv('PORT', 8085)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL', 'http://localhost:8883/backstage-api/v1')


class DevelopmentConfig(Config):
    DEBUG = os.getenv('DEBUG', True)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')


class TestingConfig(DevelopmentConfig):
    DEBUG = False
    Testing = True
