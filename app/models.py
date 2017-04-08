# -*- coding:utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime
from app.database import db

class Admin(db.Model):
    # __bind_key__ = 'qeeniao_mysql'
    __tablename__ = 'admin'
    userid = Column(String(20), primary_key = True)
    username = Column(String(20))
    password = Column(String(40))

    def __init__(self, userid = None, username = None, password = None):
        self.userid = userid
        self.username = username
        self.password = password

    # def __repr__(self):
    #     return '<User %r>' % (self.username)

# class Entries(db.Model):
#     __tablename__='entries'
#     id = db.Column(Integer,primary_key=True)
#     title = db.Column(String(100),unique=True)
#     text = db.Column(String(200),unique=True)

#     def __init__(self,title,text):
#         self.title = title
#         self.text = text

#     def __repr__(self):
#         return '<Entries %r>' % (self.title)


class Task(db.Model):
    __tablename__ = 'task'
    id = Column(Integer, primary_key = True)
    name = Column(String(100))
    userid = Column(String(30))
    created_at = Column(DateTime)
    finished_at = Column(DateTime)

    def __init__(self, id = None, name = None, userid = None, created_at = None, finished_at = None):
        self.id = id
        self.name = name
        self.userid = userid
        self.created_at = created_at
        self.finished_at = finished_at