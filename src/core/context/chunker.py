from typing import List
from src.core.context.config import ContextConfig

def chunk_text(text: str, config: ContextConfig) -> List[str]:
    if not text: return []
    size, overlap = config.chunk_size, config.chunk_overlap
    chunks, i, n = [], 0, len(text)
    while i < n:
        end = min(i + size, n)
        chunks.append(text[i:end].strip())
        i += size - overlap
    return chunks