# -*- coding: utf-8 -*-
import time

from flask import request, jsonify
from ..crawler.tweets_crawler import TweetsCrawler
from ..crawler.basicinfo_crawler import BasicinfoCrawler

tweets_crawler = TweetsCrawler()
basicinfo_crawler = BasicinfoCrawler()


'''
获取用户基础信息和推文信息，以字典形式返回
'''
def get_user_all_info(user_id = None, screen_name = None):
	user = basicinfo_crawler.get_user(user_id = user_id, screen_name = screen_name)

	if not user:
		return None

	tweets = tweets_crawler.get_user_all_timeline_return(user_id = user_id, screen_name = screen_name)

	if not tweets or len(tweets) == 0:
		return None

	return {
		'user_id': long(user.id),
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
		'time_zone': user.time_zone,
		'profile_image_url': user.profile_image_url,
		'listed_count': user.listed_count,
		'geo_enabled': user.geo_enabled,
		'profile_sidebar_fill_color': user.profile_sidebar_fill_color,
		'tweets': tweets
	}


def get_user():
	user_id = request.args.get('user_id')
	screen_name = request.args.get('screen_name')
	
	try:
		user = basicinfo_crawler.get_user(user_id = user_id, screen_name = screen_name)
	except Exception as e:
		print e
		return jsonify({'status': 0})

	if not user:
		return jsonify({'status': 0})

	user = {
		'user_id': long(user.id),
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
		'listed_count': user.listed_count,
		'geo_enabled': user.geo_enabled,
		'is_translator': user.is_translator,
		'profile_sidebar_fill_color': user.profile_sidebar_fill_color
	}

	return jsonify({'status': 1, 'user': user})


def get_user_timeline():
	user_id = request.args.get('user_id')
	screen_name = request.args.get('screen_name')
	since_id = request.args.get('since_id')
	max_id = request.args.get('max_id')
	count = request.args.get('count')
	include_rts = request.args.get('include_rts')
	exclude_replies = request.args.get('exclude_replies')

	try:
		tweets = tweets_crawler.get_user_timeline(user_id = user_id,
												  screen_name = screen_name,
												  since_id = since_id,
												  max_id = max_id,
												  count = count,
												  include_rts = include_rts,
												  exclude_replies = exclude_replies)
	except Exception as e:
		print e
		return jsonify({'status': 0})

	if not tweets:
		return jsonify({'status': 0})

	tweets_list = []
	for tt in tweets:
		tweet = tweets_crawler.tweetobj_to_dict(tt)
		try:
			tweets_list.append(tweet)
		except Exception as e:
			continue
	
	return jsonify({'status': 1, 'tweets': tweets_list})