import utils
import messages
from database import models, db
from group import check_permissions
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify

userf = Blueprint('userf', __name__)

from . import otp

WHITE_LIST = [1]


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


@userf.route('/user/get_my_info', methods=['GET'])
@login_required
def get_my_info():
    user = models.User.query.join(models.Group).with_entities(
        models.User.id, models.User.account, models.Group.name.label('group_n'), models.User.otp_status,
        models.User.banned).filter_by(csrf=current_user.get_id()).first()
    returns = {"data": {"id": user.id, "account": user.account, "group": user.group_n, "otp_status": user.otp_status,
                        "banned": user.banned}}
    returns.update(messages.OK)
    return jsonify(returns)


@userf.route('/user/add', methods=['POST'])
@login_required
@check_permissions("user.add")
def add():
    username = request.form.get('username')
    password = request.form.get('password')
    if not (username and password):
        return jsonify(messages.DATA_NONE)
    if models.User.query.filter_by(account=username).first() is not None:
        returns = messages.OK.copy()
        returns["message"] = f'Account is {returns["message"]}'
        return jsonify(returns)
    user = models.User(account=username, password=utils.get_password(password))
    group_id = request.form.get('group_id')
    if group_id is not None:
        if not utils.check_record_existence(models.Group, group_id):
            returns = messages.DOT_EXIST.copy()
            returns['message'] = f"group_id {returns['message']}"
            return jsonify(returns)
        user.group_id = group_id
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@userf.route('/user/edit', methods=['POST'])
@login_required
@check_permissions("user.edit")
def edit():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    user = models.User.query.filter_by(id=id).first()
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
        """
        if not utils.check_record_existence(models.Group, group_id):
            returns = messages.DOT_EXIST.copy()
            returns['message'] = f"group_id {returns['message']}"
            return jsonify(returns)
        """
        if utils.check_record_existence(models.Group, group_id):
            if user.group_id == 1 and models.User.query.filter(models.User.group_id == 1).count() <= 1:
                return jsonify(messages.NO_ADMIN)  # 防止可用用户中全都没有管理员权限
            user.group_id = int(group_id)
    disable_otp = request.form.get('disable_otp')
    if user.csrf == current_user.get_id():
        return jsonify(messages.NOT_DISABLE_OTP)
    if disable_otp is not None or user.otp_status != 0:  # 只能强行关闭otp不能强行打开
        if disable_otp.lower() == 'true':
            user.otp_status = 0
            user.otp_secret = None
            user.otp_act_exp_time = None
    set_banned = request.form.get('set_banned')
    if user.csrf == current_user.get_id():
        return jsonify(messages.NOT_BAN_SELF)
    if set_banned is not None:
        if set_banned.lower() == 'true':
            user.banned = 1
            user.csrf = None  # 清除被ban用户的csrf
        elif set_banned.lower() == 'false':
            user.banned = 0  # 不等于1的时候unban
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@userf.route('/user/delete', methods=['POST'])
@login_required
@check_permissions("user.delete")
def delete():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    if id in WHITE_LIST:
        return jsonify(messages.NOT_DELETE)
    user = models.User.query.filter_by(id=id).first()
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
@check_permissions("user.list")
def get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.User.query.join(models.Group).with_entities(
        models.User.id, models.User.account, models.Group.name.label('group_n'))
    search = request.values.get("search")
    if search is not None:
        querying = querying.filter(models.User.account.like(f"%{search}%"))
    group_id = request.values.get("group_id")
    if group_id is not None:
        querying = querying.filter_by(group_id=group_id)  # 都写死3个了，这里也直接写死的了
    pagination = querying.paginate(page=page, per_page=20)
    users = [{"id": i.id, "account": i.account, "group": i.group_n} for i in pagination.items]
    returns = {"data": {"users": users, "total": pagination.total, "current": page, "maximum": pagination.pages}}
    returns.update(messages.OK)
    return jsonify(returns)


@userf.route('/user/query', methods=['GET', 'POST'])
@login_required
@check_permissions("user.query")
def query():
    id_ = request.values.get("id")
    if id_ is None:
        return jsonify(messages.DATA_NONE)
    user = models.User.query.join(models.Group).with_entities(
        models.User.id, models.User.account, models.Group.name.label('group_n'), models.User.otp_status,
        models.User.banned).filter_by(id=id_).first()
    if user is None:
        return jsonify(messages.DATA_NONE)
    returns = {"data": {"id": user.id, "account": user.account, "group": user.group_n, "otp_status": user.otp_status,
                        "banned": user.banned}}
    returns.update(messages.OK)
    return jsonify(returns)


@userf.route('/user/import_xls', methods=['POST'])
@login_required
@check_permissions("user.import_xls")
def import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = utils.load_xls_file(file.read(), "用户")
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["用户名", "密码", "用户组"] != result[0][:3]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    repeat_users = []
    error_lens = []
    repeat_user_lens = []
    try:
        with db.session.begin(nested=True):
            group_cache = {}
            user_adds = []
            for i in result[1:]:
                if "" in i[:2]:  # 账号密码为空直接忽略或者已经添加过了
                    error_lens.append(result.index(i) + 1)
                    continue
                if i[0] in repeat_users or i[0] in [user.account for user in user_adds]:
                    if i[0] not in repeat_users:
                        repeat_users.append(i[0])
                    error_lens.append(result.index(i) + 1)
                    continue  # 重复添加
                if models.User.query.filter_by(account=i[0]).first() is not None:
                    repeat_users.append(i[0])
                    error_lens.append(result.index(i) + 1)
                    continue
                group_id = None
                if i[2] != "":
                    if i[2] in group_cache.keys():
                        group_id = group_cache[i[2]]
                    else:
                        group = models.Group.query.filter_by(name=i[2]).first()
                        if group is not None:
                            group_id = group.id
                    group_cache[i[2]] = group_id
                user_adds.append(models.User(account=i[0], password=utils.get_password(i[1]), group_id=group_id))
            returns = {"data": {"ok": len(user_adds), "repeat": len(repeat_user_lens),
                                "repeat_lens_users": repeat_user_lens, "error": len(error_lens),
                                "error_lens": error_lens}}
            db.session.bulk_save_objects(user_adds)
        returns.update(messages.OK)
        return jsonify(returns)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
