import utils
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
    esession = models.Examsession(id=id_, name=name)
    try:
        with db.session.begin(nested=True):
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
        return jsonify(messages.NOT_FOUND)
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
def get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.Examsession.query
    search = request.values.get("search")
    if search is not None:
        querying = querying.filter(models.Examsession.name.like(f"%{search}%"))
    pagination = querying.paginate(page=page, per_page=20)
    sessions = [{"id": i.id, "name": i.name} for i in pagination.items]
    data = {"sessions": sessions, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@exam.route('/exam/session/query', methods=['GET', 'POST'])
@login_required
@check_permissions(2)
def query():
    id_ = request.values.get("id")
    if id_ is None:
        return jsonify(messages.DATA_NONE)
    esession = models.Examsession.query.filter_by(id=id_).first()
    if esession is None:
        return jsonify(messages.DATA_NONE)
    returns = {"data": {"id": esession.id, "name": esession.name}}
    returns.update(messages.OK)
    return jsonify(returns)


@exam.route('/exam/session/import_xls', methods=['POST'])
@login_required
@check_permissions(1)
def import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = utils.load_xls_file(file.read(), "考试信息")
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["考试信息"] != result[0][:1]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    try:
        with db.session.begin(nested=True):
            for i in result[1:]:
                esession = models.Examsession(name=i[0])
                db.session.add(esession)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
