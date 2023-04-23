import time
import messages
import utils as gutils
import auth.utils as autils
from database import models, db
from flask import request, Blueprint, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "/auth/unauthorized"


class User(UserMixin, models.User):
    def __init__(self):
        super(User, self).__init__()

    def get_id(self):
        return str(self.csrf)

    def set_password(self, password):
        self.password = autils.get_password(password)

    def vailidate_password(self, password):
        return autils.vailidate_password(self.password, password)


@login_manager.user_loader
def user_loader(csrf):
    if User.query.filter_by(csrf=csrf).first():
        user = User()
        user.csrf = csrf
        return user
    return None


@auth.route('/auth/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not (username and password):
        return jsonify(messages.DATA_NONE)
    user = User.query.filter_by(account=username).first()
    if user is None:
        return jsonify(messages.AUTH_ERROR)
    if not user.vailidate_password(password):
        return jsonify(messages.AUTH_ERROR)
    session.permanent = True
    user.csrf = gutils.sha256(f'{user.id}-{time.time()}-{user.password}')
    # 登入后刷新csrf 让旧的失效 采用用户数字id+时间戳+密码进行哈希生成 防止重复
    db.session.commit()
    # 提交修改到数据库
    login_user(user)
    session["_uid"] = user.id
    return jsonify(messages.OK)
    


@auth.route('/auth/logout', methods=['GET', 'POST'])
@login_required
def logout():
    User.query.filter_by(csrf=current_user.get_id()).update({'csrf': None})
    # 退出登入后让csrf失效，先获取+修改，等logout_user执行之后再提交修改
    logout_user()
    db.session.commit()
    return jsonify(messages.OK)


@auth.route('/auth/unauthorized')
@login_manager.unauthorized_handler
def unauthorized():
    return jsonify(messages.NO_LOGIN)
