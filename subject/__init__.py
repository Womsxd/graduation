import messages
from database import models, db
from group import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from flask import request, jsonify, Blueprint

subject = Blueprint('subject', __name__)


@subject.route('/subject/add', methods=['POST'])
@login_required
@check_permissions(1)
def add():

    id_ = request.form.get('id')
    name = request.form.get('name')
    if not (id_ and name):
        return jsonify(messages.DATA_NONE)
    subj = models.Subject()
    subj.id_ = id_
    subj.name = name
    try:
        with db.session.begin():
            db.session.add(subj)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@subject.route('/subject/edit', methods=['POST'])
@login_required
@check_permissions(2)
def edit():
    id_ = request.form.get('id')
    name = request.form.get('name')
    if id_ is None:
        return jsonify(messages.DATA_NONE)
    subj = models.Subject.query.filter_by(id=id_).first()
    if subj is None:
        return jsonify(messages.DATABASE_ERROR)
    if name is not None:
        subj.name = name
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@subject.route('/subject/delete', methods=['POST'])
@login_required
@check_permissions(1)
def delete():
    id_ = request.form.get('id')
    if id_ is None:
        return jsonify(messages.DATA_NONE)
    subj = models.Subject.query.filter_by(id=id_).first()
    if subj is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(subj)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@subject.route('/subject/list', methods=['GET', 'POST'])
@login_required
@check_permissions(2)
def slist():
    page = request.values.get("page", 1, type=int)
    pagination = models.Subject.query.paginate(page=page, per_page=20)
    subjects = [{"id": i.id, "name": i.account} for i in pagination.items]
    data = {"subjects": subjects, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)
