# OTA Design - Pi4 Services and Apps Update via Cloud

## 1. Scope

This design defines over-the-air (OTA) updates for Raspberry Pi 4 runtime services and application binaries managed in this project.

In scope:

- Cloud-orchestrated OTA for Pi4 service and app artifacts
- Download, verify, stage, apply, and report lifecycle
- systemd-managed restart/health-check behavior after update
- Rollback strategy for failed service/app update

Out of scope (V1):

- Full A/B rootfs image OTA
- Bootloader and kernel partition switching
- Firmware/DTB OTA

## 2. Goals and Non-Goals

### 2.1 Goals

1. Update Pi4 service/app artifacts remotely from cloud
2. Preserve service availability with controlled restart policy
3. Ensure cryptographic integrity and authenticity of update bundles
4. Provide deterministic state machine and audit trail
5. Support safe rollback for service/app-level failures

### 2.2 Non-Goals

1. Replace full OS image in V1
2. Guarantee zero downtime for every service
3. Multi-node orchestration semantics in V1

## 3. High-Level Architecture

Actors:

- Cloud OTA Orchestrator
- Artifact Storage (object store)
- MQTT Broker
- Pi4 OTA Agent (on device)
- systemd services/apps (`av-core-*` and related components)

Control plane:

- Cloud sends OTA command to Pi4 via MQTT (`vehicle/cmd/ota`)

Data plane:

- Pi4 OTA Agent downloads bundle from artifact storage over HTTPS

Status plane:

- Pi4 OTA Agent publishes status/events to MQTT (`vehicle/telemetry/ota`)

## 4. OTA Update Unit

Update unit in V1: **service/app bundle**.

Bundle contains:

1. `manifest.json` (metadata, version, target, hashes, pre/post actions)
2. `payload.tar.zst` (binaries/config/scripts)
3. `manifest.sig` (signature of manifest)

Target locations (example):

- `/opt/av/releases/<version>/...`
- `/opt/av/current -> /opt/av/releases/<version>` symlink
- systemd units continue to reference stable paths or launcher wrappers

## 5. Versioning and Identity

Per device metadata:

- `device_id`
- `current_version`
- `channel` (stable/canary/dev)
- `target_profile` (pi4-prod/pi4-lab)

Bundle metadata:

- `bundle_id`
- `bundle_version`
- `min_agent_version`
- `target_profile`
- `compatible_from_versions`
- `created_at`

## 6. MQTT Interface Contracts

### 6.1 Command Topic

- Topic: `vehicle/cmd/ota`

Command payload (example):

```json
{
  "cmd_id": "ota-2026-04-26-0001",
  "action": "start",
  "bundle_url": "https://artifacts.example.com/pi4/av-bundle-1.2.0.tar.zst",
  "manifest_url": "https://artifacts.example.com/pi4/av-bundle-1.2.0.manifest.json",
  "signature_url": "https://artifacts.example.com/pi4/av-bundle-1.2.0.manifest.sig",
  "sha256": "<payload_sha256>",
  "channel": "stable",
  "deadline_utc": "2026-04-27T03:00:00Z",
  "allow_rollback": true
}
```

### 6.2 Telemetry Topic

- Topic: `vehicle/telemetry/ota`

Status payload (example):

```json
{
  "cmd_id": "ota-2026-04-26-0001",
  "device_id": "pi4-001",
  "state": "DOWNLOADING",
  "progress": 42,
  "current_version": "1.1.4",
  "target_version": "1.2.0",
  "timestamp": "2026-04-26T23:18:00Z",
  "error_code": "",
  "error_message": ""
}
```

## 7. Device-Side OTA Agent Design

OTA agent service on Pi4:

- Name: `av-ota-agent.service`
- Optional timer: `av-ota-agent.timer` (poll/reconcile if command missed)

Directories:

- `/var/lib/av-ota/inbox` (downloaded artifacts)
- `/var/lib/av-ota/stage` (expanded/staged bundle)
- `/var/lib/av-ota/state.json` (agent state)
- `/var/log/av-ota.log` (update log)
- `/opt/av/releases/<version>` (installed release)
- `/opt/av/current` (active symlink)

Main responsibilities:

1. Receive OTA command
2. Validate device/channel/target profile
3. Download manifest/signature/payload
4. Verify signature and hash
5. Execute pre-checks
6. Stage release atomically
7. Switch active release reference
8. Restart/refresh impacted services
9. Run post-update health checks
10. Commit or rollback
11. Publish terminal status

## 8. OTA State Machine

States:

