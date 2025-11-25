import os
from datetime import datetime, timezone
OBSERVABILITY_CONFIG = {
    "log_dir": "/mnt/data/hypothesi_logs",
    "events_file": "events.jsonl",
    "metrics_file": "metrics.jsonl"
}
def utc_timestamp(): return datetime.now(timezone.utc).isoformat()