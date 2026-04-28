from __future__ import annotations
import psutil
from .models import now


def health_payload(seq: int, services: dict):
    return {
        "schema_version": 1,
        "timestamp_utc": now(),
        "source": "pi4-health",
        "sequence_id": seq,
        "cpu_pct": psutil.cpu_percent(interval=None),
        "mem_pct": psutil.virtual_memory().percent,
        "temp_c": 0.0,
        "services": services,
    }
