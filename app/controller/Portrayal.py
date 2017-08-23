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
from app.controller import verify
from app.models import TypicalCharacter
from flask import request, render_template, jsonify, session, make_response, send_file

from portrayal.XMLInteraction.GenerateXML import GenerateUserXml
from portrayal import UserProfile

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

	if s_search == '':
		users = collect.find().skip(data_start).limit(data_length)
		count = collect.find().count()
	else:
		pattern = re.compile(".*" + s_search + ".*")
		query = {"$or":[{"name": pattern}, {"category": pattern}, {"interest_tags": pattern}, 
		{"screen_name": pattern}, {"description": pattern}, {"location": pattern}, {"name": pattern}]}

		users = collect.find(query).skip(data_start).limit(data_length)
		count = collect.find(query).count()

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

	cql = '''MATCH(a{user_id:%s})-[:following*0..%s]->(f) return count(distinct f) as count''' % (user_id, deepth)
	res = graph.data(cql)
	total = res[0]['count']

	cql = '''MATCH(a{user_id:%s})-[:following*0..%s]->(f) return distinct f.user_id as user_id,
			f.screen_name as screen_name, f.statuses_count as statuses_count, f.friends_count as friends_count,
			f.followers_count as followers_count, f.influence_score as influence_score, f.category as category 
			skip %s limit %s''' % (user_id, deepth, data_start, data_length)
	res = graph.data(cql)

	friends = []

	for item in res:
		friends.append({
			'user_id': item['user_id'],
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

	cql = '''Match(f)-[:following*0..%s]->(a{user_id:%s}) return count(distinct f) as count''' % (deepth, user_id)
	res = graph.data(cql)
	total = res[0]['count']

	cql = '''Match(f)-[:following*0..%s]->(a{user_id:%s}) return distinct f.user_id as user_id,
			f.screen_name as screen_name, f.statuses_count as statuses_count, f.friends_count as friends_count,
			f.followers_count as followers_count, f.influence_score as influence_score, f.category as category 
			skip %s limit %s''' % (deepth, user_id, data_start, data_length)
	res = graph.data(cql)

	friends = []

	for item in res:
		friends.append({
			'user_id': item['user_id'],
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
			'user_id': item['user_id'],
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
	cql = '''MATCH path = allShortestPaths((a:Typical { user_id: %s})<-[:following*..%s]-
			(b:Typical { user_id: %s})) RETURN path''' % (user_id, deepth, follower_id)

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
	cql = '''MATCH path = allShortestPaths((a:Typical { user_id: %s})-[:following*..%s]->
			(b:Typical { user_id: %s})) RETURN path''' % (user_id, deepth, friend_id)

	paths = graph.data(cql)

	res = []
	for item in paths:
		path = item['path']

		res.append(map(lambda x: {'name': x['screen_name']}, path.nodes()))

	return jsonify({"paths": res})


'''
获取典型人物关系，包括朋友、粉丝、互粉人物
'''
@verify
def get_typical_relation(user_id):
	sql = "select target_user_id from relation where following = 'True' and 'followed_by' = 'False' and source_user_id = '%s'" % user_id
	following = db.session.execute(sql)

	following_res = set()
	for item in following:
		following_res.add(item[0])
	
	sql = "select source_user_id from relation where followed_by = 'True' and following = 'False' and target_user_id = '%s'" % user_id
	following = db.session.execute(sql)

	for item in following:
		following_res.add(item[0])


	sql = "select target_user_id from relation where followed_by = 'True' and following = 'False' and source_user_id = '%s'" % user_id
	followed = db.session.execute(sql)

	followed_res = set()
	for item in followed:
		followed_res.add(item[0])
	
	sql = "select source_user_id from relation where following = 'True' and 'followed_by' = 'False' and target_user_id = '%s'" % user_id
	followed = db.session.execute(sql)

	for item in followed:
		followed_res.add(item[0])

	dfans = set()
	sql = "select source_user_id, target_user_id from relation where following = 'True' and 'followed_by' = 'True' and (target_user_id = '%s' or source_user_id = '%s')"% (user_id, user_id)
	followed = db.session.execute(sql)

	for item in followed:
		dfans.add(item[0])
		dfans.add(item[1])

	if user_id + '' in dfans:
		dfans.remove(user_id + '')

	user = {}
	user['friends'] = list(following_res)
	user['followers'] = list(followed_res)
	user['dfans'] = list(dfans)

	return jsonify(user)


'''
获取典型人物详情，包括人物基础信息、画像信息、关心信息
'''
@verify
def typical_character_detail(user_id):
	mdb = MongoDB().connect()
	collect = mdb['typical']

	user = collect.find_one({'_id': long(user_id)})
	
	user['ratio'] = user['followers_count'] if not user['friends_count'] else round(user['followers_count'] * 1.0 / user['friends_count'], 2)
	user['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(user['created_at'].replace('+0000 ','')))
	user['crawler_date'] = str(user['crawler_date']).split(" ")[0]
	user['psy_seq'] = user['psy_seq'].replace('pos', '1').replace("neg", "-1")

	s = ''
	for item in user['activity_list']:
		s += "," + str(item)
	user['activity_list'] = s[1:]

	get_image(user['profile_image_url'], user['screen_name'])

	related_users = collect.find({'category': user['category'], '_id': {"$ne": user['_id']}}).limit(10)

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
				'userid': user.id,
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

	out = UserProfile.UserProfileFromDic(user)

	db = MongoDB().connect()
	collect = db['typical']

	cur_user = collect.find_one({'_id': long(out['userid'])})

	out['_id'] = long(out['userid'])
	del out['userid']
	del out['tweets']

	if cur_user == None:
		collect.insert_one(out)

		th = threading.Thread(target = relation_thread, args = (out['_id'],))
		th.start()

	else:
		collect.delete_one({'_id': long(out['_id'])})
		collect.insert_one(out)

	with app.app_context():
		TypicalCharacter.query.filter(TypicalCharacter.id == task_id).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})


'''
标准人物样本库人物关系抓取
'''
def relation_thread(user_id):
	db = MongoDB().connect()
	collect = db['typical']

	user_id = long(user_id)
	stuids = collect.find({}, {'_id': 1})

	friends = []
	followers = []

	for item in stuids:
		relation = relation_crawler.show_friendship_sleep(source_user_id = user_id, target_user_id = item['_id'])
		
		if not relation:
			continue

		if relation['relationship']['source']['followed_by'] == True:
			followers.append(item['_id'])

		if relation['relationship']['source']['following'] == True:
			friends.append(item['_id'])

	for item in friends:
		pass

	for item in followers:
		pass


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

	return jsonify({'status': 1})


'''
下载用户画像XML文件
'''
@verify
def download_user_xml(user_id):
	db = MongoDB().connect()
	collect = db['typical']

	user = collect.find_one({'_id': long(user_id)})
	user['user_id'] = str(user['_id'])
	file_name = GenerateUserXml(user)

	response = make_response(send_file(file_name))
	response.headers["Content-Disposition"] = "attachment; filename=%s.xml" % user['screen_name']
	return response