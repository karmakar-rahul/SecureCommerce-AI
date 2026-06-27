"""
MongoDB Writer for SecureCommerce AI.
"""

from database.mongodb import MongoDB
from database.collections import LOGIN_COLLECTION


class MongoWriter:

    def __init__(self):
        self.collection = MongoDB().get_collection(LOGIN_COLLECTION)
    def insert_event(self, event: dict) -> None:
        self.collection.insert_one(event)

    # new batch insert 
    def insert_many(self, events: list[dict]) -> None:
        if not events:
            return
        self.collection.insert_many(events, ordered=False)