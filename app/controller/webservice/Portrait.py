#coding=utf-8
import threading

from flask import request, jsonify
from Crawling import get_user_all_info
from ..crawler.database import MongoDB
from ..portrayal.user_profile import user_profile


def crawl_profile():
	user_id = request.args.get('user_id')
	screen_name = request.args.get('screen_name')

	if not user_id and not screen_name:
		return jsonify({'status': 0})

	user_list = request.args.get('user_list')
	search_type = request.args.get('search_type')
	
	th = threading.Thread(target = crawl_profile_thread, args = (user_id, screen_name, user_list, search_type))
	th.start()

	return jsonify({'status': 1})


def crawl_profile_thread(user_id, screen_name, user_list = None, search_type = 'screen_name'):
	db = MongoDB().connect()
	collect = db['profile']

	print screen_name

	if not user_list:
		user_info = get_user_all_info(user_id, screen_name)

		if not user_info:
			return

		print 1
		user_info = user_profile(user_info)
		del user_info['tweets']
		print user_info
		collect.insert_one(user_info)
	else:
		user_list = user_list.split(',')

		for item in user_list:
			try:
				if search_type == 'user_id':
					user_info = get_user_all_info(user_id = item)

					if not user_info:
						continue

					user_info = user_profile(user_info)
				
				else:
					user_info = get_user_all_info(screen_name = item)

					if not user_info:
						continue

					user_info = user_profile(user_info)

				collect.insert_one(user_info)
			except Exception as e:
				print e
				continue