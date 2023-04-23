import messages
from exam import exam
from database import models, db
from flask import request, jsonify
from group import check_permissions
from flask_login import login_required


@exam.route('/exam/session/add', methods=['POST'])
@login_required
@check_permissions(1)
def add():
    esession = models.Examsession()
    esession.id = request.form.get('id')
    esession.name = request.form.get('name')
    if esession.id is None or esession.name is None:
        return jsonify(messages.DATA_NONE)
    db.session.add(esession)
    db.session.commit()
    return jsonify(messages.OK)


@exam.route('/exam/session/edit', methods=['POST'])
@login_required
@check_permissions(1)
def edit():
    id = request.form.get('id')
    name = request.form.get('name')
    esession = models.Examsession.query.filter_by(id=id).first()
    if id is None or esession is None:
        return jsonify(messages.DATA_NONE)
    if name is not None:
        esession.name = name
    db.session.commit()
    return jsonify(messages.OK)


@exam.route('/exam/session/delete', methods=['POST'])
@login_required
@check_permissions(1)
def delete():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    models.Examsession.query.filter_by(id=id).delete()
    db.session.commit()
    return jsonify(messages.OK)


@exam.route('/exam/session/list', methods=['GET', 'POST'])
@login_required
@check_permissions(1)
def ulist():
    page = int(request.values.get("page", 1))
    sesession = models.Examsession.query.offset((page - 1) * 20).limit(20).all()
    total = models.Examsession.query.count()
    maximum = int(total / 20) + 1
    data = []
    for i in sesession:
        data.append({"id": i.id, "name": i.account, "college": i.college})
    return jsonify(
        {'code': 0, "message": "", "data": {"users": data, "total": total, "current": page, "maximum": maximum}})
