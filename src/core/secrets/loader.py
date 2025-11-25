import os
from typing import Optional, Dict
from src.core.config import is_local_mode
from src.core.logger import debug

_SECRET_CACHE: Dict[str, Optional[str]] = {}

def load_dotenv_if_local(dotenv_path: str = ".env"):
    if not is_local_mode(): return
    abs_path = os.path.abspath(dotenv_path)
    if not os.path.exists(abs_path): return

    try:
        with open(abs_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line: continue
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())
    except Exception as e:
        debug(f"Failed to load .env: {e}", tag="secrets")

def get_secret(key: str, required: bool = True) -> Optional[str]:
    if key in _SECRET_CACHE: return _SECRET_CACHE[key]
    val = os.environ.get(key)
    if val is None:
        if required:
            if is_local_mode(): debug(f"Missing secret: {key}", tag="secrets")
            else: raise RuntimeError(f"Required secret '{key}' not found.")
        _SECRET_CACHE[key] = None
        return None
    _SECRET_CACHE[key] = val
    return val

load_dotenv_if_local()