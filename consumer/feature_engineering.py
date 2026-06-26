"""
Real-time Feature Engineering
"""

from consumer.preprocessing import Preprocessor
from shared.schemas import FeatureVector


class FeatureEngineer:

    def build_features(self, event):

        timestamp = Preprocessor.parse_timestamp(
            event["timestamp"]
        )

        return FeatureVector(
            event_id=event["event_id"],

            failed_attempts=event["failed_attempts"],

            login_attempt_rate=1,

            unique_ip_count=1,

            device_switch_rate=0,

            country_switch_rate=0,

            login_hour=timestamp.hour,

            is_business_hours=Preprocessor.is_business_hours(
                timestamp
            ),

            travel_speed_kmh=0,

            response_time_ms=event["response_time_ms"]
        )