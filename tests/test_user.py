import unittest

from response_operations_ui.user import User


class TestUser(unittest.TestCase):

    def test_user_id(self):
        user = User("token123")
        self.assertEquals(user.id, "token123")
