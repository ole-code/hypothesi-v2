from src.core.config import RUNTIME_MODE

def debug(*args, **kwargs):
    """
    Notebook & production-safe debug helper.
    """
    try:
        if RUNTIME_MODE == "local":
            allowed = {k: v for k, v in kwargs.items()
                       if k in ("sep", "end", "file", "flush")}
            print("[DEBUG]", *args, **allowed)
    except Exception:
        pass