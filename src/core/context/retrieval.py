import re
from sklearn.neighbors import NearestNeighbors
from src.core.logger import debug
from src.core.context.config import ContextConfig

try:
    from sentence_transformers import SentenceTransformer
    _HAS_ST = True
except ImportError:
    _HAS_ST = False

class RetrievalEngine:
    def __init__(self, config: ContextConfig):
        self.config = config
        self.chunks = []
        self.index = None
        self.model = None
        if _HAS_ST:
            try: self.model = SentenceTransformer("all-MiniLM-L6-v2")
            except: pass

    def build_index(self, chunks):
        self.chunks = chunks
        if self.model and chunks:
            try:
                embeddings = self.model.encode(chunks)
                self.index = NearestNeighbors(n_neighbors=self.config.retrieval_k).fit(embeddings)
            except: pass

    def search(self, query: str):
        if not query.strip() or not self.chunks: return []
        if self.index and self.model:
            try:
                vec = self.model.encode([query])
                _, idx = self.index.kneighbors(vec)
                return [self.chunks[i] for i in idx[0]]
            except: pass
        
        # Fallback: lexical overlap
        q_toks = set(re.findall(r"\w+", query.lower()))
        scores = []
        for c in self.chunks:
            c_toks = set(re.findall(r"\w+", c.lower()))
            scores.append((len(q_toks & c_toks), c))
        return [s[1] for s in sorted(scores, key=lambda x: x[0], reverse=True)[:self.config.retrieval_k]]