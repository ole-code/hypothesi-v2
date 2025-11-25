import os
import re
from src.core.config import is_prod_mode
from src.core.logger import debug

class GeminiKeyError(Exception): pass

def validate_gemini_api_key(env_var_name: str = "GEMINI_API_KEY") -> None:
    key = os.environ.get(env_var_name)
    if not key:
        msg = f"{env_var_name} is missing."
        if is_prod_mode(): raise GeminiKeyError(msg)
        debug(msg, tag="secrets"); return

    if not key.startswith("AIza"):
        msg = f"{env_var_name} malformed — expected prefix 'AIza'."
        if is_prod_mode(): raise GeminiKeyError(msg)
        debug(msg, tag="secrets"); return