"""
Kafka Producer for SecureCommerce AI
"""

import json
import time
from kafka import KafkaProducer
from producer.event_builder import EventBuilder
from configs.kafka_config import KafkaConfig
producer = KafkaProducer(
    bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)
builder = EventBuilder()


def main():
    print("Kafka Producer Started...")
    while True:
        event = builder.build_event()
        producer.send(
            KafkaConfig.LOGIN_TOPIC,
            event.to_dict()
        )
        print(
            f"Sent -> {event.event_id} | "
            f"{event.attack_type.value}"
        )
        time.sleep(0.01)

if __name__ == "__main__":
    main()