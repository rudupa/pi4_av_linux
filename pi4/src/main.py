from __future__ import annotations
import argparse
import json
import time
import yaml
from pathlib import Path
from .models import VehicleState, PerceptionInputs
from .control import planner, controller
from .sim import step
from .telemetry import TelemetryClient, state_payload
from .health import health_payload


def run(config_path: str):
    cfg = yaml.safe_load(Path(config_path).read_text())
    dt = 1.0 / float(cfg.get("tick_hz", 20))
    mode = cfg.get("mode", "auto")
    fault = {}

    state = VehicleState(mode=mode)
    inputs = PerceptionInputs()
    tclient = TelemetryClient(cfg)

    def on_message(client, userdata, msg):
        nonlocal mode, fault
        try:
            payload = json.loads(msg.payload.decode()) if msg.payload else {}
        except Exception:
            payload = {}
        topic = msg.topic
        if topic == cfg["commands"]["mode"]:
            req = payload.get("mode")
            if req in ["manual", "auto", "safe", "degraded"]:
                mode = req
                tclient.publish(cfg["mqtt"]["topic_events"], {"schema_version":1,"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),"source":"pi4-cmd","sequence_id":state.seq,"event_type":"cmd_mode_applied","details":{"mode":mode}})
            else:
                tclient.publish(cfg["mqtt"]["topic_events"], {"schema_version":1,"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),"source":"pi4-cmd","sequence_id":state.seq,"event_type":"cmd_mode_rejected","details":{"reason":"invalid_mode"}})
        elif topic == cfg["commands"]["reset"]:
            state.speed_mps = 0.0
            state.x = state.y = state.heading_deg = 0.0
        elif topic == cfg["commands"]["fault_inject"]:
            fault = {"delay_control": bool(payload.get("enabled", True))}
        elif topic == cfg["commands"]["replay"]:
            pass

    tclient.client.on_message = on_message
    tclient.start()

    while True:
        now_ts = time.time()
        if inputs.is_stale(now_ts, timeout_s=0.75):
            mode_eff = "degraded"
        else:
            mode_eff = mode

        plan = planner(inputs, mode_eff)
        cmd = controller(state, plan)
        state = step(state, cmd, dt, fault)

        tclient.publish(cfg["mqtt"]["topic_state"], state_payload(state, mode_eff))
        tclient.publish(cfg["mqtt"]["topic_health"], health_payload(state.seq, {"pi4-main": "active"}))
        tclient.publish(cfg["mqtt"]["topic_perception_summary"], {
            "schema_version": 1,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": "pi4-main",
            "sequence_id": state.seq,
            "object_count": len(inputs.objects),
            "radar_target_count": len(inputs.radar) if isinstance(inputs.radar, list) else 0,
            "fps": 1.0 / dt,
            "drop_ratio": 0.0,
        })
        tclient.flush()
        time.sleep(dt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="pi4/config/runtime.yaml")
    args = ap.parse_args()
    run(args.config)

if __name__ == "__main__":
    main()
