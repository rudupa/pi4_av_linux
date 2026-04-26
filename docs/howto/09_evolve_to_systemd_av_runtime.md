# Task 09: Evolve to Full AV Runtime Stack with systemd

## Goal
Migrate from BusyBox SysV init to systemd for production-grade AV service management, and add AV runtime tooling packages.

## What was performed

### 1. Switched init system
Changed `configs/pi4_64_defconfig`:
- Added `BR2_INIT_SYSTEMD=y` to replace BusyBox init.
- Added `BR2_PACKAGE_SYSTEMD=y`, `BR2_PACKAGE_SYSTEMD_JOURNALD=y`, `BR2_PACKAGE_SYSTEMD_NETWORKD=y`, `BR2_PACKAGE_SYSTEMD_RESOLVED=y`.

### 2. Added AV runtime packages
Added to defconfig:
- `BR2_PACKAGE_OPENSSH=y` — remote SSH access
- `BR2_PACKAGE_SCREEN=y` — persistent terminal sessions
- `BR2_PACKAGE_SYSTEMD_NETWORKD=y` — systemd network management
- `BR2_PACKAGE_SYSTEMD_RESOLVED=y` — systemd DNS resolution

### 3. Created systemd service unit files
Five `.service` files under `br2_external/package/av_services/`:

| File | Type | Key features |
|---|---|---|
| `av-core-orchestrator.service` | simple | Wants gateway/logger, WatchdogSec=30s, StartLimitBurst=5 |
| `av-core-gateway.service` | simple | After=network.target, WatchdogSec=30s |
| `av-core-health.service` | simple | After=orchestrator, WatchdogSec=60s |
| `av-core-logger.service` | simple | After=systemd-journald |
| `av-core-ota.service` | oneshot | ConditionPathExists=/var/lib/av-core/ota |

All long-running services use:
- `Restart=on-failure` with `RestartSec=5s`
- `WatchdogSec=` to kill hung processes
- `StartLimitIntervalSec=60s`, `StartLimitBurst=5` to prevent crash loops
- `StandardOutput=journal`, `StandardError=journal` for structured logging

### 4. Updated av_services.mk
Added `AV_SERVICES_INSTALL_INIT_SYSTEMD` hook:
- Installs `.service` files to `/usr/lib/systemd/system/`
- Creates `multi-user.target.wants/` symlinks to enable services at boot

Both `AV_SERVICES_INSTALL_INIT_SYSV` and `AV_SERVICES_INSTALL_INIT_SYSTEMD` are present:
Buildroot uses the appropriate one based on the selected init system.

## On-target verification

After flashing and booting:
```bash
# Check all AV services
systemctl status av-core-orchestrator av-core-gateway av-core-health av-core-logger

# View structured logs for a service
journalctl -u av-core-orchestrator -f

# View logs since last boot
journalctl -u av-core-orchestrator --boot

# Restart a service
systemctl restart av-core-orchestrator
```

## Outcome
- Image uses systemd as PID 1.
- All AV services start on boot via `multi-user.target`.
- Crashed services restart automatically.
- Hung services are killed and restarted via watchdog.
- Logs are available via `journalctl`.
