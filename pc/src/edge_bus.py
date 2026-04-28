from __future__ import annotations
import json
import os
import time

class EdgePublisher:
    """Baseline publish adapter. In production, replace with pyzenoh publisher."""
    def __init__(self, out_dir: str = "pc/outbox"):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    def publish(self, topic: str, payload: dict):
        safe = topic.strip("/").replace("/", "_")
        path = f"{self.out_dir}/{int(time.time()*1000)}_{safe}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
