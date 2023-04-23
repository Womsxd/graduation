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
@check_permissions(1)
def add():
    sid = request.form.get('sid')
    name = request.form.get('name')
    sex = request.form.get('sex')
    class_ = request.form.get('class')
    if not (sid and name and sex and class_):
        return jsonify(messages.DATA_NONE)
    stu = models.Student()
    stu.sid = sid
    stu.name = name
    stu.sex = sex
    stu.class_ = class_
    try:
        with db.session.begin():
            db.session.add(stu)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@student.route('/student/edit', methods=['POST'])
@login_required
@check_permissions(2)
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
        stu.sex = sex
    if stu.class_ is not None:
        stu.class_ = class_
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@student.route('/student/delete', methods=['POST'])
@login_required
@check_permissions(1)
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
@check_permissions(2)
def slist():
    page = request.values.get("page", 1, type=int)
    pagination = models.Student.query.join(models.Clas).with_entities(
        models.Student.sid, models.Student.name, models.Student.sex, models.Clas.name.label('class_n')
        # 由于class表里面的name与student相同，这里就需要设置别名来防止冲突
    ).paginate(page=page, per_page=20)  # 这里连带查询了class表获取名称，做到一次查完全部 提升查询效率
    students = [{"id": i.id, "sid": i.sid, "name": i.name, "sex": utils.SexEnum(i.sex).value,
                 "class": i.class_n} for i in pagination.items]
    data = {"students": students, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@student.route('/student/query', methods=['POST'])
@login_required
@check_permissions(2)
def query():
    sid = request.form.get("sid")  # 防止某些学校奇奇怪怪的带字母的学号规则
    if sid is None:
        return jsonify(messages.DATA_NONE)
    stu = models.Student.query.join(models.Clas).with_entities(
        models.Student.id, models.Student.sid, models.Student.name, models.Student.sex,
        models.Clas.name.label('class_n')
    ).filter_by(sid=sid).first()
    if stu is None:
        return jsonify(messages.DATA_NONE)
    return jsonify(
        {'code': 0, "message": "",
         "data": {"id": stu.id, "sid": stu.sid, "name": stu.name, "sex": utils.SexEnum(stu.sex).value,
                  "class": stu.class_n}})
