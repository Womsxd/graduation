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
@check_permissions("exam.info.add")
def info_add():
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
    info = models.Examinfo(sid=sid, sessions_id=int(session_id), subject_id=subject_id, result=result)
    try:
        db.session.add(info)
        db.session.commit()
        return jsonify(messages.OK)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)


@exam.route('/exam/info/edit', methods=['POST'])
@login_required
@check_permissions("exam.info.edit")
def info_edit():
    id = request.form.get('id')
    if id is None:
        return jsonify(messages.DATA_NONE)
    info = models.Examinfo.query.filter_by(id=id).first()
    if info is None:
        return jsonify(messages.NOT_FOUND)
    sid = request.form.get("sid")
    if sid is not None:
        if not utils.check_record_existence(models.Student, sid=sid):
            return jsonify(messages.DOT_EXIST.copy(message=f"sid {messages.DOT_EXIST['message']}"))
        info.sid = sid
    session_id = request.form.get("session_id")
    if session_id is not None:
        """
        if not utils.check_record_existence(models.Examsession, session_id):
            return jsonify(messages.DOT_EXIST.copy(message=f"session_id {messages.DOT_EXIST['message']}"))
        """
        if utils.check_record_existence(models.Examsession, session_id):
            info.session_id = session_id
    subject_id = request.form.get("subject_id")
    if subject_id is not None:
        """
        if not utils.check_record_existence(models.Examsession, subject_id):
            return jsonify(messages.DOT_EXIST.copy(message=f"subject_id {messages.DOT_EXIST['message']}"))
        """
        if utils.check_record_existence(models.Examsession, subject_id):
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
@check_permissions("exam.info.delete")
def info_delete():
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
@check_permissions("exam.info.list")
def info_get_list():
    page = request.values.get("page", 1, type=int)
    querying = models.Examinfo.query.join(models.Examsession).join(models.Subject).join(models.Student). \
        join(models.Clas).join(models.College).with_entities(
        models.Examinfo.id, models.Examsession.name, models.College.name.label('college_n'), models.Clas.grade,
        models.Clas.name.label("class_n"), models.Subject.name.label("subject_n"), models.Examinfo.sid,
        models.Student.name.label("student_n"), models.Student.sex, models.Examinfo.result)
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
        {"id": i.id, "exam": i.name, "college": i.college_n, "grade": i.grade, "class": i.class_n,
         "subject": i.subject_n, "sid": i.sid, "student": i.student_n, "sex": i.sex, "result": i.result} for i in
        pagination.items]
    returns = {"data": {"infos": infos, "total": pagination.total, "current": page, "maximum": pagination.pages}}
    returns.update(messages.OK)
    return jsonify(returns)


@exam.route('/exam/info/query', methods=['GET', 'POST'])
@login_required
@check_permissions("exam.info.query")
def info_query():
    id_ = request.values.get("id")
    if id_ is None:
        return jsonify(messages.DATA_NONE)
    info = models.Examinfo.query.options(
        joinedload(models.Examsession), joinedload(models.Subject),
        joinedload(models.Student).selectinload(models.Clas).selectinload(models.College)).with_entities(
        models.Examinfo.id, models.Examsession.name, models.College.name.label('college_n'), models.Clas.grade,
        models.Clas.name.label("class_n"), models.Subject.name.label("subject_n"), models.Examinfo.sid,
        models.Student.name.label("student_n"), models.Student.sex).first()
    if info is None:
        return jsonify(messages.DATA_NONE)
    returns = {"data": {"id": info.id, "exam": info.name, "college": info.college_n, "grade": info.grade,
                        "class": info.class_n, "subject": info.subject, "sid": info.sid, "student": info.student_n,
                        "sex": info.sex, "result": info.result}}
    returns.update(messages.OK)
    return jsonify(returns)


@exam.route('/exam/info/import_xls', methods=['POST'])
@login_required
@check_permissions("exam.info.import_xls")
def info_import_xls():
    file = request.files.get('file')
    if file is None:
        return jsonify(messages.DATA_NONE)
    result = utils.load_xls_file(file.read(), "考试结果")
    if result is None:
        return jsonify(messages.NOT_XLS_FILE)
    if not result:
        return jsonify(messages.XLS_NAME_ERROR)
    if ["考试信息", "学号", "姓名", "科目", "成绩"] != result[0][:5]:
        return jsonify(messages.XLS_TITLE_ERROR)
    if len(result[1:]) == 0:
        return jsonify(messages.XLS_IMPORT_EMPTY)
    error_sid = []
    error_lines = []
    try:
        with db.session.begin(nested=True):
            session_cache = {}
            subject_cache = {}
            querys_sid = []
            info_adds = []
            for i in result[1:]:
                if "" in i[1]:  # 学号名称为空直pass
                    error_lines.append(result.index(i) + 1)
                    continue
                if i[1] in error_sid:
                    continue  # 处理已经进缓存的 学号不存在的数据
                else:
                    if i[1] not in querys_sid:  # 在可被查询到的缓存里面就不需要接下来的判断了
                        student = models.Student.query.filter_by(sid=i[1]).first()
                        if student is None:
                            error_sid.append(i[1])  # 上面缓存没进去之后之后这里加入缓存
                        else:
                            querys_sid.append(i[1])  # 可以被查询到的学号的缓存
                session_id = None
                if i[0] != "":
                    if i[0] in session_cache.keys():
                        session_id = session_cache[i[0]]
                    else:
                        session = models.Examsession.query.filter_by(name=i[0]).first()
                        if session is not None:
                            session_id = session.id
                    session_cache[i[0]] = session_id
                subject_id = None
                if i[3] != "":
                    if i[3] in subject_cache.keys():
                        subject_id = subject_cache[i[3]]
                    else:
                        subject = models.Subject.query.filter_by(name=i[3]).first()
                        if subject is not None:
                            subject_id = subject.id
                    subject_cache[i[3]] = subject_id
                result = None
                if i[4] != "":
                    if not utils.is_decimal(i[4]):
                        result = utils.ResultMap().to_number(i[4])
                    else:
                        result = float(i[4])
                info_adds.append(models.Examinfo(sid=i[1], session_id=session_id, subject_id=subject_id, result=result))
            returns = {
                "data": {"ok": len(info_adds), "error": len(error_lines) + len(error_sid), "error_sid": error_sid,
                         "error_lines": error_lines}}
            db.session.bulk_save_objects(info_adds)
        returns.update(messages.OK)
        return jsonify(returns)
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(messages.DATABASE_ERROR)
