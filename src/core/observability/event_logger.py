import json
from src.core.observability.config import utc_timestamp
from src.core.logger import debug

def log_event(event_type: str, payload: dict):
    entry = {"ts": utc_timestamp(), "type": event_type, "payload": payload}
    debug(f"[EVENT:{event_type}] {str(payload)[:100]}", tag="obs")