# BusyBox Init vs systemd

## Overview

| Aspect | BusyBox Init (SysV) | systemd |
|---|---|---|
| PID 1 binary | `/sbin/init` from BusyBox | `/lib/systemd/systemd` |
| Service definition | Shell scripts in `/etc/init.d/S??*` | Unit files in `/usr/lib/systemd/system/` |
| Boot style | Sequential (one at a time) | Parallel (dependency graph) |
| Service dependencies | By script naming order only | Declarative `After=`, `Requires=`, `Wants=` |
| Crash recovery | Manual or custom in script | `Restart=on-failure` built in |
| Hung process detection | None built in | `WatchdogSec=` kills and restarts |
| Logging | syslogd → `/var/log/messages` | `journald` → `journalctl` |
| Log filtering | grep on text files | `journalctl -u <service> --since` |
| Structured logs | No | Yes (key=value fields, log levels) |
| Network management | ifupdown or custom scripts | `systemd-networkd` |
| DNS resolution | resolv.conf, custom | `systemd-resolved` |
| Service control CLI | `start-stop-daemon`, manual | `systemctl start/stop/restart/status` |
| Socket activation | No | Yes |
| cgroup isolation | No | Yes (CPU/memory limits per service) |
| Image size overhead | ~1 MB (BusyBox itself) | ~30–50 MB |

---

## Service lifecycle: BusyBox vs systemd

### BusyBox SysV style (former approach in this repo)

`/etc/init.d/S99avcore`:
```sh
start-stop-daemon -S -x /usr/local/bin/av-core-orchestrator -b
```

Limitations:
- No automatic restart on crash.
- No watchdog.
- No dependency on network or other services being ready.
- Logs go to stdout only if you redirect manually.

### systemd style (current approach in this repo)

`/usr/lib/systemd/system/av-core-orchestrator.service`:
```ini
[Unit]
After=network.target av-core-gateway.service

[Service]
ExecStart=/usr/local/bin/av-core-orchestrator
Restart=on-failure
WatchdogSec=30s
StandardOutput=journal
```

Gains:
- Restarts automatically after crash.
- Killed and restarted if hung for 30s.
- Does not start until network and gateway are ready.
- Logs are structured and queryable via `journalctl`.

---

## Defconfig change

Before:
```
# (no init system line — BusyBox init was implicit default)
```

After:
```
BR2_INIT_SYSTEMD=y
```

---

## On-target commands compared

| Task | BusyBox | systemd |
|---|---|---|
| Start a service | `/etc/init.d/S99avcore start` | `systemctl start av-core-orchestrator` |
| Stop a service | `/etc/init.d/S99avcore stop` | `systemctl stop av-core-orchestrator` |
| Check status | `/etc/init.d/S99avcore status` | `systemctl status av-core-orchestrator` |
| View logs | `cat /var/log/messages` | `journalctl -u av-core-orchestrator` |
| Follow live logs | `tail -f /var/log/messages` | `journalctl -u av-core-orchestrator -f` |
| List all services | `ls /etc/init.d/` | `systemctl list-units` |
| Enable at boot | File naming convention | `systemctl enable av-core-orchestrator` |

---

## Why this repo moved to systemd

This repo targets AV development workloads where:
- Services must have explicit startup dependencies (network before gateway, gateway before orchestrator).
- Crashed or hung services must recover automatically without operator intervention.
- Structured, timestamped logs are required for post-incident analysis.
- Industry AV stacks (Autoware, ROS 2 production deployments, NVIDIA DRIVE OS) all assume systemd.
