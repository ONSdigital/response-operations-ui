import unittest
from collections import namedtuple

from response_operations_ui.exceptions.exceptions import (
    ApiError,
    InternalError,
    SearchRespondentsException,
    UpdateContactDetailsException,
    ServiceUnavailableException,
)

fake_response = namedtuple("Response", "url status_code text exception")


class TestApiError(unittest.TestCase):
    def test_new_api_error_contains_correct_data(self):
        exception = ApiError(fake_response(url="TESTURL", status_code=318, text="TESTMSG", exception="EXCEPTION"))

        self.assertEqual(exception.url, "TESTURL")
        self.assertEqual(exception.status_code, 318)
        self.assertEqual(exception.message, "TESTMSG")

    def test_internal_error_exception(self):
        exception = InternalError("EXCEPTION", "URL", 318)

        self.assertEqual(exception.exception, "EXCEPTION")
        self.assertEqual(exception.url, "URL")
        self.assertEqual(exception.status, 318)
        self.assertEqual(str(exception), "url: URL status:318 exception:EXCEPTION")

    def test_update_contact_details_exception(self):
        exception = UpdateContactDetailsException("RUREF", "FORM", "RESPDETS", 318)

        self.assertEqual(exception.ru_ref, "RUREF")
        self.assertEqual(exception.form, "FORM")
        self.assertEqual(exception.respondent_details, "RESPDETS")
        self.assertEqual(exception.status_code, 318)

    def test_search_respondent_exception(self):
        resp = fake_response(url="TESTURL", status_code=318, text="TESTMSG", exception="EXCEPTION")
        exception = SearchRespondentsException(resp, kw1="KW1", kw2="KW2", kw3="KW3")

        self.assertEqual(exception.status_code, 318)
        self.assertEqual(exception.response, resp)
        self.assertEqual(exception.kw1, "KW1")
        self.assertEqual(exception.kw2, "KW2")
        self.assertEqual(exception.kw3, "KW3")
        
    def test_service_unavailable_exception(self):
        exception = ServiceUnavailableException(["Error1", "Error2"], 503)
        
        self.assertEqual(exception.status_code, 503)
        self.assertEqual(exception.errors[0], "Error1")
        self.assertEqual(exception.errors[1], "Error2")
