from app.models import Task
from flask import request, render_template, jsonify

def task_list():
	tasks = Task.query.filter().all()
	return render_template('task_list.html', tasks = tasks)

def task_delete():
	id = request.form['id']
	res = Task.query.filter(Task.id == id).delete()

	if res != None:
		return jsonify({'status': 1})
	else:
		return jsonify({'status': 0})