import time
import datetime
from app.database import db
from app.models import Task
from flask import request, render_template, jsonify, session

def task_list():
	tasks = Task.query.filter().all()

	for task in tasks:
		if len(task.remark) > 8:
			task.remark = task.remark[0:8]
			task.remark += ' ...'

	return render_template('task_list.html', tasks = tasks)

def task_delete():
	id = request.form['id']
	res = Task.query.filter(Task.id == id).delete()

	if res != None:
		return jsonify({'status': 1})
	else:
		return jsonify({'status': 0})

def task_add():
	return render_template('task_add.html')

def task_add_submit():
	task = Task(task_name = request.form['task_name'], userid = session['userid'], search_name = request.form['search_name'], 
		remark = request.form['remark'], created_at = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
		search_type = request.form['type'])

	db.session.add(task)
	db.session.commit()
	return jsonify({'status': 1})