import time
import urllib
import json

from app.controller import verify
from app.models import Task
from twitter import error
from flask import request, render_template, jsonify, redirect, url_for

from crawler.basicinfo_crawler import BasicinfoCrawler
from crawler.relation_crawler import RelationCrawler
from crawler.tweets_crawler import TweetsCrawler

basicinfo_crawler = BasicinfoCrawler()
relation_crawler = RelationCrawler()
tweets_crawler = TweetsCrawler()


@verify
def user_search():
	return render_template('user_search.html')

@verify
def get_user_tweets():
	screen_name = request.form['screen_name']
	max_id = request.form['max_id']
	count = 30

	if max_id == '0':
		max_id = 1

	max_id = long(max_id) - 1
	tweets = tweets_crawler.get_user_timeline(screen_name = screen_name, max_id = max_id, count = count)

	res = []
	for i in range(len(tweets)):
		tweet = tweets[i]
		res.append({
			'id': tweet.id,
			'text':tweet.text,
			'created_at':tweet.created_at,
			'favorite_count':tweet.favorite_count,
			'retweet_count':tweet.retweet_count,
			'lang':tweet.lang,
			'source':tweet.source
		})

	return jsonify(res)

@verify
def user_profile(screen_name):
	user = basicinfo_crawler.get_user(screen_name = screen_name)
	friends = []
	followers = []
	try:
		friends = relation_crawler.get_friends(screen_name = screen_name, count = 30)
		for friend in friends:
			friend.created_at = time.strftime('%Y-%m-%d', time.strptime(friend.created_at.replace('+0000 ','')))
			if len(friend.description) > 28:
				friend.description = friend.description[0:28]
				friend.description += ' ...'

	except error.TwitterError as te:
		pass

	try:
		followers = relation_crawler.get_followers(screen_name = screen_name, count = 30)
		for follower in followers:
			follower.created_at = time.strftime('%Y-%m-%d', time.strptime(follower.created_at.replace('+0000 ','')))
			if len(follower.description) > 8:
				follower.description = follower.description[0:18]
				follower.description += ' ...'

	except error.TwitterError as te:
		pass

	# get_image(user.default_profile_image, screen_name)
	# print user.created_at
	# print time.strptime(user.created_at, '%a %b %d %H:%M:%S +0000 %Y')
	# print time.strftime('%Y-%m-%d', time.strptime(user.created_at))
	user.created_at = time.strftime('%Y-%m-%d', time.strptime(user.created_at.replace('+0000 ','')))

	# time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}
	return render_template('user_profile.html', user = user, followers = followers, friends = friends)

def getImage(url, screen_name):  
    urllib.urlretrieve(url, url_for('static',filename='profile/%s.jpg' % screen_name))  
     

@verify
def user_search_detail():
	data = json.loads(request.form['aoData'])

	for item in data:
		if item['name'] == 'sSearch':
			s_search = item['value']
			break

		# if data[i]['name'] == 'iDisplayStart':
		# 	data_start = data[i]['value']

		# if data[i]['name'] == 'iDisplayLength':
		# 	data_length == data[i]['value']

		# if data[i]['name'] == 'sEcho':
		# 	s_echo = data[i]['value']

	print s_search	


	return jsonify({'data': []})
	# $data = json_decode(html_entity_decode(I('aoData')),true);
	#     if( strlen(trim($sSearch)) == 0 ) {  
	#         $count = $Model->query("select count(*) as ct from rt_teacher");
	#         $infolist = $Model->query("select * from rt_teacher limit ".$dataStart.",".$dataLength);
	#     }
	#     else {
	#         $field = array("employee_id","name","gender","nation","date_format(birth_date,'%Y-%c-%d')","date_format(work_date,'%Y-%c-%d')","date_format(submit_date,'%Y-%c-%d')","positional_title","education_background",
	#             "politics_status","homephone","mobilephone","rank","identity_card_number","department",
	#             "home_address","status","native_place","physical_condition","tips1", "tips2", "tips3" );
	#         $sqlstring = "select * from rt_teacher where ";
	#         for ($i=0; $i < count($field)-1; $i++) { 
	#             $sqlstring = $sqlstring.$field[$i]." like "."'%".$sSearch."%' "."or "     ;
	#         }
	#         $sqlstring= $sqlstring."tips3"." like "."'%".$sSearch."%' ";
	#         $count = $Model->query(str_replace("*","count(*) as ct",$sqlstring));
	#         $infolist = $Model->query($sqlstring." limit ".$dataStart.",".$dataLength);
	#     }
	#     $res['sEcho'] = $sEcho;
	#     $res['status'] = 1;
	#     $res['iTotalRecords'] = $count[0]['ct'];
	#     $res['iTotalDisplayRecords'] = $count[0]['ct'];
	#     $res['aaData'] = $infolist;
	#     $this->ajaxReturn($res);
	# }

@verify
def relation_search():
	return render_template('relation_search.html')

@verify
def task_list():
	tasks = Task.query.filter().all()

	for task in tasks:
		if len(task.remark) > 8:
			task.remark = task.remark[0:8]
			task.remark += ' ...'

	return render_template('task_list.html', tasks = tasks)

@verify
def tweets_search():
	return render_template('tweets_search.html')