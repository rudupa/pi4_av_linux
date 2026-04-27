# Features Index

This folder contains feature-level design documents for major system capabilities.

## Available Feature Documents

1. [OTA_DESIGN.md](OTA_DESIGN.md)
- Design for cloud-driven OTA updates of Pi4 services and applications
- Covers bundle format, OTA agent, MQTT control/status, rollback, and security model

2. [PERCEPTION_DESIGN.md](PERCEPTION_DESIGN.md)
- Design for the perception subsystem running on the PC edge node
- Covers startup lifecycle, 33 FPS processing, frame dropping, profiling, parallel models, and radar integration

## Full AV Feature Roadmap

This section summarizes the major features of a full AV stack and classifies them by current project status.

### Implemented or Partially Implemented in This Repo

1. Pi4 runtime platform
- Buildroot-based Pi4 image
- systemd service management
- diagnostics, SSH, logging, watchdog-style service supervision

2. AV service packaging and supervision
- `av_services` packaged into the image
- systemd units for orchestrator, gateway, health, logger, and OTA service shell

3. Health monitoring and boot-time verification
- runtime health service integration
- boot-time feature report generation

4. Telemetry and messaging baseline
- MQTT packages available on Pi4 image
- ZeroMQ available on Pi4 image

5. Local dashboard platform support
- Pi4-side runtime support and architecture defined

### Designed in Docs, Pending Full Implementation

1. OTA updates
- See [OTA_DESIGN.md](OTA_DESIGN.md)

2. Perception subsystem
- See [PERCEPTION_DESIGN.md](PERCEPTION_DESIGN.md)

3. Static, dynamic, and functional system architecture
- See architecture docs under `docs/architecture/`

### Pending Major AV Features

1. Sensor ingestion
- camera, radar, LiDAR, GNSS, IMU, CAN data ingestion pipelines

2. Sensor fusion
- camera-radar or camera-radar-LiDAR fusion
- object association, fused tracks, confidence management

3. Localization
- GNSS/IMU fusion
- odometry and map-relative localization

4. Mapping
- map ingestion, map services, and route context support

5. Scene understanding
- drivable area, traffic sign/light handling, occupancy interpretation

6. Prediction
- future motion estimation for tracked objects

7. Planning
- route planning, behavior planning, motion planning, fallback maneuvers

8. Control
- closed-loop steering/throttle/brake control beyond current baseline service scaffolding

9. Vehicle interface
- robust CAN/Ethernet adapter logic, actuator abstraction, diagnostics feedback

10. Logging and replay
- raw data recording, event replay, scenario-based validation

11. Cloud observability and command stack
- telemetry ingestion service
- storage
- dashboards
- remote command UI/API

12. Security hardening extensions
- stronger credential management
- signed OTA artifacts
- optional SELinux or MAC policy hardening

13. Simulation and digital twin extensions
- scenario runner
- fault injection
- multi-vehicle simulation

14. Safety and degraded operation
- mode management
- stale-data handling
- minimum-risk behavior policies

## Suggested Priority Order

1. Perception
2. Telemetry and cloud stack
3. Dashboard/HMI completion
4. OTA implementation
5. Sensor fusion
6. Localization
7. Planning and control expansion
8. Logging/replay and safety behavior

## Intended Use

Use these documents to:

1. Define feature scope and implementation boundaries
2. Guide backlog creation and implementation planning
3. Align runtime behavior, interfaces, and operational expectations
