"""
Kafka configuration for SecureCommerce AI.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class KafkaConfig:

    BOOTSTRAP_SERVERS = os.getenv(
        "KAFKA_BROKER",
        "localhost:9092"
    )

    LOGIN_TOPIC = os.getenv(
        "KAFKA_TOPIC",
        "login_events"
    )
