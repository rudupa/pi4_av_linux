# Telemetry and Cloud Stack Design (V1)

## 1. Scope

This document defines the telemetry and cloud stack design for the distributed AV simulation.

System context:

- Pi4 publishes runtime telemetry and receives remote commands
- Cloud ingests telemetry, stores history, exposes dashboards, and sends commands
- PC-side perception remains outside the cloud control plane and is represented through Pi4-published summaries where needed

In scope:

- Pi4 telemetry publication
- MQTT broker and topic design
- Cloud ingestion pipeline
- Time-series storage
- Dashboard and analytics layer
- Remote command API/UI
- Security and reliability considerations

Out of scope (V1):

- Fleet-scale multi-region deployment
- Complex stream processing pipelines
- ML model training infrastructure

## 2. Goals

1. Provide reliable telemetry uplink from Pi4 to cloud
2. Support low-complexity remote commands from cloud to Pi4
3. Persist state, health, and perception summary history
4. Expose actionable dashboards for runtime monitoring
5. Keep cloud interactions outside the hard real-time control loop

## 3. High-Level Architecture

Actors:

- Pi4 MQTT client
- MQTT broker
- Telemetry ingestion service
- Time-series database
- Dashboard/analytics service
- Remote command API/UI

Flow split:

1. Uplink:
- Pi4 -> MQTT -> ingestion -> storage -> dashboards

2. Downlink:
- Operator/UI -> command API -> MQTT -> Pi4

## 4. Data Classes

### 4.1 Vehicle State Telemetry

Examples:

- speed
- steering angle
- throttle and brake state
- vehicle mode
- simulated pose
- timestamp

Topic:

- `vehicle/telemetry/state`

### 4.2 Health Telemetry

Examples:

- CPU usage
- memory usage
- temperature
- disk usage
- service health
- link status
- watchdog/restart counters

Topic:

- `vehicle/telemetry/health`

### 4.3 Perception Summary Telemetry

Examples:

- object count
- lane confidence summary
- radar target count
- fused track count
- perception latency
- frame drop ratio

Topic:

- `vehicle/perception/summary`

### 4.4 OTA and Operations Telemetry

Examples:

- current software version
- build id
- OTA state
- command execution results
- reboot/update reason

Suggested topics:

- `vehicle/telemetry/version`
- `vehicle/telemetry/ota`
- `vehicle/telemetry/events`

## 5. MQTT Topic Design

### 5.1 Telemetry Topics (Pi4 -> Cloud)

- `vehicle/telemetry/state`
- `vehicle/telemetry/health`
- `vehicle/perception/summary`
- `vehicle/telemetry/version`
- `vehicle/telemetry/ota`
- `vehicle/telemetry/events`

### 5.2 Command Topics (Cloud -> Pi4)

- `vehicle/cmd/mode`
- `vehicle/cmd/reset`
- `vehicle/cmd/fault_inject`
- `vehicle/cmd/replay`
- `vehicle/cmd/ota`

### 5.3 Topic Design Rules

1. Keep telemetry and command topics separate
2. Use explicit nouns and stable naming
3. Include schema version in payload, not topic name, for V1
4. Use retained messages only where operationally justified

## 6. Payload Design

### 6.1 Common Required Fields

Every payload should include:

- `schema_version`
- `device_id`
- `timestamp_utc`
- `source`
- `sequence_id`

### 6.2 Example State Payload

```json
{
  "schema_version": 1,
  "device_id": "pi4-001",
  "timestamp_utc": "2026-04-26T20:15:30Z",
  "source": "vehicle-sim",
  "sequence_id": 10421,
  "mode": "auto",
  "speed_mps": 5.4,
  "steering_deg": -3.2,
  "throttle_pct": 21.0,
  "brake_pct": 0.0,
  "pose": {
    "x": 12.5,
    "y": 3.1,
    "heading_deg": 91.0
  }
}
```

### 6.3 Example Health Payload

```json
{
  "schema_version": 1,
  "device_id": "pi4-001",
  "timestamp_utc": "2026-04-26T20:15:30Z",
  "source": "health-monitor",
  "sequence_id": 7781,
  "cpu_pct": 42.0,
  "mem_pct": 37.0,
  "temp_c": 58.4,
  "disk_pct": 29.0,
  "network": {
    "link_up": true,
    "tx_kbps": 240.0,
    "rx_kbps": 680.0
  },
  "services": {
    "av-core-orchestrator": "active",
    "av-core-health": "active"
  }
}
```

