# TODO - Distributed AV Simulation Backlog

## Purpose

This backlog tracks pending implementation work across the full distributed system:

- PC side (edge perception and playback)
- Pi4 side (control, simulation, local runtime)
- Cloud side (telemetry, storage, remote operations)

Note:
- This repository primarily implements the Pi4 image/runtime.
- PC and cloud tasks are included here as system-level pending work to complete the end-to-end architecture.

## Milestone Targets

- M1: Edge loop functional (sensor playback -> perception -> Pi control -> state)
- M2: Local observability functional (Pi dashboard + health + logs)
- M3: Cloud telemetry and command loop functional
- M4: Reliability and replay tooling for experiments

---

## 1. PC Side (Edge Compute) - Pending Tasks

### 1.1 Sensor Ingestion and Playback

- [x] Implement camera playback service for recorded streams (single and multi-camera)
- [x] Define camera calibration loading flow (intrinsics and extrinsics)
- [x] Implement timestamp-normalized sensor playback scheduler
- [x] Implement radar playback service (range, doppler, angle data)
- [x] Support synchronized camera + radar playback profiles
- [x] Add playback controls (start, pause, seek, rate control, loop)
- [x] Add dropped-frame and lag detection metrics

### 1.2 Perception Processing

- [x] Implement camera object detection pipeline (baseline model)
- [x] Implement lane detection pipeline for forward camera
- [x] Implement radar target clustering and tracking baseline
- [x] Implement camera-radar association/fusion module (late fusion baseline)
- [x] Add occupancy/grid or free-space estimation output
- [x] Define perception output schema versioning (V1)
- [x] Add confidence threshold and class filtering policy

### 1.3 Edge Messaging and Interfaces

- [x] Implement Zenoh publishers for `/sensor/*`
- [x] Implement Zenoh publishers for `/perception/*`
- [x] Add message serialization contracts and backward compatibility checks
- [x] Add interface contract tests against Pi-side consumers
- [x] Add edge-side QoS and rate governance per topic

### 1.4 Edge Runtime and Ops

- [x] Add PC-side service supervisor scripts (dev and production modes)
- [x] Add structured logging with correlation IDs per frame/tick
- [x] Add GPU utilization and inference latency telemetry export
- [x] Add benchmark suite for camera and radar throughput

---

## 2. Pi4 Side (Vehicle Node) - Pending Tasks

### 2.1 Control and Simulation Core

- [x] Implement production control loop module boundary (planner vs controller)
- [x] Add deterministic fixed-step simulation tick manager
- [x] Implement configurable vehicle dynamics parameter profiles
- [x] Add fault injection hooks in simulator (sensor dropout, delayed perception)
- [x] Add mode manager (`manual`, `auto`, `safe`, `degraded`)

### 2.2 Perception Consumption and Fusion Inputs

- [x] Implement robust subscription handlers for `/perception/objects`
- [x] Implement robust subscription handlers for `/perception/lane`
- [x] Add radar perception input contract on Pi side
- [x] Add perception freshness/timeout handling (stale data guards)
- [x] Add fallback behavior when camera or radar stream is missing

### 2.3 Local Dashboard and UX

- [x] Add dashboard panels for camera detections summary
- [x] Add dashboard panels for radar targets summary
- [x] Add control-mode and fault-state indicators
- [x] Add chart history window for speed/steering/health
- [x] Add simple run controls (replay mode, reset simulation)

### 2.4 Telemetry and Commands (Pi MQTT Client)

- [x] Finalize telemetry payload schema versions for state/health/perception summary
- [x] Add command validation and rejection reporting
- [x] Add MQTT reconnect and offline queue strategy
- [x] Add command execution audit events to telemetry stream

### 2.5 Platform, Security, and Operability

- [x] Add default SSH hardening profile for release images
- [x] Add runtime config file for static/DHCP network policy selection
- [x] Add persistent service health heartbeat endpoint
- [x] Add packaging hooks for version/build metadata in image
- [x] Add on-target smoke-test script for post-flash verification

---

## 3. Cloud Side - Pending Tasks

### 3.1 MQTT and Ingestion

- [x] Deploy MQTT broker with TLS and topic ACLs
- [x] Implement telemetry ingestion service for `vehicle/telemetry/*`
- [x] Implement ingestion for `vehicle/perception/summary`
- [x] Add schema validation and dead-letter handling
- [x] Add device identity and auth token management

### 3.2 Storage and Analytics

- [x] Provision time-series database (InfluxDB or TimescaleDB)
- [x] Define retention policies by signal class
- [x] Add downsampling pipelines for long-range analytics
- [x] Implement data quality checks (missing intervals, outliers)

### 3.3 Dashboards and Monitoring

- [x] Build live telemetry dashboard (state, health, perception summary)
- [x] Build historical trend dashboards (run-level comparisons)
- [x] Build alerting rules (temperature, watchdog resets, link drops)
- [x] Add command history and acknowledgment panels

### 3.4 Remote Commands and Control API

- [x] Implement command API for `mode`, `reset`, `fault_inject`, `replay`
- [x] Add RBAC policy for command issuance
- [x] Add idempotency and replay protection for command requests
- [x] Add command ack timeout and retry policy

---

## 4. Cross-System Interface and Data Contracts - Pending Tasks

### 4.1 Topic and Schema Governance

- [x] Publish authoritative topic catalog (Zenoh + MQTT)
- [x] Define JSON or binary schema contracts with version fields
- [x] Add compatibility matrix for producer/consumer versions
- [x] Add schema linting checks in CI

### 4.2 Time and Sync

- [x] Define canonical timestamp format and clock source policy
- [x] Add end-to-end latency budget per pipeline segment
- [x] Add clock skew detection between PC and Pi4

### 4.3 Camera and Radar Data Model

- [x] Define unified object model for camera and radar outputs
- [x] Define radar target uncertainty fields (range/velocity/angle covariance)
- [x] Define fused track lifecycle states (new, tracked, lost)
- [x] Define confidence and conflict resolution policy in fusion stage

---

## 5. Testing and Validation - Pending Tasks

### 5.1 Unit and Integration Tests

- [x] Add unit tests for control, simulation, and health components
- [x] Add interface tests for Zenoh topic contracts
- [x] Add interface tests for MQTT telemetry and commands
- [x] Add camera-radar fusion module tests with canned datasets

### 5.2 Scenario and System Tests

- [x] Add end-to-end smoke test: playback -> perception -> control -> telemetry
- [x] Add degraded network scenario tests (edge-cloud disconnect)
- [x] Add stale perception scenario tests and expected fail-safe behavior
- [x] Add high-load scenario tests for PC inference and Pi control stability

### 5.3 Acceptance Criteria and Quality Gates

- [x] Define pass/fail thresholds for control latency and telemetry lag
- [x] Define perception minimum quality metrics for camera and radar pipelines
- [x] Add release checklist for image, services, and cloud readiness

---

## 6. Release and DevOps - Pending Tasks

- [x] Add CI pipeline for build + static checks + schema checks
- [x] Add artifact version tagging for image and service binaries
- [x] Add deployment manifests for cloud stack (broker, DB, dashboards)
- [x] Add reproducible experiment profile files (dataset + config + expected outputs)
- [x] Add changelog automation for architecture and interface changes

---

## 7. Suggested Execution Order

1. PC playback + camera/radar baseline perception outputs
2. Pi robust control/simulation with perception freshness guards
3. Pi dashboard enhancements and stable telemetry publishing
4. Cloud broker + storage + baseline dashboards
5. Remote command API with audit and ack
6. Cross-system schema governance and CI gates
7. Reliability testing, degraded-mode validation, and release hardening
