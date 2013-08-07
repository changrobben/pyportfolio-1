
import pymongo
import datetime
from pymongo import MongoClient


def get_db():
	client = MongoClient()
	db = client['myweb']
	return (db, client)



