"""
Train Isolation Forest model for SecureCommerce AI.
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATASET     = "datasets/processed/training_dataset.csv"
MODEL_PATH  = "ml_engine/model.pkl"
SCALER_PATH = "ml_engine/scaler.pkl"

# Must exactly match FEATURE_COLUMNS in predict.py
# Excludes event_id and label (not features), and excludes
# login_hour / is_business_hours which have zero variance when
# the producer runs only during business hours.
FEATURE_COLUMNS = [
    "failed_attempts",
    "login_attempt_rate",
    "unique_ip_count",
    "device_switch_rate",
    "country_switch_rate",
    "travel_speed_kmh",
    "response_time_ms",
]


def main():
    print("Loading dataset…")
    df = pd.read_csv(DATASET)

    attack_rate = df["label"].mean()
    print(f"  Total samples : {len(df)}")
    print(f"  Attack rate   : {attack_rate:.3%}  ({df['label'].sum()} attacks)")

    # Verify all expected columns are present
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Training dataset is missing columns: {missing}\n"
            "Re-run  python -m ml_engine.feature_builder  first."
        )

    # Check for zero-variance features and warn
    stds = df[FEATURE_COLUMNS].std()
    zero_var = stds[stds == 0].index.tolist()
    if zero_var:
        print(f"\n  WARNING: zero-variance features (will not help model): {zero_var}")
        print("  Consider running the producer at different times to vary login_hour,")
        print("  or remove them from FEATURE_COLUMNS.\n")

    X = df[FEATURE_COLUMNS].fillna(0)

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # contamination = actual attack rate in the dataset (3%)
    CONTAMINATION = round(float(attack_rate), 4)
    CONTAMINATION = max(0.01, min(CONTAMINATION, 0.5))  # clamp to valid range
    print(f"\n  contamination = {CONTAMINATION} (derived from dataset attack rate)")

    print("Training Isolation Forest…")
    model = IsolationForest(
        n_estimators=300,
        contamination=CONTAMINATION,
        max_samples="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_scaled)

    os.makedirs("ml_engine", exist_ok=True)
    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print()
    print("Training complete.")
    print(f"  Features ({len(FEATURE_COLUMNS)}): {FEATURE_COLUMNS}")
    print(f"  Model  → {MODEL_PATH}")
    print(f"  Scaler → {SCALER_PATH}")
    print()
    print("Next: python -m ml_engine.evaluate")


if __name__ == "__main__":
    main()