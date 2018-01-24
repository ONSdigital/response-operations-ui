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

    def test_login_success(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        
        response_value = self.login(response.location, 'user', 'pass')
        self.assertIn(b'View list of business surveys', response_value.data)

    def test_login(self):
        response = self.app.get('/surveys')
        self.assertEqual(response.status_code, 302)

        response_value = self.login(response.location, 'user', 'pass')
        self.assertIn(b'Monthly Business Survey - Retail Sales Index', response_value.data)

    def test_logout(self):
        response = self.logout()
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)
