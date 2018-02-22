from flask_login import UserMixin

import jwt


def decode_access_token(access_token):
    decoded_jwt = jwt.decode(
        access_token,
        verify=False,
        leeway=10,
    )
    return decoded_jwt


def get_user_id(access_token):
    decoded_jwt = decode_access_token(access_token)
    return decoded_jwt.get('user_id')


class User(UserMixin):

    def __init__(self, token, user_id=None):
        self.id = token
        self.token = token
        self.user_id = user_id

    def get_user_id(self):
        if not self.user_id:
            self.user_id = get_user_id(self.token)
        return self.user_id
