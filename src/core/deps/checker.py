from src.core.logger import debug
from src.core.config import is_local_mode # <--- FIXED IMPORT
from src.core.deps.manifest import DEPENDENCIES
from src.core.deps.tester import try_import

def check_agent_dependencies(agent_name: str, required_deps: list):
    if is_local_mode(): debug(f"Checking deps for {agent_name}", tag="deps")
    missing = []
    for key in required_deps:
        spec = DEPENDENCIES.get(key)
        if not spec: continue
        ok, _, _ = try_import(spec["import_name"])
        if not ok: missing.append(key)
    
    if missing:
        debug(f"Agent {agent_name} missing: {missing}", tag="deps")
        return False
    return True