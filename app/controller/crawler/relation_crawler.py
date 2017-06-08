# -*- coding:utf-8 -*-
import time
import threading

from app import app
from twitter import error
from api import Api, API_COUNT
# from app.database import db


class RelationCrawler:
	api = Api().get_api
	
	def show_friendship(source_user_id, source_screen_name, target_user_id, target_screen_name):
		if not source_user_id and not source_screen_name:
			return None

		if not target_user_id and not target_screen_name:
			return None

		return self.api().ShowFriendship(source_user_id, source_screen_name, target_user_id, target_screen_name)


	def get_friendids(self,
                      user_id = None,
                      screen_name = None,
                      cursor = None,
                      total_count = 30000):

		if user_id == None and screen_name == None:
			return None

		return self.api().GetFriendIDs(user_id = user_id,
				                       screen_name = screen_name,
				                       cursor = cursor,
				                       total_count = total_count)


	def get_friendids_paged(self,
	                        user_id = None,
	                        screen_name = None,
	                        cursor = -1,
	                        stringify_ids = False,
	                        count = 5000):

		if user_id == None and screen_name == None:
			return None

		return self.api().GetFriendIDsPaged(user_id = user_id,
					                        screen_name = screen_name,
					                        cursor = cursor,
					                        count = count,
					                        stringify_ids = stringify_ids)


	def get_friends(self,
                    user_id = None,
                    screen_name = None,
                    cursor = None,
                    total_count = None,
                    skip_status = True,
                    include_user_entities = True):

		if user_id == None and screen_name == None:
			return None

		return self.api().GetFriends(user_id = user_id,
			                         screen_name = screen_name,
			                  	     cursor = cursor,
			                  	     total_count = total_count,
			                  	     skip_status = skip_status,
			                  	     include_user_entities = include_user_entities)
		

	def get_friends_paged(self,
                   		  user_id = None,
                          screen_name = None,
                          cursor = -1,
                          count = 200,
                          skip_status = True,
                          include_user_entities = True):

		if user_id == None and screen_name == None:
			return None

		return self.api().GetFriendsPaged(user_id = user_id,
				                       	  screen_name = screen_name,
				                       	  cursor = cursor,
				                       	  count = count,
				                       	  skip_status = skip_status,
				                       	  include_user_entities = include_user_entities)


	def get_all_friendids(user_id = None, screen_name = None):

		if user_id == None and screen_name == None:
			return None

		cursor = -1
		sleep_count = 0

		api = self.api

		while cursor != 0:
			try:
				out = api().GetFriendIDsPaged(user_id = user_id, cursor = cursor, count = 5000)
				cursor = out[0]
				friend_list = out[2]
			except error.TwitterError as te:
				if te.message[0]['code'] == 88:
					sleep_count += 1
					if sleep_count == API_COUNT:
						print "sleeping..."
						sleep_count = 0
						time.sleep(700)
					continue
				else:
					continue

			except Exception as e:
				continue


	def get_followerids(self,
	                    user_id = None,
	                    screen_name = None,
	                    cursor = None,
	                    total_count = 30000):

		if user_id == None and screen_name == None:
			return None

		return self.api().GetFollowerIDs(user_id = user_id,
					                     screen_name = screen_name,
					              	     cursor = cursor,
					               	     total_count = total_count)


	def get_followerids_paged(self,
		                      user_id = None,
		                      screen_name = None,
		                      cursor = -1,
		                      stringify_ids = False,
		                      count = 5000):

		if user_id == None and screen_name == None:
			return None

		return self.api().GetFollowerIDsPaged(user_id = user_id,
						                 	  screen_name = screen_name,
						                 	  cursor = cursor,
						                 	  count = count,
						                 	  stringify_ids = stringify_ids)


	def get_followers(self,
	                  user_id = None,
	                  screen_name = None,
	                  cursor = None,
	                  total_count = None,
	                  skip_status = True,
	                  include_user_entities = True):

		if user_id == None and screen_name == None:
			return None

		return self.api().GetFollowers(user_id = user_id,
				                       screen_name = screen_name,
				                       cursor = cursor,
				                       total_count = total_count,
				                       skip_status = skip_status,
				                       include_user_entities = include_user_entities)


	def get_followers_paged(self,
	                   		user_id = None,
	                        screen_name = None,
	                        cursor = -1,
	                        count = 200,
	                        skip_status = True,
	                        include_user_entities = True):

		if user_id == None and screen_name == None:
			return None

		return self.api().GetFollowersPaged(user_id = user_id,
					                        screen_name = screen_name,
					                        cursor = cursor,
					                        count = count,
					                        skip_status = skip_status,
					                        include_user_entities = include_user_entities)


	def get_all_followersids(user_id = None, screen_name = None):

		if user_id == None and screen_name == None:
			return None

		cursor = -1
		sleep_count = 0

		api = self.api

		while cursor != 0:
			try:
				out = api().GetFollowersIDsPaged(user_id = user_id, cursor = cursor, count = 5000)
				cursor = out[0]
				friend_list = out[2]

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