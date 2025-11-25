from src.core.logger import debug

class ContextConfig:
    def __init__(self, chunk_size=800, chunk_overlap=100, retrieval_k=5):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retrieval_k = retrieval_k
    
debug("ContextConfig loaded", tag="ctx")