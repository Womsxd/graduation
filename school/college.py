import utils
import messages
from . import school
from database import models, db
from flask import request, jsonify
from group import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

WHITE_LIST = [1]


@school.route('/school/college/add', methods=['POST'])
@login_required
@check_permissions("school.college.add")
def add():
    name = request.form.get('name')
    if name is None:
        return jsonify(messages.DATA_NONE)
    college = models.College(name=name)
    try:
        db.session.add(college)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/college/edit', methods=['POST'])
@login_required
@check_permissions("school.college.edit")
def edit():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    if id in WHITE_LIST:
        return jsonify(messages.NOT_DELETE)
    college = models.College.query.filter_by(id=id).first()
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
@check_permissions("school.college.delete")
def delete():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    if id in WHITE_LIST:
        return jsonify(messages.NOT_DELETE)
    college = models.College.query.filter_by(id=id).first()
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
@check_permissions("school.college.list")
def get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.College.query
    search = request.values.get("search")
    if search is not None:
        querying = querying.filter(models.College.name.like(f"%{search}%"))
    pagination = querying.paginate(page=page, per_page=20)
    colleges = [{"id": i.id, "name": i.account} for i in pagination.items]
    data = {"colleges": colleges, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@school.route('/school/college/query', methods=['GET', 'POST'])
@login_required
@check_permissions("school.college.query")
def query():
    cid = request.values.get("id")
    if cid is None:
        return jsonify(messages.DATA_NONE)
    college = models.College.query.filter_by(id=cid).first()
    if college is None:
        return jsonify(messages.DATA_NONE)
    returns = {"data": {"id": college.id, "name": college.name}}
    returns.update(messages.OK)
    return jsonify(returns)


@school.route('/school/college/import_xls', methods=['POST'])
@login_required
@check_permissions("school.college.import_xls")
def import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = [i for i in utils.load_xls_file(file.read(), "学院") if i != ""]
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["学院名称"] != result[0][:1]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    try:
        with db.session.begin(nested=True):
            college_adds = []
            for i in result[1:]:
                college_adds.append(models.College(name=i[0]))
            db.session.bulk_save_objects(college_adds)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
