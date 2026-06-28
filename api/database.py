"""
MongoDB connection for the SecureCommerce-AI FastAPI backend.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class Database:

    def __init__(self):
        uri = (
            f"mongodb://"
            f"{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
            f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@"
            f"{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/"
        )

        self.client = MongoClient(
            uri,
            serverSelectionTimeoutMS=3000
        )

        self.db = self.client[
            os.getenv("MONGO_DATABASE", "securecommerce_ai")
        ]


database = Database()