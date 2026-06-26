"""
Offline Feature Builder for SecureCommerce AI.
Creates a training dataset from MongoDB using
vectorized pandas operations.
"""

import os

import pandas as pd

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


class OfflineFeatureBuilder:

    def __init__(self):

        uri = (
            f"mongodb://"
            f"{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
            f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@"
            f"{os.getenv('MONGO_HOST')}:"
            f"{os.getenv('MONGO_PORT')}/"
        )

        self.client = MongoClient(uri)

        self.db = self.client[
            os.getenv("MONGO_DATABASE")
        ]

    def load_events(self):

        cursor = self.db.login_logs.find(
            {},
            {
                "_id": 0
            }
        )

        df = pd.DataFrame(list(cursor))

        print(f"Loaded {len(df)} events.")

        return df

    def preprocess(self, df):

        # Timestamp

        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )

        # Sort

        df = df.sort_values(
            [
                "user_id",
                "timestamp"
            ]
        )

        # Login Hour

        df["login_hour"] = (
            df["timestamp"].dt.hour
        )

        # Business Hours

        df["is_business_hours"] = (
            (
                df["login_hour"] >= 9
            ) &
            (
                df["login_hour"] <= 18
            )
        ).astype(int)

        # Label

        df["label"] = (
            df["attack_type"] != "NORMAL"
        ).astype(int)

        return df

    def save(self, df):

        os.makedirs(
            "datasets/processed",
            exist_ok=True
        )

        output = (
            "datasets/processed/"
            "training_dataset.csv"
        )

        df.to_csv(
            output,
            index=False
        )

        print(f"Saved -> {output}")


def main():

    builder = OfflineFeatureBuilder()

    df = builder.load_events()

    df = builder.preprocess(df)

    builder.save(df)


if __name__ == "__main__":

    main()