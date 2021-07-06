from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, username=None):
        self.id = user_id
        self.username = username
