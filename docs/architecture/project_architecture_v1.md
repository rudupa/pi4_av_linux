# Distributed Autonomous Vehicle Simulation - Project Architecture V1

## 1. Overview

This project implements a distributed autonomous vehicle simulation using three tiers:

- Edge Compute Node (Asus Strix G16, RTX 5070 Ti)
- Vehicle Node (Raspberry Pi 4B)
- Cloud Backend

The architecture models a practical AV pipeline:

Perception -> Planning and Control -> Vehicle State -> Telemetry -> Cloud Commands

Core communication technologies:

- Zenoh for low-latency edge communication between laptop and Pi
- MQTT for cloud telemetry and remote command exchange between Pi and cloud
- Local Pi-hosted web dashboard for runtime visualization

## 2. System Scope and Objectives

V1 objectives:

1. Real-time edge perception and control loop simulation
2. Deterministic state simulation and health monitoring on Pi
3. Reliable cloud telemetry ingestion and remote command path
4. Clear separation of edge and cloud communication concerns
5. Operable developer workflow for build, boot, validate, and iterate

Out of scope for V1:

1. Production safety certification
2. Real actuator hardware-in-the-loop control
3. Multi-vehicle orchestration at scale

## 3. High-Level Architecture

### 3.1 Logical Components

1. Edge Compute Node (Laptop)
- Sensor playback
- GPU perception inference
- Zenoh publication of perception outputs
- Optional heavy visualization

2. Vehicle Node (Raspberry Pi)
- Planning and control loop
- Vehicle state simulation
- Health monitoring
- Zenoh and MQTT bridge responsibilities
- Local dashboard and WebSocket stream

3. Cloud Backend
- MQTT broker and ingestion
- Time-series storage
- Dashboards and analytics
- Remote command API and UI

### 3.2 Deployment Topology

- Laptop <-> Pi via Ethernet (preferred) or Wi-Fi using Zenoh
- Pi <-> Cloud via Internet using MQTT over TLS
- Dashboard is served from Pi and accessed over browser

## 4. Communication Architecture

### 4.1 Edge Layer (Zenoh: Laptop <-> Pi)

Purpose:
- High-throughput, low-latency transport for sensor and perception data

Representative topics:

Sensor streams:
- /sensor/camera
- /sensor/lidar
- /sensor/imu

Perception outputs:
- /perception/objects
- /perception/lane
- /perception/occupancy_grid

Control and state:
- /vehicle/steering_cmd
- /vehicle/throttle_cmd
- /vehicle/brake_cmd
- /vehicle/state

Roles:
- Laptop publishes sensor and perception
- Pi subscribes to perception and publishes control and state

### 4.2 Cloud Layer (MQTT: Pi <-> Cloud)

Purpose:
- Reliable telemetry uplink and remote command downlink

Telemetry topics (Pi -> Cloud):
- vehicle/telemetry/state
- vehicle/telemetry/health
- vehicle/perception/summary

Command topics (Cloud -> Pi):
- vehicle/cmd/mode
- vehicle/cmd/reset
- vehicle/cmd/fault_inject
- vehicle/cmd/replay

Roles:
- Pi periodically publishes telemetry
- Cloud persists and visualizes telemetry
- Cloud publishes commands, Pi applies control-mode changes

## 5. Node Responsibilities

### 5.1 Edge Compute Node (Laptop)

Responsibilities:

1. Replay recorded camera, LiDAR, and log streams
2. Run GPU perception models (object, lane, point cloud)
3. Publish perception artifacts to Zenoh
4. Provide optional high-fidelity visualization

Primary services:

- Sensor Playback Service
- Perception Service
- Optional Visualization Service

### 5.2 Vehicle Node (Raspberry Pi)

Responsibilities:

1. Subscribe to edge perception topics
2. Run planning and control (rule-based, PID, or pure pursuit)
3. Simulate vehicle dynamics and state
4. Publish simulated state to edge consumers
5. Monitor health (CPU, memory, temp, network)
6. Publish telemetry to cloud via MQTT
7. Consume remote commands via MQTT
8. Serve local real-time dashboard via WebSocket bridge

Primary services:

