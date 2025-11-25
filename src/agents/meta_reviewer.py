import json
from src.core.observability.helpers import agent_start, agent_end
from src.core.observability.error_reporter import capture_and_log_exception

def MetaReviewerAgentFactory(context_engine, llm_callable=None):
    class MetaAgent:
        def review(self, struct, claims, evidence, reliability, session_id=None):
            agent_start(session_id, "MetaReviewer")
            
            # Defaults
            final = {
                "executive_summary": "Automated Review: Analysis complete.",
                "structured_data": struct,
                "claims": claims,
                "evidence_links": evidence,
                "reliability_score": reliability.get("score", 0),
                # ADDED: Pass the full reliability object so UI can read the explanation
                "reliability": reliability, 
                "limitations": "None detected.",
                "recommendation": "Review manually."
            }

            if llm_callable:
                try:
                    prompt = (
                        "Generate a scientific meta-review JSON.\n"
                        "Fields: executive_summary, limitations, recommendation.\n"
                        "No Markdown.\n\n"
                        f"Score: {reliability.get('score')}\n"
                        f"Claims: {json.dumps(claims[:5])}\n"
                    )
                    response = llm_callable(prompt, agent_name="MetaReviewer")
                    clean_json = response.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(clean_json)
                    
                    final["executive_summary"] = parsed.get("executive_summary", final["executive_summary"])
                    final["limitations"] = parsed.get("limitations", final["limitations"])
                    final["recommendation"] = parsed.get("recommendation", final["recommendation"])
                except Exception as e:
                    capture_and_log_exception({"where": "MetaReviewer_LLM", "error": str(e)})

            agent_end(session_id, "MetaReviewer")
            return final

    return MetaAgent()