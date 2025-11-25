from src.core.context.config import ContextConfig
from src.core.context.session import Session
from src.core.context.memory import ShortTermMemory
from src.core.context.provenance import ProvenanceTracker
from src.core.context.chunker import chunk_text
from src.core.context.retrieval import RetrievalEngine

class ContextEngine:
    def __init__(self, user_id="anon", config=None):
        self.config = config or ContextConfig()
        self.session = Session(user_id)
        self.st_memory = ShortTermMemory()
        self.provenance = ProvenanceTracker()
        self.retriever = RetrievalEngine(self.config)
        self.chunks = []

    def ingest_text(self, text: str):
        chunks = chunk_text(text, self.config)
        self.chunks.extend(chunks)
        self.retriever.build_index(self.chunks)
        self.provenance.add({"count": len(chunks)}, source="ingest")
    
    def retrieve(self, query):
        return self.retriever.search(query)