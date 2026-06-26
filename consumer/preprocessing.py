"""
Preprocessing utilities for SecureCommerce AI.
"""
from datetime import datetime

class Preprocessor:
    @staticmethod
    def parse_timestamp(timestamp: str) -> datetime:
        """
        Convert ISO-8601 timestamp string to datetime object.
        """
        return datetime.fromisoformat(timestamp)
    @staticmethod
    def is_business_hours(dt: datetime) -> bool:
        """
        Returns True if login occurred during business hours.
        """
        return 9 <= dt.hour <= 18
    @staticmethod
    def login_success(login_status: str) -> int:
        """
        Encode login status.
        SUCCESS -> 1
        FAILED -> 0
        """
        return 1 if login_status == "SUCCESS" else 0
    @staticmethod
    def attack_label(attack_type: str) -> int:
        """
        Encode attack type.
        NORMAL -> 0
        Attack -> 1
        """
        return 0 if attack_type == "NORMAL" else 1