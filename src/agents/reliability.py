# ============================================================
# [7.4] RELIABILITY SCORING AGENT (Restored from Kaggle Block 7.4)
# ============================================================

import time
import json
from src.core.observability.helpers import agent_start, agent_end
from src.core.observability.error_reporter import capture_and_log_exception
from src.core.tools.sanitizer import sanitizer
from src.core.tools.text_prep import text_preprocessor
from src.core.deps.checker import check_agent_dependencies

def ReliabilityScoringAgentFactory(context_engine, llm_callable=None):

    class ReliabilityScoringAgent:
        def __init__(self, context_engine, llm_callable=None):
            self.context_engine = context_engine
            self.llm = llm_callable
            self.agent_name = "ReliabilityScoringAgent"
            
            # Dependency checks (non-fatal)
            try:
                check_agent_dependencies(self.agent_name, ["numpy", "pandas"])
            except: pass

        # ------------------------------------------------------
        # Fallback heuristic scoring (deterministic)
        # ------------------------------------------------------
        def _heuristic_score(self, structured, claims, evidence_links):
            try:
                score = 0
                reasons = []

                # 1. Methods section (+30)
                if (structured.get("methods") or "").strip():
                    score += 30
                    reasons.append("Methods section present (+30)")
                else:
                    reasons.append("Methods section missing (0)")

                # 2. Results section (+20)
                if (structured.get("results") or "").strip():
                    score += 20
                    reasons.append("Results section present (+20)")
                else:
                    reasons.append("Results section missing (0)")

                # 3. Claim/Evidence alignment (+30 max)
                total_claims = len(claims or [])
                supporting = 0
                contradicting = 0

                for link in (evidence_links or []):
                    evs = link.get("evidence", [])
                    if any(ev.get("classification") == "supports" for ev in evs):
                        supporting += 1
                    if any(ev.get("classification") == "contradicts" for ev in evs):
                        contradicting += 1

                ratio = supporting / total_claims if total_claims else 0
                align_score = int(round(ratio * 30))
                score += align_score
                reasons.append(
                    f"Claim-evidence alignment: {supporting}/{max(total_claims,1)} (+{align_score})"
                )

                # 4. Contradiction penalty (-20)
                if contradicting > 0:
                    score -= 20
                    reasons.append("Contradictory evidence found (-20)")

                # 5. Title + Abstract check (+10)
                if len(structured.get("title", "")) > 5 and len(structured.get("abstract", "")) > 50:
                    score += 10
                    reasons.append("Title + abstract adequate (+10)")
                else:
                    reasons.append("Title/abstract insufficient (0)")

                score = max(0, min(100, score))
                return score, "; ".join(reasons)

            except Exception as e:
                capture_and_log_exception({"where": "7.4._heuristic_score", "error": str(e)})
                return 0, "Heuristic scoring failed; forced score=0."

        # ------------------------------------------------------
        # LLM scoring (optional, safe)
        # ------------------------------------------------------
        def _llm_score(self, structured, claims, evidence_links):
            if not self.llm:
                return None, None

            try:
                # Compact inputs for prompt
                short_struct = {
                    "title": structured.get("title", "")[:300],
                    "abstract": structured.get("abstract", "")[:800],
                    "methods": structured.get("methods", "")[:800],
                    "results": structured.get("results", "")[:800],
                }

                # Simplified evidence list
                compressed_evidence = []
                for entry in (evidence_links or []):
                    compressed_evidence.append({
                        "claim": (entry.get("claim") or "")[:200],
                        "evidence_count": len(entry.get("evidence", [])),
                        "top_classification": entry.get("evidence", [{}])[0].get("classification", "none") if entry.get("evidence") else "none"
                    })

                prompt_raw = (
                    "Evaluate the reliability of the scientific document. "
                    "Provide a score (0–100) and a short explanation. "
                    "Return STRICT JSON ONLY:\n\n"
                    "{\"score\": NUMBER, \"explanation\": \"text\"}\n\n"
                    "Do not use Markdown formatting.\n\n"
                    f"Structured summary: {json.dumps(short_struct)}\n"
                    f"Claims alignment data: {json.dumps(compressed_evidence)}\n"
                )

                safe_prompt = text_preprocessor(sanitizer(prompt_raw, max_lines=200))

                out = self.llm(
                    safe_prompt,
                    agent_name=self.agent_name,
                    max_output_tokens=350,
                    temperature=0.0
                )
                
                # Clean Gemini markdown if present
                clean_json = out.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_json)

                val = int(parsed.get("score", 0))
                val = max(0, min(100, val))

                return val, parsed.get("explanation", "")

            except Exception as e:
                capture_and_log_exception({"where": "7.4._llm_score", "error": str(e)})
                return None, None

        # ------------------------------------------------------
        # MAIN: score()
        # ------------------------------------------------------
        def score(self, structured_doc, claims, evidence_links, session_id=None):
            sid = session_id or "unknown-session"
            agent_start(sid, self.agent_name, {"claims": len(claims or [])})

            try:
                # sanitize fields
                safe_struct = {
                    k: text_preprocessor(sanitizer(v), normalize_whitespace=True) if isinstance(v, str) else v
                    for k, v in (structured_doc or {}).items()
                }

                # LLM attempt
                score_val, explanation = None, None
                if self.llm:
                    score_val, explanation = self._llm_score(safe_struct, claims, evidence_links)

                # Fallback heuristic (Use YOUR logic from Block 7.4)
                if score_val is None:
                    score_val, explanation = self._heuristic_score(safe_struct, claims, evidence_links)

                result = {
                    "score": int(score_val),
                    "explanation": explanation
                }

                agent_end(sid, self.agent_name, {"score": result["score"]})
                return result

            except Exception as e:
                err_id = capture_and_log_exception({"where": "7.4.score.top", "error": str(e)})
                return {"score": 0, "explanation": f"Error: {str(e)}"}

    return ReliabilityScoringAgent(context_engine, llm_callable)