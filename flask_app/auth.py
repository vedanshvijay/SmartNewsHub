from flask_login import LoginManager, UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User as UserModel

login_manager = LoginManager()
login_manager.login_view = 'main.login'

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    user = UserModel.query.get(int(user_id))
    if user:
        return User(user.id, user.username, user.password_hash)
    return None 