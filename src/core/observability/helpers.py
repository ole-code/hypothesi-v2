from src.core.logger import debug

def agent_start(sid, name, extra=None):
    debug(f"START {name} ({sid})", tag="obs")

def agent_end(sid, name, extra=None):
    debug(f"END {name} ({sid})", tag="obs")