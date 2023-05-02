import utils
import messages
from . import school
from database import models, db
from flask import request, jsonify
from group import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

WHITE_LIST = [1]


@school.route('/school/class/add', methods=['POST'])
@login_required
@check_permissions("school.class.add")
def class_add():
    name = request.form.get('name')
    if name is None:
        return jsonify(messages.DATA_NONE)
    college = request.form.get('college')
    grade = request.form.get("grade")
    if college is not None:
        if not utils.check_record_existence(models.College, college):
            returns = messages.DOT_EXIST.copy()
            returns['message'] = f"college {returns['message']}"
            return jsonify(returns)
    class_ = models.Clas(name=name, college_id=college, grade=grade)
    try:
        db.session.add(class_)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/edit', methods=['POST'])
@login_required
@check_permissions("school.class.edit")
def class_edit():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    if id in WHITE_LIST:
        return jsonify(messages.NOT_DELETE)
    class_ = models.Clas.query.filter_by(id=id).first()
    if class_ is None:
        return jsonify(messages.NOT_FOUND)
    name = request.form.get('name')
    if name is not None:
        class_.name = name
    college = request.form.get('college')
    if college is not None:
        if not utils.check_record_existence(models.College, college):
            returns = messages.DOT_EXIST.copy()
            returns['message'] = f"college {returns['message']}"
            return jsonify(returns)
    grade = request.form.get("grade")
    if grade is None:
        class_.grade = grade
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/delete', methods=['POST'])
@login_required
@check_permissions("school.class.delete")
def class_delete():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    if id in WHITE_LIST:
        return jsonify(messages.NOT_DELETE)
    class_ = models.Clas.query.filter_by(id=id).first()
    if class_ is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(class_)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/grades', methods=['GET', 'POST'])
@login_required
@check_permissions("school.class.grades")
def class_get_grades():
    page = request.values.get("page", 1, type=int)
    pagination = db.session.query(models.Clas.grade).distinct().paginate(page=page, per_page=20)
    data = {"grades": pagination.items, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@school.route('/school/class/list', methods=['GET', 'POST'])
@login_required
@check_permissions("school.class.list")
def class_get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.Student.query.join(models.Clas).with_entities(
        models.Clas.id, models.Clas.name, models.Clas.grade, models.College.name.label('college_n')
    )
    search = request.values.get("search")
    if search is not None:
        querying = querying.filter(models.College.name.like(f"%{search}%"))
    college_id = request.values.get("college_id")
    if college_id is not None:
        querying = querying.filter_by(college_id=college_id)
    grade = request.form.get("grade")
    if grade is None:
        querying = querying.filter_by(grade=grade)
    pagination = querying.paginate(page=page, per_page=20)
    classes = [{"id": i.id, "name": i.name, "grade": i.grade, "college_name": i.college_n}
               for i in pagination.items]
    data = {"classes": classes, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@school.route('/school/class/query', methods=['GET', 'POST'])
@login_required
@check_permissions("school.class.query")
def get_query():
    cid = request.values.get("id")
    if cid is None:
        return jsonify(messages.DATA_NONE)
    class_ = models.Clas.query.join(models.College).with_entities(
        models.Clas.id, models.Clas.name, models.Clas.grade, models.College.name.label("college_n")
    ).filter_by(id=cid).first()
    if class_ is None:
        return jsonify(messages.DATA_NONE)
    returns = {"data": {"id": class_.id, "name": class_.name, "grade": class_.grade, "college": class_.college_n}}
    returns.update(messages.OK)
    return jsonify(returns)


@school.route('/school/class/import_xls', methods=['POST'])
@login_required
@check_permissions("school.class.import_xls")
def get_import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = utils.load_xls_file(file.read(), "班级")
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["学院", "年级", "班级名称"] != result[0][:3]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    try:
        with db.session.begin(nested=True):
            college_cache = {}
            class_adds = []
            for i in result[1:]:
                if [2] == "":  # 没有班级名称直接跳过了，没学院和年级还有默认兜底，没班级名字直接pass
                    continue
                college_id = None
                grade = None
                if i[0]:
                    if i[0] not in college_cache.keys():
                        college = models.College.query.filter_by(name=i[1]).first()
                        if college:
                            college_id = college.id
                        college_cache[i[0]] = college_id
                    else:
                        college_id = college_cache[i[0]]
                if i[1]:
                    grade = i[1]
                class_adds.append(models.Clas(name=i[2], collede_id=college_id, grade=grade))
            db.session.bulk_save_objects(class_adds)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
