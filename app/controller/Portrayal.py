import re
import time
import json
import urllib
import threading

from app import app
from app.database import db
from twitter import error
from crawler.db import MongoDB
from app.controller import verify
from app.models import TypicalCharacter
from flask import request, render_template, jsonify, session, redirect, url_for

from portrayal import UserProfile

from crawler.basicinfo_crawler import BasicinfoCrawler
from crawler.relation_crawler import RelationCrawler
from crawler.tweets_crawler import TweetsCrawler

basicinfo_crawler = BasicinfoCrawler()
tweets_crawler = TweetsCrawler()

@verify
def typical_character_list():
	return render_template('portrayal/typical_character_list.html')

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

@verify
def get_typical_friends(user_id):
	sql = "select target_user_id from relation where following = 'True' and source_user_id = '%s'" % user_id
	following = db.session.execute(sql)

	following_res = set()
	for item in following:
		following_res.add(item[0])
	
	sql = "select source_user_id from relation where followed_by = 'True' and target_user_id = '%s'" % user_id
	following = db.session.execute(sql)

	for item in following:
		following_res.add(item[0])

	count = len(following_res)
	data = json.loads(request.form['aoData'])

	for item in data:
		if item['name'] == 'iDisplayLength':
			data_length = item['value']

		if item['name'] == 'iDisplayStart':
			data_start = item['value'];      
	
	data_length = int(data_length)
	data_start = int(data_start)

	following_res = list(following_res)[data_start : data_start + data_length]

	mdb = MongoDB().connect()
	collect = mdb['typical']

	res = []
	for user_id in following_res:
		user = collect.find_one({'_id': long(user_id)})
		res.append({
			"user_id": user['_id'],
			"screen_name": user['screen_name'],
			"statuses_count": user['statuses_count'],
			"friends_count": user['friends_count'],
			"followers_count": user['followers_count'],
			"category": user['category'],
			"influence_score": user['influence_score']
		})


	return jsonify({'aaData': res, 'iTotalDisplayRecords': count})


@verify
def get_typical_followers(user_id):
	sql = "select target_user_id from relation where followed_by = 'True' and source_user_id = '%s'" % user_id
	followed = db.session.execute(sql)

	followed_res = set()
	for item in followed:
		followed_res.add(item[0])
	
	sql = "select source_user_id from relation where following = 'True' and target_user_id = '%s'" % user_id
	followed = db.session.execute(sql)

	for item in followed:
		followed_res.add(item[0])

	count = len(followed_res)
	data = json.loads(request.form['aoData'])

	for item in data:
		if item['name'] == 'iDisplayLength':
			data_length = item['value']

		if item['name'] == 'iDisplayStart':
			data_start = item['value'];      
	
	data_length = int(data_length)
	data_start = int(data_start)

	followed_res = list(followed_res)[data_start : data_start + data_length]

	mdb = MongoDB().connect()
	collect = mdb['typical']

	res = []
	for user_id in followed_res:
		user = collect.find_one({'_id': long(user_id)})
		res.append({
			"user_id": user['_id'],
			"screen_name": user['screen_name'],
			"statuses_count": user['statuses_count'],
			"friends_count": user['friends_count'],
			"followers_count": user['followers_count'],
			"category": user['category'],
			"influence_score": user['influence_score']
		})


	return jsonify({'aaData': res, 'iTotalDisplayRecords': count})

@verify
def get_typical_dfans(user_id):
	dfans = set()
	sql = "select source_user_id, target_user_id from relation where following = 'True' and followed_by = 'True' and (target_user_id = '%s' or source_user_id = '%s')"% (user_id, user_id)
	realtion = db.session.execute(sql)

	for item in realtion:
		dfans.add(item[0])
		dfans.add(item[1])

	if user_id + '' in dfans:
		dfans.remove(user_id + '')

	count = len(dfans)

	data = json.loads(request.form['aoData'])

	for item in data:
		if item['name'] == 'iDisplayLength':
			data_length = item['value']

		if item['name'] == 'iDisplayStart':
			data_start = item['value'];      
	
	data_length = int(data_length)
	data_start = int(data_start)

	dfans = list(dfans)[data_start : data_start + data_length]

	mdb = MongoDB().connect()
	collect = mdb['typical']

	res = []
	for user_id in dfans:
		user = collect.find_one({'_id': long(user_id)})
		res.append({
			"user_id": user['_id'],
			"screen_name": user['screen_name'],
			"statuses_count": user['statuses_count'],
			"friends_count": user['friends_count'],
			"followers_count": user['followers_count'],
			"category": user['category'],
			"influence_score": user['influence_score']
		})

	return jsonify({'aaData': res, 'iTotalDisplayRecords': count})


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

@verify
def typical_character_detail(user_id):
	mdb = MongoDB().connect()
	collect = mdb['typical']

	user = collect.find_one({'_id': long(user_id)})

	user['ratio'] = user['followers_count'] if not user['friends_count'] else round(user['followers_count'] * 1.0 / user['friends_count'], 2)
	user['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(user['created_at'].replace('+0000 ','')))
	user['crawler_date'] = str(user['crawler_date']).split(" ")[0]
	user['psy_seq'] = user['psy_seq'].replace('pos', '1').replace("neg", "-1")

	get_image(user['profile_image_url'], user['screen_name'])

	related_users = collect.find({'category': user['category'], '_id': {"$ne": user['_id']}}).limit(6)

	ru_arr = []
	for ru in related_users:
		ru_arr.append({
			'_id': ru['_id'],
			'screen_name': ru['screen_name'],
			'name': ru['name']
		})
		get_image(ru['profile_image_url'], ru['screen_name'])

	return render_template('portrayal/typical_character_detail.html', user = user, related_users = ru_arr)


def get_image(url, screen_name):
	urllib.urlretrieve(url.replace('normal.','bigger.'), 'app/static/profile/%s.jpg' % screen_name)

@verify
def typical_character_add():
	return render_template('portrayal/typical_character_add.html')

@verify
def typical_character_add_submit():
	screen_name = request.form['screen_name']

	if(screen_name == ''):
		return jsonify({'status': 0})

	status = 1

	try:
		user = basicinfo_crawler.get_user(screen_name = screen_name)
	except error.TwitterError as te:
		if te.message[0]['code'] == 88:
			status = "ratelimit"

		elif te.message[0]['code'] == 63:
			status = "suspend"

		elif te.message[0]['code'] == 50:
			status = "notfound"
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


def portrayal_thread(user, task_id):
	tweet_list = tweets_crawler.get_user_all_timeline_temp(screen_name = user['screen_name'])
	user['tweets'] = tweet_list

	out = UserProfile.UserProfileFromDic(user)

	db = MongoDB().connect()
	collect = db['typical']

	cur_user = collect.find_one({'_id': long(out['userid'])})

	out['_id'] = out['userid']
	del out['userid']
	del out['tweets']

	if cur_user == None:
		collect.insert_one(out)

	else:
		collect.remove({'_id': long(out['_id'])})
		collect.insert_one(out)

	with app.app_context():
		TypicalCharacter.query.filter(TypicalCharacter.id == task_id).update({'finished_at': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))})

@verify
def typical_character_newlist():
	return render_template('portrayal/typical_character_newlist.html')

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

@verify
def typical_character_newdelete():
	user_id = request.form['user_id']
	TypicalCharacter.query.filter(TypicalCharacter.user_id == user_id).delete()

	db = MongoDB().connect()
	collect = db['typical']

	collect.delete_one({'_id': long(user_id)})

	return jsonify({'status': 1})
