from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict["id"]
        self.email = user_dict["email"]
        self.role = user_dict["role"]
        self.created_at = user_dict["created_at"]
