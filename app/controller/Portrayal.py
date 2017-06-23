import re
import json

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
			"_id": u['_id'],
			"screen_name": u['screen_name'],
			"name": u['name'],
			"friends_count": u['friends_count'],
			"followers_count": u['followers_count'],
			"statuses_count": u['statuses_count'],
			"category": u['category'],
			"influence_score": round(u['influence_score'],3)
		})

	return jsonify({'aaData': res, 'iTotalDisplayRecords': count})