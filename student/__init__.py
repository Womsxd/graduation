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
    print(db.session.commit())
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
def ulist():
    page = int(request.values.get("page", 1))
    students = models.Student.query.offset((page - 1) * 20).limit(20).all()
    total = models.Student.query.count()
    maximum = int(total / 20) + 1
    data = []
    for i in students:
        data.append({"id": i.id,"sid": i.sid, "name": i.name,"class":i.class_})
    return jsonify(
        {'code': 0, "message": "", "data": {"users": data, "total": total, "current": page, "maximum": maximum}})

@student.route('/student/query', methods=['post'])
@login_required
@check_permissions(2)
def query():
    sid = request.form.get("sid")
    stu = models.Student.query.filter_by(sid=sid).first()
    if sid is None or stu is None:
        return jsonify(messages.DATA_NONE)
    return jsonify({'code': 0, "message": "", "data": {"sid": stu.sid, "name": stu.name, "sex": stu.sex, "class": stu.class_}})
