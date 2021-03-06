#coding=utf-8
import threading

from flask import request, jsonify
from Crawling import get_user_all_info
from ..crawler.database import MongoDB
from ..portrayal.user_profile import user_profile


def crawl_profile_sync():
	user_id = request.args.get('user_id')
	screen_name = request.args.get('screen_name')

	if not user_id and not screen_name:
		return jsonify({'status': 0})

	user_info = get_user_all_info(user_id, screen_name)

	if not user_info or len(user_info['tweets']) == 0:
		return jsonify({'status': 0})

	try:
		user_info = user_profile(user_info)
	except Exception as e:
		print e
		return jsonify({'status': 0})

	del user_info['tweets']

	return jsonify({'status': 1, 'user': user_info})


def crawl_profile():
	user_id = request.args.get('user_id')
	screen_name = request.args.get('screen_name')
	user_list = request.args.get('user_list')

	if not user_id and not screen_name and not user_list:
		return jsonify({'status': 0})

	search_type = request.args.get('search_type')
	
	th = threading.Thread(target = crawl_profile_thread, args = (user_id, screen_name, user_list, search_type))
	th.start()

	return jsonify({'status': 1})


def crawl_profile_thread(user_id, screen_name, user_list = None, search_type = 'screen_name'):
	db = MongoDB().connect()
	collect = db['profile']

	if not user_list:
		user_info = get_user_all_info(user_id, screen_name)

		if not user_info or len(user_info['tweets']) == 0:
			return
		
		try:
			user_info = user_profile(user_info)
		except Exception as e:
			print e
			return

		user_info['_id'] = long(user_info['user_id'])
		del user_info['user_id']

		collect.delete_one({'_id': user_info['_id']})
		collect.insert_one(user_info)
	else:
		user_list = user_list.split(',')

		for item in user_list:
			try:
				if search_type == 'user_id':
					user_info = get_user_all_info(user_id = item)

				else:
					user_info = get_user_all_info(screen_name = item)

				if not user_info or len(user_info['tweets']) == 0:
					continue

				user_info = user_profile(user_info)

				user_info['_id'] = long(user_info['user_id'])
				del user_info['user_id']

				collect.delete_one({'_id': user_info['_id']})
				collect.insert_one(user_info)
			except Exception as e:
				print e
				continue