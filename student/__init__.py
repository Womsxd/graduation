from database import models, db
from group import check_permissions
from flask import request, jsonify, Blueprint
from flask_login import login_required

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
        return jsonify({'code': 3, "message": "data Not equal to None"})
    db.session.add(stu)
    print(db.session.commit())
    return jsonify({'code': 0, "message": ""})
