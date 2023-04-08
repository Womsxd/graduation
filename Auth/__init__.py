import json
import utils
from flask import request, Blueprint
from database import models
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)
login_managet = LoginManager()
login_managet.session_protection = "strong"
login_managet.login_view = "/auth/nologin"


class User(UserMixin, models.User):
    def __init__(self):
        super(User, self).__init__()

    def set_password(self, password):
        self.password = generate_password_hash(password, "pbkdf2:sha512")

    def vailidate_password(self, password):
        return check_password_hash(self.password, password)


@login_managet.user_loader
def load_loader(id):
    if User.query.filter_by(id=id).first():
        user = User()
        user.id = id
        return user
    return None


@auth.route('/auth/login', methods=['post'])
def login():
    account = request.form.get('account')
    password = request.form.get('password')
    print(password)
    user = User.query.filter_by(account=account).first()
    if user is not None and user.vailidate_password(password):
        login_user(user, fresh=True)
        return json.dumps({'code': 0, "message": ""})
    return json.dumps({'code': 1, "message": "Account/Password Error"})


@auth.route('/auth/logout', methods=['get', 'post'])
@login_required
def logout():
    logout_user()
    return json.dumps({'code': 0, "message": ""})


@auth.route('/auth/nologin')
def nologin():
    return json.dumps({'code': 2, "message": "NoLogin"})
