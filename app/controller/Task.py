import time
import threading

from app import app
from app.controller import verify
from app.database import db
from app.models import Task
from flask import request, render_template, jsonify, session, url_for, redirect

from crawler.basicinfo_crawler import BasicinfoCrawler
from crawler.relation_crawler import RelationCrawler
from crawler.tweets_crawler import TweetsCrawler

basicinfo_crawler = BasicinfoCrawler()
relation_crawler = RelationCrawler()
tweets_crawler = TweetsCrawler()

@verify
def task_list():
	tasks = Task.query.filter().all()

	for task in tasks:
		if len(task.remark) > 8:
			task.remark = task.remark[0:8]
			task.remark += ' ...'

	return render_template('task_list.html', tasks = tasks)

@verify
def task_delete():
	id = request.form['id']
	res = Task.query.filter(Task.id == id).delete()

	if res != None:
		return jsonify({'status': 1})
	else:
		return jsonify({'status': 0})

@verify
def task_add():
	return render_template('task_add.html')

def tweet_process(screen_name, task_id):
	tweets_crawler.get_user_all_timeline(screen_name = screen_name)
	with app.app_context():
		Task.query.filter(Task.id == task_id).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})

def basicinfo_process(screen_name, task_id):
	basicinfo_crawler.get_all_users([screen_name])
	with app.app_context():
		Task.query.filter(Task.id == task_id).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})

@verify
def task_add_submit():
	screen_name = request.form['search_name']
	search_type = request.form['type']

	task = Task(task_name = request.form['task_name'], userid = session['userid'], search_name = request.form['search_name'], 
		remark = request.form['remark'], created_at = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
		search_type = request.form['type'])

	db.session.add(task)
	db.session.commit()

	if search_type.find('1') != -1:
		t = threading.Thread(target = tweet_process, args = (screen_name, task.id))
		t.start()
	
	if search_type.find('4') != -1:
		t = threading.Thread(target = basicinfo_process, args = (screen_name, task.id))
		t.start()

	return jsonify({'status': 1})