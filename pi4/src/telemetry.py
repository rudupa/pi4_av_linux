from __future__ import annotations
import json
import queue
import time
import paho.mqtt.client as mqtt
from .models import VehicleState, now


class TelemetryClient:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.q = queue.Queue(maxsize=500)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.connected = False

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        self.connected = True
        for t in [self.cfg["commands"]["mode"], self.cfg["commands"]["reset"], self.cfg["commands"]["fault_inject"], self.cfg["commands"]["replay"]]:
            client.subscribe(t, qos=1)

    def start(self):
        self.client.connect_async(self.cfg["mqtt"]["host"], int(self.cfg["mqtt"]["port"]))
        self.client.loop_start()

    def publish(self, topic: str, payload: dict):
        try:
            self.q.put_nowait((topic, payload))
        except queue.Full:
            _ = self.q.get_nowait()
            self.q.put_nowait((topic, payload))

    def flush(self):
        while not self.q.empty() and self.connected:
            topic, payload = self.q.get()
            self.client.publish(topic, json.dumps(payload), qos=1)


def state_payload(state: VehicleState, mode: str):
    return {
        "schema_version": 1,
        "timestamp_utc": now(),
        "source": "pi4-sim",
        "sequence_id": state.seq,
        "mode": mode,
        "speed_mps": state.speed_mps,
        "steering_deg": state.steering_deg,
        "throttle_pct": state.throttle_pct,
        "brake_pct": state.brake_pct,
        "pose": {"x": state.x, "y": state.y, "heading_deg": state.heading_deg}
    }
