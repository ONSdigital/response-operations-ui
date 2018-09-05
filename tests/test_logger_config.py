import logging
import os
import unittest

from structlog import wrap_logger
from testfixtures import log_capture

from response_operations_ui.logger_config import logger_initial_config


class TestLoggerConfig(unittest.TestCase):

    @log_capture()
    def test_success(self, l):
        os.environ['JSON_INDENT_LOGGING'] = '1'
        logger_initial_config(service_name='response-operations-ui')
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg
        message_contents = '{\n "event": "Test",\n "zipkin_trace_id": "",\n "zipkin_span_id": "",' \
                           '\n "level": "error",\n "service": "response-operations-ui"'
        self.assertIn(message_contents, message)

    @log_capture()
    def test_indent_type_error(self, l):
        os.environ['JSON_INDENT_LOGGING'] = 'abc'
        logger_initial_config(service_name='response-operations-ui')
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg
        self.assertIn('{"event": "Test", "zipkin_trace_id": "", "zipkin_span_id": "",'
                      ' "level": "error", "service": "response-operations-ui"', message)

    @log_capture()
    def test_indent_value_error(self, l):
        logger_initial_config(service_name='response-operations-ui')
        logger = wrap_logger(logging.getLogger())
        logger.error('Test')
        message = l.records[0].msg
        self.assertIn('{"event": "Test", "zipkin_trace_id": "", "zipkin_span_id": "",'
                      ' "level": "error", "service": "response-operations-ui"', message)
