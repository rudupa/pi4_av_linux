from __future__ import annotations
import random
import time
import cv2
import numpy as np
from .radar import RadarTarget, cluster_targets


def detect_objects(frame: np.ndarray, confidence_threshold: float = 0.4):
    # Baseline detector: contour-based proxy for moving/bright objects.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objs = []
    idx = 0
    for c in cnts[:20]:
        x, y, w, h = cv2.boundingRect(c)
        conf = min(0.95, 0.5 + (w * h) / 20000.0)
        if conf < confidence_threshold:
            continue
        objs.append({
            "id": f"cam-{idx}",
            "class": "vehicle" if w > 40 else "unknown",
            "confidence": round(conf, 3),
            "bbox": [float(x), float(y), float(w), float(h)],
            "range_m": float(max(1.0, 40.0 - h / 5.0)),
            "rel_velocity_mps": 0.0,
            "source_flags": ["camera"],
            "track_state": "tracked",
            "uncertainty": {"range_cov": 1.5, "velocity_cov": 2.0, "angle_cov": 0.6},
        })
        idx += 1
    return objs


def detect_lane(frame: np.ndarray):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=80, maxLineGap=20)
    return {"line_count": int(0 if lines is None else len(lines))}


def free_space_grid(frame: np.ndarray):
    h, w, _ = frame.shape
    return {"grid_w": 20, "grid_h": 20, "occupied_ratio": float(random.uniform(0.05, 0.35))}


def fuse_camera_radar(camera_objects: list, radar_targets: list[RadarTarget]):
    clusters = cluster_targets(radar_targets)
    if not clusters:
        return camera_objects
    fused = []
    for i, obj in enumerate(camera_objects):
        if i < len(clusters):
            rt = clusters[i]
            obj = dict(obj)
            obj["range_m"] = float((obj["range_m"] + rt.r) / 2.0)
            obj["rel_velocity_mps"] = float(rt.v)
            obj["source_flags"] = ["camera", "radar", "fused"]
        fused.append(obj)
    return fused


def profile_frame(fn, *args, **kwargs):
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    return out, (time.perf_counter() - t0) * 1000.0
