# coding: utf-8
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Clas(db.Model):
    __tablename__ = 'class'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(20), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'))
    college = db.relationship('College', backref='users')


class College(db.Model):
    __tablename__ = 'college'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(20), nullable=False)


class Examinfo(db.Model):
    __tablename__ = 'examinfo'

    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Text, nullable=False)
    sessions = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.Integer, nullable=False)
    result = db.Column(db.Float, nullable=False)


class Examsession(db.Model):
    __tablename__ = 'examsessions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(30))


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(20), nullable=False)
    inherit = db.Column(db.Text())


class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text(20), nullable=False)
    sex = db.Column(db.Integer, nullable=False, server_default=text("1"))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    _class = db.relationship('Clas', backref='users')


class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(30), nullable=False)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.Text(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False, server_default=text("3"))
    csrf = db.Column(db.Text, unique=True)
    group = db.relationship('Group', backref='users')
