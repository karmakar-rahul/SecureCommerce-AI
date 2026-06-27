"""
Evaluate the trained Isolation Forest model for SecureCommerce AI.
"""

import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score

DATASET = "datasets/processed/training_dataset.csv"
MODEL   = "ml_engine/model.pkl"
SCALER  = "ml_engine/scaler.pkl"

# Must match train.py and predict.py exactly
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
    df     = pd.read_csv(DATASET)
    X      = df[FEATURE_COLUMNS].fillna(0)
    y_true = df["label"]

    scaler = joblib.load(SCALER)
    model  = joblib.load(MODEL)

    X_scaled    = scaler.transform(X)
    predictions = model.predict(X_scaled)
    y_pred      = (predictions == -1).astype(int)

    cm = confusion_matrix(y_true, y_pred)

    print()
    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)
    print()
    print("Confusion Matrix  (rows=actual, cols=predicted)")
    print(f"                  Pred Normal   Pred Attack")
    print(f"  Actual Normal   {cm[0][0]:>11}   {cm[0][1]:>11}")
    print(f"  Actual Attack   {cm[1][0]:>11}   {cm[1][1]:>11}")
    print()
    print(classification_report(y_true, y_pred, digits=4,
          target_names=["Normal", "Attack"]))

    prec = precision_score(y_true, y_pred, zero_division=0)
    rec  = recall_score(y_true,  y_pred, zero_division=0)
    f1   = f1_score(y_true,     y_pred, zero_division=0)

    print(f"Total samples      : {len(df)}")
    print(f"True attacks       : {y_true.sum()} ({y_true.mean():.2%})")
    print(f"Predicted anomalies: {y_pred.sum()} ({y_pred.mean():.2%})")
    print()
    print(f"Precision : {prec:.2%}  (target: 50–70%)")
    print(f"Recall    : {rec:.2%}")
    print(f"F1-score  : {f1:.2%}")

    if prec < 0.50:
        print("\n⚠  Precision below target. Likely cause: device_switch_rate")
        print("   is all-zero (producer uses fixed device per user). That")
        print("   feature adds no signal — consider removing it from")
        print("   FEATURE_COLUMNS in train.py and retraining.")
    else:
        print("\n✓  Precision in target range.")


if __name__ == "__main__":
    main()