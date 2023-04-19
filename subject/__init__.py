from database import models, db
from group import check_permissions
from flask import request, jsonify, Blueprint
from flask_login import login_required

subject = Blueprint('subject', __name__)


@subject.route('/subject/add', methods=['post'])
@login_required
@check_permissions(1)
def add():
    subj = models.Subject()
    subj.id_ = request.form.get('id')
    subj.name = request.form.get('name')
    if subj.sid is None and subj.name is None:
        return jsonify({'code': 3, "message": "data Not equal to None"})
    db.session.add(subj)
    print(db.session.commit())
    return jsonify({'code': 0, "message": ""})


@subject.route('/subject/edit', methods=['post'])
@login_required
@check_permissions(2)
def edit():
    id_ = request.form.get('id')
    name = request.form.get('name')
    subj = models.Subject.query.filter_by(id=id_).first()
    if id_ is None or subj is None:
        return jsonify({'code': 3, "message": "id Not equal to None"})
    if name is not None:
        subj.name = name
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@subject.route('/subject/delete', methods=['post'])
@login_required
@check_permissions(1)
def delete():
    id_ = request.form.get('id')
    if id_ is None:
        return jsonify({'code': 3, "message": "sid Not equal to None"})
    models.Subject.query.filter_by(id=id_).delete()
    db.session.commit()
    return jsonify({'code': 0, "message": ""})


@subject.route('/subject/list', methods=['get', 'post'])
@login_required
@check_permissions(2)
def ulist():
    page = int(request.values.get("page", 1))
    subjects = models.Subject.query.offset((page - 1) * 20).limit(20).all()
    total = models.Subject.query.count()
    maximum = int(total / 20) + 1
    data = []
    for i in subjects:
        data.append({"id": i.id, "name": i.account})
    return jsonify(
        {'code': 0, "message": "", "data": {"users": data, "total": total, "current": page, "maximum": maximum}})
