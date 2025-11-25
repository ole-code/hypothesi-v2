import json
import re
from src.core.observability.helpers import agent_start, agent_end
from src.core.observability.error_reporter import capture_and_log_exception
from src.core.tools.sanitizer import sanitizer

def ScientificStructureExtractorFactory(context_engine, llm_callable=None, **kwargs):
    class Extractor:
        def extract(self, text, session_id=None):
            agent_start(session_id, "StructureExtractor")
            
            # Default Output
            out = {
                "title": "Unknown Title",
                "abstract": "",
                "methods": "", 
                "results": "", 
                "conclusion": "",
                # ADDED: Pass full text so downstream agents don't starve
                "full_text": text or "" 
            }

            # 1. Try LLM Extraction
            if llm_callable:
                try:
                    prompt = (
                        "Extract structure from this text. Return STRICT JSON.\n"
                        "Keys: title, abstract, methods, results, conclusion.\n"
                        "If a section is missing, leave it empty strings.\n\n"
                        f"Text: {text[:15000]}"
                    )
                    response = llm_callable(prompt, agent_name="Structure")
                    clean_json = response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    out.update(data) # Merge LLM results
                    out["full_text"] = text # Ensure full_text persists
                    agent_end(session_id, "StructureExtractor")
                    return out
                except Exception as e:
                    capture_and_log_exception({"where": "Structure_LLM", "error": str(e)})

            # 2. Heuristic Fallback
            safe = sanitizer(text)
            lines = safe.splitlines()
            if lines: out["title"] = lines[0][:200]

            # Regex splitting
            parts = re.split(r'(?mi)\n+(abstract|methods?|results?|conclusion|discussion)\b', "\n" + safe)
            
            if len(parts) > 1:
                it = iter(parts)
                next(it)
                for h, content in zip(it, it):
                    key = h.lower().strip()
                    if "abstract" in key: out["abstract"] += content
                    elif "method" in key: out["methods"] += content
                    elif "result" in key: out["results"] += content
                    elif "concl" in key or "discuss" in key: out["conclusion"] += content
            else:
                # Fallback: If no headers found, put everything in abstract so it isn't lost
                out["abstract"] = safe[:5000] 

            agent_end(session_id, "StructureExtractor")
            return out

    return Extractor()