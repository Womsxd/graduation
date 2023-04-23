import messages
from school import school
from database import models, db
from flask import request, jsonify
from group import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError


@school.route('/school/college/add', methods=['POST'])
@login_required
@check_permissions(1)
def add():
    cid = request.form.get('id')
    name = request.form.get('name')
    if not (cid and name):
        return jsonify(messages.DATA_NONE)
    college = models.College()
    college.id = cid
    college.name = name
    try:
        with db.session.begin():
            db.session.add(college)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/college/edit', methods=['POST'])
@login_required
@check_permissions(1)
def edit():
    cid = request.form.get('id')
    if cid is None:
        return jsonify(messages.DATA_NONE)
    college = models.College.query.filter_by(id=cid).first()
    if college is None:
        return jsonify(messages.NOT_FOUND)
    name = request.form.get('name')
    if name is not None:
        college.name = name
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/college/delete', methods=['POST'])
@login_required
@check_permissions(1)
def delete():
    cid = request.form.get('id')
    if cid is None:
        return jsonify(messages.DATA_NONE)
    college = models.College.query.filter_by(id=cid).first()
    if college is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(college)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/college/list', methods=['GET', 'POST'])
@login_required
@check_permissions(1)
def sclist():
    page = request.values.get("page", 1, type=int)
    pagination = models.College.query.paginate(page=page, per_page=20)
    colleges = [{"id": i.id, "name": i.account} for i in pagination.items]
    data = {"colleges": colleges, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)
