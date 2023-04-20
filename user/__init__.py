import messages
import auth.utils
from database import models, db
from group import check_permissions
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

userf = Blueprint('userf', __name__)


@userf.route('/user/changepwd', methods=['post'])
@login_required
def changepwd():
    old_pwd = request.form.get("old_pwd")
    new_pwd = request.form.get("new_pwd")
    user = models.User.query.filter_by(csrf=current_user.get_id()).first()
    if old_pwd is None or new_pwd is None or user is None:
        return jsonify(messages.DATA_NONE)
    if not auth.utils.vailidate_password(user.password, old_pwd):
        return jsonify(messages.PASSWORD_ERROR)
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
    user = models.User.query.filter_by(account=account).first()
    if account is None or user is None:
        return jsonify(messages.DATA_NONE)
    if password is not None:
        user.password = auth.utils.get_password(password)
        user.csrf = None
    if groupid is not None:
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
    page = int(request.values.get("page", 1))
    users = models.User.query.offset((page - 1) * 20).limit(20).all()
    total = models.User.query.count()
    maximum = int(total / 20) + 1
    data = []
    for i in users:
        data.append({"id": i.id, "account": i.account, "group": i.groupid})
    rej = {}
    rej.update(messages.OK_DATA)
    rej["data"] = {"users": data, "total": total, "current": page, "maximum": maximum}
    return jsonify(rej)
