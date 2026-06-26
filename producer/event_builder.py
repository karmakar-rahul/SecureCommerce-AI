"""
Event Builder for SecureCommerce AI.
Creates realistic login events from synthetic users.
"""

import json
import random
import uuid

from datetime import datetime, UTC

import pandas as pd
from faker import Faker
from shared.schemas import LoginEvent
from shared.enums import (
    LoginStatus,
    AttackType,
)

from shared.helpers import generate_session_id
fake = Faker()
class EventBuilder:

    def __init__(self):
        self.users = pd.read_csv(
            "datasets/synthetic/users.csv"
        )
        with open(
            "datasets/sample/attack_profiles.json",
            "r"
        ) as file:
            self.attack_profiles = json.load(file)

    def _choose_attack(self):
        r = random.random()
        normal = self.attack_profiles["normal"]["probability"]
        brute = self.attack_profiles["brute_force"]["probability"]

        if r < normal:
            return AttackType.NORMAL
        elif r < normal + brute:
            return AttackType.BRUTE_FORCE
        return AttackType.CREDENTIAL_STUFFING

    def build_event(self):
        user = self.users.sample(1).iloc[0]
        attack = self._choose_attack()

        login_status = LoginStatus.SUCCESS
        failed_attempts = 0

        country = user["country"]
        city = user["city"]
        latitude = user["latitude"]
        longitude = user["longitude"]

        device = user["preferred_device"]
        browser = user["preferred_browser"]

        if attack == AttackType.BRUTE_FORCE:
            login_status = LoginStatus.FAILED
            failed_attempts = random.randint(10, 30)

        elif attack == AttackType.CREDENTIAL_STUFFING:
            login_status = random.choice(
                [
                    LoginStatus.SUCCESS,
                    LoginStatus.FAILED
                ]
            )
            failed_attempts = random.randint(5, 15)
            location = self.users.sample(1).iloc[0]
            country = location["country"]
            city = location["city"]
            latitude = location["latitude"]
            longitude = location["longitude"]

        return LoginEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            user_id=user["user_id"],
            username=user["username"],
            role=user["role"],
            ip_address=fake.ipv4_public(),
            country=country,
            city=city,
            latitude=float(latitude),
            longitude=float(longitude),
            device=device,
            browser=browser,
            login_status=login_status,
            attack_type=attack,
            failed_attempts=failed_attempts,
            session_id=generate_session_id(),
            response_time_ms=random.uniform(50, 600)

        )


if __name__ == "__main__":
    builder = EventBuilder()
    for _ in range(5):
        print(builder.build_event())