# -*- coding:utf-8 -*-
import re
import time
import json
import urllib
import threading

from app import app
from app.database import db
from twitter import error
from crawler.database import MongoDB, Neo4j
from py2neo import Graph, Node, Relationship
from app.controller import verify
from app.models import TypicalCharacter
from flask import request, render_template, jsonify, session, make_response, send_file

from portrayal import user_profile
from portrayal.interest_extract import tag_cloud
from portrayal.tools.generate_xml import generate_user_xml

from crawler.basicinfo_crawler import BasicinfoCrawler
from crawler.relation_crawler import RelationCrawler
from crawler.tweets_crawler import TweetsCrawler

graph = Neo4j().connect()

basicinfo_crawler = BasicinfoCrawler()
tweets_crawler = TweetsCrawler()
relation_crawler = RelationCrawler()


'''
典型人物列表页面
'''
@verify
def typical_character_list():
	return render_template('portrayal/typical_character_list.html')


'''
获取型人物列表详情
'''
@verify
def typical_character_list_detail():
	data = json.loads(request.form['aoData'])

	for item in data:
		if item['name'] == 'sSearch':
			s_search = item['value'].strip()

		if item['name'] == 'iDisplayLength':
			data_length = item['value']

		if item['name'] == 'iDisplayStart':
			data_start = item['value'];      
	
	data_length = int(data_length)

	db = MongoDB().connect()
	collect = db['typical']

	field = {'screen_name': 1, 'name': 1, 'friends_count': 1, 'followers_count': 1, 'statuses_count': 1, 'influence_score': 1, 'category': 1}

	if s_search == '':
		users = collect.find({}, field).skip(data_start).limit(data_length)
		count = collect.find({}, {'_id': 1}).count()
	else:
		pattern = re.compile(".*" + s_search + ".*")
		query = {"$or":[{"name": pattern}, {"category": pattern}, {"interest_tags": pattern}, 
		{"screen_name": pattern}, {"description": pattern}, {"location": pattern}, {"name": pattern}]}

		users = collect.find(query, field).skip(data_start).limit(data_length)
		count = collect.find(query, {'_id': 1}).count()

	res = []
	for u in users:
		res.append({
			"_id": str(u['_id']),
			"screen_name": u['screen_name'],
			"name": u['name'],
			"friends_count": u['friends_count'],
			"followers_count": u['followers_count'],
			"statuses_count": u['statuses_count'],
			"category": u['category'],
			"influence_score": round(u['influence_score'],3)
		})

	return jsonify({'aaData': res, 'iTotalDisplayRecords': count})


'''
获取典型人物的朋友
'''
@verify
def get_typical_friends(user_id):
	data = json.loads(request.form['aoData'])
	deepth = json.loads(request.form['deepth'])

	for item in data:
		if item['name'] == 'iDisplayLength':
			data_length = item['value']

		if item['name'] == 'iDisplayStart':
			data_start = item['value'];      
	
	data_length = int(data_length)
	data_start = int(data_start)

	cql = '''MATCH(a{user_id:%s})-[:following*1..%s]->(f) return count(distinct f) as count''' % (user_id, deepth)
	res = graph.data(cql)
	total = res[0]['count']

	cql = '''MATCH(a{user_id:%s})-[:following*1..%s]->(f) return distinct f.user_id as user_id,
			f.screen_name as screen_name, f.statuses_count as statuses_count, f.friends_count as friends_count,
			f.followers_count as followers_count, f.influence_score as influence_score, f.category as category 
			skip %s limit %s''' % (user_id, deepth, data_start, data_length)
	res = graph.data(cql)

	friends = []

	for item in res:
		friends.append({
			'user_id': str(item['user_id']),
			'screen_name': item['screen_name'],
			'statuses_count': item['statuses_count'],
			'friends_count': item['friends_count'],
			'followers_count': item['followers_count'],
			'influence_score': round(item['influence_score'], 3),
			'category': item['category']
		})

	return jsonify({'aaData': friends, 'iTotalDisplayRecords': total})


