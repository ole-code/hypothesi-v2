import time
import unicodedata

from src.core.context.engine import ContextEngine
from src.core.orchestrator import Orchestrator
from src.agents.ingestion.dispatcher import auto_ingest
from src.core.observability.error_reporter import capture_and_log_exception
from src.core.logger import debug
from src.core.tools.sanitizer import sanitizer
from src.core.tools.text_prep import text_preprocessor

class Hypothesi:
    """
    Unified public API for scientific analysis.
    Production-safe version of hypothesi.analyze().
    """

    def __init__(self, user_id="default", llm_callable=None):
        self.context_engine = ContextEngine(user_id=user_id)
        self.orchestrator = Orchestrator(self.context_engine)
        self.llm_callable = llm_callable
        debug(f"Hypothesi initialized for user {user_id}", tag="system")

    def analyze(self, source, use_llm=False, **kwargs):
        t0 = time.time()
        try:
            # 1. Ingest
            raw = auto_ingest(source, **kwargs)
            if isinstance(raw, dict) and raw.get("error"):
                return raw

            # 2. Clean / Normalize
            cleaned = sanitizer(raw, max_lines=kwargs.get("max_lines", 5000))
            cleaned = text_preprocessor(cleaned, normalize_whitespace=True)
            cleaned = unicodedata.normalize("NFKC", cleaned)

            # 3. Run Pipeline
            final = self.orchestrator.run(
                raw_text=cleaned,
                use_llm=use_llm,
                llm_callable=self.llm_callable,
                embedder=kwargs.get("embedder", None),
                retrieval_k=kwargs.get("retrieval_k", 5)
            )
            return final

        except Exception as e:
            eid = capture_and_log_exception({"where": "hypothesi_analyze", "error": str(e)})
            return {
                "error": True, 
                "error_id": eid, 
                "message": str(e),
                "duration_s": time.time() - t0
            }