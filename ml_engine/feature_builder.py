"""
Offline Feature Builder for SecureCommerce AI.
Creates a training dataset from MongoDB using vectorized pandas operations.
"""

import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

WINDOW = "5min"


def _haversine_vectorized(lat1, lon1, lat2, lon2) -> np.ndarray:
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(np.radians(lat1))
        * np.cos(np.radians(lat2))
        * np.sin(dlon / 2) ** 2
    )
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def _switch_rate(arr: np.ndarray) -> float:
    """Fraction of values in window that differ from the modal value."""
    if len(arr) == 0:
        return 0.0
    counts = np.bincount(arr.astype(int))
    modal  = counts.argmax()
    return float((arr != modal).mean())


def _rolling_features_for_group(group: pd.DataFrame) -> pd.DataFrame:
    """
    Compute rolling features for one user's events.
    group has a DatetimeIndex (timestamp) and user_id is NOT in the index —
    it was kept as a regular column so it survives reset_index() later.
    """
    g = group.sort_index()

    # Encode string columns → integer codes (rolling needs numeric dtype)
    ip_codes,  _ = pd.factorize(g["ip_address"])
    dev_codes, _ = pd.factorize(g["device"])
    cty_codes, _ = pd.factorize(g["country"])

    ip_s  = pd.Series(ip_codes.astype(np.float64),  index=g.index)
    dev_s = pd.Series(dev_codes.astype(np.float64), index=g.index)
    cty_s = pd.Series(cty_codes.astype(np.float64), index=g.index)

    g = g.copy()

    # login_attempt_rate: events per minute in 5-min window
    g["login_attempt_rate"] = (
        g["failed_attempts"].astype(float)
        .rolling(WINDOW, min_periods=1)
        .count()
        / 5.0
    )

    # unique_ip_count
    g["unique_ip_count"] = (
        ip_s
        .rolling(WINDOW, min_periods=1)
        .apply(lambda x: int(pd.Series(x).nunique()), raw=True)
        .astype(int)
    )

    # device_switch_rate
    g["device_switch_rate"] = (
        dev_s
        .rolling(WINDOW, min_periods=1)
        .apply(_switch_rate, raw=True)
    )

    # country_switch_rate
    g["country_switch_rate"] = (
        cty_s
        .rolling(WINDOW, min_periods=1)
        .apply(_switch_rate, raw=True)
    )

    return g


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
        self.db     = self.client[os.getenv("MONGO_DATABASE")]

    def load_events(self) -> pd.DataFrame:
        fields = {
            "_id": 0,
            "event_id": 1, "user_id": 1, "timestamp": 1,
            "ip_address": 1, "device": 1, "country": 1,
            "latitude": 1, "longitude": 1,
            "failed_attempts": 1, "response_time_ms": 1,
            "attack_type": 1,
        }
        cursor = self.db.login_logs.find({}, fields)
        df = pd.DataFrame(list(cursor))
        print(f"Loaded {len(df)} events.")
        return df

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["timestamp"]        = pd.to_datetime(df["timestamp"], utc=True)
        df["failed_attempts"]  = pd.to_numeric(df["failed_attempts"],  errors="coerce").fillna(0).astype(int)
        df["response_time_ms"] = pd.to_numeric(df["response_time_ms"], errors="coerce").fillna(0.0)
        df["latitude"]         = pd.to_numeric(df["latitude"],         errors="coerce").fillna(0.0)
        df["longitude"]        = pd.to_numeric(df["longitude"],        errors="coerce").fillna(0.0)
        for col in ("ip_address", "device", "country"):
            df[col] = df[col].fillna("unknown").astype(str)
        df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)
        return df

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Simple time features
        df["login_hour"]        = df["timestamp"].dt.hour
        df["is_business_hours"] = (
            (df["login_hour"] >= 9) & (df["login_hour"] <= 18)
        ).astype(int)
        df["label"] = (df["attack_type"] != "NORMAL").astype(int)

        # --- Rolling features ---
        # Set timestamp as index ONLY for the rolling window.
        # Keep user_id as a plain column (do NOT include it in set_index).
        # After groupby+apply, reset_index() restores timestamp as a column
        # and user_id remains intact as a regular column.
        print("Computing rolling features…")
        df_indexed = df.set_index("timestamp")   # user_id stays as column

        result = (
            df_indexed
            .groupby("user_id")
            .apply(_rolling_features_for_group)
            .reset_index()
        )

# Remove duplicated user_id if created
        if "level_1" in result.columns:
            result = result.drop(columns=["level_1"])

# Ensure timestamp column name is correct
        if "index" in result.columns:
            result = result.rename(columns={"index": "timestamp"})

        df = result

        # --- Travel speed (haversine between consecutive events per user) ---
        print("Computing travel speed…")
        df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

        df["_prev_lat"] = df.groupby("user_id")["latitude"].shift(1)
        df["_prev_lon"] = df.groupby("user_id")["longitude"].shift(1)
        df["_prev_ts"]  = df.groupby("user_id")["timestamp"].shift(1)

        has_prev = df["_prev_lat"].notna()

        elapsed_hours = (
            (df.loc[has_prev, "timestamp"] - df.loc[has_prev, "_prev_ts"])
            .dt.total_seconds() / 3600.0
        )
        dist_km = _haversine_vectorized(
            df.loc[has_prev, "_prev_lat"], df.loc[has_prev, "_prev_lon"],
            df.loc[has_prev, "latitude"],  df.loc[has_prev, "longitude"],
        )

        df["travel_speed_kmh"] = 0.0
        df.loc[has_prev, "travel_speed_kmh"] = np.where(
            elapsed_hours > 0, dist_km / elapsed_hours, 0.0
        )
        df.drop(columns=["_prev_lat", "_prev_lon", "_prev_ts"], inplace=True)

        return df

    def save(self, df: pd.DataFrame) -> None:
        feature_cols = [
            "event_id",
            "failed_attempts",
            "login_attempt_rate",
            "unique_ip_count",
            "device_switch_rate",
            "country_switch_rate",
            "login_hour",
            "is_business_hours",
            "travel_speed_kmh",
            "response_time_ms",
            "label",
        ]
        out_df = df[feature_cols].copy()

        os.makedirs("datasets/processed", exist_ok=True)
        output = "datasets/processed/training_dataset.csv"
        out_df.to_csv(output, index=False)

        print(f"\nSaved {len(out_df)} rows → {output}")
        print(f"Attack rate : {out_df['label'].mean():.3%}")
        print("\nFeature summary:")
        print(out_df[feature_cols[1:-1]].describe().round(3).to_string())


def main():
    builder = OfflineFeatureBuilder()
    df      = builder.load_events()
    df      = builder.preprocess(df)
    df      = builder.build_features(df)
    builder.save(df)


if __name__ == "__main__":
    main()