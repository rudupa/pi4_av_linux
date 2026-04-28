from __future__ import annotations
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class RadarTarget:
    r: float
    v: float
    a: float


def cluster_targets(points: List[RadarTarget]) -> List[RadarTarget]:
    if not points:
        return []
    # Baseline: simple binning cluster by angle and range.
    clusters = {}
    for p in points:
        key = (round(p.a / 5.0), round(p.r / 3.0))
        clusters.setdefault(key, []).append(p)
    out = []
    for pts in clusters.values():
        out.append(RadarTarget(
            r=float(np.mean([x.r for x in pts])),
            v=float(np.mean([x.v for x in pts])),
            a=float(np.mean([x.a for x in pts])),
        ))
    return out
