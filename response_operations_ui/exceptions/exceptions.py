class ApiError(Exception):
    def __init__(self, response):
        self.url = response.url
        self.status_code = response.status_code
        self.message = response.text


class InternalError(Exception):
    def __init__(self, exception, url=None, status=500):
        self.exception = exception
        self.url = url
        self.status = status

    def __str__(self):
        return f"url: {self.url} status:{self.status} exception:{self.exception}"


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

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class UserDoesNotExist(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class NotifyError(Exception):
    def __init__(self, description=None, error=None, **kwargs):
        self.description = description
        self.error = error
        for k, v in kwargs.items():
            self.__dict__[k] = v


class RURetrievalError(Exception):
    def __init__(self, response, ru_ref):
        self.ru_ref = ru_ref
        self.url = response.url
        self.status_code = response.status_code
        self.message = response.text
