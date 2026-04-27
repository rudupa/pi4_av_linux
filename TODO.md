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

- [ ] Implement camera playback service for recorded streams (single and multi-camera)
- [ ] Define camera calibration loading flow (intrinsics and extrinsics)
- [ ] Implement timestamp-normalized sensor playback scheduler
- [ ] Implement radar playback service (range, doppler, angle data)
- [ ] Support synchronized camera + radar playback profiles
- [ ] Add playback controls (start, pause, seek, rate control, loop)
- [ ] Add dropped-frame and lag detection metrics

### 1.2 Perception Processing

- [ ] Implement camera object detection pipeline (baseline model)
- [ ] Implement lane detection pipeline for forward camera
- [ ] Implement radar target clustering and tracking baseline
- [ ] Implement camera-radar association/fusion module (late fusion baseline)
- [ ] Add occupancy/grid or free-space estimation output
- [ ] Define perception output schema versioning (V1)
- [ ] Add confidence threshold and class filtering policy

### 1.3 Edge Messaging and Interfaces

- [ ] Implement Zenoh publishers for `/sensor/*`
- [ ] Implement Zenoh publishers for `/perception/*`
- [ ] Add message serialization contracts and backward compatibility checks
- [ ] Add interface contract tests against Pi-side consumers
- [ ] Add edge-side QoS and rate governance per topic

### 1.4 Edge Runtime and Ops

- [ ] Add PC-side service supervisor scripts (dev and production modes)
- [ ] Add structured logging with correlation IDs per frame/tick
- [ ] Add GPU utilization and inference latency telemetry export
- [ ] Add benchmark suite for camera and radar throughput

---

## 2. Pi4 Side (Vehicle Node) - Pending Tasks

### 2.1 Control and Simulation Core

- [ ] Implement production control loop module boundary (planner vs controller)
- [ ] Add deterministic fixed-step simulation tick manager
- [ ] Implement configurable vehicle dynamics parameter profiles
- [ ] Add fault injection hooks in simulator (sensor dropout, delayed perception)
- [ ] Add mode manager (`manual`, `auto`, `safe`, `degraded`)

### 2.2 Perception Consumption and Fusion Inputs

- [ ] Implement robust subscription handlers for `/perception/objects`
- [ ] Implement robust subscription handlers for `/perception/lane`
- [ ] Add radar perception input contract on Pi side
- [ ] Add perception freshness/timeout handling (stale data guards)
- [ ] Add fallback behavior when camera or radar stream is missing

### 2.3 Local Dashboard and UX

- [ ] Add dashboard panels for camera detections summary
- [ ] Add dashboard panels for radar targets summary
- [ ] Add control-mode and fault-state indicators
- [ ] Add chart history window for speed/steering/health
- [ ] Add simple run controls (replay mode, reset simulation)

### 2.4 Telemetry and Commands (Pi MQTT Client)

- [ ] Finalize telemetry payload schema versions for state/health/perception summary
- [ ] Add command validation and rejection reporting
- [ ] Add MQTT reconnect and offline queue strategy
- [ ] Add command execution audit events to telemetry stream

### 2.5 Platform, Security, and Operability

- [ ] Add default SSH hardening profile for release images
- [ ] Add runtime config file for static/DHCP network policy selection
- [ ] Add persistent service health heartbeat endpoint
- [ ] Add packaging hooks for version/build metadata in image
- [ ] Add on-target smoke-test script for post-flash verification

---

## 3. Cloud Side - Pending Tasks

### 3.1 MQTT and Ingestion

- [ ] Deploy MQTT broker with TLS and topic ACLs
- [ ] Implement telemetry ingestion service for `vehicle/telemetry/*`
- [ ] Implement ingestion for `vehicle/perception/summary`
- [ ] Add schema validation and dead-letter handling
- [ ] Add device identity and auth token management

### 3.2 Storage and Analytics

- [ ] Provision time-series database (InfluxDB or TimescaleDB)
- [ ] Define retention policies by signal class
- [ ] Add downsampling pipelines for long-range analytics
- [ ] Implement data quality checks (missing intervals, outliers)

### 3.3 Dashboards and Monitoring

- [ ] Build live telemetry dashboard (state, health, perception summary)
- [ ] Build historical trend dashboards (run-level comparisons)
- [ ] Build alerting rules (temperature, watchdog resets, link drops)
- [ ] Add command history and acknowledgment panels

### 3.4 Remote Commands and Control API

- [ ] Implement command API for `mode`, `reset`, `fault_inject`, `replay`
- [ ] Add RBAC policy for command issuance
- [ ] Add idempotency and replay protection for command requests
- [ ] Add command ack timeout and retry policy

---

## 4. Cross-System Interface and Data Contracts - Pending Tasks

### 4.1 Topic and Schema Governance

- [ ] Publish authoritative topic catalog (Zenoh + MQTT)
- [ ] Define JSON or binary schema contracts with version fields
- [ ] Add compatibility matrix for producer/consumer versions
- [ ] Add schema linting checks in CI

### 4.2 Time and Sync

- [ ] Define canonical timestamp format and clock source policy
- [ ] Add end-to-end latency budget per pipeline segment
- [ ] Add clock skew detection between PC and Pi4

### 4.3 Camera and Radar Data Model

- [ ] Define unified object model for camera and radar outputs
- [ ] Define radar target uncertainty fields (range/velocity/angle covariance)
- [ ] Define fused track lifecycle states (new, tracked, lost)
- [ ] Define confidence and conflict resolution policy in fusion stage

---

## 5. Testing and Validation - Pending Tasks

### 5.1 Unit and Integration Tests

- [ ] Add unit tests for control, simulation, and health components
- [ ] Add interface tests for Zenoh topic contracts
- [ ] Add interface tests for MQTT telemetry and commands
- [ ] Add camera-radar fusion module tests with canned datasets

### 5.2 Scenario and System Tests

- [ ] Add end-to-end smoke test: playback -> perception -> control -> telemetry
- [ ] Add degraded network scenario tests (edge-cloud disconnect)
- [ ] Add stale perception scenario tests and expected fail-safe behavior
- [ ] Add high-load scenario tests for PC inference and Pi control stability

### 5.3 Acceptance Criteria and Quality Gates

- [ ] Define pass/fail thresholds for control latency and telemetry lag
- [ ] Define perception minimum quality metrics for camera and radar pipelines
- [ ] Add release checklist for image, services, and cloud readiness

---

## 6. Release and DevOps - Pending Tasks

- [ ] Add CI pipeline for build + static checks + schema checks
- [ ] Add artifact version tagging for image and service binaries
- [ ] Add deployment manifests for cloud stack (broker, DB, dashboards)
- [ ] Add reproducible experiment profile files (dataset + config + expected outputs)
- [ ] Add changelog automation for architecture and interface changes

---

## 7. Suggested Execution Order

1. PC playback + camera/radar baseline perception outputs
2. Pi robust control/simulation with perception freshness guards
3. Pi dashboard enhancements and stable telemetry publishing
4. Cloud broker + storage + baseline dashboards
5. Remote command API with audit and ack
6. Cross-system schema governance and CI gates
7. Reliability testing, degraded-mode validation, and release hardening
