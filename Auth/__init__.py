from app import app
from Database import models
from flask_login import LoginManager, UserMixin

login_managet = LoginManager()
login_managet.init_app(app)


class User(UserMixin, models.User):
    def __init__(self):
        super(User, self).__init__()
