# SecureCommerce AI

Real-time big data analytics platform for detecting brute-force account takeover attempts in e-commerce login traffic.

## Module 1: Synthetic Data Generation

Module 1 creates labeled synthetic login events that can feed the rest of the pipeline:

- Kafka producer replay
- MongoDB persistence
- dashboard monitoring
- rule-based detection
- ML feature engineering and model training

The project scope is intentionally limited to brute-force login attacks.

### Generate a sample dataset

```powershell
python scripts/generate_synthetic_data.py --events 10000 --attack-rate 0.08
```

Outputs are written to `datasets/synthetic/`:

- `login_events.jsonl`
- `login_events.csv`
- `users.csv`
- `generation_summary.json`

### Event Label

`label = 0` means normal login activity.

`label = 1` means brute-force attack activity.

