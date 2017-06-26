import re
import time
import json
import urllib

from crawler.db import MongoDB
from app.controller import verify
from flask import request, render_template, jsonify, session, redirect, url_for

@verify
def typical_character_list():
	return render_template('portrayal/typical_character_list.html')

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

def typical_character_detail(user_id):
	db = MongoDB().connect()
	collect = db['typical']

	user = collect.find_one({'_id': long(user_id)})

	user['ratio'] = user['followers_count'] if not  user['friends_count'] else round(user['followers_count'] * 1.0 / user['friends_count'], 2)
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