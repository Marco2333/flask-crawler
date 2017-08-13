# -*- coding:utf-8 -*-
import os
import time
import json
import warnings
import threading

from app import app
from crawler.db import MongoDB
from app.controller import verify
from app.database import db
from app.models import Task, Admin
from pybloom import BloomFilter
from werkzeug import secure_filename
from flask import request, render_template, jsonify, session, url_for, redirect

from crawler.basicinfo_crawler import BasicinfoCrawler
from crawler.relation_crawler import RelationCrawler
from crawler.tweets_crawler import TweetsCrawler

basicinfo_crawler = BasicinfoCrawler()
relation_crawler = RelationCrawler()
tweets_crawler = TweetsCrawler()

LOCK = threading.Lock()


'''
返回任务列表
'''
@verify
def task_list():
	tasks = Task.query.filter().all()

	res = []
	for task in tasks:
		res.append({
			'id': task.id,
			'task_name': task.task_name,
			'created_at': task.created_at,
			'userid': task.userid,
			'search_name': task.search_name,
			'finished_at': task.finished_at,
			'search_type': task.search_type,
			'remark': task.remark[0:8] + " ..." if len(task.remark) > 8 else task.remark
		})

	return render_template('task_list.html', tasks = res)


'''
返回任务详情
'''
@verify
def task_detail(task_id):
	task = Task.query.filter(Task.id == task_id).first()
	user = Admin.query.filter(Admin.userid == task.userid).first()

	res = {
		'id': task.id,
		'task_name': task.task_name,
		'user_name': user.username,
		'created_at': task.created_at,
		'finished_at': task.finished_at,
		'screen_name': task.search_name,
		'remark': task.remark,
		'thread_num': task.thread_num,
		'deepth': task.deepth,
		'extension': task.extension,
		'tweet_num': task.tweet_num,
		'basicinfo_num': task.basicinfo_num,
		'type': '文件导入' if task.is_file else '广度优先扩展',
		'search_type': task.search_type,
		'basicinfo_num_finished': '',
		'tweet_num_finished': ''
	}

	if '4' in task.search_type:
		sql = "select count(*) from task_%s" % task.id
		bsc = db.session.execute(sql).first()
		res['basicinfo_num_finished'] = bsc[0]

	if '1' in task.search_type:
		md = MongoDB().connect()
		collect = md["task_%s" % task.id]
		res['tweet_num_finished'] = collect.find().count()

	return render_template('task_detail.html', task = res)


'''
删除任务
'''
@verify
def task_delete():
	id = request.form['id']
	res = Task.query.filter(Task.id == id).delete()

	if res != None:
		return jsonify({'status': 1})
	else:
		return jsonify({'status': 0})


'''
返回任务添加页面
'''
@verify
def task_add():
	if 'status' in request.args:
		status = request.args['status']
		if int(status) == 1:
			return render_template('task_add.html', status = 1)

	return render_template('task_add.html')


'''
返回任务上传页面
'''
@verify
def file_upload():
	if 'status' in request.args:
		status = request.args['status']
		if int(status) == 1:
			return render_template('file_upload.html', status = 1)
	
	return render_template('file_upload.html')


