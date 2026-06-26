"""
Real-time prediction module for SecureCommerce AI.
"""

import joblib
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "failed_attempts",
    "login_hour",
    "is_business_hours",
    "response_time_ms",
]


class AnomalyPredictor:

    def __init__(self):
        self.model = joblib.load(
            "ml_engine/model.pkl"
        )
        self.scaler = joblib.load(
            "ml_engine/scaler.pkl"
        )

    def predict(self, feature_vector):

        X = pd.DataFrame([{
            "failed_attempts": feature_vector.failed_attempts,
            "login_hour": feature_vector.login_hour,
            "is_business_hours": int(feature_vector.is_business_hours),
            "response_time_ms": feature_vector.response_time_ms,
        }])

        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        score = self.model.decision_function(
            X_scaled
        )[0]

        return {
            "prediction": int(prediction),
            "is_anomaly": bool(prediction == -1),
            "anomaly_score": float(score)
        }