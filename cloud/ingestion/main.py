import json
import os
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from jsonschema import validate

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "dev-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "av")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "telemetry")

SCHEMAS = {
  "vehicle/telemetry/state": {"required": ["schema_version","timestamp_utc","sequence_id"]},
  "vehicle/telemetry/health": {"required": ["schema_version","timestamp_utc","sequence_id"]},
  "vehicle/perception/summary": {"required": ["schema_version","timestamp_utc","sequence_id"]},
}

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def on_connect(m, userdata, flags, rc, props=None):
    m.subscribe("vehicle/telemetry/#", qos=1)
    m.subscribe("vehicle/perception/summary", qos=1)


def on_message(m, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        if msg.topic in SCHEMAS:
            for k in SCHEMAS[msg.topic]["required"]:
                if k not in payload:
                    raise ValueError(f"missing {k}")
        p = Point(msg.topic.replace("/", "_")).field("payload", json.dumps(payload)).time(payload.get("timestamp_utc"), WritePrecision.S)
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)
    except Exception as e:
        dead = Point("dead_letter").field("topic", msg.topic).field("error", str(e)).field("raw", msg.payload.decode(errors="ignore"))
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=dead)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set("pi4", "pi4pass")
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(MQTT_HOST, MQTT_PORT)
mqttc.loop_forever()
