import time
class ShortTermMemory:
    def __init__(self): self.items = []
    def add(self, content, metadata=None):
        self.items.append({"ts": time.time(), "content": content, "meta": metadata or {}})

class LongTermMemory:
    def __init__(self): self.store = {}
    def add(self, key, val): self.store[key] = val