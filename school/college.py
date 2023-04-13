from school import school
from database import models, db
from group import check_permissions
from flask import request, jsonify
from flask_login import login_required


@school.route('/school/college/add', methods=['post'])
@login_required
@check_permissions(1)
def add():
    cid = request.form.get('id')
    name = request.form.get('name')
    if cid is None and name is None:
        return jsonify({'code': 3, "message": "id/name Not equal to None"})
    college = models.College()
    college.id = cid
    college.name = name
    db.session.add(college)
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@school.route('/school/college/edit', methods=['post'])
@login_required
@check_permissions(1)
def edit():
    cid = request.form.get('id')
    name = request.form.get('name')
    college = models.College.query.filter_by(id=cid).first()
    if cid is None or college is None:
        return jsonify({'code': 3, "message": "id Not equal to None"})
    if name is not None:
        college.name = name
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@school.route('/school/college/delete', methods=['post'])
@login_required
@check_permissions(1)
def delete():
    cid = request.form.get('id')
    if cid is None:
        return jsonify({'code': 3, "message": "id Not equal to None"})
    models.College.query.filter_by(id=cid).delete()
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@school.route('/school/college/list', methods=['get', 'post'])
@login_required
@check_permissions(1)
def ulist():
    page = int(request.values.get("page", 1))
    colleges = models.College.query.offset((page - 1) * 20).limit(20).all()
    total = models.College.query.count()
    maximum = int(total / 20) + 1
    data = []
    for i in colleges:
        data.append({"id": i.id, "name": i.account})
    return jsonify(
        {'code': 0, "message": "", "data": {"users": data, "total": total, "current": page, "maximum": maximum}})
