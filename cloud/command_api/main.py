from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
import time
import paho.mqtt.client as mqtt

app = FastAPI(title="AV Command API")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set("operator", "operatorpass")
client.connect_async(MQTT_HOST, MQTT_PORT)
client.loop_start()

seen_cmd = {}

ROLE_KEYS = {"operator-token": "operator", "viewer-token": "viewer"}

class Command(BaseModel):
    cmd_id: str
    payload: dict


def require_role(token: str | None, needed="operator"):
    role = ROLE_KEYS.get(token or "")
    if role != needed:
        raise HTTPException(403, "forbidden")


def publish(topic: str, cmd: Command):
    now = time.time()
    if cmd.cmd_id in seen_cmd and now - seen_cmd[cmd.cmd_id] < 600:
        return {"status": "duplicate_ignored"}
    seen_cmd[cmd.cmd_id] = now
    out = dict(cmd.payload)
    out["schema_version"] = 1
    out["cmd_id"] = cmd.cmd_id
    client.publish(topic, __import__("json").dumps(out), qos=2)
    return {"status": "published"}

@app.post("/cmd/mode")
def cmd_mode(cmd: Command, x_api_token: str | None = Header(default=None)):
    require_role(x_api_token)
    return publish("vehicle/cmd/mode", cmd)

@app.post("/cmd/reset")
def cmd_reset(cmd: Command, x_api_token: str | None = Header(default=None)):
    require_role(x_api_token)
    return publish("vehicle/cmd/reset", cmd)

@app.post("/cmd/fault_inject")
def cmd_fault(cmd: Command, x_api_token: str | None = Header(default=None)):
    require_role(x_api_token)
    return publish("vehicle/cmd/fault_inject", cmd)

@app.post("/cmd/replay")
def cmd_replay(cmd: Command, x_api_token: str | None = Header(default=None)):
    require_role(x_api_token)
    return publish("vehicle/cmd/replay", cmd)
