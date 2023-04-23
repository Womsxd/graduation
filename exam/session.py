import messages
from exam import exam
from database import models, db
from flask import request, jsonify
from group import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError


@exam.route('/exam/session/add', methods=['POST'])
@login_required
@check_permissions(1)
def add():
    id_ = request.form.get('id')
    name = request.form.get('name')
    if not (id_ and name):
        return jsonify(messages.DATA_NONE)
    esession = models.Examsession()
    esession.id = id_
    esession.name = name
    try:
        with db.session.begin():
            db.session.add(esession)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@exam.route('/exam/session/edit', methods=['POST'])
@login_required
@check_permissions(1)
def edit():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    esession = models.Examsession.query.filter_by(id=id).first()
    if esession is None:
        return jsonify(messages.DATA_NONE)
    name = request.form.get('name')
    if name is not None:
        esession.name = name
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@exam.route('/exam/session/delete', methods=['POST'])
@login_required
@check_permissions(1)
def delete():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    esession = models.Examsession.query.filter_by(id=id).first()
    if esession is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(esession)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@exam.route('/exam/session/list', methods=['GET', 'POST'])
@login_required
@check_permissions(1)
def ulist():
    page = request.values.get("page", 1, type=int)
    pagination = models.Examsession.query.paginate(page=page, per_page=20)
    sessions = [{"id": i.id, "name": i.name} for i in pagination.items]
    data = {"sessions": sessions, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)
