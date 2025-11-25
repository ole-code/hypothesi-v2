import os

DEFAULT_RUNTIME_MODE = "local"
_VALID_RUNTIME_MODES = {"local", "prod"}

_runtime_mode_env = os.environ.get("HYPOTHESI_RUNTIME_MODE")
RUNTIME_MODE = (_runtime_mode_env or DEFAULT_RUNTIME_MODE).strip().lower()

def is_local_mode() -> bool:
    return RUNTIME_MODE == "local"

def is_prod_mode() -> bool:
    return RUNTIME_MODE == "prod"