1. `IDLE`
2. `VALIDATING_COMMAND`
3. `DOWNLOADING`
4. `VERIFYING`
5. `PRECHECK`
6. `STAGING`
7. `APPLYING`
8. `RESTARTING_SERVICES`
9. `HEALTHCHECK`
10. `COMMITTED`
11. `ROLLBACK_IN_PROGRESS`
12. `ROLLED_BACK`
13. `FAILED`

Failure transitions:

- Download/verify failure -> `FAILED`
- Healthcheck failure with rollback enabled -> `ROLLBACK_IN_PROGRESS` -> `ROLLED_BACK`
- Healthcheck failure with rollback disabled -> `FAILED`

## 9. Apply and Restart Strategy

### 9.1 Atomic Deployment Pattern

1. Install payload to new versioned release dir
2. Validate file layout and permissions
3. Update symlink `/opt/av/current` atomically
4. Restart only impacted services

### 9.2 Service Restart Ordering

Suggested order:

1. `av-core-orchestrator`
2. `av-core-gateway`
3. `av-core-health`
4. `av-core-logger`
5. `av-core-ota` (if updated last)

Use systemd:

- `systemctl daemon-reload` when unit files changed
- `systemctl restart <service>` for affected services
- `systemctl is-active <service>` for readiness check

## 10. Health Check and Rollback

Post-update checks:

1. All targeted services are `active`
2. No crash-loop detected within stabilization window
3. Optional functional probe endpoint returns success
4. OTA telemetry heartbeat remains healthy

Rollback method (V1):

1. Restore previous symlink target
2. Restart affected services
3. Mark failed bundle in local denylist cache
4. Publish rollback result telemetry

## 11. Security Model

1. Manifest must be signed with trusted private key
2. Device verifies signature using pinned public key
3. Payload hash must match manifest hash
4. OTA artifact downloads must use HTTPS/TLS
5. MQTT command issuer must be authenticated and authorized
6. Command payload must include replay protection fields (`cmd_id`, optional nonce/timestamp)

Key storage:

- Public verification key in read-only config path on Pi4
- Device credentials for MQTT stored with restrictive permissions

## 12. Cloud Components for OTA

### 12.1 OTA Orchestrator

Responsibilities:

1. Select target devices by channel/profile
2. Publish OTA command
3. Track OTA state transitions
4. Surface progress/failure dashboard

### 12.2 Artifact Service

Responsibilities:

1. Store versioned bundles and manifests
2. Expose signed URL or authenticated download API
3. Retain provenance metadata (build id, commit, signer)

### 12.3 OTA Dashboard

Display:

- Fleet update progress
- Per-device state and errors
- Rollback events
- Version distribution

## 13. Packaging and Build Integration (Pi4 Repo)

Repository tasks:

1. Add OTA agent package in `br2_external/package/` (new package)
2. Install agent binary/script and systemd unit files
3. Add required dependencies (curl/wget, openssl/libsodium, jq if script-based)
4. Add config defaults under `/etc/av-ota/`
5. Add defconfig symbols to enable OTA agent package

Suggested package name:

- `pi4_ota_agent`

## 14. Observability and Audit

Emit structured events for each step:

- `ota.command.received`
- `ota.download.started`
- `ota.verify.ok`
- `ota.apply.started`
- `ota.healthcheck.failed`
- `ota.rollback.completed`
- `ota.commit.completed`

Persist locally and publish summary via MQTT.

## 15. Failure Scenarios

1. Invalid signature -> reject bundle, state `FAILED`
2. Partial download -> retry with backoff, then fail
3. Insufficient disk space -> fail precheck
4. Service fails to start -> rollback if enabled
5. Reboot during update -> resume from `state.json` and safe recovery step

## 16. Implementation Phases

### Phase 1 (MVP)

1. Script-based OTA agent
2. Signed manifest + hash verification
3. Versioned release directory + symlink switch
4. Restart impacted services
5. Basic rollback
6. MQTT status reporting

### Phase 2

1. Binary OTA agent with stricter transaction control
2. Delta bundle support
3. Staged rollout (canary -> stable)
4. Command RBAC and stronger anti-replay controls

### Phase 3

1. Extend to image-level A/B OTA strategy
2. Boot-partition and kernel-aware updates
3. Full fleet policy engine and progressive rollout controls

## 17. Acceptance Criteria (V1)

1. Cloud can trigger OTA command to a specific Pi4
2. Pi4 validates signature/hash before apply
3. Updated services/apps run from new version path
4. OTA status is visible end-to-end in telemetry
5. Failed update automatically rolls back when enabled
6. Device remains remotely reachable after update/rollback
