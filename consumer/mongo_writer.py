"""
MongoDB Writer
"""
from database.mongodb import MongoDB
from database.collections import LOGIN_COLLECTION


class MongoWriter:

    def __init__(self):
        self.collection = MongoDB().get_collection(
            LOGIN_COLLECTION
        )
    def insert_event(self, event):
        self.collection.insert_one(event)