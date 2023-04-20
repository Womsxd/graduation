import messages
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
        return jsonify(messages.DATA_NONE)
    college = models.College()
    college.id = cid
    college.name = name
    db.session.add(college)
    db.session.commit()
    return jsonify(messages.OK)


@school.route('/school/college/edit', methods=['post'])
@login_required
@check_permissions(1)
def edit():
    cid = request.form.get('id')
    name = request.form.get('name')
    college = models.College.query.filter_by(id=cid).first()
    if cid is None or college is None:
        return jsonify(messages.DATA_NONE)
    if name is not None:
        college.name = name
    db.session.commit()
    return jsonify(messages.OK)


@school.route('/school/college/delete', methods=['post'])
@login_required
@check_permissions(1)
def delete():
    cid = request.form.get('id')
    if cid is None:
        return jsonify(messages.DATA_NONE)
    models.College.query.filter_by(id=cid).delete()
    db.session.commit()
    return jsonify(messages.OK)


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
        data.append({"id": i.id, "name": i.name})
    rej = {}
    rej.update(messages.OK_DATA)
    rej["data"] = {"college": data, "total": total, "current": page, "maximum": maximum}
    return jsonify(rej)
