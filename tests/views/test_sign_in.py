import unittest

from response_operations_ui import app


class TestSignIn(unittest.TestCase):
    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def login(self, path, username, password):
        return self.app.post(path, data={'username': username, 'password': password},
                             follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_sign_in_page(self):
        response = self.app.get('/sign-in')
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)

    def test_logout(self):
        response = self.logout()
        self.assertIn(b'You\'ve logged out', response.data)
