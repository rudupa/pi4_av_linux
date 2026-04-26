# Pi4 Feature Verification Checklist

Use this checklist on Raspberry Pi 4 after flashing the latest image.

## 1. Boot and OS Validation

- [ ] Pi4 boots successfully from the new SD card image.
- [ ] Login prompt appears on console or SSH is reachable.
- [ ] Confirm architecture:
  - Command: uname -m
  - Expected: aarch64
- [ ] Confirm kernel is running:
  - Command: uname -r
- [ ] Confirm root filesystem is mounted:
  - Command: mount | grep " on / "

## 2. systemd and Core Runtime

- [ ] Confirm systemd is PID 1:
  - Command: ps -p 1 -o comm=
  - Expected: systemd
- [ ] Confirm systemd is healthy:
  - Command: systemctl is-system-running
  - Expected: running or degraded (investigate degraded if shown)
- [ ] Confirm journalctl is available:
  - Command: journalctl --version

## 3. AV Service Unit Presence

- [ ] Confirm unit files exist:
  - ls /usr/lib/systemd/system/av-core-orchestrator.service
  - ls /usr/lib/systemd/system/av-core-gateway.service
  - ls /usr/lib/systemd/system/av-core-health.service
  - ls /usr/lib/systemd/system/av-core-logger.service
  - ls /usr/lib/systemd/system/av-core-ota.service
- [ ] Confirm services are enabled:
  - Command: systemctl is-enabled av-core-orchestrator av-core-gateway av-core-health av-core-logger

## 4. AV Service Runtime Status

- [ ] Check orchestrator status:
  - Command: systemctl status av-core-orchestrator --no-pager
- [ ] Check gateway status:
  - Command: systemctl status av-core-gateway --no-pager
- [ ] Check health status:
  - Command: systemctl status av-core-health --no-pager
- [ ] Check logger status:
  - Command: systemctl status av-core-logger --no-pager
- [ ] Review recent logs:
  - Command: journalctl -u av-core-orchestrator -u av-core-gateway -u av-core-health -u av-core-logger -n 100 --no-pager

## 5. AV Binary and Config Validation

- [ ] Confirm binaries are present:
  - ls /usr/local/bin/av-core-orchestrator
  - ls /usr/local/bin/av-core-gateway
  - ls /usr/local/bin/av-core-health
  - ls /usr/local/bin/av-core-logger
  - ls /usr/local/bin/av-core-ota
- [ ] Confirm config directory exists:
  - Command: ls -la /etc/av-core
- [ ] Confirm expected config files exist:
  - ls /etc/av-core/orchestrator.conf
  - ls /etc/av-core/gateway.conf
  - ls /etc/av-core/health.conf
  - ls /etc/av-core/logger.conf
  - ls /etc/av-core/ota.conf
- [ ] Confirm runtime directories exist:
  - ls -ld /var/lib/av-core/ota
  - ls -ld /var/log/av-core

## 6. Network and Time Services

- [ ] Confirm networkd service state:
  - Command: systemctl status systemd-networkd --no-pager
- [ ] Confirm resolved service state:
  - Command: systemctl status systemd-resolved --no-pager
- [ ] Confirm DNS resolution works:
  - Command: resolvectl query github.com
- [ ] Confirm timesync service state:
  - Command: systemctl status systemd-timesyncd --no-pager
- [ ] Confirm time sync source:
  - Command: timedatectl timesync-status

## 7. Diagnostic and Debug Tooling

- [ ] htop available:
  - Command: htop --version
- [ ] strace available:
  - Command: strace -V
- [ ] lshw available:
  - Command: lshw -version
- [ ] man available:
  - Command: man --version
- [ ] lscpu available:
  - Command: lscpu
- [ ] lspci available:
  - Command: lspci
- [ ] lsusb available:
  - Command: lsusb
- [ ] screen available:
  - Command: screen --version

## 8. SSH and Remote Access

- [ ] sshd enabled:
  - Command: systemctl is-enabled sshd
- [ ] sshd active:
  - Command: systemctl status sshd --no-pager
- [ ] Remote login test from host succeeds.

## 9. Sensor and Vehicle I/O Baseline

- [ ] CAN utilities available:
  - Command: cansend --help
- [ ] I2C tools available:
  - Command: i2cdetect -V
- [ ] GPIO tools available:
  - Command: gpioinfo
- [ ] GPS daemon available:
  - Command: gpsd -V

## 10. Optional Stress and Reboot Validation

- [ ] Reboot and verify AV services auto-start:
  - Command: reboot
  - After reboot: systemctl status av-core-orchestrator --no-pager
- [ ] Confirm no critical boot errors:
  - Command: journalctl -p err -b --no-pager
- [ ] Confirm watchdog/restart behavior by simulating service stop:
  - Command: systemctl stop av-core-orchestrator
  - Command: systemctl status av-core-orchestrator --no-pager
  - Expected: service restarts automatically if policy applies

## 11. Acceptance Criteria

Mark image as validated only when all are true:

- [ ] systemd-based boot is stable.
- [ ] Core AV services are active and logging to journal.
- [ ] AV binaries and configs are present in expected paths.
- [ ] Network, DNS, and time sync are operational.
- [ ] Diagnostic and remote access toolchain works.
- [ ] Reboot preserves service startup behavior.
