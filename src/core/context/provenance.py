import time
class ProvenanceTracker:
    def __init__(self): self.records = []
    def add(self, item, source="unknown"):
        self.records.append({"ts": time.time(), "source": source, "item": item})