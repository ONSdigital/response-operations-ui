import json
import unittest

from response_operations_ui.common.pagination_processor import pagination_processor


class TestPagination(unittest.TestCase):
    href = "search?email=example@example.com"
    expected_page_link_with_href_json = [
        {"url": "search?email=example@example.com&page=1"},
        {"url": "search?email=example@example.com&page=2"},
        {"url": "search?email=example@example.com&page=3"},
    ]
    expected_page_link_without_href_json = [
        {"url": "?page=1"},
        {"url": "?page=2"},
        {"url": "?page=3"},
    ]

    def test_pagination_with_href(self):
        pagination = pagination_processor(6, 2, 2, self.href)
        self.assertEqual(pagination["page_links"], self.expected_page_link_with_href_json)
        self.assertEqual(pagination["current_page_number"], 2)

    def test_pagination_without_href(self):
        pagination = pagination_processor(6, 2, 3)
        self.assertEqual(pagination["page_links"], self.expected_page_link_without_href_json)
        self.assertEqual(pagination["current_page_number"], 3)
