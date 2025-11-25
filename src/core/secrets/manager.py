from typing import Callable, Dict, Optional, List
from src.core.config import is_local_mode
from src.core.logger import debug
from src.core.secrets.loader import get_secret as _get_secret

Validator = Callable[[Optional[str]], None]

class RuntimeSecrets:
    def __init__(self):
        self._cache: Dict[str, Optional[str]] = {}
        self._validators: Dict[str, Validator] = {}

    def get(self, key: str, required: bool = False) -> Optional[str]:
        if key in self._cache: return self._cache[key]
        value = _get_secret(key, required=False)
        if value is None:
            if required:
                msg = f"Required secret '{key}' missing."
                if is_local_mode(): debug(msg, tag="secrets_mgr")
                else: raise RuntimeError(msg)
            self._cache[key] = None
            return None
        
        if key in self._validators:
            self._validators[key](value)
            
        self._cache[key] = value
        return value

    def require(self, key: str) -> str:
        return self.get(key, required=True)

_runtime_instance = RuntimeSecrets()
def get_runtime_secrets() -> RuntimeSecrets:
    return _runtime_instance