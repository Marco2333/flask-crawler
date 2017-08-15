# -*- coding:utf-8 -*-
from sqlalchemy import Column, Integer, String, DateTime
from app.database import db

class Admin(db.Model):
    __tablename__ = 'admin'
    userid = Column(String(20), primary_key = True)
    username = Column(String(20))
    password = Column(String(40))

    def __init__(self, userid = None, username = None, password = None):
        self.userid = userid
        self.username = username
        self.password = password


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

    thread_num = Column(Integer)
    deepth = Column(Integer)
    # style = Column(Integer)
    extension = Column(Integer)
    tweet_num = Column(Integer)
    # friends_num = Column(Integer)
    # followers_num = Column(Integer)
    basicinfo_num = Column(Integer)
    is_file = Column(Integer)
    file_content = Column(Integer)


class TypicalCharacter(db.Model):
    __tablename__ = 'typical_character'
    id = Column(Integer, primary_key = True)
    screen_name = Column(String(50))
    user_id = Column(String(50))
    created_at = Column(String(40))
    finished_at = Column(String(40))
    admin_id = Column(String(30))