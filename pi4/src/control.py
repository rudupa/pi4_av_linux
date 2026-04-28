from __future__ import annotations
from .models import VehicleState, PerceptionInputs


def planner(inputs: PerceptionInputs, mode: str):
    target_speed = 6.0 if mode == "auto" else 0.0
    if inputs.objects:
        target_speed = min(target_speed, 3.0)
    return {"target_speed": target_speed, "target_heading": 0.0}


def controller(state: VehicleState, plan: dict):
    err = plan["target_speed"] - state.speed_mps
    throttle = max(0.0, min(100.0, 30.0 * err))
    brake = max(0.0, min(100.0, -25.0 * err))
    steering = max(-20.0, min(20.0, plan["target_heading"] - state.heading_deg))
    return {"throttle_pct": throttle, "brake_pct": brake, "steering_deg": steering}
