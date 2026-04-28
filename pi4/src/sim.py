from __future__ import annotations
import math
from .models import VehicleState


def step(state: VehicleState, cmd: dict, dt: float, fault: dict | None = None):
    fault = fault or {}
    throttle = cmd["throttle_pct"]
    brake = cmd["brake_pct"]
    if fault.get("delay_control"):
        throttle *= 0.6
    accel = 0.03 * throttle - 0.04 * brake
    state.speed_mps = max(0.0, state.speed_mps + accel * dt)
    state.steering_deg = cmd["steering_deg"]
    state.throttle_pct = throttle
    state.brake_pct = brake
    state.heading_deg += state.steering_deg * 0.03 * dt
    state.x += state.speed_mps * math.cos(math.radians(state.heading_deg)) * dt
    state.y += state.speed_mps * math.sin(math.radians(state.heading_deg)) * dt
    state.seq += 1
    return state
