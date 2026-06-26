"""
Rule Engine for SecureCommerce AI.
Combines ML prediction with business rules.
"""
from shared.enums import RiskLevel

class RuleEngine:
    def evaluate(self, event, prediction):
        score = prediction["anomaly_score"]
        failed = event["failed_attempts"]
        attack = event["attack_type"]
        if prediction["is_anomaly"] and failed >= 10:
            risk = RiskLevel.HIGH
        elif prediction["is_anomaly"]:
            risk = RiskLevel.MEDIUM
        else:
            risk = RiskLevel.LOW
        return {
            "risk_level": risk.value,
            "attack_type": attack,
            "failed_attempts": failed,
            "anomaly_score": score
        }