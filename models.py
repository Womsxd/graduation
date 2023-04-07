# coding: utf-8
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Clas(db.Model):
    __tablename__ = 'class'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    college = db.Column(db.Integer)


class College(db.Model):
    __tablename__ = 'college'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)


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
    name = db.Column(db.Text)


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)


class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    sex = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    _class = db.Column('class', db.Integer, nullable=False)


class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    groupid = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
