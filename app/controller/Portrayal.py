import re
import time
import json
import urllib
import threading

from twitter import error
from crawler.db import MongoDB
from app.controller import verify
from flask import request, render_template, jsonify, session, redirect, url_for

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
def typical_character_detail(user_id):
	db = MongoDB().connect()
	collect = db['typical']

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
			threading.Thread(target = portrayal_thread, args = (user,))

	return jsonify({'status': status})


def portrayal_thread(user):
	tweet_list = tweets_crawler.get_user_all_timeline_temp(screen_name = user.screen_name)
	user['tweets'] = tweet_list
	