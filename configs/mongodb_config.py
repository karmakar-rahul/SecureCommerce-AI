"""
MongoDB configuration.
"""

import os
from dotenv import load_dotenv

load_dotenv()
class MongoConfig:

    HOST = os.getenv("MONGO_HOST", "localhost")
    PORT = int(os.getenv("MONGO_PORT", 27017))
    USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    DATABASE = os.getenv("MONGO_DATABASE", "securecommerce_ai")