# -*- coding:utf-8 -*-
from py2neo import Graph
from pymongo import MongoClient


class MongoDB:
	def connect(self, db_name = 'twitter'):
		client = MongoClient('127.0.0.1', 27017)  

		db = client[db_name]
		db.authenticate("twitteruser", "aliyunmongodb_")

		self.db = db

		return db


class Neo4j:
	def connect(self):
		graph = Graph('http://localhost:7474', 
				     username = 'neo4j', 
				     password = 'aliyunneo4j@')

		return graph