"""
Real-time (Online) Feature Engineering for SecureCommerce AI.

"""

import time
from collections import defaultdict, deque
from math import radians, cos, sin, asin, sqrt
from typing import Optional

from consumer.preprocessing import Preprocessor
from shared.schemas import FeatureVector

WINDOW_SECONDS = 300   
MAX_IDLE_HOURS = 1     



def _haversine_kmh(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    elapsed_seconds: float,
) -> float:
    """Return km/h speed between two geo-coords given travel time."""
    if elapsed_seconds <= 0:
        return 0.0
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    distance_km = 2 * R * asin(sqrt(a))
    return distance_km / (elapsed_seconds / 3600)


class FeatureEngineer:
    """
    Maintains a per-user sliding window and computes behavioural
    features without touching MongoDB.
    """
    def __init__(self):
        # user_id -> deque of (epoch_ts, ip, device, country, lat, lon)
        self._windows: dict[str, deque] = defaultdict(
            lambda: deque()
        )
        self._last_seen: dict[str, float] = {}

    # public API 

    def build_features(self, event: dict) -> FeatureVector:
        user_id = event["user_id"]
        now_ts  = time.time()

        # Parse event timestamp for hour/business-hour features
        timestamp = Preprocessor.parse_timestamp(event["timestamp"])

        # Record in sliding window
        entry = (
            now_ts,
            event.get("ip_address", ""),
            event.get("device", ""),
            event.get("country", ""),
            float(event.get("latitude", 0.0)),
            float(event.get("longitude", 0.0)),
        )
        window = self._windows[user_id]
        window.append(entry)
        self._last_seen[user_id] = now_ts

        # Evict entries outside the time window
        cutoff = now_ts - WINDOW_SECONDS
        while window and window[0][0] < cutoff:
            window.popleft()

        # Evict idle users to keep memory bounded
        self._evict_idle_users(now_ts)

        #compute features from window 
        n = len(window)

        # login_attempt_rate
        window_minutes = WINDOW_SECONDS / 60
        login_attempt_rate = n / window_minutes

        # unique IPs 
        unique_ip_count = len({e[1] for e in window})

        # device switch rate: fraction of events with a different device
        # from the most common device in the window
        devices = [e[2] for e in window]
        if devices:
            most_common_device = max(set(devices), key=devices.count)
            device_switch_rate = sum(
                1 for d in devices if d != most_common_device
            ) / max(n, 1)
        else:
            device_switch_rate = 0.0

        # country switch rate
        countries = [e[3] for e in window]
        if countries:
            most_common_country = max(set(countries), key=countries.count)
            country_switch_rate = sum(
                1 for c in countries if c != most_common_country
            ) / max(n, 1)
        else:
            country_switch_rate = 0.0

        # impossible travel speed: compare current event to previous
        travel_speed_kmh = self._compute_travel_speed(window, entry)

        return FeatureVector(
            event_id=event["event_id"],
            failed_attempts=event["failed_attempts"],
            login_attempt_rate=round(login_attempt_rate, 4),
            unique_ip_count=unique_ip_count,
            device_switch_rate=round(device_switch_rate, 4),
            country_switch_rate=round(country_switch_rate, 4),
            login_hour=timestamp.hour,
            is_business_hours=Preprocessor.is_business_hours(timestamp),
            travel_speed_kmh=round(travel_speed_kmh, 2),
            response_time_ms=event["response_time_ms"],
        )

    # private helpers 

    def _compute_travel_speed(self, window: deque, current: tuple) -> float:
        if len(window) < 2:
            return 0.0
        # Compare current event to the one just before it
        prev = window[-2]  
        cur  = current
        elapsed = cur[0] - prev[0]
        return _haversine_kmh(
            prev[4], prev[5],   # prev lat, lon
            cur[4],  cur[5],    # cur lat, lon
            elapsed,
        )

    def _evict_idle_users(self, now_ts: float) -> None:
        evict_before = now_ts - MAX_IDLE_HOURS * 3600
        idle = [
            uid for uid, ts in self._last_seen.items()
            if ts < evict_before
        ]
        for uid in idle:
            del self._windows[uid]
            del self._last_seen[uid]