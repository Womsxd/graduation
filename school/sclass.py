import messages
from school import school
from database import models, db
from flask import request, jsonify
from group import check_permissions
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError


@school.route('/school/class/add', methods=['POST'])
@login_required
@check_permissions(1)
def add():
    id_ = request.form.get('id')
    name = request.form.get('name')
    college = request.form.get('college')
    if not (id_ and name and college):
        return jsonify(messages.DATA_NONE)
    class_ = models.Clas()
    class_.id = id_
    class_.name = name
    class_.college = college
    try:
        with db.session.begin(nested=True):
            db.session.add(class_)
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/edit', methods=['POST'])
@login_required
@check_permissions(1)
def edit():
    cid = request.form.get('id')
    if cid is None:
        return jsonify(messages.DATA_NONE)
    class_ = models.Clas.query.filter_by(id=cid).first()
    if class_ is None:
        return jsonify(messages.NOT_FOUND)
    name = request.form.get('name')
    college = request.form.get('college')
    if name is not None:
        class_.name = name
    if college is not None:
        class_.college = college
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/delete', methods=['POST'])
@login_required
@check_permissions(1)
def delete():
    cid = request.form.get('id')
    if cid is None:
        return jsonify(messages.DATA_NONE)
    class_ = models.Clas.query.filter_by(id=cid).first()
    if class_ is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(class_)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@school.route('/school/class/list', methods=['GET', 'POST'])
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
