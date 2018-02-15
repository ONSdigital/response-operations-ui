

class ApiError(Exception):

    def __init__(self, response):
        self.url = response.url
        self.status_code = response.status_code


class InternalError(Exception):

    def __init__(self, exception, url=None, status=500):
        self.exception = exception
        self.url = url
        self.status = status

    def __str__(self):
        return ' '.join('url:', self.url, 'status:', self.status, 'exception:', str(self.exception))
