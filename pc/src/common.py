from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import queue
import threading
import time
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Metrics:
    received_frames: int = 0
    processed_frames: int = 0
    dropped_frames: int = 0
    lag_events: int = 0
    inference_ms_last: float = 0.0
    fps_last: float = 0.0
    gpu_utilization_pct: float = 0.0
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class LatestFrameQueue:
    def __init__(self, max_size: int = 2):
        self._q = queue.Queue(maxsize=max_size)
        self._lock = threading.Lock()

    def push(self, item) -> bool:
        with self._lock:
            dropped = False
            if self._q.full():
                try:
                    self._q.get_nowait()
                    dropped = True
                except queue.Empty:
                    pass
            self._q.put_nowait(item)
            return dropped

    def pop(self, timeout: float = 0.1):
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None


class FixedRateTimer:
    def __init__(self, hz: float):
        self.period = 1.0 / hz
        self.next_tick = time.perf_counter()

    def wait_next(self):
        self.next_tick += self.period
        dt = self.next_tick - time.perf_counter()
        if dt > 0:
            time.sleep(dt)
