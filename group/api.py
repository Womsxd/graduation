import messages
from database import models, db
from . import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, request, jsonify

groups = Blueprint('group', __name__)
WHITE_LIST = [1, 2, 3]


@groups.route('/group/add', methods=['POST'])
@login_required
@check_permissions("group.add")
def add():
    name = request.form.get("name")
    if name is None:
        return jsonify(messages.DATA_NONE)
    permissions = request.form.get("permissions")
    inherit = request.form.get("inherit")
    group = models.Group(name=name, permissions=permissions, inherit=inherit)
    try:
        db.session.add(group)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@groups.route('/group/edit', methods=['POST'])
@login_required
@check_permissions("group.edit")
def edit():
    id = request.form.get("id")
    if id is None:
        return jsonify(messages.DATA_NONE)
    group = models.Group.query.filter_by(id=id).first()
    if group is None:
        return jsonify(messages.NOT_FOUND)
    name = request.form.get("name")
    if name is not None:
        group.name = name
    permissions = request.form.get("permissions")
    if permissions is not None:
        group.permissions = permissions
    inherit = request.form.get("inherit")
    if inherit is not None:
        group.inherit = inherit
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@groups.route('/group/delete', methods=['POST'])
@login_required
@check_permissions("group.delete")
def delete():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    if id in WHITE_LIST:
        return jsonify(messages.NOT_DELETE)
    group = models.Group.query.filter_by(id=id).first()
    if group is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(group)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@groups.route('/group/list', methods=['POST'])
@login_required
@check_permissions("group.list")
def get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.Group.query
    search = request.values.get("search")
    if search is not None:
        querying = querying.filter(models.Group.name.like(f"%{search}%"))
    pagination = querying.paginate(page=page, per_page=20)
    group = [{"id": i.id, "name": i.name} for i in pagination.items]
    data = {"groups": group, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@groups.route('/group/query', methods=['POST'])
@login_required
@check_permissions("group.query")
def query():
    id_ = request.values.get("id")
    if id_ is None:
        return jsonify(messages.DATA_NONE)
    group = models.Group.query.filter_by(id=id_).first()
    if group is None:
        return jsonify(messages.DATA_NONE)
    returns = {"data": {"id": group.id, "name": group.name, "permissions": group.permissions, "inherit": group.inherit}}
    returns.update(messages.OK)
    return jsonify(returns)
