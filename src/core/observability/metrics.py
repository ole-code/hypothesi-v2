import os
import json
from collections import defaultdict
from src.core.logger import debug
from src.core.observability.config import OBSERVABILITY_CONFIG

METRICS_FILE = OBSERVABILITY_CONFIG["metrics_file"]

def read_metrics():
    if not os.path.exists(METRICS_FILE):
        return []
    records = []
    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except Exception:
                    continue
    except Exception as e:
        debug(f"Failed reading metrics: {e}", tag="metrics")
    return records

def aggregate_token_usage(records):
    by_agent = defaultdict(lambda: {"tokens_in": 0, "tokens_out": 0, "calls": 0})
    for r in records:
        agent = r.get("agent", "unknown")
        by_agent[agent]["tokens_in"] += r.get("prompt_tokens", 0)
        by_agent[agent]["tokens_out"] += r.get("completion_tokens", 0)
        by_agent[agent]["calls"] += 1
    return by_agent