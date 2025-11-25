from src.agents.ingestion.dispatcher import auto_ingest
from src.core.observability.error_reporter import capture_and_log_exception

def orchestrator_run_ingest(orchestrator, source, **kwargs):
    try:
        raw = auto_ingest(source)
        return orchestrator.run(raw, **kwargs)
    except Exception as e:
        capture_and_log_exception({"where": "ingest_wrapper", "error": str(e)})
        return {"error": str(e)}