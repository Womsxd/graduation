import time
import pyotp
import utils
import messages
from database import models, db
from sqlalchemy.exc import SQLAlchemyError
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
        self.password = utils.get_password(password)

    def validate_password(self, password):
        return utils.validate_password(self.password, password)


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
    if user is None:  # 检测用户是否存在
        return jsonify(messages.AUTH_ERROR)
    if not user.validate_password(password):  # 检测密码是否错误
        return jsonify(messages.AUTH_ERROR)
    if user.otp_status == 1:  # 检测是否开启双因数身份验证
        otp_code = request.form.get('otp_code')
        if otp_code is None:
            return jsonify(messages.NEED_OTP)
        if not pyotp.TOTP(user.otp_secret).verify(otp_code):  # 检测双因数认识是否成功
            return jsonify(messages.OTP_VERIFY_ERROR)
    session.permanent = True
    user.csrf = utils.sha256(f'{user.id}-{time.time()}-{user.password}')
    # 登入后刷新csrf 让旧的失效 采用用户数字id+时间戳+密码进行哈希生成 防止重复
    try:
        # 提交修改到数据库
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
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
