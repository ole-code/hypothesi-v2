import json
import re
from src.core.observability.helpers import agent_start, agent_end
from src.core.observability.error_reporter import capture_and_log_exception
from src.core.tools.sanitizer import sanitizer
from src.core.tools.text_prep import text_preprocessor

def ClaimExtractionAgentFactory(context_engine, llm_callable=None, **kwargs):
    class ClaimAgent:
        def __init__(self):
            self.agent_name = "ClaimExtractionAgent"

        def _heuristic_scan(self, text):
            """Scans raw text for claim-like sentences."""
            if not text: return []
            
            # Clean and split
            clean = text_preprocessor(sanitizer(text, max_lines=1000))
            # Split by punctuation
            sentences = re.split(r'(?<=[\.\?\!])\s+', clean)
            
            # Keywords that imply a finding
            keywords = re.compile(r'(?i)\b(show|suggest|found|observ|demonstrat|increas|decreas|significan|result|conclud)\b')
            
            claims = []
            for s in sentences:
                s = s.strip()
                # Filter for reasonable length and keywords
                if 20 < len(s) < 500 and keywords.search(s):
                    claims.append(s)
            
            return list(set(claims))[:10]

        def extract(self, struct, session_id=None):
            agent_start(session_id, self.agent_name)
            
            claims = []
            
            # 1. Try LLM
            if llm_callable:
                try:
                    prompt = (
                        "Extract 3-5 core scientific claims from this data. "
                        "Return STRICT JSON: {\"claims\": [\"string\"]}\n"
                        f"Data: {json.dumps({k:v for k,v in struct.items() if k != 'full_text'})}"
                    )
                    res = llm_callable(prompt, agent_name="Claims")
                    clean = res.replace("```json", "").replace("```", "").strip()
                    claims = json.loads(clean).get("claims", [])
                except Exception as e:
                    capture_and_log_exception({"where": "Claim_LLM", "error": str(e)})

            # 2. Heuristic Fallback (Targeted Sections)
            if not claims:
                # Try specific sections first
                priority_text = (struct.get("results", "") + " " + struct.get("conclusion", "") + " " + struct.get("abstract", ""))
                claims = self._heuristic_scan(priority_text)

            # 3. "Nuclear" Fallback (Scan Full Text)
            if not claims and struct.get("full_text"):
                # If structure failed, scan the raw text
                claims = self._heuristic_scan(struct["full_text"])

            agent_end(session_id, self.agent_name)
            
            # Ensure we never return None
            return {"claims": claims if claims else []}

    return ClaimAgent()