import os
import json
import subprocess
from datetime import datetime

from fastapi import APIRouter, HTTPException
from api.database import database

router = APIRouter()



# Dashboard Summary
@router.get("/summary")
def get_summary():
    db = database.db
    total = db.login_logs.count_documents({})
    attacks = db.login_logs.count_documents(
        {"attack_type": {"$ne": "NORMAL"}}
    )
    anomalies = db.login_logs.count_documents(
        {"ml_prediction.is_anomaly": True}
    )
    high = db.login_logs.count_documents(
        {"alert.risk_level": "HIGH"}
    )
    return {
        "total_events": total,
        "attacks": attacks,
        "anomalies": anomalies,
        "high_risk": high,
    }

# Latest Events
@router.get("/events")
def get_events():
    db = database.db
    cursor = (
        db.login_logs
        .find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(8)
    )
    return list(cursor)

# ML Metrics
@router.get("/ml")
def get_ml_metrics():
    metrics_file = os.path.join("outputs", "metrics.json")
    if not os.path.exists(metrics_file):
        raise HTTPException(
            status_code=404,
            detail="metrics.json not found. Run 'python -m ml_engine.evaluate' first."
        )
    with open(metrics_file, "r") as f:
        return json.load(f)

# System Status
@router.get("/system")
def get_system_status():
    db = database.db
    total = db.login_logs.count_documents({})
    attacks = db.login_logs.count_documents(
        {"attack_type": {"$ne": "NORMAL"}}
    )

    anomalies = db.login_logs.count_documents(
        {"ml_prediction.is_anomaly": True}
    )

    kafka = "Stopped"
    mongo = "Stopped"

    try:

        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=3,
        )

        containers = result.stdout.lower()

        if "kafka" in containers:
            kafka = "Running"

        if "mongo" in containers:
            mongo = "Running"

    except Exception:
        pass

    return {
        "kafka": kafka,
        "mongodb": mongo,
        "producer": "Ready",
        "consumer": "Ready",
        "model": "Isolation Forest",
        "dataset_size": total,
        "attacks": attacks,
        "anomalies": anomalies,
        "version": "v1.0",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }