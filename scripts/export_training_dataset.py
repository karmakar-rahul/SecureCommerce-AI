"""
Export training dataset from MongoDB.
Reads login events from MongoDB, engineers ML features,
and exports them as a CSV file.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from consumer.feature_engineering import FeatureEngineer

load_dotenv()


def main():
    uri = (
        f"mongodb://"
        f"{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
        f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@"
        f"{os.getenv('MONGO_HOST')}:"
        f"{os.getenv('MONGO_PORT')}/"
    )
    client = MongoClient(uri)
    db = client[os.getenv("MONGO_DATABASE")]
    collection = db["login_logs"]
    engineer = FeatureEngineer()
    records = []
    cursor = collection.find()

    for event in cursor:
        event.pop("_id", None)
        features = engineer.build_features(event)
        row = features.to_dict()
        # Ground truth (used only for evaluation,
        # NOT as an input feature)
        row["label"] = (
            0
            if event["attack_type"] == "NORMAL"
            else 1
        )
        records.append(row)

    df = pd.DataFrame(records)
    output_path = "datasets/processed/training_dataset.csv"
    os.makedirs(
        "datasets/processed",
        exist_ok=True
    )
    df.to_csv(
        output_path,
        index=False
    )
    print(f"Exported {len(df)} records.")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()