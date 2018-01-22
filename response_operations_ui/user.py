from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.username = "user"
        self.password = "pass"

    # def __repr__(self):
    #     return "%d/%s/%s" % (self.id, self.username, self.password)
