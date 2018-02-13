class ApiError(Exception):

    def __init__(self, response):
        self.url = response.url
        self.status_code = response.status_code


class NoMessages(Exception):
    pass
