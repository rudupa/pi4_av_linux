from __future__ import annotations
import argparse
import glob
import json
import os
import threading
from dataclasses import dataclass
import time
import cv2
import numpy as np
import yaml
from .common import LatestFrameQueue, FixedRateTimer, Metrics, utc_now
from .edge_bus import EdgePublisher
from .perception import detect_objects, detect_lane, free_space_grid, fuse_camera_radar, profile_frame
from .radar import RadarTarget
from .schema_utils import validate_schema

@dataclass
class ControlState:
    running: bool = True
    paused: bool = False
    playback_rate: float = 1.0
    loop: bool = True
    offset: int = 0


class PlaybackNode:
    def __init__(self, config_path: str):
        self.cfg = yaml.safe_load(open(config_path, "r", encoding="utf-8"))
        self.metrics = Metrics()
        self.ctrl = ControlState()
        self.q = LatestFrameQueue(max_size=self.cfg.get("queue_size", 2))
        self.pub = EdgePublisher()
        self.seq = 0
        self.camera_files = sorted(glob.glob("pc/dataset/camera/*.jpg"))
        self.radar_files = sorted(glob.glob("pc/dataset/radar/*.json"))

    def load_calibration(self):
        return yaml.safe_load(open(self.cfg["camera"]["calibration_file"], "r", encoding="utf-8"))

    def run_producer(self):
        target = self.cfg.get("fps_target", 33)
        timer = FixedRateTimer(target)
        i = self.ctrl.offset
        while self.ctrl.running:
            if self.ctrl.paused:
                time.sleep(0.05)
                continue
            if not self.camera_files:
                frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            else:
                if i >= len(self.camera_files):
                    if self.ctrl.loop:
                        i = 0
                    else:
                        break
                frame = cv2.imread(self.camera_files[i])
            payload = {
                "schema_version": 1,
                "timestamp_utc": utc_now(),
                "source": "pc-playback",
                "sequence_id": self.seq,
                "shape": list(frame.shape),
            }
            dropped = self.q.push((frame, payload, i))
            self.metrics.received_frames += 1
            if dropped:
                self.metrics.dropped_frames += 1
            self.seq += 1
            i += 1
            timer.wait_next()

    def _load_radar(self, idx: int):
        if idx < len(self.radar_files):
            data = json.load(open(self.radar_files[idx], "r", encoding="utf-8"))
            return [RadarTarget(float(t["r"]), float(t["v"]), float(t["a"])) for t in data.get("targets", [])]
        return []

    def run_consumer(self):
        while self.ctrl.running:
            item = self.q.pop(0.2)
            if item is None:
                self.metrics.lag_events += 1
                continue
            frame, sensor_meta, idx = item
            radar_targets = self._load_radar(idx)
            cam_objs, ms_obj = profile_frame(detect_objects, frame, self.cfg.get("confidence_threshold", 0.4))
            lane, ms_lane = profile_frame(detect_lane, frame)
            occ, ms_occ = profile_frame(free_space_grid, frame)
            fused = fuse_camera_radar(cam_objs, radar_targets)

            out_obj = {
                "schema_version": 1,
                "timestamp_utc": utc_now(),
                "source": "pc-perception",
                "sequence_id": sensor_meta["sequence_id"],
                "objects": fused,
            }
            validate_schema("perception_objects_v1", out_obj)
            self.pub.publish(self.cfg["topics"]["perception_objects"], out_obj)

            lane_msg = {
                "schema_version": 1,
                "timestamp_utc": utc_now(),
                "source": "pc-perception",
                "sequence_id": sensor_meta["sequence_id"],
                "lane": lane,
                "free_space": occ,
            }
            self.pub.publish(self.cfg["topics"]["perception_lane"], lane_msg)

            self.metrics.processed_frames += 1
            self.metrics.inference_ms_last = ms_obj + ms_lane + ms_occ
            self.metrics.fps_last = min(self.cfg.get("fps_target", 33), 1000.0 / max(self.metrics.inference_ms_last, 1.0))
            self.metrics.gpu_utilization_pct = 0.0

    def run(self):
        _ = self.load_calibration()
        tp = threading.Thread(target=self.run_producer, daemon=True)
        tc = threading.Thread(target=self.run_consumer, daemon=True)
        tp.start(); tc.start()
        while self.ctrl.running:
            time.sleep(1.0)
            print({"processed": self.metrics.processed_frames, "drop": self.metrics.dropped_frames, "fps": round(self.metrics.fps_last,2), "infer_ms": round(self.metrics.inference_ms_last,2)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="pc/config/default.yaml")
    args = ap.parse_args()
    PlaybackNode(args.config).run()

if __name__ == "__main__":
    main()
