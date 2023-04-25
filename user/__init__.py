import utils
import messages
from database import models, db
from group import check_permissions
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

userf = Blueprint('userf', __name__)


@userf.route('/user/change_password', methods=['POST'])
@login_required
def change_password():
    old_pwd = request.form.get("old_pwd")
    new_pwd = request.form.get("new_pwd")
    if not (old_pwd and new_pwd):
        return jsonify(messages.DATA_NONE)
    user = models.User.query.filter_by(csrf=current_user.get_id()).first()
    if not utils.validate_password(user.password, old_pwd):
        return jsonify(messages.PASSWORD_ERROR)  # 就这里使用password提示
    user.password = utils.get_password(new_pwd)
    user.csrf = None
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@userf.route('/user/add', methods=['POST'])
@login_required
@check_permissions(1)
def add():
    username = request.form.get('username')
    password = request.form.get('password')
    if not (username and password):
        return jsonify(messages.DATA_NONE)
    user = models.User(account=username, password=utils.get_password(password))
    group_id = request.form.get('group_id')
    if group_id:
        if models.Group.query.filter_by(id=group_id).first() is None:
            return jsonify(messages.NO_GROUP)
        user.group_id = int(group_id)
    try:
        with db.session.begin():
            db.session.add(user)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@userf.route('/user/edit', methods=['POST'])
@login_required
@check_permissions(1)
def edit():
    username = request.form.get('username')
    if username is None:
        return jsonify(messages.DATA_NONE)
    user = models.User.query.filter_by(account=username).first()
    if user is None:
        return jsonify(messages.NOT_FOUND)
    password = request.form.get('password')
    group_id = request.form.get('group_id')
    if password is not None:
        if user.csrf == current_user.get_id():  # 防止管理员在这里修改掉自己的密码，应为csrf只能同时存在一个，所以直接判断是否相等
            return jsonify(messages.DOT_CHANGE_OWN_PASSWORD)  # 返回报错，引导用户使用change_password来修改自己的密码
        user.password = utils.get_password(password)  # 生成存储安全的密码
        user.csrf = None
    if group_id is not None:
        if user.groupid != group_id:
            if models.Group.query.filter_by(id=group_id).first() is None:
                return jsonify(messages.NO_GROUP)
            if user.groupid == 1 and models.User.query.filter(models.User.groupid == 1).count() <= 1:
                return jsonify(messages.NO_ADMIN)  # 防止可用用户中全都没有管理员权限
            user.group_id = group_id
    disable_otp = request.form.get('disable_otp')
    if disable_otp is not None or user.otp_status != 0:  # 只能强行关闭otp不能强行打开
        if disable_otp.lower() == 'true':
            user.otp_status = 0
            user.otp_secret = None
            user.otp_act_exp_time = None
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@userf.route('/user/delete', methods=['POST'])
@login_required
@check_permissions(1)
def delete():
    username = request.form.get('username')
    if username is None:
        return jsonify(messages.DATA_NONE)
    user = models.User.query.filter_by(account=username).first()
    if user is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@userf.route('/user/list', methods=['GET', 'POST'])
@login_required
@check_permissions(1)
def ulist():
    page = request.values.get("page", 1, type=int)
    pagination = models.User.query.join(models.Group).with_entities(
        models.User.id, models.User.account, models.Group.name.label('group_n')
    ).paginate(page=page, per_page=20)
    users = [{"id": i.id, "account": i.account, "group": i.group_n} for i in pagination.items]
    data = {"users": users, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@userf.route('/user/search', methods=['GET', 'POST'])
@login_required
@check_permissions(1)
def search():
    key = request.values.get("key")
    if key is None:
        return jsonify(messages.NOT_SEARCH_KEY)
    page = request.values.get("page", 1, type=int)
    pagination = models.User.query.join(models.Group).with_entities(
        models.User.id, models.User.account, models.Group.name.label('group_n')
    ).filter(models.User.account.like(f"%{key}%")).paginate(page=page, per_page=20)
    users = [{"id": i.id, "account": i.account, "group": i.group_n} for i in pagination.items]
    data = {"users": users, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@userf.route('/user/import_xls', methods=['POST'])
@login_required
@check_permissions(1)
def import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = utils.load_xls_file(file.read(), "用户")
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["用户名", "密码", "用户组"] != result[0][:2]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    ok, error = 0, 0
    all_groups = models.Group.query.all()  # 这玩意量少，就单独领出来先全部导入进来
    #  models.Group.query.filter_by(or_(models.Group.name == i[2], models.Group.name.ilike(i[2]))).first() 给量多的
    try:
        with db.session.begin():
            for i in result:
                group = None
                for g in all_groups:
                    if g.name.lower() == i[2].lower():
                        group = g
                        break
                if not group:
                    error += 1
                    continue
                user = models.User(account=i[0], password=utils.get_password(i[1]), group_id=group.id)
                ok += 1
                db.session.add(user)
        returns = {"data": {"ok": ok, "error": error}}
        returns.update(messages.OK)
        return jsonify(returns)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
