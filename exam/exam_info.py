import utils
import messages
from exam import exam
from database import models, db
from flask import request, jsonify
from group import check_permissions
from sqlalchemy.orm import joinedload
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError


@exam.route('/exam/info/add', methods=['POST'])
@login_required
@check_permissions(2)
def add():
    sid = request.form.get("sid")
    session_id = request.form.get("session_id")
    subject_id = request.form.get("subject_id")
    if not (sid and session_id and subject_id):
        return jsonify(messages.DATA_NONE)
    if not utils.check_record_existence(models.Examsession, session_id):
        returns = messages.DOT_EXIST.copy()
        returns['message'] = f"session_id {returns['message']}"
        return jsonify(returns)
    if not utils.check_record_existence(models.Subject, subject_id):
        returns = messages.DOT_EXIST.copy()
        returns['message'] = f"subject_id {returns['message']}"
        return jsonify(returns)
    result = request.form.get("result")
    info = models.Examinfo(sid=sid, session_id=session_id, subject_id=subject_id, result=result)
    try:
        db.session.add(info)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@exam.route('/exam/info/edit', methods=['POST'])
@login_required
@check_permissions(2)
def edit():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    info = models.Examinfo.query.filter_by(id=id).first()
    if info is None:
        return jsonify(messages.NOT_FOUND)
    sid = request.form.get("sid")
    if sid is not None:
        if not utils.check_record_existence(models.User, sid=sid):
            return jsonify(messages.DOT_EXIST.copy(message=f"sid {messages.DOT_EXIST['message']}"))
        info.sid = sid
    session_id = request.form.get("session_id")
    if session_id is not None:
        if not utils.check_record_existence(models.Examsession, session_id):
            return jsonify(messages.DOT_EXIST.copy(message=f"session_id {messages.DOT_EXIST['message']}"))
        info.session_id = session_id
    subject_id = request.form.get("subject_id")
    if subject_id is not None:
        if not utils.check_record_existence(models.Examsession, subject_id):
            return jsonify(messages.DOT_EXIST.copy(message=f"subject_id {messages.DOT_EXIST['message']}"))
        info.subject_id = subject_id
    result = request.form.get("result")
    if result is not None:
        info.result = result
    try:
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@exam.route('/exam/info/delete', methods=['POST'])
@login_required
@check_permissions(2)
def delete():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    info = models.Examsession.query.filter_by(id=id).first()
    if info is None:
        return jsonify(messages.NOT_FOUND)
    try:
        db.session.delete(info)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@exam.route('/exam/info/list', methods=['GET', 'POST'])
@login_required
@check_permissions(2)
def get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.Examinfo.query.options(
        joinedload(models.Examsession), joinedload(models.Subject), joinedload(models.Student), joinedload(models.Clas),
        joinedload(models.College)).with_entities(
        models.Examinfo.id, models.Examsession.name, models.College.name.label('college_n'), models.Clas.grade,
        models.Clas.name.label("class_n"), models.Subject.name.label("subject_n"), models.Examinfo.sid,
        models.Student.name.label("student_n"), models.Student.sex)
    search_name = request.values.get("search_name")
    college_id = request.values.get("college_id")
    if college_id is not None:
        querying = querying.filter(models.College.id == college_id)
    class_id = request.values.get("class_id")
    if class_id is not None:
        querying = querying.filter(models.Clas.id == class_id)
    subject_id = request.values.get("subject_id")
    if subject_id is not None:
        querying = querying.filter(models.Subject.id == subject_id)
    sex = request.values.get("sex")
    if sex is not None:
        querying = querying.filter(models.Student.sex == sex)
    if search_name is not None:
        querying = querying.filter(models.Examinfo.sid.like(f"%{search_name}%"))
    search_sid = request.values.get("search_sid")
    if search_sid is not None:
        querying = querying.filter(models.Examinfo.sid.like(f"%{search_sid}%"))
    pagination = querying.paginate(page=page, per_page=20)
    infos = [
        {"id": i.id, "exam": i.name, "college": i.college_n, "grade": i.grade, "class": i.class_n, "subject": i.subject,
         "sid": i.sid, "student": i.student_n, "sex": i.sex} for i in pagination.items]
    returns = {"data": {"infos": infos, "total": pagination.total, "current": page, "maximum": pagination.pages}}
    returns.update(messages.OK)
    return jsonify(returns)
