# coding: utf-8
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class College(db.Model):  # 学院
    __tablename__ = 'college'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(20), nullable=False)


class Clas(db.Model):  # 班级
    __tablename__ = 'class'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(20), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id', ondelete='SET DEFAULT'), nullable=False
                           , server_default=text("1"))

    college = db.relationship('College', backref='class')

    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )

    # https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#orm-declarative-table-configuration


class Examsession(db.Model):  # 考试信息
    __tablename__ = 'examsessions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(30))


class Subject(db.Model):  # 科目
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(30), nullable=False)


class Student(db.Model):  # 学生信息
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text(20), nullable=False)
    sex = db.Column(db.Integer, nullable=False, server_default=text("1"))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='SET DEFAULT'),
                         nullable=False, server_default=text("1"))

    _class = db.relationship('Clas', backref='student')

    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )


class Examinfo(db.Model):  # 考试成绩
    __tablename__ = 'examinfo'

    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Text, db.ForeignKey('student.sid', ondelete='cascade'), nullable=False)
    sessions_id = db.Column(db.Integer, db.ForeignKey('examsessions.id', ondelete='SET DEFAULT'),
                            nullable=False, server_default=text("1"))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='SET DEFAULT'),
                           nullable=False, server_default=text("1"))
    result = db.Column(db.Float, nullable=False)

    student = db.relationship('Student', backref='examinfo')
    sessions = db.relationship('Examsession', backref='examinfo')
    subject = db.relationship('Subject', backref='examinfo')

    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )


class Group(db.Model):  # 权限组
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(20), nullable=False)
    inherit = db.Column(db.Text())


class User(db.Model):  # 用户组
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.Text(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False, server_default=text("3"))
    csrf = db.Column(db.Text, unique=True)
    otp_status = db.Column(db.Integer, server_default=text("0"))
    otp_secret = db.Column(db.Text, unique=True)
    otp_act_exp_time = db.Column(db.Integer)

    group = db.relationship('Group', backref='user')

    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )
