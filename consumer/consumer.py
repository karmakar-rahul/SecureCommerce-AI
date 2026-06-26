"""
Kafka Consumer for SecureCommerce AI.
Reads login events from Kafka, performs feature engineering,
runs ML inference, applies rule engine, and stores the
enriched event into MongoDB.
"""

import json

from kafka import KafkaConsumer

from configs.kafka_config import KafkaConfig

from consumer.mongo_writer import MongoWriter
from consumer.feature_engineering import FeatureEngineer
from consumer.rules_engine import RuleEngine

from ml_engine.predict import AnomalyPredictor


writer = MongoWriter()
engineer = FeatureEngineer()
predictor = AnomalyPredictor()
rule_engine = RuleEngine()
consumer = KafkaConsumer(
    KafkaConfig.LOGIN_TOPIC,
    bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    value_deserializer=lambda message: json.loads(
        message.decode("utf-8")
    ),
)


def main():

    from time import perf_counter

    print("Kafka Consumer Started...")

    for message in consumer:

        event = message.value

        start = perf_counter()

        # Feature Engineering
        features = engineer.build_features(event)
        t1 = perf_counter()

        # ML Prediction
        prediction = predictor.predict(features)
        t2 = perf_counter()

        event["ml_prediction"] = prediction

        # Rule Engine
        alert = rule_engine.evaluate(event, prediction)
        t3 = perf_counter()

        event["alert"] = alert

        # MongoDB
        writer.insert_event(event)
        t4 = perf_counter()

        print(
            f"FE={t1-start:.4f}s | "
            f"ML={t2-t1:.4f}s | "
            f"RULE={t3-t2:.4f}s | "
            f"DB={t4-t3:.4f}s"
        )

        print(
            f"{event['attack_type']:<22}"
            f"| ML={prediction['prediction']:>2} "
            f"| Risk={alert['risk_level']:<6} "
            f"| Score={prediction['anomaly_score']:.4f}"
        )
if __name__ == "__main__":
    main()