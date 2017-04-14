import time
import threading

from app import config
# from config import THREAD_NUM
from twitter import error
from app.api import ApiList, ApiCount
# from app.database import Mysql

class BasicinfoCrawler:
	def __init__(self):
		self.api_index = 0
		
	def get_user(self,
				user_id = None, 
				screen_name = None, 
				include_entities = False):

		if user_id == None and screen_name == None:
			return None
		
		print screen_name
			
		api = ApiList[self.api_index]
		self.api_index = (self.api_index + 1) / ApiCount

		user = api.GetUser(user_id = user_id,	
						   screen_name = screen_name, 
						   include_entities = include_entities)

		return user


	def get_all_users(user_list = None, 
					  include_entities = True):		

		if len(user_list) == 0:
			return

		i = 0
		thread_pool = []
		self.lock = threading.Lock()

		while i < THREAD_NUM:

			threads.append(threading.Thread(target = get_users_thread, 
											args = (include_entities,)))
			craw_thread.start()
			thread_pool.append(craw_thread)
			i = i + 1

		for thread in thread_pool:
			thread.join()

	def get_users_thread(user_list = None, include_entities = True):
		sleep_count = 0
		lock = self.lock
		api_index = self.api_index
		mysql = Mysql()
		mysql.connect()

		while len(user_list) > 0:
			if lock.acquire():
				user_id = user_list.pop(0)
				lock.release()

			api = ApiList[api_index]
			api_index = (api_index + 1) / ApiCount

			try:
				user = api.GetUser(user_id = user_id,	
								   screen_name = screen_name, 
								   include_entities = include_entities)

			except error.TwitterError as te:
				if te.message[0]['code'] == 88:
					sleep_count += 1
					if sleep_count == ApiCount:
						print "sleeping..."
						sleep_count = 0
						time.sleep(700)
					continue
				else:
					continue
			except Exception as e:	
				continue

			try:
				is_translator = 0
				if hasattr(user, "is_translator"):
					is_translator = 1 if user.is_translator else 0

				name = user.name.replace("'","\\'")
				location = user.location.replace("'","\\'") if user.description else ''
				description = user.description.replace("'","\\'") if user.description else ''
				protected = 1 if user.protected else 0
				verified = 1 if user.verified else 0
				geo_enabled = 1 if user.geo_enabled else 0
				listed_count = user.listed_count if user.listed_count else 0
				default_profile_image = 1 if user.default_profile_image else 0 

				sql = """INSERT INTO user_fill_3(user_id, screen_name, name, location, created_at, description, statuses_count, friends_count, 
						followers_count, favourites_count, lang, protected, time_zone, verified, utc_offset, geo_enabled, listed_count,
						is_translator, default_profile_image, profile_background_color, profile_sidebar_fill_color, profile_image_url, crawler_date) VALUES
						('%s', '%s', '%s', '%s', '%s', '%s', %d, %d, %d, %d, '%s', %d, '%s', %d, '%s', %d, %d, %d, %d,
						'%s', '%s', '%s', '%s')""" % (user_id, user.screen_name, name, location, user.created_at, description, user.statuses_count, \
						user.friends_count, user.followers_count, user.favourites_count, user.lang, protected, user.time_zone, verified, \
						user.utc_offset, geo_enabled, listed_count, is_translator, default_profile_image, user.profile_background_color, \
						user.profile_sidebar_fill_color, user.profile_image_url, time.strftime('%Y-%m-%d',time.localtime(time.time()))) 

			except Exception as e:
				continue

			try:
				mysql.execute(sql)
			except Exception as e:
				continue

		mysql.close()