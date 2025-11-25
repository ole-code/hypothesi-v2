import time
import re
from typing import List, Dict, Any
from src.core.observability.helpers import agent_start, agent_end
from src.core.observability.error_reporter import capture_and_log_exception
from src.core.tools.sanitizer import sanitizer
from src.core.tools.text_prep import text_preprocessor
from src.core.tools.rag_wrapper import rag_retriever_wrapper
from src.core.deps.checker import check_agent_dependencies

def EvidenceLinkingAgentFactory(context_engine, retriever_callable=None, llm_callable=None, embedder=None, retrieval_k=5):
    
    if not retriever_callable:
        retriever_callable = rag_retriever_wrapper(context_engine)

    class EvidenceLinkingAgent:
        def __init__(self):
            self.agent_name = "EvidenceLinkingAgent"
            self.retrieval_k = retrieval_k
            
            # Dependency check (non-fatal)
            try: check_agent_dependencies(self.agent_name, ["sentence_transformers"])
            except: pass

        def _heuristic_classify(self, claim: str, chunk: str) -> str:
            """
            Restored Logic from Block 7.3:
            Keyword-based support/contradiction detection.
            """
            try:
                c = (chunk or "").lower()
                
                # Logic from Kaggle Block 7.3
                support_pattern = re.compile(
                    r"\b(significant|support|consistent|increase|decrease|improve|improves|benefit|better|show|reduction|reduced|associate|associated|suggest)\b",
                    re.I
                )
                contradict_pattern = re.compile(
                    r"\b(no evidence|not significant|contradict|did not|failed to|no effect|inconsistent|reversed|null effect|no difference)\b",
                    re.I
                )

                if contradict_pattern.search(c):
                    return "contradicts"
                if support_pattern.search(c):
                    return "supports"

                # Token overlap fallback (3+ matching big words)
                claim_tokens = set(re.findall(r"\b\w{4,}\b", (claim or "").lower()))
                chunk_tokens = set(re.findall(r"\b\w{4,}\b", c))
                if claim_tokens and len(claim_tokens & chunk_tokens) >= 3:
                    return "supports"

                return "insufficient"
            except:
                return "insufficient"

        def _llm_classify(self, claim, chunk, session_id):
            try:
                prompt = (
                    "Classify if the Evidence supports, contradicts, or is insufficient for the Claim.\n"
                    "Return ONE word: supports / contradicts / insufficient.\n\n"
                    f"Claim: {claim}\nEvidence: {chunk}"
                )
                resp = llm_callable(prompt, session_id=session_id, agent_name=self.agent_name)
                text = resp.lower().strip()
                if "contrad" in text: return "contradicts"
                if "support" in text: return "supports"
                return "insufficient"
            except:
                return None

        def link_evidence(self, claims, session_id=None):
            sid = session_id or "unknown-session"
            agent_start(sid, self.agent_name)

            results = []
            try:
                for claim in claims:
                    # Sanitize claim before retrieval
                    safe_claim = text_preprocessor(sanitizer(claim))
                    
                    # Retrieve
                    chunks, prov = retriever_callable(safe_claim, k=self.retrieval_k)
                    evidence_entries = []

                    for i, chunk in enumerate(chunks):
                        safe_chunk = text_preprocessor(sanitizer(chunk))
                        classification = None

                        # 1. Try LLM
                        if llm_callable:
                            classification = self._llm_classify(safe_claim, safe_chunk, sid)
                        
                        # 2. Fallback Heuristic
                        if not classification:
                            classification = self._heuristic_classify(safe_claim, safe_chunk)

                        evidence_entries.append({
                            "chunk": safe_chunk,
                            "classification": classification,
                            "provenance": prov[i] if i < len(prov) else {"source": "retrieval"}
                        })

                    results.append({
                        "claim": claim,
                        "evidence": evidence_entries
                    })
                
                agent_end(sid, self.agent_name)
                return {"links": results}

            except Exception as e:
                capture_and_log_exception({"where": "EvidenceLinking", "error": str(e)})
                return {"links": [], "error": str(e)}

    return EvidenceLinkingAgent()