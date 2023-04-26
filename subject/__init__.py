import utils
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
    name = request.form.get('name')
    if name is None:
        return jsonify(messages.DATA_NONE)
    subj = models.Subject(name=name)
    try:
        db.session.add(subj)
        db.session.commit()
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
        return jsonify(messages.NOT_FOUND)
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
def get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.Subject.query
    search = request.values.get("search")
    if search is not None:
        querying = querying.filter(models.Subject.name.like(f"%{search}%"))
    pagination = querying.paginate(page=page, per_page=20)
    subjects = [{"id": i.id, "name": i.name} for i in pagination.items]
    data = {"subjects": subjects, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@subject.route('/subject/query', methods=['GET', 'POST'])
@login_required
@check_permissions(2)
def query():
    id_ = request.values.get("id")
    if id_ is None:
        return jsonify(messages.DATA_NONE)
    subj = models.Subject.query.filter_by(id=id_).first()
    if subj is None:
        return jsonify(messages.DATA_NONE)
    returns = {"data": {"id": subj.id, "name": subj.name}}
    returns.update(messages.OK)
    return jsonify(returns)


@subject.route('/subject/import_xls', methods=['POST'])
@login_required
@check_permissions(1)
def import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = utils.load_xls_file(file.read(), "科目")
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["科目名称"] != result[0][:1]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    try:
        with db.session.begin(nested=True):
            subject_adds = []
            for i in result[1:]:
                subject_adds.append(models.Subject(name=i[0]))
            db.session.bulk_save_objects(subject_adds)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
