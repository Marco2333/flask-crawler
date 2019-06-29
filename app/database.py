# -*- coding:utf-8 -*-

from app import app
from flask_sqlalchemy import SQLAlchemy
# from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
