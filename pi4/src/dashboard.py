from __future__ import annotations
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI(title="Pi4 Dashboard API")
_state = {"speed_mps": 0.0, "steering_deg": 0.0, "mode": "auto", "health": {}, "camera_detections": 0, "radar_targets": 0}

@app.get("/state")
def state():
    return _state

@app.post("/state")
def update(payload: dict):
    _state.update(payload)
    return {"ok": True}

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    while True:
      await ws.send_json(_state)
      await asyncio.sleep(0.2)
