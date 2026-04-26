# Defconfig: Foundation Image vs Full AV Runtime Stack

## Summary

| Category | Foundation (before) | AV Runtime Stack (after) |
|---|---|---|
| Init system | BusyBox SysV (implicit) | systemd (`BR2_INIT_SYSTEMD=y`) |
| Logging | syslogd | systemd-journald |
| Networking | ifupdown/DHCP | systemd-networkd + systemd-resolved |
| Remote access | None | OpenSSH |
| Process inspection | None | htop, strace, util-linux (lscpu, lsblk) |
| Hardware inspection | None | lshw, pciutils (lspci), usbutils (lsusb) |
| Man pages | None | man-db |
| Session management | None | screen |
| AV service startup | S99avcore SysV script | Systemd unit files per service |
| Boot validation report | Manual only | Automated boot report via `pi4-feature-check.service` |

---

## Packages added for full AV runtime

### Init and service management
```
BR2_INIT_SYSTEMD=y
BR2_PACKAGE_SYSTEMD=y
BR2_PACKAGE_SYSTEMD_JOURNALD=y
BR2_PACKAGE_SYSTEMD_NETWORKD=y
BR2_PACKAGE_SYSTEMD_RESOLVED=y
```

### Diagnostics and debugging
```
BR2_PACKAGE_HTOP=y
BR2_PACKAGE_LSHW=y
BR2_PACKAGE_MAN_DB=y
BR2_PACKAGE_PCIUTILS=y
BR2_PACKAGE_STRACE=y
BR2_PACKAGE_USBUTILS=y
BR2_PACKAGE_UTIL_LINUX=y
BR2_PACKAGE_UTIL_LINUX_BINARIES=y
```

### Remote access and operations
```
BR2_PACKAGE_OPENSSH=y
BR2_PACKAGE_SCREEN=y
BR2_PACKAGE_PI4_FEATURE_CHECK=y
```

---

## Package purpose reference

| Package symbol | Command(s) provided | Purpose |
|---|---|---|
| `BR2_PACKAGE_HTOP` | `htop` | Interactive process viewer |
| `BR2_PACKAGE_LSHW` | `lshw` | Hardware listing |
| `BR2_PACKAGE_MAN_DB` | `man` | Manual pages |
| `BR2_PACKAGE_OPENSSH` | `ssh`, `sshd` | Remote access |
| `BR2_PACKAGE_PCIUTILS` | `lspci` | PCI device listing |
| `BR2_PACKAGE_SCREEN` | `screen` | Persistent terminal sessions |
| `BR2_PACKAGE_STRACE` | `strace` | System call tracing |
| `BR2_PACKAGE_USBUTILS` | `lsusb` | USB device listing |
| `BR2_PACKAGE_UTIL_LINUX` + `_BINARIES` | `lscpu`, `lsblk`, `lsns`, `findmnt` | System/block/namespace utilities |
| `BR2_PACKAGE_SYSTEMD_JOURNALD` | `journalctl` | Structured log access |
| `BR2_PACKAGE_SYSTEMD_NETWORKD` | `networkctl` | Network interface management |
| `BR2_PACKAGE_SYSTEMD_RESOLVED` | `resolvectl` | DNS resolution management |
| `BR2_PACKAGE_PI4_FEATURE_CHECK` | `pi4_feature_check.sh`, `pi4-feature-check.service` | Boot-time feature validation and report generation (`/var/log/pi4_feature_report.md`) |

---

## Packages not added and why

| Command | Reason not available |
|---|---|
| `lsdev` | Not a Buildroot package. Equivalent: `lspci`, `lsusb`, `/proc/interrupts` |
| `journalctl` (BusyBox) | Requires systemd. Now available via `BR2_PACKAGE_SYSTEMD_JOURNALD=y` |
