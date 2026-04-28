from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class VehicleState:
    mode: str = "auto"
    speed_mps: float = 0.0
    steering_deg: float = 0.0
    throttle_pct: float = 0.0
    brake_pct: float = 0.0
    x: float = 0.0
    y: float = 0.0
    heading_deg: float = 0.0
    seq: int = 0


@dataclass
class PerceptionInputs:
    objects: list = field(default_factory=list)
    lane: dict = field(default_factory=dict)
    radar: dict = field(default_factory=dict)
    objects_ts: float = 0.0
    lane_ts: float = 0.0
    radar_ts: float = 0.0

    def is_stale(self, now_ts: float, timeout_s: float = 0.5):
        return (now_ts - self.objects_ts) > timeout_s or (now_ts - self.lane_ts) > timeout_s
