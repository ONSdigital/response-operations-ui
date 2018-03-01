import cfenv
from flask import current_app


class ONSCloudFoundry(object):

    def __init__(self):
        self._cf_env = cfenv.AppEnv()

    def __bool__(self):
        return self._cf_env.app

    @property
    def redis(self):
        return self._cf_env.get_service(name=current_app.app_config['REDIS_SERVICE'])