- Zenoh Edge Client
- Control and Vehicle Simulation Service
- Health Monitor
- Zenoh to WebSocket Bridge
- Web Dashboard Service
- MQTT Telemetry Publisher
- MQTT Command Listener

### 5.3 Cloud Backend

Responsibilities:

1. Broker MQTT traffic
2. Persist telemetry into time-series storage
3. Expose observability dashboards
4. Expose remote command API and control UI

Primary services:

- MQTT Broker
- Telemetry Ingestion and Storage
- Dashboard and Analytics
- Command API and UI

## 6. End-to-End Data Flows

### 6.1 Edge Runtime Loop

1. Laptop playback publishes /sensor/*
2. Laptop perception consumes /sensor/* and publishes /perception/*
3. Pi control consumes /perception/* and computes control commands
4. Pi simulator updates vehicle dynamics and publishes /vehicle/state
5. Pi dashboard stack streams state and perception summaries to browser

### 6.2 Cloud Telemetry and Remote Control Loop

1. Pi publishes telemetry to vehicle/telemetry/* and vehicle/perception/summary
2. Cloud broker receives and forwards to ingestion
3. Storage persists signals for historical analysis
4. Dashboards render current and historical metrics
5. Cloud command UI publishes vehicle/cmd/*
6. Pi command listener applies mode and behavior updates

## 7. Technology Rationale

### 7.1 Zenoh for Edge IPC

- Very low latency and strong throughput for robotics payloads
- Peer-oriented design suitable for constrained edge networks
- Good fit for continuous sensor and perception streams

### 7.2 MQTT for Cloud Integration

- Mature, lightweight pub/sub for telemetry and control events
- Easy TLS hardening and cloud compatibility
- Strong ecosystem for broker, storage, and dashboard integration

### 7.3 Pi-Hosted Web Dashboard

- Lightweight operational visibility close to control node
- Real-time updates over WebSocket without heavy client runtime
- Useful for field debugging even without cloud dependency

## 8. Reliability and Observability Strategy

1. Separate edge and cloud channels to isolate failure domains
2. Local control loop on Pi can continue if cloud link is degraded
3. Health telemetry provides actionable runtime diagnostics
4. Dashboard enables immediate local triage during bring-up
5. MQTT command path supports remote recovery operations

## 9. Security and Networking Baseline

1. Use MQTT over TLS for cloud communications
2. Restrict broker ACLs by topic and client identity
3. Keep edge Zenoh segment on trusted local network
4. Rotate credentials and avoid plaintext secrets in images
5. Prefer static IP on Pi for lab reproducibility when needed

## 10. V1 Deployment Profile

Laptop:
- Zenoh client and optional router
- Sensor playback
- GPU perception

Pi:
- Zenoh router/client
- Control and simulation
- Health monitor
- Dashboard and WebSocket bridge
- MQTT telemetry and command client

Cloud:
- MQTT broker
- Time-series database (InfluxDB or TimescaleDB)
- Dashboard stack (Grafana or Plotly)
- Command API/UI

## 11. Versioned Interface Contracts (V1)

Recommended initial schema contracts:

1. Perception object list
- Timestamp
- Track ID
- Class
- Confidence
- Position and velocity estimates

2. Vehicle state
- Timestamp
- Speed
- Steering angle
- Position and heading
- Simulated IMU fields

3. Health status
- CPU and memory utilization
- Temperature
- Network link and packet metrics
- Service heartbeat

4. Command payloads
- Mode change
- Reset trigger
- Fault injection type and intensity
- Replay control fields

## 12. Future Extension Path

1. Multi-Pi fleet simulation with per-vehicle namespaces
2. Map-based cloud visualization and route context
3. ROS2 interoperability via Zenoh bridge patterns
4. OTA-style update workflows for edge services
5. Full traffic recording and replay across edge-cloud boundary

## 13. Acceptance Criteria for V1

V1 is complete when:

1. Edge perception publishes and Pi control loop runs continuously
2. Pi publishes stable telemetry to cloud topics
3. Cloud dashboards show live and historical data
4. Cloud command path can change Pi simulation mode remotely
5. Local dashboard shows state, perception summary, and health in real time
6. Reboot and reconnect behaviors are repeatable in lab setup
