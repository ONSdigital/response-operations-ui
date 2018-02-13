class ApiError(Exception):

    def __init__(self, response):
        self.url = response.url
        self.status_code = response.status_code


class NoMessagesError(Exception):
    """ Thrown when getting a list of messages but the response doesn't
    contain a key named 'messages'.
    """
    pass
