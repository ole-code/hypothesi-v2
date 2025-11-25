import os
from src.core.config import is_local_mode
from src.core.logger import debug
from src.core.secrets.manager import get_runtime_secrets

def auto_inject_default():
    if not is_local_mode(): return
    RS = get_runtime_secrets()
    try:
        val = RS.get("GEMINI_API_KEY", required=False)
        if val and "GEMINI_API_KEY" not in os.environ:
            os.environ["GEMINI_API_KEY"] = val
            debug("Injected GEMINI_API_KEY into os.environ", tag="secrets")
    except Exception: pass