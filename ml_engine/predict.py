"""
Real-time prediction module for SecureCommerce AI.
FEATURE_COLUMNS must exactly match train.py.
"""

import os
import logging
import joblib
import pandas as pd

log = logging.getLogger(__name__)

MODEL_PATH  = "ml_engine/model.pkl"
SCALER_PATH = "ml_engine/scaler.pkl"

# Must exactly match FEATURE_COLUMNS in train.py
FEATURE_COLUMNS = [
    "failed_attempts",
    "login_attempt_rate",
    "unique_ip_count",
    "device_switch_rate",
    "country_switch_rate",
    "travel_speed_kmh",
    "response_time_ms",
]

_PENDING_PREDICTION = {
    "prediction":    0,
    "is_anomaly":    False,
    "anomaly_score": 0.0,
    "status":        "pending_model",
}


class AnomalyPredictor:

    def __init__(self):
        self.model  = None
        self.scaler = None
        self._warned = False

    def _try_load(self) -> bool:
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            self.model  = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            log.info("Model loaded from %s", MODEL_PATH)
            return True
        return False

    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, feature_vector) -> dict:
        if not self.is_ready():
            if not self._try_load():
                if not self._warned:
                    log.warning(
                        "model.pkl not found — running in data-collection mode.\n"
                        "  Run:  python -m ml_engine.feature_builder\n"
                        "        python -m ml_engine.train\n"
                        "  Model will activate automatically on the next event."
                    )
                    self._warned = True
                return _PENDING_PREDICTION

        X = pd.DataFrame([{
            "failed_attempts":     feature_vector.failed_attempts,
            "login_attempt_rate":  feature_vector.login_attempt_rate,
            "unique_ip_count":     feature_vector.unique_ip_count,
            "device_switch_rate":  feature_vector.device_switch_rate,
            "country_switch_rate": feature_vector.country_switch_rate,
            "travel_speed_kmh":    feature_vector.travel_speed_kmh,
            "response_time_ms":    feature_vector.response_time_ms,
        }])

        X_scaled   = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        score      = self.model.decision_function(X_scaled)[0]

        return {
            "prediction":    int(prediction),
            "is_anomaly":    bool(prediction == -1),
            "anomaly_score": float(score),
            "status":        "ok",
        }