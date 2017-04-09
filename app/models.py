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


class Task(db.Model):
    __tablename__ = 'task'
    id = Column(Integer, primary_key = True)
    task_name = Column(String(100))
    userid = Column(String(30))
    created_at = Column(DateTime)
    finished_at = Column(DateTime)
    search_name = Column(String(30))
    search_type = Column(Integer)
    remark = Column(String(300))

    def __init__(self, task_name = None, userid = None, search_name = None,  remark = None, created_at = None, finished_at = None, search_type = '1'):
        self.task_name = task_name
        self.userid = userid
        self.created_at = created_at
        self.finished_at = finished_at
        self.search_type = search_type
        self.search_name = search_name
        self.remark = remark