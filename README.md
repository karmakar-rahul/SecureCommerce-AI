<div align="center">

# SecureCommerce AI

**Real-time fraud and anomaly detection for e-commerce login events**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-2.8+-231F20?style=flat&logo=apachekafka&logoColor=white)](https://kafka.apache.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-47A248?style=flat&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.5+-F7931E?style=flat&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)

*A streaming ML pipeline that detects brute-force and credential-stuffing attacks in real time, with a dark-theme Streamlit dashboard for live monitoring.*

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Pipeline](#running-the-pipeline)
- [Dashboard](#dashboard)
- [ML Model](#ml-model)
- [Configuration](#configuration)
- [Roadmap](#roadmap)

---

## Overview

SecureCommerce AI is a real-time anomaly detection system built around a Kafka producer-consumer pipeline. Synthetic login events — generated at ~100 events/second — flow through Apache Kafka into a consumer that enriches each event with behavioural features, scores it against an Isolation Forest model, and stores the result in MongoDB. A Streamlit dashboard visualises the live event stream, active alerts, global attack geography, and ML performance metrics.

**Current model performance (45,557 training events):**

| Metric | Value |
|--------|-------|
| Precision | **53.79%** |
| Recall | 53.91% |
| F1-Score | 53.85% |
| Accuracy | 97.22% |
| Training attack rate | 3.005% |

---

### Data flow

1. **Producer** samples a synthetic user from `datasets/synthetic/users.csv`, applies an attack profile (`97% NORMAL / 2% BRUTE_FORCE / 1% CREDENTIAL_STUFFING`), and publishes a `LoginEvent` to Kafka.
2. **Consumer** reads events in batches, computes a 5-minute sliding-window `FeatureVector` per user entirely in RAM, runs the Isolation Forest, applies the rules engine, and writes enriched documents to MongoDB in batches of 50.
3. **Dashboard** queries MongoDB directly and auto-refreshes every 30 seconds.
4. **Offline retraining** exports a training CSV from MongoDB via `feature_builder.py`, retrains the model, and drops new `model.pkl` / `scaler.pkl` artifacts — the consumer picks them up automatically on the next event.

---

## Features

### Pipeline
- **Kafka consumer group** with persistent offset commits — restarting the consumer never replays the historical backlog
- **Batched MongoDB inserts** (`insert_many`) — 50× fewer round-trips vs per-event `insert_one`
- **Lazy model loading** — consumer starts in data-collection mode if no model exists, activates inference automatically once trained, no restart required
- **In-memory sliding window** per user (5 minutes) for real-time feature computation with zero database queries

### ML
- **Isolation Forest** (300 trees, `contamination` auto-derived from dataset attack rate)
- **7 behavioural features**: `failed_attempts`, `login_attempt_rate`, `unique_ip_count`, `device_switch_rate`, `country_switch_rate`, `travel_speed_kmh`, `response_time_ms`
- **Rule engine** overlays business logic on top of ML scores (HIGH risk = anomaly + ≥10 failed attempts)
- Offline evaluation with confusion matrix, per-class classification report, and precision target check

### Dashboard (Streamlit)
- **Overview** — KPI metrics, event volume timeline, attack/risk distribution, top targeted users, failure heatmap by hour
- **Live Alerts** — real-time scrolling alert list with risk badges, full event log table, CSV export
- **Geo Intelligence** — world map of attack origins, country-level summary table
- **ML Performance** — confusion matrix, anomaly score distribution, feature comparison box plots
- Sidebar filters by risk level and attack type; adjustable time window (1h / 6h / 12h / 24h); 30-second auto-refresh

---

## Project Structure

```
SecureCommerce-AI/
├── configs/
│   ├── kafka_config.py          # Kafka broker + topic settings
│   └── mongodb_config.py        # MongoDB connection settings
│
├── producer/
│   ├── producer.py              # Kafka producer (100 events/sec)
│   └── event_builder.py         # Synthetic login event generator
│
├── consumer/
│   ├── consumer.py              # Kafka consumer with batched MongoDB writes
│   ├── feature_engineering.py   # Online sliding-window feature computation
│   ├── mongo_writer.py          # MongoDB insert_many wrapper
│   ├── preprocessing.py         # Timestamp parsing + business-hours flag
│   └── rules_engine.py          # Risk level assignment (ML + rules)
│
├── ml_engine/
│   ├── feature_builder.py       # Offline feature export from MongoDB
│   ├── train.py                 # Isolation Forest training
│   ├── predict.py               # Real-time inference (lazy model load)
│   ├── evaluate.py              # Confusion matrix + classification report
│   ├── model.pkl                # Trained model artifact (git-ignored)
│   └── scaler.pkl               # StandardScaler artifact (git-ignored)
│
├── dashboard/
│   └── dashboard.py             # Streamlit 4-page dashboard
│
├── shared/
│   ├── schemas.py               # LoginEvent, FeatureVector dataclasses
│   ├── enums.py                 # AttackType, RiskLevel, DeviceType, etc.
│   └── helpers.py               # Session ID generator
│
├── database/
│   ├── mongodb.py               # MongoClient factory
│   └── collections.py           # Collection name constants
│
├── datasets/
│   ├── synthetic/
│   │   └── users.csv            # 1000 synthetic users
│   ├── sample/
│   │   └── attack_profiles.json # Attack probability configuration
│   └── processed/
│       └── training_dataset.csv # Exported feature CSV (git-ignored)
│
├── docker-compose.yml           # Kafka + Zookeeper + MongoDB containers
├── .env.example                 # Environment variable template
└── requirements.txt             # Python dependencies
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker Desktop
- Anaconda (recommended) or `venv`

### 1. Clone the repository

```bash
git clone https://github.com/karmakar-rahul/SecureCommerce-AI.git
cd SecureCommerce-AI
```

### 2. Create and activate the environment

```bash
conda create -n securecommerce python=3.11
conda activate securecommerce
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your MongoDB credentials
```

`.env` template:
```env
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=yourpassword
MONGO_DATABASE=securecommerce_ai

KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=login_events
```

### 4. Start infrastructure

```bash
docker compose up -d
```

This starts:
- Apache Kafka on `localhost:9092`
- Zookeeper on `localhost:2181`
- MongoDB on `localhost:27017`

---

## Running the Pipeline

Open four terminals, all from the project root with the conda environment active.

### Terminal 1 — Producer

```bash
python -m producer.producer
```

Outputs one line per event. You should see a mix of `NORMAL`, `BRUTE_FORCE`, and `CREDENTIAL_STUFFING` events.

### Terminal 2 — Consumer

```bash
python -m consumer.consumer
```

On first run (no model yet), the consumer starts in **DATA COLLECTION** mode — events are stored to MongoDB without ML scoring. This is expected.

### Terminal 3 — Train the model (once you have ~5,000+ events)

```bash
# Export features from MongoDB
python -m ml_engine.feature_builder

# Train the Isolation Forest
python -m ml_engine.train

# Evaluate
python -m ml_engine.evaluate
```

The consumer in Terminal 2 will automatically detect the new `model.pkl` and switch to **INFERENCE** mode on the next event — no restart needed.

### Terminal 4 — Dashboard

```bash
streamlit run dashboard/dashboard.py
```

Opens at `http://localhost:8501`.

---

## Dashboard

| Page | What it shows |
|------|---------------|
| **Overview** | KPIs · event volume timeline · attack/risk distribution · top targeted users · country breakdown · failure heatmap |
| **Live Alerts** | Scrollable alert feed with risk badges · full event log table · CSV export |
| **Geo Intelligence** | World map of login origins (blue = normal, red = brute force, amber = credential stuffing) · country summary table |
| **ML Performance** | Static confusion matrix · live anomaly score histogram · feature comparison box plots |

**Sidebar controls:**
- Time window: 1h / 6h / 12h / 24h
- Risk level filter: HIGH / MEDIUM / LOW
- Attack type filter
- Auto-refresh toggle (30s)

---

## ML Model

### Algorithm

[Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) — an unsupervised anomaly detection algorithm that isolates anomalies by randomly partitioning features. Anomalies require fewer splits to isolate and receive lower (more negative) anomaly scores.

### Features

| Feature | Source | Description |
|---------|--------|-------------|
| `failed_attempts` | Raw event | Login failures in this event |
| `login_attempt_rate` | 5-min window | Logins per minute for this user |
| `unique_ip_count` | 5-min window | Distinct IPs used by this user |
| `device_switch_rate` | 5-min window | Fraction of events with non-preferred device |
| `country_switch_rate` | 5-min window | Fraction of events from non-preferred country |
| `travel_speed_kmh` | Consecutive events | Speed implied by location change (impossible travel) |
| `response_time_ms` | Raw event | API response latency |

### Hyperparameters

```python
IsolationForest(
    n_estimators=300,
    contamination=0.0301,   # auto-derived from dataset attack rate
    max_samples="auto",     # sqrt(n_samples)
    random_state=42,
    n_jobs=-1,
)
```

### Retraining

The model is trained offline from the MongoDB event store. To retrain after collecting more data:

```bash
python -m ml_engine.feature_builder   # re-exports training_dataset.csv
python -m ml_engine.train             # overwrites model.pkl + scaler.pkl
python -m ml_engine.evaluate          # prints updated confusion matrix
```

The running consumer picks up the new model automatically.

---

## Configuration

### Attack profiles (`datasets/sample/attack_profiles.json`)

```json
{
  "normal":              { "probability": 0.97 },
  "brute_force":         { "probability": 0.02, "failed_attempts_range": [10, 40] },
  "credential_stuffing": { "probability": 0.01, "failed_attempts_range": [5, 15] }
}
```

> **Note:** If you change the attack probabilities, update `contamination` in `train.py` to match the new attack rate, or simply retrain — `contamination` is auto-derived from `df["label"].mean()` in the current `train.py`.

### Consumer tuning (`consumer/consumer.py`)

```python
BATCH_SIZE   = 50    # MongoDB insert_many batch size
LOG_INTERVAL = 100   # Progress log every N events
```

---

## Roadmap

- [x] Kafka producer-consumer pipeline
- [x] Online sliding-window feature engineering
- [x] Isolation Forest with calibrated contamination
- [x] Batched MongoDB inserts
- [x] Lazy model loading + hot-reload
- [x] Streamlit monitoring dashboard
- [ ] Impossible travel speed capping (2000 km/h ceiling)
- [x] Replace Streamlit with HTML/CSS/JS professional frontend
- [ ] Add `failed_ratio` feature (failures / total attempts per window)
- [ ] Geodesic distance feature between consecutive login countries
- [ ] Per-user baseline model (one-class SVM per high-value account)
- [ ] Kafka multi-partition scaling
- [ ] Prometheus + Grafana metrics export

---

<div align="center">
<sub>Built with Python · Apache Kafka · MongoDB · scikit-learn · Streamlit</sub>
</div>