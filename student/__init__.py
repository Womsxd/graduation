import utils
import messages
from database import models, db
from group import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from flask import request, jsonify, Blueprint

student = Blueprint('student', __name__)


@student.route('/student/add', methods=['POST'])
@login_required
@check_permissions("student.add")
def add():
    sid = request.form.get('sid')
    name = request.form.get('name')
    class_ = request.form.get('class')
    if not (sid and name):
        return jsonify(messages.DATA_NONE)
    try:
        sex = int(request.form.get('sex'))
    except ValueError:
        returns = messages.DOT_EXIST.copy()
        returns['message'] = f"sex {returns['message']}"
        return jsonify(returns)
    if not sex in utils.SexMap.number_map.keys():
        returns = messages.DOT_EXIST.copy()
        returns['message'] = f"sex {returns['message']}"
        return jsonify(returns)
    if not utils.check_record_existence(models.Clas, class_):
        returns = messages.DOT_EXIST.copy()
        returns['message'] = f"class {returns['message']}"
        return jsonify(returns)
    stu = models.Student(sid=sid, name=name, sex=sex, class_id=int(class_))
    try:
        db.session.add(stu)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@student.route('/student/edit', methods=['POST'])
@login_required
@check_permissions("student.edit")
def edit():
    id_ = request.form.get('id')
    if id_ is None:
        return jsonify(messages.DATA_NONE)
    stu = models.Student.query.filter_by(id=id_).first()
    if stu is None:
        return jsonify(messages.NOT_FOUND)
    sid = request.form.get('sid')
    name = request.form.get('name')
    sex = request.form.get('sex')
    class_ = request.form.get('class')
    if sid is not None:
        stu.sid = sid  # 让学号也可修改，防止学号输入错误无法修改
    if name is not None:
        stu.name = name
    if sex is not None:
        try:
            sex = int(sex)
        except ValueError:
            returns = messages.DOT_EXIST.copy()
            returns['message'] = f"sex {returns['message']}"
            return jsonify(returns)
        if not sex in utils.SexMap.number_map.keys():
            returns = messages.DOT_EXIST.copy()
            returns['message'] = f"sex {returns['message']}"
            return jsonify(returns)
    if stu.class_id is not None:
        """
        if not utils.check_record_existence(models.Clas, class_):
            returns = messages.DOT_EXIST.copy()
            returns['message'] = f"class {returns['message']}"
            return jsonify(returns)
        """
        if utils.check_record_existence(models.Clas, class_):
            stu.class_id = int(class_)
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@student.route('/student/delete', methods=['POST'])
@login_required
@check_permissions("student.delete")
def delete():
    sid = request.form.get('sid')
    if sid is None:
        return jsonify(messages.DATA_NONE)
    stu = models.Student.query.filter_by(sid=sid).first()
    if not stu:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@student.route('/student/list', methods=['GET', 'POST'])
@login_required
@check_permissions("student.list")
def get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.Student.query.join(models.Clas).join(models.College).with_entities(
        models.Student.id, models.Student.sid, models.Student.name, models.Student.sex, models.Student.class_id,
        models.Clas.name.label('class_n'), models.College.name.label('college_n'))
    search = request.values.get("search")
    if search is not None:
        querying = querying.filter(models.Student.name.like(f"%{search}%"))
    sex = request.values.get("sex")
    if sex is not None:
        querying = querying.filter_by(sex=sex)
    class_id = request.values.get("class_id")
    if class_id is not None:
        querying = querying.filter_by(class_id=class_id)
    pagination = querying.paginate(page=page, per_page=20)
    to = utils.SexMap()
    students = [{"id": i.id, "sid": i.sid, "name": i.name, "sex": to.to_string(i.sex),
                 "class": i.class_n} for i in pagination.items]
    data = {"students": students, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@student.route('/student/query', methods=['POST'])
@login_required
@check_permissions("student.query")
def query():
    sid = request.form.get("sid")
    if sid is None:
        return jsonify(messages.DATA_NONE)
    stu = models.Student.query.join(models.Clas).with_entities(
        models.Student.id, models.Student.sid, models.Student.name, models.Student.sex,
        models.Clas.name.label('class_n')).filter_by(sid=sid).first()
    if stu is None:
        return jsonify(messages.DATA_NONE)
    to = utils.SexMap()
    returns = {"data": {"id": stu.id, "sid": stu.sid, "name": stu.name, "sex": to.to_string(stu.sex),
                        "class": stu.class_n}}
    returns.update(messages.OK)
    return jsonify(returns)


@student.route('/student/import_xls', methods=['POST'])
@login_required
@check_permissions("student.import_xls")
def import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = utils.load_xls_file(file.read(), "学生")
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["学号", "姓名", "性别", "班级"] != result[0][:4]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    error_lens = []
    error_students = []
    try:
        with db.session.begin(nested=True):
            class_cache = {}
            student_adds = []
            for i in result[1:]:
                if "" in i[:2]:
                    error_lens.append(result.index(i) + 1)
                    continue
                if i[0] in [stu.sid for stu in student_adds]:
                    continue
                if i[0] in error_students or models.User.query.filter_by(account=i[0]).first() is not None:
                    if i[0] not in error_students:
                        error_students.append(i[0])
                    continue
                class_id = None
                if i[3] != "":
                    if i[3] in class_cache.keys():
                        class_id = class_cache[i[3]]
                    else:
                        class_ = models.Clas.query.filter_by(name=i[3]).first()
                        if class_ is not None:
                            class_id = class_.id
                    class_cache[i[3]] = class_id
                sex = None
                if i[2] != "":
                    if not utils.is_number(i[2]):
                        to = utils.SexMap()
                        sex = to.to_number(i[2])
                    else:
                        if i[2] in utils.SexMap.number_map.keys():
                            sex = i[2]
                student_adds.append(models.Student(sid=i[0], name=i[1], sex=sex, class_id=class_id))
            returns = {"data": {"ok": len(student_adds), "error": len(error_lens) + len(error_students),
                                "error_lens": error_lens, "error_students": error_students}}
            db.session.bulk_save_objects(student_adds)
        returns.update(messages.OK)
        return jsonify(returns)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