'''
获取典型人物粉丝
'''
@verify
def get_typical_followers(user_id):
	data = json.loads(request.form['aoData'])
	deepth = json.loads(request.form['deepth'])

	for item in data:
		if item['name'] == 'iDisplayLength':
			data_length = item['value']

		if item['name'] == 'iDisplayStart':
			data_start = item['value'];      
	
	data_length = int(data_length)
	data_start = int(data_start)

	cql = '''Match(f)-[:following*1..%s]->(a{user_id:%s}) return count(distinct f) as count''' % (deepth, user_id)
	res = graph.data(cql)
	total = res[0]['count']

	cql = '''Match(f)-[:following*1..%s]->(a{user_id:%s}) return distinct f.user_id as user_id,
			f.screen_name as screen_name, f.statuses_count as statuses_count, f.friends_count as friends_count,
			f.followers_count as followers_count, f.influence_score as influence_score, f.category as category 
			skip %s limit %s''' % (deepth, user_id, data_start, data_length)
	res = graph.data(cql)

	friends = []

	for item in res:
		friends.append({
			'user_id': str(item['user_id']),
			'screen_name': item['screen_name'],
			'statuses_count': item['statuses_count'],
			'friends_count': item['friends_count'],
			'followers_count': item['followers_count'],
			'influence_score': round(item['influence_score'], 3),
			'category': item['category']
		})

	return jsonify({'aaData': friends, 'iTotalDisplayRecords': total})


'''
获取典型人物互粉人物
'''
@verify
def get_typical_dfans(user_id):
	data = json.loads(request.form['aoData'])

	for item in data:
		if item['name'] == 'iDisplayLength':
			data_length = item['value']

		if item['name'] == 'iDisplayStart':
			data_start = item['value'];      
	
	data_length = int(data_length)
	data_start = int(data_start)

	cql = '''Match(f)-[:following]->(a{user_id:%s})-[:following]->(f) return count(distinct f) as count''' % (user_id)
	res = graph.data(cql)
	total = res[0]['count']

	cql = '''Match(f)-[:following]->(a{user_id:%s})-[:following]->(f) return distinct f.user_id as user_id,
			f.screen_name as screen_name, f.statuses_count as statuses_count, f.friends_count as friends_count,
			f.followers_count as followers_count, f.influence_score as influence_score, f.category as category 
			skip %s limit %s''' % (user_id, data_start, data_length)
	res = graph.data(cql)

	friends = []

	for item in res:
		friends.append({
			'user_id': str(item['user_id']),
			'screen_name': item['screen_name'],
			'statuses_count': item['statuses_count'],
			'friends_count': item['friends_count'],
			'followers_count': item['followers_count'],
			'influence_score': round(item['influence_score'], 3),
			'category': item['category']
		})

	return jsonify({'aaData': friends, 'iTotalDisplayRecords': total})


'''
获取典型人物与粉丝的关系路径
'''
@verify
def typical_followers_path(user_id, follower_id, deepth):
	cql = '''MATCH path = allShortestPaths((a:Typical { user_id: %s})-[:following*1..%s]->
			(b:Typical { user_id: %s})) RETURN path''' % (follower_id, deepth, user_id)

	paths = graph.data(cql)

	res = []
	for item in paths:
		path = item['path']

		res.append(map(lambda x: {'name': x['screen_name']}, path.nodes()))

	return jsonify({"paths": res})


'''
获取典型人物与朋友的关系路径
'''
@verify
def typical_friends_path(user_id, friend_id, deepth):
	cql = '''MATCH path = allShortestPaths((a:Typical { user_id: %s})-[:following*1..%s]->
			(b:Typical { user_id: %s})) RETURN path''' % (user_id, deepth, friend_id)

	paths = graph.data(cql)

	res = []
	for item in paths:
		path = item['path']

		res.append(map(lambda x: {'name': x['screen_name']}, path.nodes()))

	return jsonify({"paths": res})


