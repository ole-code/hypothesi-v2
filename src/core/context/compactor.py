from src.core.context.config import ContextConfig
from src.core.logger import debug

class ContextCompactor:
    def __init__(self, max_tokens=None):
        self.max_tokens = max_tokens or 6000

    def _estimate_tokens(self, text: str):
        # Rough heuristic: 1 token ~= 4 chars
        return max(1, int(len(text) / 4))

    def compact(self, chunks):
        total = sum(self._estimate_tokens(c) for c in chunks)
        if total <= self.max_tokens:
            return chunks

        debug("Compacting context to fit token budget...", tag="compactor")
        out = chunks.copy()
        while out and sum(self._estimate_tokens(c) for c in out) > self.max_tokens:
            out.pop(0) # Remove oldest chunks
        return out