'''
提交任务添加，开始后台执行抓取任务
'''
@verify
def task_add_submit():
	screen_name = request.form['search_name']
	search_type = request.form.getlist('type')

	thread_num = int(request.form['thread'])
	deepth = int(request.form['deepth'])
	extension = request.form['extension']

	if thread_num < 1 or thread_num > 6:
		return redirect(url_for('task_add'))

	if deepth < 1 or deepth > 6:
		return redirect(url_for('task_add'))

	st = ""
	tweet_num = None
	basicinfo_num = None

	if '1' in search_type:
		tweet_num = request.form['tweet_num']
		st += '1'

	if '4' in search_type:
		basicinfo_num = request.form['basicinfo_num']
		st += '4'

	task = Task(task_name = request.form['task_name'], userid = session['userid'], search_name = request.form['search_name'], 
		thread_num = thread_num, deepth = deepth, extension = extension, search_type = st, tweet_num = tweet_num,  basicinfo_num = basicinfo_num, 
		remark = request.form['remark'], created_at = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

	db.session.add(task)
	db.session.commit()

	args = {}
	args['screen_name'] = screen_name
	args['id'] = task.id
	args['thread_num'] = thread_num
	args['deepth'] = deepth
	args['extension'] = extension

	if st == '1':
		args['tweet_num'] = tweet_num
		t = threading.Thread(target = tweet_process, args = (args,))
		t.start()
	
	if st == '4':
		args['basicinfo_num'] = basicinfo_num
		t = threading.Thread(target = basicinfo_process, args = (args,))
		t.start()

	if st == '14':
		args['tweet_num'] = tweet_num
		args['basicinfo_num'] = basicinfo_num
		t = threading.Thread(target = tweet_basicinfo_process, args = (args,))
		t.start()

	return redirect(url_for('task_add', status = 1))


'''
提交文件上传，开始后台执行抓取任务
'''
@verify
def file_upload_submit():
	file = request.files['file']

	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	else:
		return redirect(url_for('file_upload'))

	search_type = request.form.getlist('type')
	# thread_num = int(request.form['thread'])

	st = ""
	if '1' in search_type:
		st += '1'

	if '4' in search_type:
		st += '4'

	task = Task(task_name = request.form['task_name'], userid = session['userid'], search_type = st, remark = request.form['remark'], 
		is_file = 1, created_at = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

	db.session.add(task)
	db.session.commit()

	t = threading.Thread(target = read_and_crawler, args = (os.path.join(app.config['UPLOAD_FOLDER'], filename), search_type, task.id))
	t.start()
	
	return redirect(url_for('file_upload', status = 1))


'''
判断上传文件类型是否合法
'''
def allowed_file(filename):
	ALLOWED_EXTENSIONS = set(['txt'])
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


'''
读取文件内容，并执行抓取任务
'''
def read_and_crawler(file_name, search_type, task_id):
	file = open(file_name)
	user_list = set()

	while 1:
	    lines = file.readlines(100000)
	    if not lines:
	        break
	    for line in lines:
	    	res = line.split(" ")
	    	for s in res:
	        	user_list.add(s.strip())

	user_list = list(user_list)

	if '1' in search_type:
		with app.app_context():
			Task.query.filter(Task.id == task_id).update({'tweet_num': len(user_list)})

		t = threading.Thread(target = tweet_process_file, args = (task_id, user_list,))
		t.start()
	
	if '4' in search_type:
		with app.app_context():
			Task.query.filter(Task.id == task_id).update({'basicinfo_num': len(user_list)})

		t = threading.Thread(target = basicinfo_process_file, args = (task_id, user_list,))
		t.start()


'''
线程：抓取所有用户推文，并保存在数据库中
'''
def tweet_process_file(task_id, user_list):
	collect_name = "task_" + str(task_id)
	tweets_crawler.get_all_users_timeline(user_list, collect_name)

	with app.app_context():
		Task.query.filter(Task.id == task_id).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


'''
线程：抓取所有用户基础信息，并保存在数据库中
'''
def basicinfo_process_file(task_id, user_list):
	table_name = "task_" + str(task_id)
	create_table(table_name)
	basicinfo_crawler.get_all_users(user_list, table_name)

	with app.app_context():
		Task.query.filter(Task.id == task_id).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


'''
线程：从一个用户出发，广度优先抓取相关用户的推文信息
'''
def tweet_process(args):
	user_list = []
	collect_name = "task_" + str(args['id'])
	tweets_crawler.get_user_all_timeline(screen_name = args['screen_name'], collect_name = collect_name)

	thread_num = int(args['thread_num'])
	tweet_num = int(args['tweet_num'])
	deepth = int(args['deepth'])
	extension = int(args['extension'])

	user = basicinfo_crawler.get_user(screen_name = args['screen_name'])

	relation_thread = threading.Thread(target = thread_extension, 
									args = (user_list, user.id, tweet_num, deepth, extension))
	relation_thread.start()
	
	while (tweet_num < 6 and relation_thread.is_alive()) or (tweet_num > 6 and len(user_list) < 5):
		time.sleep(1)

	while len(user_list) != 0:
		i = 0
		threads_pool = []

		while i < thread_num:
			if len(user_list) == 0:
				break

			if LOCK.acquire():
				user_id = user_list.pop(0)
				LOCK.release()

			thread = threading.Thread(target = tweets_crawler.get_user_all_timeline, 
											args = (user_id, collect_name, ))
			thread.start()
			threads_pool.append(thread)
			i = i + 1

		for thread in threads_pool:
			thread.join()

	with app.app_context():
		Task.query.filter(Task.id == args['id']).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


'''
线程：从一个用户出发，广度优先抓取相关用户的基础信息
'''
def basicinfo_process(args):
	user_list = []
	table_name = "task_" + str(args['id'])
	
	create_table(table_name)

	basicinfo_crawler.get_user_save(screen_name = args['screen_name'], table_name = table_name)

	thread_num = int(args['thread_num'])
	basicinfo_num = int(args['basicinfo_num'])
	deepth = int(args['deepth'])
	extension = int(args['extension'])

	user = basicinfo_crawler.get_user(screen_name = args['screen_name'])

	relation_thread = threading.Thread(target = thread_extension, 
									args = (user_list, user.id, basicinfo_num, deepth, extension))
	relation_thread.start()
	
	while (basicinfo_num < 6 and relation_thread.is_alive()) or (basicinfo_num > 6 and len(user_list) < 5):
		time.sleep(1)

	while len(user_list) != 0 or relation_thread.is_alive():
		if len(user_list) == 0:
			print "sleeping, relation crawler is slow!"
			time.sleep(10)
			continue

		i = 0
		threads_pool = []

		while i < thread_num:
			if len(user_list) == 0:
				break

			if LOCK.acquire():
				user_id = user_list.pop(0)
				LOCK.release()

			thread = threading.Thread(target = basicinfo_crawler.get_user_save, args = (user_id, table_name, ))
			thread.start()
			threads_pool.append(thread)
			i = i + 1

		for thread in threads_pool:
			thread.join()

	with app.app_context():
		Task.query.filter(Task.id == args['id']).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


'''
线程：从一个用户出发，广度优先抓取相关用户的基础信息和推文信息
'''
def tweet_basicinfo_process(args):
	tweet_user_list = []
	basicinfo_user_list = []

	table_name = "task_" + str(args['id'])

	create_table(table_name)

	basicinfo_crawler.get_user_save(screen_name = args['screen_name'], table_name = table_name)

	collect_name = "task_" + str(args['id'])

	tweets_crawler.get_user_all_timeline(screen_name = args['screen_name'], collect_name = collect_name)

	thread_num = int(args['thread_num'])
	tweet_num = int(args['tweet_num'])
	basicinfo_num = int(args['basicinfo_num'])
	deepth = int(args['deepth'])
	extension = int(args['extension'])

	user = basicinfo_crawler.get_user(screen_name = args['screen_name'])

	rt = threading.Thread(target = thread_extension_tweet_basicinfo, 
									args = (tweet_user_list, basicinfo_user_list, user.id, tweet_num, basicinfo_num, deepth, extension,))
	rt.start()

	tt = threading.Thread(target = tweet_thread, 
									args = (tweet_num, tweet_user_list, thread_num, collect_name,))
	tt.start()

	bt = threading.Thread(target = basicinfo_thread, 
									args = (basicinfo_num, basicinfo_user_list, thread_num, table_name,))
	bt.start()

	rt.join()
	tt.join()
	bt.join()
	
	with app.app_context():
		Task.query.filter(Task.id == args['id']).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


'''
扩展线程：从一个用户出发，广度优先扩展与之相关的用户，并保存在 user_list 中，供其他线程抓取信息
'''
def thread_extension(user_list, user_id, person_num, deepth, extension):
	bloom_filter = BloomFilter(capacity = int(person_num), error_rate = 0.001)
	bloom_filter.add(str(user_id))
	user_list_temp = [(user_id, 0)]

	count = 1	

	while count < person_num:
		user_if = user_list_temp.pop(0)
		user_id = user_if[0]
		user_deepth = user_if[1]

		if user_deepth >= deepth:
			return

		if extension == 1 or extension == 3:
			cursor = -1
			while cursor != 0:
				users_info = relation_crawler.get_friendids_paged(user_id = user_id, cursor = cursor)
				cursor = users_info[0]
				friend_list = users_info[2]
				
				for u in friend_list:
					u = str(u)
					
					if u not in bloom_filter:
						user_list_temp.append((u, user_deepth + 1))
						bloom_filter.add(u)

						if LOCK.acquire():
							user_list.append(u)
							LOCK.release()
						
		 				count += 1
						if count >= person_num:
							return

		elif extension == 2 or extension == 3:
			cursor = -1
			while cursor != 0:
				users_info = relation_crawler.get_followerids_paged(user_id = user_id, cursor = cursor)
				cursor = users_info[0]
				friend_list = users_info[2]

				for u in friend_list:
					u = str(u)

					if u not in bloom_filter:
						user_list_temp.append((u, user_deepth + 1))
						bloom_filter.add(u)

						if LOCK.acquire():
							user_list.append(u)
							LOCK.release()

						count += 1
						if count >= person_num:
							return

	user_list_temp = []
	bloom_filter = None


'''
创建表，如果表已存在，则先删除原表
'''
def create_table(table_name):
	ctx = app.app_context()
	ctx.push()

	sql = "DROP TABLE IF EXISTS `%s`" % table_name
	
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')
		try:
			db.session.execute(sql)
			db.session.commit()
		except Exception as e:
			print e

	sql = "create table %s like user_task" % table_name
	try:
		db.session.execute(sql)
		db.session.commit()
	except Exception as e:
		print e


'''
基础信息线程：抓取指定数量用户的基础信息
'''
def basicinfo_thread(basicinfo_num, basicinfo_user_list, thread_num, table_name):
	n = 1
	while n < basicinfo_num:
		if len(basicinfo_user_list) == 0:
			print "(basicinfo_thread)sleeping, relation crawler is slow!"
			time.sleep(3)
			continue

		i = 0
		threads_pool = []

		thread_num = 3 if thread_num > 3 else thread_num

		while i < thread_num:
			if len(basicinfo_user_list) == 0:
				break

			if LOCK.acquire():
				user_id = basicinfo_user_list.pop(0)
				LOCK.release()

			n += 1
			thread = threading.Thread(target = basicinfo_crawler.get_user_save, args = (user_id, table_name, ))
			thread.start()
			threads_pool.append(thread)
			i = i + 1

		for thread in threads_pool:
			thread.join()


'''
推文信息线程：抓取指定数量用户的推文信息
'''
def tweet_thread(tweet_num, tweet_user_list, thread_num, collect_name):
	n = 1
	while n < tweet_num:

		if len(tweet_user_list) == 0:
			print "(tweet_thread)sleeping, relation crawler is slow!"
			time.sleep(3)
			continue

		i = 0
		threads_pool = []

		thread_num = 3 if thread_num > 3 else thread_num

		while i < thread_num:
			if len(tweet_user_list) == 0:
				break

			if LOCK.acquire():
				user_id = tweet_user_list.pop(0)
				LOCK.release()

			n += 1
			thread = threading.Thread(target = tweets_crawler.get_user_all_timeline, args = (user_id, collect_name, ))
			thread.start()
			threads_pool.append(thread)
			i = i + 1

		for thread in threads_pool:
			thread.join()


'''
扩展线程（同时需要抓取基础信息和推文信息时）：从一个用户出发，广度优先扩展与之
相关的用户，并保存在 (basicinfo/tweet)_user_list 中，供其他线程抓取信息
'''
def thread_extension_tweet_basicinfo(tweet_user_list, 
									 basicinfo_user_list, 
									 user_id, 
									 tweet_person_num, 
									 basicinfo_person_num, 
									 deepth, 
									 extension):

	person_num = max(tweet_person_num, basicinfo_person_num)
	bloom_filter = BloomFilter(capacity = int(person_num), error_rate = 0.001)
	bloom_filter.add(str(user_id))
	user_list_temp = [(user_id, 0)]

	count = 1
	tweet_count = 1
	basicinfo_count = 1

	while count < person_num:
		cursor = -1
		user_if = user_list_temp.pop(0)
		user_id = user_if[0]
		user_deepth = user_if[1]

		if user_deepth >= deepth:
			return

		if extension == 1 or extension == 3:
			while cursor != 0:
				users_info = relation_crawler.get_friendids_paged(user_id = user_id, cursor = cursor)
				cursor = users_info[0]
				friend_list = users_info[2]
				for u in friend_list:
					u = str(u)
					if u not in bloom_filter:
						user_list_temp.append((u, user_deepth + 1))
						bloom_filter.add(u)

						if tweet_count < tweet_person_num and LOCK.acquire():
							tweet_count += 1
							tweet_user_list.append(u)
							LOCK.release()

						if basicinfo_count < basicinfo_person_num and LOCK.acquire():
							basicinfo_count += 1
							basicinfo_user_list.append(u)
							LOCK.release()
 
		 				count += 1	
						if count >= person_num:
							return

		elif extension == 2 or extension == 3:
			cursor = -1
			while cursor != 0:
				users_info = relation_crawler.get_followerids_paged(user_id = user_id, cursor = cursor)
				cursor = users_info[0]
				friend_list = users_info[2]
				for u in friend_list:
					u = str(u)
					if u not in bloom_filter:
						user_list_temp.append((u, user_deepth + 1))
						bloom_filter.add(u)

						if tweet_count < tweet_person_num and LOCK.acquire():
							tweet_count += 1
							tweet_user_list.append(u)
							LOCK.release()

						if basicinfo_count < basicinfo_person_num and LOCK.acquire():
							basicinfo_count += 1
							basicinfo_user_list.append(u)
							LOCK.release()

						count += 1
						if count >= person_num:
							return

	user_list_temp = []
	bloom_filter = None


'''
根据关键词查询相关用户
'''
def user_search_keyword():
	data = json.loads(request.form['aoData'])

	for item in data:
		if item['name'] == 'sSearch':
			s_search = item['value']
			break

	if s_search == '':
		return jsonify({'aaData': []})

	user_list = []
	user_list = basicinfo_crawler.get_user_search(term = s_search, count = 20)

	res = []
	for user in user_list:
		res.append({
			'screen_name': user.screen_name,
			# 'name': user.name,
			'created_at': time.strftime('%Y-%m-%d', time.strptime(user.created_at.replace('+0000 ',''))),
			'followers_count': user.followers_count,
			'friends_count': user.friends_count,
			'statuses_count': user.statuses_count,
		})

	return jsonify({'aaData': res})