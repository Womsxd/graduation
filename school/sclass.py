from school import school
from database import models, db
from group import check_permissions
from flask import request, jsonify
from flask_login import login_required


@school.route('/school/class/add', methods=['post'])
@login_required
@check_permissions(1)
def add():
    clas = models.Clas()
    clas.id = request.form.get('id')
    clas.name = request.form.get('name')
    clas.id = request.form.get('college')
    if clas.id is None or clas.name is None:
        return jsonify({'code': 3, "message": "id/name Not equal to None"})
    db.session.add(clas)
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@school.route('/school/class/edit', methods=['post'])
@login_required
@check_permissions(1)
def edit():
    cid = request.form.get('id')
    name = request.form.get('name')
    college = request.form.get('college')
    clas = models.Clas.query.filter_by(id=cid).first()
    if cid is None or clas is None:
        return jsonify({'code': 3, "message": "id Not equal to None"})
    if name is not None:
        clas.name = name
    if college is not None:
        clas.college = college
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@school.route('/school/class/delete', methods=['post'])
@login_required
@check_permissions(1)
def delete():
    cid = request.form.get('id')
    if cid is None:
        return jsonify({'code': 3, "message": "id Not equal to None"})
    models.Clas.query.filter_by(id=cid).delete()
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@school.route('/school/class/list', methods=['get', 'post'])
@login_required
@check_permissions(1)
def ulist():
    page = int(request.values.get("page", 1))
    sclas = models.Clas.query.offset((page - 1) * 20).limit(20).all()
    total = models.Clas.query.count()
    maximum = int(total / 20) + 1
    data = []
    for i in sclas:
        data.append({"id": i.id, "name": i.account, "college": i.college})
    return jsonify(
        {'code': 0, "message": "", "data": {"users": data, "total": total, "current": page, "maximum": maximum}})