## 7. Pi4 Telemetry Publisher Design

Responsibilities:

1. Collect local state, health, and feature summaries
2. Normalize into stable payload schemas
3. Publish at configured periodic rates
4. Handle MQTT reconnect and transient broker failures
5. Emit command result telemetry after remote actions

Suggested publication rates:

- state: 5-10 Hz
- health: 1 Hz
- perception summary: 2-5 Hz
- version/config: on boot and on change
- OTA/events: event-driven

Publisher constraints:

1. Must not block control loop on network delays
2. Should use non-blocking or decoupled queue-based publishing
3. Must bound queue growth under disconnect conditions

## 8. Cloud Ingestion Design

Responsibilities:

1. Subscribe to all Pi4 telemetry topics
2. Validate payload shape and schema version
3. Reject malformed payloads cleanly
4. Transform payloads into storage records
5. Forward to time-series database

Ingestion outputs:

- measurement records for time-series storage
- event/audit records for command and OTA history
- dead-letter records for malformed payloads

## 9. Storage Design

Recommended V1 options:

- InfluxDB
- TimescaleDB

Storage categories:

1. high-rate metrics
2. low-rate health signals
3. event logs
4. command history
5. OTA status history

Retention strategy:

1. High-rate state telemetry: shorter retention or downsampled retention
2. Health metrics: medium retention
3. Events and OTA history: longer retention
4. Version/config history: long retention

## 10. Dashboard and Analytics Design

### 10.1 Dashboard Pages

1. Live vehicle state
- speed
- steering
- mode
- pose

2. Health dashboard
- CPU, memory, temperature
- service status
- network quality

3. Perception summary dashboard
- object count
- radar target count
- perception fps/latency
- frame drop ratio

4. OTA and operations dashboard
- current version
- last update result
- command history

### 10.2 Alerts

Suggested initial alerts:

- Pi temperature too high
- repeated service restart
- broker disconnect duration exceeded
- telemetry silent for threshold duration
- OTA failure

## 11. Remote Command Stack

### 11.1 Command API/UI Responsibilities

1. Expose operator controls for mode/reset/replay/fault injection/OTA
2. Validate commands before publish
3. Require identity and authorization
4. Track command lifecycle and acknowledgments

### 11.2 Command Handling Requirements

1. Every command includes `cmd_id`
2. Every command is acknowledged in telemetry or event stream
3. Invalid commands are rejected and logged
4. Commands must not destabilize local control logic

## 12. Reliability and Failure Handling

### 12.1 Broker Disconnect

Behavior:

- Pi4 continues local runtime
- telemetry publish queue is bounded
- reconnect with backoff
- health event published when connection returns

### 12.2 Ingestion Failure

Behavior:

- broker still accepts messages
- ingestion retries or dead-letters malformed/failed records
- dashboard may show partial lag

### 12.3 Storage Failure

Behavior:

- ingestion should surface alarms
- command path can remain available if broker remains healthy

## 13. Security Design

1. Use MQTT over TLS
2. Require authenticated broker clients
3. Use broker ACLs to restrict publish/subscribe topics
4. Sign or strongly control OTA command issuance path
5. Protect stored credentials on Pi4 filesystem
6. Audit command and OTA actions

## 14. Observability of the Cloud Stack

Track:

1. broker connection counts
2. telemetry ingest rates by topic
3. malformed payload count
4. storage write latency
5. dashboard query latency
6. command success/failure rate
7. OTA trigger and outcome statistics

## 15. Deployment Model (V1)

Suggested deployment:

1. MQTT broker
2. ingestion service
3. time-series DB
4. dashboard service
5. command API/UI

Possible implementations:

- Mosquitto for broker
- lightweight Python or Node ingestion service
- InfluxDB or TimescaleDB for storage
- Grafana for dashboards
- simple operator UI/API for commands

## 16. Acceptance Criteria (V1)

1. Pi4 publishes state, health, and perception summary successfully
2. Cloud persists telemetry and shows live dashboard views
3. Command API can trigger at least mode/reset actions end-to-end
4. Broker disconnect does not break Pi4 local control runtime
5. Telemetry and command actions are auditable

## 17. Implementation Checklist

1. Define final payload schemas with version fields
2. Implement Pi4 publisher modules and bounded queues
3. Deploy MQTT broker with TLS and ACLs
4. Implement ingestion validation and storage writes
5. Build first Grafana dashboards
6. Implement command API/UI for mode/reset/replay/fault injection/OTA
7. Add alerts and audit events
