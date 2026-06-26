"""
Train Isolation Forest model for SecureCommerce AI.
"""

import os
import joblib
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


DATASET = "datasets/processed/training_dataset.csv"
MODEL_PATH = "ml_engine/model.pkl"
SCALER_PATH = "ml_engine/scaler.pkl"


FEATURE_COLUMNS = [
    "failed_attempts",
    "login_hour",
    "is_business_hours",
    "response_time_ms",
]


def main():
    print("Loading dataset...")
    df = pd.read_csv(DATASET)
    X = df[FEATURE_COLUMNS]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("Training Isolation Forest...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.10,
        random_state=42,
        n_jobs=-1,

    )

    model.fit(X_scaled)
    os.makedirs("ml_engine", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print()
    print("Training Complete")
    print(f"Samples : {len(df)}")
    print(f"Features: {len(FEATURE_COLUMNS)}")
    print(f"Model saved  -> {MODEL_PATH}")
    print(f"Scaler saved -> {SCALER_PATH}")


if __name__ == "__main__":
    main()