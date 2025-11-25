from src.core.observability.error_reporter import capture_and_log_exception
from src.core.tools.rag_wrapper import rag_retriever_wrapper
from src.agents.structure import ScientificStructureExtractorFactory
from src.agents.claims import ClaimExtractionAgentFactory
from src.agents.evidence import EvidenceLinkingAgentFactory
from src.agents.reliability import ReliabilityScoringAgentFactory
from src.agents.meta_reviewer import MetaReviewerAgentFactory

class Orchestrator:
    def __init__(self, context_engine):
        self.context_engine = context_engine

    def run(self, raw_text, use_llm=False, llm_callable=None, **kwargs):
        try:
            self.context_engine.ingest_text(raw_text)
            
            extractor = ScientificStructureExtractorFactory(self.context_engine, llm_callable)
            claim_agent = ClaimExtractionAgentFactory(self.context_engine, llm_callable)
            retriever = rag_retriever_wrapper(self.context_engine)
            evidence_agent = EvidenceLinkingAgentFactory(self.context_engine, retriever, llm_callable)
            rel_agent = ReliabilityScoringAgentFactory(self.context_engine, llm_callable)
            meta_agent = MetaReviewerAgentFactory(self.context_engine, llm_callable)

            struct = extractor.extract(raw_text)
            claims = claim_agent.extract(struct).get("claims", [])
            evidence = evidence_agent.link_evidence(claims).get("links", [])
            score = rel_agent.score(struct, claims, evidence)
            final = meta_agent.review(struct, claims, evidence, score)
            
            return final
        except Exception as e:
            capture_and_log_exception({"where": "orchestrator", "error": str(e)})
            return {"error": str(e)}