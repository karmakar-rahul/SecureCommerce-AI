"""
Kafka Consumer for SecureCommerce AI.
Reads login events from Kafka, performs feature engineering,
runs ML inference, applies rule engine, and stores the
enriched event into MongoDB.

"""

import json
import logging

from kafka import KafkaConsumer

from configs.kafka_config import KafkaConfig
from consumer.mongo_writer import MongoWriter
from consumer.feature_engineering import FeatureEngineer
from consumer.rules_engine import RuleEngine
from ml_engine.predict import AnomalyPredictor

BATCH_SIZE   = 50    # flush to MongoDB every N events
LOG_INTERVAL = 100   # print a summary line every N events


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CONSUMER] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def build_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        KafkaConfig.LOGIN_TOPIC,
        bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS,
        group_id="securecommerce-consumer-group",

        auto_offset_reset="latest",
        enable_auto_commit=True,
        auto_commit_interval_ms=1000,   # commit offsets every 1 s
        # Performance: larger fetch batches from Kafka broker
        fetch_max_bytes=52428800,           # 50 MB
        max_partition_fetch_bytes=10485760, # 10 MB per partition
        value_deserializer=lambda raw: json.loads(raw.decode("utf-8")),
    )


def main():
    writer      = MongoWriter()
    engineer    = FeatureEngineer()
    predictor   = AnomalyPredictor()   # lazy — no crash if model absent
    rule_engine = RuleEngine()
    consumer    = build_consumer()

    log.info("Kafka Consumer started (group=securecommerce-consumer-group).")
    if predictor.is_ready():
        log.info("ML model loaded — running in full inference mode.")
    else:
        log.info(
            "ML model not found — running in DATA COLLECTION mode.\n"
            "  Events will be stored to MongoDB without ML predictions.\n"
            "  When you have enough data (~5000 events), open a second\n"
            "  terminal and run:\n"
            "    python -m ml_engine.feature_builder\n"
            "    python -m ml_engine.train\n"
            "  The model activates automatically — no consumer restart needed."
        )
    log.info("Waiting for new events on topic '%s' …", KafkaConfig.LOGIN_TOPIC)

    batch:       list[dict] = []
    processed:   int = 0
    anomalies:   int = 0

    try:
        for message in consumer:
            event = message.value

            # pipeline 
            features   = engineer.build_features(event)
            prediction = predictor.predict(features)   # safe even without model
            alert      = rule_engine.evaluate(event, prediction)

            event["ml_prediction"] = prediction
            event["alert"]         = alert

            batch.append(event)
            processed += 1

            if prediction.get("is_anomaly"):
                anomalies += 1

            #  log model activation
            # When the model hot-loads mid-run, log it once
            if processed > 1 and predictor.is_ready() and prediction.get("status") == "ok":
                pass  # normal inference, nothing to announce

            # periodic progress log
            if processed % LOG_INTERVAL == 0:
                mode = "INFERENCE" if predictor.is_ready() else "COLLECTION"
                log.info(
                    "[%s] Processed: %d | Anomalies: %d (%.1f%%) | "
                    "Pending batch: %d",
                    mode,
                    processed,
                    anomalies,
                    100 * anomalies / processed,
                    len(batch),
                )

            # flush batch to MongoDB 
            if len(batch) >= BATCH_SIZE:
                writer.insert_many(batch)
                batch.clear()

    except KeyboardInterrupt:
        log.info("Shutdown requested — flushing remaining %d events …", len(batch))
    finally:
        if batch:
            writer.insert_many(batch)
        consumer.close()
        log.info(
            "Consumer stopped. Total processed: %d | Total anomalies: %d",
            processed,
            anomalies,
        )


if __name__ == "__main__":
    main()