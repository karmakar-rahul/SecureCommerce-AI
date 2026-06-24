"""
Kafka Consumer for SecureCommerce AI.
Reads login events from Kafka and stores them in MongoDB.
"""

import json
from kafka import KafkaConsumer
from configs.kafka_config import KafkaConfig
from consumer.mongo_writer import MongoWriter


# Initialize MongoDB Writer
writer = MongoWriter()

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    KafkaConfig.LOGIN_TOPIC,
    bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    value_deserializer=lambda message: json.loads(
        message.decode("utf-8")
    ),
)

def main():
    print("Kafka Consumer Started...")
    for message in consumer:
        event = message.value
        # Insert into MongoDB
        writer.insert_event(event)
        print(
            f"Inserted -> {event['event_id']} | "
            f"{event['attack_type']} | "
            f"{event['country']}"
        )


if __name__ == "__main__":
    main()