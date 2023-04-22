import messages
import auth.utils
from database import models, db
from sqlalchemy.orm import aliased
from group import check_permissions
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

userf = Blueprint('userf', __name__)


@userf.route('/user/change_password', methods=['post'])
@login_required
def change_password():
    old_pwd = request.form.get("old_pwd")
    new_pwd = request.form.get("new_pwd")
    user = models.User.query.filter_by(csrf=current_user.get_id()).first()
    if old_pwd is None or new_pwd is None or user is None:
        return jsonify(messages.DATA_NONE)
    if not auth.utils.vailidate_password(user.password, old_pwd):
        return jsonify(messages.PASSWORD_ERROR)  # 就这里使用password提示
    user.password = auth.utils.get_password(new_pwd)
    user.csrf = None
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@userf.route('/user/add', methods=['post'])
@login_required
@check_permissions(1)
def add():
    user = models.User()
    user.account = request.form.get('account')
    password = request.form.get('password')
    groupid = request.form.get('groupid')
    if user.account is None and password is None:
        return jsonify(messages.DATA_NONE)
    user.password = auth.autils.get_password(password)
    if groupid is not None:
        user.groupid = groupid
    db.session.add(user)
    return jsonify(messages.OK)


@userf.route('/user/edit', methods=['post'])
@login_required
@check_permissions(1)
def edit():
    account = request.form.get('account')
    password = request.form.get('password')
    groupid = request.form.get('groupid')
    if account is None:
        return jsonify(messages.DATA_NONE)
    user = models.User.query.filter_by(account=account).first()
    if user is None:
        return jsonify(messages.NOT_FOUND)
    if password is not None:
        if user.csrf == current_user.get_id():  # 防止管理员在这里修改掉自己的密码，应为csrf只能同时存在一个，所以直接判断是否相等
            return jsonify(messages.DOT_CHANGE_OWN_PASSWORD)  # 返回报错，引导用户使用change_password来修改自己的密码
        user.password = auth.utils.get_password(password)  # 生成存储安全的密码
        user.csrf = None
    if groupid is not None:
        if user.groupid != groupid:
            if user.groupid == 1 and models.User.query.filter(models.User.groupid == 1).count() <= 1:
                return jsonify(messages.NO_ADMIN)  # 防止可用用户中全都没有管理员权限
            user.groupid = groupid
    db.session.commit()
    return jsonify(messages.OK)


@userf.route('/user/delete', methods=['post'])
@login_required
@check_permissions(1)
def delete():
    account = request.form.get('account')
    if account is None:
        return jsonify(messages.DATA_NONE)
    models.User.query.filter_by(account=account).delete()
    db.session.commit()
    return jsonify(messages.OK)


@userf.route('/user/list', methods=['get', 'post'])
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
