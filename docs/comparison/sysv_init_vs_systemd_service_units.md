# SysV Init Script vs systemd Service Unit

## The change in this repo

The av_services package previously started only via a single SysV init script.
It now uses five individual systemd unit files — one per service — with explicit dependencies, watchdog, and restart policies.

---

## Side-by-side: S99avcore vs av-core-orchestrator.service

### Before: `/etc/init.d/S99avcore` (SysV)

```sh
#!/bin/sh
DAEMON=/usr/local/bin/av-core-orchestrator
PIDFILE=/var/run/av-core-orchestrator.pid

case "$1" in
  start)
    start-stop-daemon -S -x $DAEMON -b -m -p $PIDFILE
    ;;
  stop)
    start-stop-daemon -K -p $PIDFILE
    ;;
  restart)
    $0 stop; $0 start
    ;;
  status)
    start-stop-daemon -T -p $PIDFILE && echo "running" || echo "stopped"
    ;;
esac
```

Limitations:
- No knowledge of what else must be running first.
- No restart on crash.
- No watchdog for hung process.
- Logs go nowhere unless the process itself opens a log file.

### After: `/usr/lib/systemd/system/av-core-orchestrator.service`

```ini
[Unit]
Description=AV Core Orchestrator
After=network.target av-core-gateway.service av-core-logger.service
Wants=av-core-gateway.service av-core-logger.service av-core-health.service

[Service]
Type=simple
ExecStart=/usr/local/bin/av-core-orchestrator
EnvironmentFile=-/etc/av-core/orchestrator.conf
Restart=on-failure
RestartSec=5s
WatchdogSec=30s
StandardOutput=journal
StandardError=journal
StartLimitIntervalSec=60s
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
```

Gains over SysV:
- Starts only after network, gateway, and logger are ready.
- Restarts automatically within 5s on crash.
- Killed and restarted if it stops responding for 30s.
- Logs directly to journald — queryable by timestamp, log level, and field.
- Prevents crash loops: stops trying after 5 failures in 60s.

---

## Full service unit inventory

| Unit file | Depends on | Type | Watchdog |
|---|---|---|---|
| `av-core-orchestrator.service` | network, gateway, logger | simple | 30s |
| `av-core-gateway.service` | network | simple | 30s |
| `av-core-health.service` | network, orchestrator | simple | 60s |
| `av-core-logger.service` | systemd-journald | simple | 30s |
| `av-core-ota.service` | network, orchestrator | oneshot | none |

---

## Install hook comparison in av_services.mk

### Before (SysV hook)
```make
define AV_SERVICES_INSTALL_INIT_SYSV
    $(INSTALL) -D -m 0755 $(AV_SERVICES_PKGDIR)/S99avcore \
        $(TARGET_DIR)/etc/init.d/S99avcore
endef
```

### After (systemd hook added)
```make
define AV_SERVICES_INSTALL_INIT_SYSTEMD
    $(INSTALL) -D -m 0644 ... av-core-orchestrator.service \
        $(TARGET_DIR)/usr/lib/systemd/system/
    ...
    ln -sf .../av-core-orchestrator.service \
        $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/
endef
```

Both hooks remain in the file. Buildroot activates the correct one based on the selected init system (`BR2_INIT_SYSTEMD=y` or default BusyBox).
