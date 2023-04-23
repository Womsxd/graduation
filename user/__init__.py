import messages
import auth.utils
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
    if not auth.utils.vailidate_password(user.password, old_pwd):
        return jsonify(messages.PASSWORD_ERROR)  # 就这里使用password提示
    user.password = auth.utils.get_password(new_pwd)
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
    user = models.User()
    user.account = username
    user.password = auth.autils.get_password(password)
    group_id = request.form.get('group_id')
    if group_id:
        if models.Group.query.filter_by(id=group_id).first() is None:
            return jsonify(messages.NO_GROUP)
        user.group_id = group_id
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
        user.password = auth.utils.get_password(password)  # 生成存储安全的密码
        user.csrf = None
    if group_id is not None:
        if user.groupid != group_id:
            if models.Group.query.filter_by(id=group_id).first() is None:
                return jsonify(messages.NO_GROUP)
            if user.groupid == 1 and models.User.query.filter(models.User.groupid == 1).count() <= 1:
                return jsonify(messages.NO_ADMIN)  # 防止可用用户中全都没有管理员权限
            user.group_id = group_id
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
    models.User.query.filter_by(account=username).delete()
    try:
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
