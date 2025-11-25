import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

# Core Imports
from src.core.context.engine import ContextEngine
from src.core.orchestrator import Orchestrator
from src.agents.ingestion.dispatcher import auto_ingest
from src.core.tools.llm_wrapper import llm_wrapper
from src.core.secrets.manager import get_runtime_secrets
from src.utils.verification import run_structural_verification

app = FastAPI(title="Hypothesi v2.0", description="Autonomous Scientific Review System")

# 1. Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Input Schema
class ReviewRequest(BaseModel):
    source: str
    source_type: Optional[str] = None  # Optional: Auto-detected if missing
    use_llm: bool = False
    llm_model: str = "gemini-2.0-flash"

# 2. Serve the UI at the root path
@app.get("/")
def read_root():
    return FileResponse('static/index.html')

@app.get("/health")
def health_check():
    status = run_structural_verification()
    if not status["ok"]:
        return {"status": "unhealthy", "errors": status["errors"]}
    return {"status": "ok", "system": "Hypothesi v2.0", "mode": status["runtime_mode"]}

@app.post("/review")
def run_review(req: ReviewRequest):
    try:
        # Setup
        context_engine = ContextEngine(user_id="web-user")
        orchestrator = Orchestrator(context_engine)

        llm_callable = None
        if req.use_llm:
            try:
                get_runtime_secrets().require("GEMINI_API_KEY")
                # Pass the requested model to the wrapper
                llm_callable = llm_wrapper(model_id=req.llm_model)
            except Exception as e:
                return {"error": "LLM requested but configuration failed", "details": str(e)}

        # Auto-Ingest
        # We ignore req.source_type if provided, relying on auto-detection for robustness
        cleaned_text = auto_ingest(req.source)
        
        if isinstance(cleaned_text, dict) and cleaned_text.get("error"):
             return cleaned_text

        # Run
        result = orchestrator.run(
            raw_text=cleaned_text,
            use_llm=req.use_llm,
            llm_callable=llm_callable
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)