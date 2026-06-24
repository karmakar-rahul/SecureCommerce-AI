"""
MongoDB Connection
"""
from pymongo import MongoClient
from configs.mongodb_config import MongoConfig


class MongoDB:
    def __init__(self):
        uri = (
            f"mongodb://{MongoConfig.USERNAME}:"
            f"{MongoConfig.PASSWORD}@"
            f"{MongoConfig.HOST}:"
            f"{MongoConfig.PORT}/"
        )

        self.client = MongoClient(uri)
        self.db = self.client[MongoConfig.DATABASE]

    def get_collection(self, name):
        return self.db[name]