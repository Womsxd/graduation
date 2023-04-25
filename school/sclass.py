import utils
import messages
from . import school
from database import models, db
from flask import request, jsonify
from group import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError


@school.route('/school/class/add', methods=['POST'])
@login_required
@check_permissions(1)
def add():
    cid = request.form.get('id')
    name = request.form.get('name')
    college = request.form.get('college')
    if not (cid and name and college):
        return jsonify(messages.DATA_NONE)
    class_ = models.Clas()
    class_.id = cid
    class_.name = name
    class_.college = college
    try:
        with db.session.begin(nested=True):
            db.session.add(class_)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/edit', methods=['POST'])
@login_required
@check_permissions(1)
def edit():
    cid = request.form.get('id')
    if cid is None:
        return jsonify(messages.DATA_NONE)
    class_ = models.Clas.query.filter_by(id=cid).first()
    if class_ is None:
        return jsonify(messages.NOT_FOUND)
    name = request.form.get('name')
    college = request.form.get('college')
    if name is not None:
        class_.name = name
    if college is not None:
        class_.college = college
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/delete', methods=['POST'])
@login_required
@check_permissions(1)
def delete():
    cid = request.form.get('id')
    if cid is None:
        return jsonify(messages.DATA_NONE)
    class_ = models.Clas.query.filter_by(id=cid).first()
    if class_ is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(class_)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/list', methods=['GET', 'POST'])
@login_required
@check_permissions(1)
def get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.Student.query.join(models.Clas).with_entities(
        models.Clas.id, models.Clas.name, models.College.name.label('college_n')
    )
    search = request.values.get("search")
    if search is not None:
        querying = querying.filter(models.College.name.like(f"%{search}%"))
    college_id = request.values.get("college_id")
    if college_id is not None:
        querying = querying.filter_by(college_id=college_id)
    pagination = querying.paginate(page=page, per_page=20)
    classes = [{"id": i.id, "name": i.name, "college_name": i.college_n}
               for i in pagination.items]
    data = {"classes": classes, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@school.route('/school/class/query', methods=['GET', 'POST'])
@login_required
@check_permissions(2)
def query():
    cid = request.values.get("id")
    if cid is None:
        return jsonify(messages.DATA_NONE)
    class_ = models.Clas.query.join(models.College).with_entities(
        models.Clas.id, models.Clas.name, models.College.name.label("college_n")
    ).filter_by(id=cid).first()
    if class_ is None:
        return jsonify(messages.DATA_NONE)
    returns = {"data": {"id": class_.id, "name": class_.name, "college": class_.college_n}}
    returns.update(messages.OK)
    return jsonify(returns)


@school.route('/school/class/import_xls', methods=['POST'])
@login_required
@check_permissions(1)
def import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = utils.load_xls_file(file.read(), "班级")
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["班级名称", "所属学院"] != result[0][:2]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    try:
        with db.session.begin(nested=True):
            college_cache = {}
            for i in result[1:]:
                college_id = 1  # 默认学院id
                if i[1]:
                    if i[1] not in college_cache.keys():
                        college = models.College.query.filter_by(name=i[1]).first()
                        if college:
                            college_id = college.id
                        college_cache[i[1]] = college_id
                    else:
                        college_id = college_cache[i[1]]
                class_ = models.Clas(name=i[0], collede_id=college_id)
                db.session.add(class_)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
