import messages
from database import models, db
from group import check_permissions
from flask_login import login_required
from flask import request, jsonify, Blueprint

student = Blueprint('student', __name__)


@student.route('/student/add', methods=['post'])
@login_required
@check_permissions(1)
def add():
    stu = models.Student()
    stu.sid = request.form.get('sid')
    stu.name = request.form.get('name')
    stu.sex = request.form.get('sex')
    stu.class_ = request.form.get('class')
    if stu.sid is None and stu.name is None and stu.sex is None and stu.class_ is None:
        return jsonify(messages.DATA_NONE)
    db.session.add(stu)
    return jsonify(messages.OK)


@student.route('/student/edit', methods=['post'])
@login_required
@check_permissions(2)
def edit():
    sid = request.form.get('sid')
    name = request.form.get('name')
    sex = request.form.get('sex')
    class_ = request.form.get('class')
    stu = models.Student.query.filter_by(sid=sid).first()
    if sid is None or stu is None:
        return jsonify(messages.DATA_NONE)
    if name is not None:
        stu.name = name
    if sex is not None:
        stu.sex = sex
    if stu.class_ is not None:
        stu.class_ = class_
    db.session.commit()
    return jsonify(messages.OK)


@student.route('/student/delete', methods=['post'])
@login_required
@check_permissions(1)
def delete():
    sid = request.form.get('sid')
    if sid is None:
        return jsonify(messages.DATA_NONE)
    models.Student.query.filter_by(sid=sid).delete()
    db.session.commit()
    return jsonify(messages.OK)


@student.route('/student/list', methods=['get', 'post'])
@login_required
@check_permissions(2)
def slist():
    page = request.values.get("page", 1, type=int)
    pagination = models.Student.query.join(models.Clas).with_entities(
        models.Student.sid, models.Student.name, models.Student.sex, models.Clas.name.label('class_n')
        # 由于class表里面的name与student相同，这里就需要设置别名来防止冲突
    ).paginate(page=page, per_page=20)  # 这里连带查询了class表获取名称，做到一次查完全部 提升查询效率
    students = [{"sid": i.sid, "name": i.name, "sex": i.sex, "class": i.class_n} for i in pagination.items]
    data = {"students": students, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)


@student.route('/student/query', methods=['post'])
@login_required
@check_permissions(2)
def query():
    sid = request.form.get("sid")
    stu = models.Student.query.filter_by(sid=sid).first()
    if sid is None or stu is None:
        return jsonify(messages.DATA_NONE)
    return jsonify(
        {'code': 0, "message": "", "data": {"sid": stu.sid, "name": stu.name, "sex": stu.sex, "class": stu.class_id}})
