from src.core.logger import debug
from src.core.config import is_local_mode # <--- FIXED IMPORT

class SafeEmbeddingTool:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.available = self._check_availability()

    def _check_availability(self):
        try:
            import sentence_transformers
            return True
        except ImportError:
            debug("sentence-transformers missing.", tag="embedding")
            return False

    def load(self):
        if not self.available:
            raise RuntimeError("Embedding model unavailable.")
        
        try:
            from sentence_transformers import SentenceTransformer
            if is_local_mode(): debug(f"Loading model: {self.model_name}", tag="embedding")
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            debug(f"Failed to load model: {e}", tag="embedding")
            raise RuntimeError("Model load failed.")

    def embed(self, texts):
        if self.model is None:
            raise RuntimeError("Model not loaded. Call .load() first.")
        
        single = isinstance(texts, str)
        texts = [texts] if single else texts
        
        try:
            vectors = self.model.encode(texts, show_progress_bar=False)
            vectors = vectors.tolist() # Convert numpy to list
            return vectors[0] if single else vectors
        except Exception as e:
            debug(f"Embedding failed: {e}", tag="embedding")
            raise