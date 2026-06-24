"""
General helper functions.
"""

import uuid
from datetime import datetime, UTC


def generate_event_id() -> str:
    return str(uuid.uuid4())


def generate_session_id() -> str:
    return str(uuid.uuid4())


def current_timestamp():
    return datetime.now(UTC)


def is_business_hours(hour: int):
    return 8 <= hour <= 20