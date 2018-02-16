class ApiError(Exception):

    def __init__(self, response):
        self.url = response.url
        self.status_code = response.status_code


class NoMessagesError(Exception):
    """ Thrown when getting a list of messages but the response doesn't
    contain a key named 'messages'.
    """
    pass


class InternalError(Exception):

    def __init__(self, exception, url=None, status=500):
        self.exception = exception
        self.url = url
        self.status = status

    def __str__(self):
        return f'url: {self.url} status:{self.status} exception:{self.exception}'
