import os
import json
from src.core.logger import debug
from src.core.config import is_local_mode # <--- FIXED IMPORT
from src.core.observability.config import OBSERVABILITY_CONFIG, utc_timestamp
from src.core.observability.event_logger import log_event

METRICS_FILE = OBSERVABILITY_CONFIG["metrics_file"]

def record_token_usage(agent_name, prompt_tokens=0, completion_tokens=0):
    try:
        entry = {
            "ts": utc_timestamp(),
            "agent": agent_name,
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
        }
        
        log_event("token_usage", entry)

        if is_local_mode():
            os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
            with open(METRICS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

        debug(f"[TOKEN] {agent_name}: in={prompt_tokens}, out={completion_tokens}", tag="metrics")
        return True
    except Exception as e:
        debug(f"[token_usage:error] {e}")
        return False