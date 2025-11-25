import time
from src.core.logger import debug
from src.core.config import is_local_mode  # <--- FIXED IMPORT

def capture_and_log_exception(info: dict):
    if is_local_mode():
        debug(f"[EXCEPTION] {info}", tag="error")
    return f"err-{int(time.time()*1000)}"