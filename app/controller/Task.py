import time
import threading

from app import app
from app.controller import verify
from app.database import db
from app.models import Task
from pybloom import BloomFilter
from flask import request, render_template, jsonify, session, url_for, redirect

from crawler.basicinfo_crawler import BasicinfoCrawler
from crawler.relation_crawler import RelationCrawler
from crawler.tweets_crawler import TweetsCrawler

basicinfo_crawler = BasicinfoCrawler()
relation_crawler = RelationCrawler()
tweets_crawler = TweetsCrawler()

LOCK = threading.Lock()

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
	
	while (tweet_num < 6 and relation_thread.is_alive) or (tweet_num > 6 and len(user_list) < 5):
		pass

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


def thread_extension(user_list, user_id, person_num, deepth, extension):
	bloom_filter = BloomFilter(capacity = int(person_num), error_rate = 0.001)
	bloom_filter.add(str(user_id))
	user_list_temp = [(user_id, 0)]

	count = 1	

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


# def friends_process(args):
# 	user_list = []
# 	collect_name = "task_" + str(args['id'])
# 	tweets_crawler.get_user_all_timeline(screen_name = args['screen_name'], collect_name = collect_name)

# 	thread_num = int(args['thread_num'])
# 	tweet_num = int(args['tweet_num'])
# 	deepth = int(args['deepth'])
# 	extension = int(args['extension'])

# 	user = basicinfo_crawler.get_user(screen_name = args['screen_name'])
	 
# 	tweets_crawler.get_user_all_timeline(screen_name = screen_name)
# 	with app.app_context():
# 		Task.query.filter(Task.id == task_id).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


@verify
def basicinfo_process(args):
	user_list = []
	table_name = "task_" + str(args['id'])
	basicinfo_crawler.get_user_save(screen_name = args['screen_name'], table_name = table_name)

	thread_num = int(args['thread_num'])
	basicinfo_num = int(args['basicinfo_num'])
	deepth = int(args['deepth'])
	extension = int(args['extension'])

	user = basicinfo_crawler.get_user(screen_name = args['screen_name'])

	relation_thread = threading.Thread(target = thread_extension, 
									args = (user_list, user.id, basicinfo_num, deepth, extension))
	relation_thread.start()
	
	while (basicinfo_num < 6 and relation_thread.is_alive) or (basicinfo_num > 6 and len(user_list) < 5):
		pass

	while len(user_list) != 0 or relation_thread.is_alive:

		if len(user_list) == 0:
			print "sleeping, relation crawler is slow!"
			time.sleep(100)
			continue

		i = 0
		threads_pool = []

		while i < thread_num:
			if len(user_list) == 0:
				break

			if LOCK.acquire():
				user_id = user_list.pop(0)
				LOCK.release()

			thread = threading.Thread(target = get_user_save, args = (user_id, table_name, ))
			thread.start()
			threads_pool.append(thread)
			i = i + 1

		for thread in threads_pool:
			thread.join()

	with app.app_context():
		Task.query.filter(Task.id == args['id']).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


@verify
def tweet_basicinfo_process(args):
	tweet_user_list = []
	basicinfo_user_list = []

	table_name = "task_" + str(args['id'])
	basicinfo_crawler.get_user_save(screen_name = args['screen_name'], table_name = table_name)

	collect_name = "task_" + str(args['id'])
	tweets_crawler.get_user_all_timeline(screen_name = args['screen_name'], collect_name = collect_name)

	thread_num = int(args['thread_num'])
	tweet_num = int(args['basicinfo_num'])
	basicinfo_num = int(args['basicinfo_num'])
	deepth = int(args['deepth'])
	extension = int(args['extension'])

	relation_thread = threading.Thread(target = thread_extension_tweet_basicinfo, 
									args = (tweet_user_list, basicinfo_user_list, user.id, tweet_person_num, basicinfo_num, deepth, extension))
	relation_thread.start()

	tweet_thread = threading.Thread(target = tweet_thread, 
									args = (basicinfo_num, basicinfo_user_list, thread_num, table_name))
	tweet_thread.start()

	basicinfo_thread = threading.Thread(target = basicinfo_thread, 
									args = (tweet_num, tweet_user_list, thread_num, collect_name))
	basicinfo_thread.start()

	relation_thread.join()
	tweet_thread.join()
	basicinfo_thread.join()
	
	with app.app_context():
		Task.query.filter(Task.id == args['id']).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


def basicinfo_thread(basicinfo_num, basicinfo_user_list, thread_num, table_name):

	n = 1
	while n < basicinfo_num:

		if len(basicinfo_user_list) == 0:
			print "(basicinfo_thread)sleeping, relation crawler is slow!"
			time.sleep(100)
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


def tweet_thread(tweet_num, tweet_user_list, thread_num, collect_name):

	n = 1
	while n < tweet_num:

		if len(tweet_user_list) == 0:
			print "(tweet_thread)sleeping, relation crawler is slow!"
			time.sleep(100)
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
			thread = threading.Thread(target = tweets_crawler.get_user_all_timeline, args = (user_id, table_name, ))
			thread.start()
			threads_pool.append(thread)
			i = i + 1

		for thread in threads_pool:
			thread.join()


def thread_extension_tweet_basicinfo(tweet_user_list, 
									 basicinfo_user_list, 
									 user_id, 
									 tweet_person_num, 
									 basicinfo_person_num, 
									 deepth, 
									 extension):

	person_num = max(tweet_num, basicinfo_num)
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


@verify
def task_add_submit():
	screen_name = request.form['search_name']
	search_type = request.form.getlist('type')

	thread_num = int(request.form['thread'])
	deepth = int(request.form['deepth'])
	# style = int(request.form['style'])
	extension = request.form['extension']

	if thread_num < 1 or thread_num > 6:
		return redirect(url_for('task_add'))

	if deepth < 1 or deepth > 6:
		return redirect(url_for('task_add'))

	st = ""
	tweet_num = None
	# friends_num = None
	# followers_num = None
	basicinfo_num = None

	if '1' in search_type:
		tweet_num = request.form['tweet_num']
		st += '1'

	# if '2' in search_type:
	# 	friends_num = request.form['friends_num']
	# 	st += '2'

	# if '3' in search_type:
	# 	followers_num = request.form['followers_num']
	# 	st += '3'

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
	# args['style'] = style
	args['extension'] = extension

	if st == '1':
		args['tweet_num'] = tweet_num
		t = threading.Thread(target = tweet_process, args = (args, ))
		t.start()
	
	# args['friends_num'] = friends_num
	# if st.find('2') != -1:
	# 	t = threading.Thread(target = friends_process, args = args)
	# 	t.start()
	
	# args['followers_num'] = followers_num
	# if st.find('3') != -1:
	# 	t = threading.Thread(target = followers_process, args = args)
	# 	t.start()

	if st == '1':
		args['basicinfo_num'] = basicinfo_num
		t = threading.Thread(target = basicinfo_process, args = args)
		t.start()

	if st == '14':
		args['tweet_num'] = tweet_num
		args['basicinfo_num'] = basicinfo_num
		t = threading.Thread(target = basicinfo_process, args = args)
		t.start()

	return render_template('task_add.html', status = 1)