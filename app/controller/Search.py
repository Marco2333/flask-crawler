import time
import datetime
from app.database import db
from app.models import Task
from flask import request, render_template, jsonify, session

def user_search():
	return render_template('user_search.html')

def relation_search():
	return render_template('relation_search.html')

def task_list():
	tasks = Task.query.filter().all()

	for task in tasks:
		if len(task.remark) > 8:
			task.remark = task.remark[0:8]
			task.remark += ' ...'

	return render_template('task_list.html', tasks = tasks)

def tweets_search():
	return render_template('tweets_search.html')