import os


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

    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)

    # Service URLs and Service specific config
    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL')
    PARTY_URL = os.getenv('PARTY_SERVICE_URL')
    PARTY_USERNAME = os.getenv('PARTY_USERNAME')
    PARTY_PASSWORD = os.getenv('PARTY_PASSWORD')
    SECURE_MESSAGE_URL = os.getenv('SECURE_MESSAGE_URL')
    SURVEY_URL = os.getenv('SURVEY_URL')
    SURVEY_USERNAME = os.getenv('SURVEY_USERNAME')
    SURVEY_PASSWORD = os.getenv('SURVEY_PASSWORD')
    UAA_SERVICE_URL = os.getenv('UAA_SERVICE_URL')
    RAS_SECURE_MESSAGING_JWT_SECRET = os.getenv('RAS_SECURE_MESSAGING_JWT_SECRET')


class DevelopmentConfig(Config):
    DEBUG = os.getenv('DEBUG', True)
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')
    BASIC_AUTH = (SECURITY_USER_NAME, SECURITY_USER_PASSWORD)
    REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    REDIS_DB = os.getenv('REDIS_DB', 0)

    # Service URLS and Service specific config
    BACKSTAGE_API_URL = os.getenv('BACKSTAGE_API_URL', 'http://localhost:8001/backstage-api')
    PARTY_URL = os.getenv('PARTY_URL', 'http://localhost:8081')
    PARTY_USERNAME = os.getenv('PARTY_USERNAME', 'admin')
    PARTY_PASSWORD = os.getenv('PARTY_PASSWORD', 'secret')
    SECURE_MESSAGE_URL = os.getenv('SECURE_MESSAGE_URL', 'http://localhost:5050')
    SURVEY_URL = os.getenv('SURVEY_URL', 'http://localhost:8080/')
    SURVEY_USERNAME = os.getenv('SURVEY_USERNAME', 'admin')
    SURVEY_PASSWORD = os.getenv('SURVEY_PASSWORD', 'secret')
    UAA_SERVICE_URL = os.getenv('UAA_SERVICE_URL', 'http://localhost:9080')
    RAS_SECURE_MESSAGING_JWT_SECRET = os.getenv('RAS_SECURE_MESSAGING_JWT_SECRET', 'testsecret')


class TestingConfig(DevelopmentConfig):
    DEBUG = False
    TESTING = True
    LOGIN_DISABLED = True
    WTF_CSRF_ENABLED = False
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
