"""
Evaluate the trained Isolation Forest model.
"""

import joblib
import pandas as pd

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)

DATASET = "datasets/processed/training_dataset.csv"

MODEL = "ml_engine/model.pkl"

SCALER = "ml_engine/scaler.pkl"

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
    y_true = df["label"]
    scaler = joblib.load(SCALER)
    model = joblib.load(MODEL)
    X_scaled = scaler.transform(X)
    predictions = model.predict(X_scaled)

    # Isolation Forest
    # -1 = anomaly
    #  1 = normal

    y_pred = (predictions == -1).astype(int)
    print()

    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    print()
    print("Confusion Matrix")
    print(
        confusion_matrix(
            y_true,
            y_pred
        )
    )

    print()
    print("Classification Report")
    print(
        classification_report(
            y_true,
            y_pred,
            digits=4
        )
    )

    print()
    print(f"Total samples : {len(df)}")
    print(f"True attacks  : {y_true.sum()}")
    print(f"Detected anomalies : {y_pred.sum()}")


if __name__ == "__main__":
    main()