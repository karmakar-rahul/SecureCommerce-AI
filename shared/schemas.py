"""
Shared data models used across SecureCommerce AI.
Every service (Producer, Consumer, ML Engine, Dashboard)
uses these classes.
"""

from dataclasses import dataclass, asdict
from datetime import datetime

from shared.enums import (
    LoginStatus,
    AttackType,
    RiskLevel,
    DeviceType,
    BrowserType,
    UserRole,
)



# Base Serialization Helper


def serialize_dataclass(obj):
    """
    Converts dataclass objects into JSON-serializable dictionaries.
    Handles datetime and Enum values automatically.
    """
    data = asdict(obj)
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif hasattr(value, "value"):
            data[key] = value.value
    return data



# Raw Login Event


@dataclass
class LoginEvent:
    event_id: str
    timestamp: datetime
    user_id: str
    username: str
    role: UserRole
    ip_address: str
    country: str
    city: str
    latitude: float
    longitude: float
    device: DeviceType
    browser: BrowserType
    login_status: LoginStatus
    attack_type: AttackType
    failed_attempts: int
    session_id: str
    response_time_ms: float
    def to_dict(self):
        return serialize_dataclass(self)



# Engineered Features
@dataclass
class FeatureVector:
    event_id: str
    failed_attempts: int
    login_attempt_rate: float
    unique_ip_count: int
    device_switch_rate: float
    country_switch_rate: float
    login_hour: int
    is_business_hours: bool
    travel_speed_kmh: float
    response_time_ms: float
    def to_dict(self):
        return serialize_dataclass(self)



# ML Prediction
@dataclass
class RiskAssessment:
    event_id: str
    anomaly_score: float
    rule_score: float
    final_score: float
    risk_level: RiskLevel
    detected_attack: AttackType
    is_anomaly: bool
    timestamp: datetime

    def to_dict(self):
        return serialize_dataclass(self)