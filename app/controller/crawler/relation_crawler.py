# -*- coding:utf-8 -*-
import time
import threading

from app import app
from twitter import error
from api import API_COUNT, GET_API


class RelationCrawler:
	
	def show_friendship(source_user_id, source_screen_name, target_user_id, target_screen_name):
		if not source_user_id and not source_screen_name:
			return None

		if not target_user_id and not target_screen_name:
			return None

		return GET_API().ShowFriendship(source_user_id, source_screen_name, target_user_id, target_screen_name)


	def get_friendids(self,
                      user_id = None,
                      screen_name = None,
                      cursor = None,
                      total_count = 30000):

		if user_id == None and screen_name == None:
			return None

		return GET_API().GetFriendIDs(user_id = user_id,
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

		return GET_API().GetFriendIDsPaged(user_id = user_id,
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

		return GET_API().GetFriends(user_id = user_id,
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

		return GET_API().GetFriendsPaged(user_id = user_id,
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

		while cursor != 0:
			try:
				out = GET_API().GetFriendIDsPaged(user_id = user_id, cursor = cursor, count = 5000)
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

		return GET_API().GetFollowerIDs(user_id = user_id,
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

		return GET_API().GetFollowerIDsPaged(user_id = user_id,
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

		return GET_API().GetFollowers(user_id = user_id,
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

		return GET_API().GetFollowersPaged(user_id = user_id,
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

		api = GET_API

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