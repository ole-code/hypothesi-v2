import os
import time
import unicodedata
import textwrap

from src.core.context.engine import ContextEngine
from src.core.orchestrator import Orchestrator
from src.agents.ingestion.dispatcher import auto_ingest
from src.agents.ingestion.pdf import PdfIngestionTool
from src.agents.ingestion.url import UrlIngestionTool
from src.agents.ingestion.arxiv import ArxivIngestionTool
from src.core.observability.error_reporter import capture_and_log_exception
from src.core.logger import debug

# ============================================================
# TEST A — End-to-End (Text Only)
# ============================================================
def run_test_text_only():
    start_ts = time.time()
    result = {"ok": True, "error": None, "duration_s": None, "pipeline_output": None}

    try:
        sample_text = """
        Title: The Effects of X on Y
        Abstract: We investigated whether X improves Y. We hypothesize improvement.
        Methods: Randomized controlled trial, N=120.
        Results: Significant improvements were observed.
        Conclusion: The findings support the hypothesis.
        """
        sample_text = unicodedata.normalize("NFC", sample_text)
        
        # Initialize Engine
        ce = ContextEngine(user_id="prod-test-A")
        orchestrator = Orchestrator(ce)
        
        # Run Orchestrator
        out = orchestrator.run(raw_text=sample_text, use_llm=False)
        result["pipeline_output"] = out

    except Exception as e:
        result["ok"] = False
        result["error"] = str(e)

    result["duration_s"] = time.time() - start_ts
    return result

# ============================================================
# TEST B — PDF Ingestion
# ============================================================
def run_pdf_test(path):
    t0 = time.time()
    out = {"ok": False, "error": None}
    
    if not os.path.exists(path):
        out["error"] = "File not found"
        return out

    try:
        tool = PdfIngestionTool()
        text = tool.load_pdf(path)
        out["ok"] = bool(text)
        out["text_len"] = len(text)
    except Exception as e:
        out["error"] = str(e)
    
    out["duration_s"] = time.time() - t0
    return out

# ============================================================
# TEST C — URL Ingestion
# ============================================================
def run_url_test(url):
    t0 = time.time()
    out = {"ok": False, "error": None}
    
    try:
        text = UrlIngestionTool(url)
        out["ok"] = bool(text)
        out["text_len"] = len(text)
    except Exception as e:
        out["error"] = str(e)
    
    out["duration_s"] = time.time() - t0
    return out

# ============================================================
# TEST D — Arxiv Ingestion
# ============================================================
def run_arxiv_test(arxiv_id):
    t0 = time.time()
    out = {"ok": False, "error": None}
    
    try:
        text = ArxivIngestionTool(arxiv_id)
        out["ok"] = bool(text)
        out["text_len"] = len(text)
    except Exception as e:
        out["error"] = str(e)
    
    out["duration_s"] = time.time() - t0
    return out

# ============================================================
# TEST E — Batch Pipeline
# ============================================================
def run_batch_test(items, llm_callable=None):
    results = []
    ce = ContextEngine(user_id="batch-test")
    orchestrator = Orchestrator(ce)

    for item in items:
        t0 = time.time()
        name = item.get("name", "unnamed")
        source = item.get("source")
        
        try:
            raw = auto_ingest(source)
            if isinstance(raw, dict) and raw.get("error"):
                results.append({"name": name, "error": raw["message"]})
                continue

            out = orchestrator.run(raw_text=raw, use_llm=bool(llm_callable), llm_callable=llm_callable)
            results.append({
                "name": name,
                "ok": True,
                "score": out.get("reliability_score"),
                "duration": time.time() - t0
            })
        except Exception as e:
            results.append({"name": name, "ok": False, "error": str(e)})
    
    return results