class ApiError(Exception):

    def __init__(self, response):
        self.url = response.url
        self.status_code = response.status_code
        self.message = response.text


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


class UpdateContactDetailsException(Exception):

    def __init__(self, ru_ref, form, respondent_details, status_code):
        self.ru_ref = ru_ref
        self.form = form
        self.respondent_details = respondent_details
        self.status_code = status_code


class SearchRespondentsException(Exception):

    def __init__(self, response, **kwargs):
        self.response = response
        self.status_code = response.status_code

        for k, v in kwargs:
            self[k] = v
