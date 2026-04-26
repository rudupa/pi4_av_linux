# Linux Filesystem Guide for This Buildroot Image

This document explains the Linux filesystem layout and highlights paths that matter for the Raspberry Pi Buildroot image in this repository.

## 1. Linux filesystem overview

Linux uses a single directory tree rooted at `/`.

Common top-level directories:

- `/bin`: essential user commands (for all users)
- `/sbin`: essential system commands (typically admin)
- `/etc`: system configuration
- `/dev`: device nodes (hardware and virtual devices)
- `/proc`: process and kernel runtime information (virtual)
- `/sys`: kernel device model and driver info (virtual)
- `/tmp`: temporary files
- `/var`: variable runtime data (logs, spool, state)
- `/usr`: most userland programs and libraries
- `/lib`, `/lib64`: shared libraries required by binaries
- `/home`: user home directories (not always populated in embedded images)
- `/root`: root user's home directory
- `/run`: runtime state (PID files, sockets, transient data)
- `/mnt`, `/media`: mount points for removable or extra filesystems

## 2. How this applies to your Buildroot image

This image is BusyBox-centric and Buildroot-generated. The layout is standard Linux, but minimal and embedded-oriented.

Important image-specific paths:

- `/etc/init.d/S99avcore`: BusyBox init script that starts av-core orchestrator
- `/etc/av-core/`: configuration files for av-core services
- `/usr/local/bin/av-core-*`: compiled av-core binaries
- `/var/lib/av-core/ota`: OTA working directory
- `/var/log/av-core`: av-core log directory

## 3. Core directories you will use most on Pi

### `/etc`

System configuration lives here.

Examples for this image:

- `/etc/hostname`
- `/etc/hosts`
- `/etc/inittab`
- `/etc/init.d/`
- `/etc/av-core/`

### `/usr` and `/usr/local`

Programs and libraries installed from Buildroot packages.

Examples:

- `/usr/bin`
- `/usr/sbin`
- `/usr/lib`
- `/usr/local/bin/av-core-gateway`
- `/usr/local/bin/av-core-health`
- `/usr/local/bin/av-core-logger`
- `/usr/local/bin/av-core-ota`
- `/usr/local/bin/av-core-orchestrator`

### `/var`

Writable data that changes during runtime.

Examples:

- `/var/lib/chrony`
- `/var/lib/av-core/ota`
- `/var/log`
- `/var/log/av-core`

### `/proc` and `/sys`

Virtual filesystems provided by the kernel for inspection and control.

Useful examples:

- `/proc/cpuinfo`
- `/proc/meminfo`
- `/proc/<pid>/`
- `/sys/class/net/`
- `/sys/class/gpio/`

### `/dev`

Device files for hardware interfaces.

Examples:

- `/dev/tty*`
- `/dev/i2c-*`
- `/dev/video*`
- `/dev/spidev*`
- `/dev/can*` (if exposed by driver/hardware setup)

## 4. Quick inspection commands

Run these on the Pi:

```sh
# Show top-level layout
ls -la /

# See mounted filesystems
mount

# Disk usage summary
df -h

# Show av-core binaries
ls -l /usr/local/bin/av-core-*

# Show av-core config
ls -l /etc/av-core

# Show startup script
ls -l /etc/init.d/S99avcore

# Process and kernel virtual FS checks
ls /proc | head
ls /sys/class | head
```

## 5. Boot and root filesystem note

In this repository, the built image contains:

- boot partition image: `output/images/boot.vfat`
- root filesystem image: `output/images/rootfs.ext2`
- full deployable SD image: `output/images/sdcard.img`

At runtime on Pi, the root filesystem is mounted as `/` and all paths in this document are relative to that root.

## 6. Embedded-system conventions to remember

- Keep writes to `/var` and `/tmp`; avoid unnecessary writes elsewhere.
- Treat `/proc` and `/sys` as kernel interfaces, not regular storage.
- If you add services, place configs in `/etc` and binaries in `/usr/bin` or `/usr/local/bin`.
- For BusyBox init startup, use scripts in `/etc/init.d`.

## 7. AV task to path mapping

Common operational tasks and where to look:

- Check AV binaries: `/usr/local/bin/av-core-*`
- Check AV configs: `/etc/av-core/`
- Start/stop AV stack: `/etc/init.d/S99avcore`
- Check AV runtime logs: `/var/log/av-core/`
- Check OTA download state: `/var/lib/av-core/ota/`
- Check active processes: `/proc/<pid>/` and `ps`
- Check network device state: `/sys/class/net/` and `ip addr`

Useful commands:

- Start AV stack: `sh /etc/init.d/S99avcore start`
- Stop AV stack: `sh /etc/init.d/S99avcore stop`
- Restart AV stack: `sh /etc/init.d/S99avcore restart`
- Show AV processes: `ps | grep av-core | grep -v grep`

## 8. Shutdown commands for Pi 4

Safe shutdown options:

- `poweroff`
- `shutdown -h now`
- `init 0`

Recommended default:

- `poweroff`
