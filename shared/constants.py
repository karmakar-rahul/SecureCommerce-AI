"""
Global constants used throughout SecureCommerce AI.
"""


# Project Information
PROJECT_NAME = "SecureCommerce AI"
PROJECT_VERSION = "1.0.0"


# Kafka
LOGIN_TOPIC = "login_events"


# MongoDB Collections
COLLECTION_USERS = "users"
COLLECTION_LOGIN_LOGS = "login_logs"
COLLECTION_ALERTS = "alerts"
COLLECTION_RISK = "risk_scores"


# Risk Thresholds
LOW_RISK = 30
MEDIUM_RISK = 60
HIGH_RISK = 80


# Login Behaviour
MAX_FAILED_ATTEMPTS = 10
LOGIN_WINDOW_SECONDS = 300


# Attack Simulation
NORMAL_USER_RATIO = 0.95
ATTACK_USER_RATIO = 0.05


# Geography
MAX_TRAVEL_SPEED_KMH = 900


# Time
BUSINESS_HOUR_START = 8
BUSINESS_HOUR_END = 20