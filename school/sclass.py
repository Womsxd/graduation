import messages
from school import school
from database import models, db
from flask import request, jsonify
from group import check_permissions
from flask_login import login_required


@school.route('/school/class/add', methods=['post'])
@login_required
@check_permissions(1)
def add():
    clas = models.Clas()
    clas.id = request.form.get('id')
    clas.name = request.form.get('name')
    clas.college = request.form.get('college')
    if clas.id is None or clas.name is None:
        return jsonify(messages.DATA_NONE)
    db.session.add(clas)
    db.session.commit()
    return jsonify(messages.OK)


@school.route('/school/class/edit', methods=['post'])
@login_required
@check_permissions(1)
def edit():
    cid = request.form.get('id')
    name = request.form.get('name')
    college = request.form.get('college')
    clas = models.Clas.query.filter_by(id=cid).first()
    if cid is None or clas is None:
        return jsonify(messages.DATA_NONE)
    if name is not None:
        clas.name = name
    if college is not None:
        clas.college = college
    db.session.commit()
    return jsonify(messages.OK)


@school.route('/school/class/delete', methods=['post'])
@login_required
@check_permissions(1)
def delete():
    cid = request.form.get('id')
    if cid is None:
        return jsonify(messages.DATA_NONE)
    models.Clas.query.filter_by(id=cid).delete()
    db.session.commit()
    return jsonify(messages.OK)


@school.route('/school/class/list', methods=['get', 'post'])
@login_required
@check_permissions(1)
def sclist():
    page = request.values.get("page", 1, type=int)
    pagination = models.Student.query.join(models.Clas).with_entities(
        models.Clas.id, models.Clas.name, models.College.name.label('college_n')
    ).paginate(page=page, per_page=20)
    classes = [{"id": i.id, "name": i.name, "college_name": i.college_n}
               for i in pagination.items]
    data = {"classes": classes, "total": pagination.total, "current": page, "maximum": pagination.pages}
    returns = {"data": data}
    returns.update(messages.OK)
    return jsonify(returns)