'''
获取典型人物详情，包括人物基础信息、画像信息、关心信息
'''
@verify
def typical_character_detail(user_id):
	mdb = MongoDB().connect()
	collect = mdb['typical']
	
	user = collect.find_one({'_id': long(user_id)}, {'tweets': 0})
	
	user['ratio'] = user['followers_count'] if not user['friends_count'] else round(user['followers_count'] * 1.0 / user['friends_count'], 2)
	user['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(user['created_at'].replace('+0000 ','')))
	user['crawler_date'] = str(user['crawler_date']).split(" ")[0]
	user['interest_tags'] = user['interest_tags'].replace(',', ', ')
	user['interest_tags'] = re.sub(r'#(\w+)', "<a href='https://www.twitter.com/hashtag/\g<1>' target='_blank'>#\g<1></a>", user['interest_tags'])

	s = ''
	for item in user['activity_list']:
		s += "," + str(item)
	user['activity_list'] = s[1:]

	s = ''
	for item in user['psy_with_time1']:
		s += "," + str(item)
	user['psy_with_time1'] = s[1:]

	s = ''
	for item in user['psy_with_time2']:
		s += "," + str(item)
	user['psy_with_time2'] = s[1:]

	s = ''
	for item in user['psy_with_count1']:
		s += "," + str(item)
	user['psy_with_count1'] = s[1:]

	s = ''
	for item in user['psy_with_count2']:
		s += "," + str(item)
	user['psy_with_count2'] = s[1:]

	s = ''
	s1 = ''
	for item in user['category_score']:
		s += "," + item
		s1 += "," + str(user['category_score'][item])

	user['category_score_keys'] = s[1:]
	user['category_score_values'] = s1[1:]
	
	user_tweets = collect.aggregate([{"$match": {'_id': long(user_id)}}, \
		{"$project": {"length": {"$size": "$tweets"}, "first": {"$slice": ["$tweets.created_at", 0, 1]},\
		"last": {"$slice": ["$tweets.created_at", -1]}}}])

	for item in user_tweets:
		user['tweets_count'] = item['length']
		user['tweets_start_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(item['first'][0].replace('+0000 ', '')))
		user['tweets_end_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(item['last'][0].replace('+0000 ', '')))

		break
	
	get_image(user['profile_image_url'], user['screen_name'])

	related_users = collect.find({'category': user['category'], '_id': {"$ne": user['_id']}}, {'screen_name': 1, 'name': 1, 'profile_image_url': 1}).limit(10)
	
	ru_arr = []
	for ru in related_users:
		ru_arr.append({
			'_id': str(ru['_id']),
			'screen_name': ru['screen_name'],
			'name': ru['name']
		})
		get_image(ru['profile_image_url'], ru['screen_name'])
	
	return render_template('portrayal/typical_character_detail.html', user = user, related_users = ru_arr)


'''
根据url下载图片
'''
def get_image(url, screen_name):
	urllib.urlretrieve(url.replace('normal.','bigger.'), 'app/static/profile/%s.jpg' % screen_name)


'''
典型人物添加页面
'''
@verify
def typical_character_add():
	return render_template('portrayal/typical_character_add.html')


'''
提交新增典型人物
'''
@verify
def typical_character_add_submit():
	screen_name = request.form['screen_name']

	if(screen_name == ''):
		return jsonify({'status': 0})

	status = 1

	try:
		user = basicinfo_crawler.get_user(screen_name = screen_name)
	except error.TwitterError as te:
		status = 0
		try:
			if te.message[0]['code'] == 88:
				status = "ratelimit"

			elif te.message[0]['code'] == 63:
				status = "suspend"

			elif te.message[0]['code'] == 50:
				status = "notfound"
		except Exception as ee:
			status = 0
	except:
		status = 0

	if status == 1:
		if user.protected:
			status = 'protected'

		else:
			TypicalCharacter.query.filter(TypicalCharacter.user_id == user.id).delete()
			tc = TypicalCharacter(admin_id = session['userid'], user_id = user.id, screen_name = screen_name, 
				created_at = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

			db.session.add(tc)
			db.session.commit()
			 
			user = {
				'user_id': user.id,
				'screen_name': user.screen_name,
				'name': user.name,
				'verified': user.verified,
				'friends_count': user.friends_count,
				'description': user.description,
				'crawler_date': time.strftime('%Y-%m-%d',time.localtime(time.time())),
				'followers_count': user.followers_count,
				'location': user.location,
				'statuses_count': user.statuses_count,
				'favourites_count': user.favourites_count,
				'lang': user.lang,
				'utc_offset': user.utc_offset,
				'protected': user.protected,
				'profile_background_color': user.profile_background_color,
				'default_profile_image': user.default_profile_image,
				'created_at': user.created_at,
				'profile_banner_url': user.profile_banner_url,
				'time_zone': user.time_zone,
				'profile_image_url': user.profile_image_url,
				'listed_count': user.listed_count
			}
			th = threading.Thread(target = portrayal_thread, args = (user, tc.id))
			th.start()

	return jsonify({'status': status})


'''
新增典型人物，画像线程
'''
def portrayal_thread(user, task_id):
	tweet_list = tweets_crawler.get_user_all_timeline_return(screen_name = user['screen_name'])
	user['tweets'] = tweet_list

	out = user_profile.user_profile(user)

	db = MongoDB().connect()
	collect = db['typical']

	cur_user = collect.find_one({'_id': long(out['user_id'])})

	out['_id'] = long(out['user_id'])
	del out['user_id']

	if cur_user == None:
		collect.insert_one(out)

		th = threading.Thread(target = relation_thread, args = (out,))
		th.start()
	else:
		collect.delete_one({'_id': long(out['_id'])})
		collect.insert_one(out)

	with app.app_context():
		TypicalCharacter.query.filter(TypicalCharacter.id == task_id).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


'''
标准人物样本库人物关系抓取
'''
def relation_thread(user):
	user_id = user['_id']

	db = MongoDB().connect()
	collect = db['relation']

	user_id = long(user_id)
	typical_user = collect.find_one({'_id': user_id})

	if typical_user:
		return

	user_node = Node("Typical", 
					 user_id = user_id,
					 name = user['name'],
					 category = user['category'],
					 followers_count = user['followers_count'],
					 location = user['location'],
					 utc_offset = user['utc_offset'],
					 statuses_count = user['statuses_count'],
					 description = user['description'],
					 friends_count = user['friends_count'],
					 psy = user['psy'],
					 verified = user['verified'],
					 lang = user['lang'],
					 favourites_count = user['favourites_count'],
					 screen_name = user['screen_name'],
					 influence_score = user['influence_score'],
					 created_at = user['created_at'],
					 time_zone = user['time_zone'],
					 protected = user['protected'],
					 activity = user['activity'])

	graph.create(user_node)

	cursor = -1
	friends = []

	while cursor != 0:
		out = relation_crawler.get_friendids_paged_sleep(user_id = user_id,
														 cursor = cursor, 
														 count = 5000)
		if not out:
			break
		
		friends = friends + out[2]
		cursor = out[0]

	collect.insert_one({
		'_id': user_id,
		'friends': friends
	})

	tus = collect.find()
	friends = set(friends)

	for item in tus:
		if item['_id'] == user_id:
			continue

		if item['_id'] in friends:
			friend_node = graph.find_one("Typical",
										 property_key = "user_id",
										 property_value = item['_id'])

			following = Relationship(user_node, 'following', friend_node)
			graph.create(following)
		
		if user_id in set(item['friends']):
			friend_node = graph.find_one("Typical",
										 property_key = "user_id",
										 property_value = item['_id'])

			following = Relationship(friend_node, 'following', user_node)
			graph.create(following)


'''
新增典型人物列表页面
'''
@verify
def typical_character_newlist():
	return render_template('portrayal/typical_character_newlist.html')


'''
获取新增典型人物列表详情
'''
@verify
def typical_character_newlist_detail():
	data = json.loads(request.form['aoData'])

	for item in data:
		if item['name'] == 'sSearch':
			s_search = item['value'].strip()

		if item['name'] == 'iDisplayLength':
			data_length = item['value']

		if item['name'] == 'iDisplayStart':
			data_start = item['value'];      
	
	data_length = int(data_length)
	data_start = int(data_start)

	character = TypicalCharacter.query.paginate((data_start / data_length) + 1, data_length, False).items

	if s_search == '':
		character = TypicalCharacter.query.paginate((data_start / data_length) + 1, data_length, False).items
		count = TypicalCharacter.query.filter().count()
	else:
		character = TypicalCharacter.query.filter(TypicalCharacter.screen_name.like("%"+s_search+"%")).paginate((data_start / data_length) + 1, data_length, False).items
		count = TypicalCharacter.query.filter(TypicalCharacter.screen_name.like("%"+s_search+"%")).count()
	
	res = []
	for u in character:
		res.append({
			"id": str(u.id),
			"screen_name": u.screen_name,
			"user_id": u.user_id,
			"created_at": u.created_at,
			"finished_at": u.finished_at,
			"admin_id": u.admin_id
		})

	return jsonify({'aaData': res, 'iTotalDisplayRecords': count})


'''
删除新增典型人物（包括 mysql 数据库和 MongoDB 数据库）
'''
@verify
def typical_character_newdelete():
	user_id = request.form['user_id']
	TypicalCharacter.query.filter(TypicalCharacter.user_id == user_id).delete()

	db = MongoDB().connect()
	collect = db['typical']

	collect.delete_one({'_id': long(user_id)})

	collect = db['relation']
	collect.delete_one({'_id': long(user_id)})
	
	cql = '''MATCH (a:Typical{user_id:%d})-[r:following]-(b) DETACH delete a, r''' % long(user_id)
	graph.run(cql)

	return jsonify({'status': 1})


@verify
def modify_category():
	user_id = request.form['user_id']
	category = request.form['category']

	categories = ["Entertainment", "Agriculture", "Sports", "Religion", "Military", "Politics", "Education", "Technology", "Economy"]

	if not user_id or category not in categories:
		return jsonify({'status': 0})

	db = MongoDB().connect()
	collect = db['typical']

	collect.update_one({'_id': long(user_id)}, {"$set": {"category": category}})

	return jsonify({'status': 1})


'''
下载用户画像XML文件
'''
@verify
def download_user_xml(user_id):
	db = MongoDB().connect()
	collect = db['typical']

	user = collect.find_one({'_id': long(user_id)})
	file_name = generate_user_xml(user)

	response = make_response(send_file(file_name))
	response.headers["Content-Disposition"] = "attachment; filename=%s.xml" % user['screen_name']

	return response

@verify
def download_interest_tags(user_id):
	db = MongoDB().connect()
	collect = db['typical']

	user = collect.find_one({'_id': long(user_id)}, {'interest_tags': 1, 'screen_name': 1})
	
	file_name = tag_cloud.generate_tag_cloud(user['interest_tags'], user['_id'])

	response = make_response(send_file(file_name))
	response.headers["Content-Disposition"] = "attachment; filename=%s_interest_tags.png" % user['screen_name']

	return response


'''
数据统计
'''
@verify
def typical_data_statistics():
	db = MongoDB().connect()
	collect = db['typical']

	users = collect.find({}, {'category': 1, '_id': 0, 'influence_score': 1})

	category = {
		'Politics': 0,
		'Religion': 0,
		'Military': 0,
		'Economy': 0,
		'Technology': 0,
		'Education': 0,
		'Agriculture': 0,
		'Entertainment': 0,
		'Sports': 0
	}

	influence = {}

	for i in range(15):
		influence[str(i * 10)] = 0

	for item in users:
		category[item['category']] += 1

		s = str(int(item['influence_score'] / 10) * 10)

		if int(s) >= 150:
			if not influence.has_key(s):
				influence[s] = 1
			else:
				influence[s] += 1

		else:
			influence[s] += 1

	return render_template('portrayal/typical_data_statistics.html', category = category, influence = influence)


'''
错误统计
'''
@verify
def typical_category_statistics():
	db = MongoDB().connect()
	collect = db['typical']

	total_count = collect.find({}, {}).count()

	users = collect.find({}, {'category': 1, '_id': 0, 'category_score': 1})

	category_name = ['Politics', 'Religion', 'Military', 'Economy', 'Technology', 'Education', 'Agriculture', 'Entertainment', 'Sports']
	category = {}

	for item in category_name:
		category[item] = {
			'count': 0,
			'error_count': 0,
			'sub_error_count': 0,
			'error_classified_count': 0,
			'error_distribution': {

			}
		}

		for name in category_name:
			category[item]['error_distribution'][name] = 0

	for item in category:
		del category[item]['error_distribution'][item]


	error_count = 0
	sub_error_count = 0

	for item in users:
		category[item['category']]['count'] += 1
		category_score = item['category_score']
		max_category = max(category_score, key = category_score.get)

		if max_category != item['category']:
			category[item['category']]['error_distribution'][max_category] += 1
			category[max_category]['error_classified_count'] += 1

			error_count += 1
			category[item['category']]['error_count'] += 1

			category_score[max_category] = 0
			max_category = max(category_score, key = category_score.get)

			if max_category != item['category']:
				sub_error_count += 1
				category[item['category']]['sub_error_count'] += 1

	for item in category:
		correct_count = category[item]['count'] - category[item]['error_count']
		category[item]['correct_count'] = correct_count
		category[item]['recall'] = correct_count * 1.0 / category[item]['count']
		category[item]['precision'] = correct_count * 1.0 / (correct_count + category[item]['error_classified_count'])
		category[item]['f_score'] = 2 * category[item]['recall'] * category[item]['precision'] / (category[item]['recall'] + category[item]['precision'])
		category[item]['accuracy'] = (correct_count + total_count - category[item]['count'] - category[item]['error_classified_count']) * 1.0 / total_count
		category[item]['easy_wrong_category'] = max(category[item]['error_distribution'], key = category[item]['error_distribution'].get)

	average_recall = 0
	average_precision = 0
	average_fscore = 0
	average_accuracy = 0

	for item in category:
		average_recall += category[item]['recall'] * category[item]['count'] / total_count
		average_precision += category[item]['precision'] * category[item]['count'] / total_count
		average_fscore += category[item]['f_score'] * category[item]['count'] / total_count
		average_accuracy += category[item]['accuracy'] * category[item]['count'] / total_count


	return render_template('portrayal/typical_category_statistics.html', category = category, total_count = total_count, error_count = error_count, \
	average_accuracy = average_accuracy, sub_error_count = sub_error_count, average_recall = average_recall, average_precision = average_precision, average_fscore = average_fscore)