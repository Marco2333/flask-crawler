from pymongo import MongoClient

class MongoDB:
	def connect(self, db_name = 'twitter'):
		client = MongoClient('127.0.0.1', 27017)
		db = client[db_name]
		self.db = db

		return db

	# def close(self):

