"""
Application configuration.
"""
import os
from dotenv import load_dotenv
load_dotenv()
class AppConfig:
    PROJECT_NAME = os.getenv("PROJECT_NAME")
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    LOG_LEVEL = os.getenv("LOG_LEVEL")
    LOGIN_EVENTS_PER_SECOND = int(
        os.getenv("LOGIN_EVENTS_PER_SECOND", 5)
    )