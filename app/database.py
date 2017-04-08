# -*- coding:utf-8 -*-

from app import app
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

# def init_db():
#     import flask_blog.models
#     Base.metadata.create_all(bind=engine)