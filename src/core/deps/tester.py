import importlib
import traceback

def try_import(module_name):
    if module_name is None: return True, "Built-in", None
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, "__version__", None)
        return True, version, None
    except Exception:
        return False, None, traceback.format_exc()