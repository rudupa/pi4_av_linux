# Task 10: Integrate Boot-Time Feature Report Service

## Goal
Automate post-boot validation on Pi4 and generate a report file without manual checklist execution.

## What was performed

### 1. Added a new Buildroot external package
Created package directory:
- `br2_external/package/pi4_feature_check/`

Files added:
- `Config.in`
- `pi4_feature_check.mk`
- `pi4_feature_check.sh`
- `pi4-feature-check.service`

### 2. Wired package into external Kconfig
Updated:
- `br2_external/Config.in`

Added source entry:
- `source "$BR2_EXTERNAL_PI4_AV_EXTERNAL_PATH/package/pi4_feature_check/Config.in"`

### 3. Enabled package in project defconfig
Updated:
- `configs/pi4_64_defconfig`

Enabled symbol:
- `BR2_PACKAGE_PI4_FEATURE_CHECK=y`

### 4. Installed script and systemd unit through Buildroot
`pi4_feature_check.mk` installs:
- `/usr/local/sbin/pi4_feature_check.sh`
- `/usr/lib/systemd/system/pi4-feature-check.service`

Also creates boot enable symlink:
- `/etc/systemd/system/multi-user.target.wants/pi4-feature-check.service`

### 5. Boot report behavior
At boot, `pi4-feature-check.service` runs once and writes:
- `/var/log/pi4_feature_report.md`

Checks include:
- systemd PID 1 and core services
- AV service activity
- AV binaries/config paths
- diagnostic tool availability

## Verification commands on target Pi4
```bash
systemctl status pi4-feature-check --no-pager
journalctl -u pi4-feature-check -b --no-pager
cat /var/log/pi4_feature_report.md
```

## Outcome
- Checklist execution is automated at boot.
- A reproducible, timestamped Markdown report is generated on-device.
- Validation can be audited via both report file and journald logs.
