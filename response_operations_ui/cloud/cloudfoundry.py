import cfenv


class ONSCloudFoundry(object):

    def __init__(self):
        self._cf_env = cfenv.AppEnv()

    def __bool__(self):
        return True if self._cf_env.app else False

    def redis(self, service_name):
        return self._cf_env.get_service(name=service_name)
