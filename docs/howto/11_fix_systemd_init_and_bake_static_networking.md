# Task 11: Fix systemd PID 1 and Bake Static IPv4 Networking

## Goal
Resolve a boot mismatch where systemd was installed but BusyBox was still taking PID 1, then bake persistent Ethernet IPv4 configuration into the image for direct bring-up and SSH.

## Symptoms observed
- `systemd --version` worked on target.
- `systemctl` failed with: `System has not been booted with systemd as init system (PID 1)`.
- `/sbin/init` resolved to BusyBox on the generated rootfs.
- Ethernet interface was present, but no non-loopback IPv4 address was assigned for direct PC-to-Pi access.

## Debug steps used
1. Verified Buildroot init selection in `configs/pi4_64_defconfig` and `output/.config`.
2. Verified the generated rootfs still linked `/sbin/init` to BusyBox.
3. Confirmed BusyBox default config still enabled:
   - `CONFIG_INIT=y`
   - `CONFIG_FEATURE_USE_INITTAB=y`
4. Confirmed systemd binaries and service units were present, so the failure was ownership of PID 1 rather than missing packages.
5. Verified Ethernet link visibility on-target, then observed only loopback IPv4 was configured.

## What was changed

### 1. Disable BusyBox init applet
Added BusyBox config fragment:
- `board/raspberrypi/busybox-no-init.fragment`

Fragment contents:
- `# CONFIG_INIT is not set`
- `# CONFIG_FEATURE_USE_INITTAB is not set`

Updated `configs/pi4_64_defconfig`:
- Added `BR2_PACKAGE_BUSYBOX_CONFIG_FRAGMENT_FILES="board/raspberrypi/busybox-no-init.fragment"`

This preserves BusyBox for utilities but prevents it from owning `/sbin/init`.

### 2. Bake static network config into the image
Added rootfs overlay path in `configs/pi4_64_defconfig`:
- `BR2_ROOTFS_OVERLAY="board/raspberrypi/rootfs_overlay"`

Removed older BusyBox-style DHCP setting:
- Removed `BR2_SYSTEM_DHCP="eth0"`

Added systemd-networkd config file:
- `board/raspberrypi/rootfs_overlay/etc/systemd/network/10-eth-static.network`

Configured values:
- Address: `192.168.1.100/24`
- Gateway: `192.168.1.1`
- DNS: `8.8.8.8`

The match rule uses:
- `Type=ether`
- `Name=!lo`

This avoids depending on a specific interface name such as `eth0` or `end0`.

## Build / validation notes
1. Run a clean rebuild so the BusyBox fragment is applied:
```bash
make clean && make build
```
2. Reflash the latest `output/images/sdcard.img`.
3. On target, verify:
```bash
cat /proc/1/comm
readlink -f /sbin/init
ip -4 addr
systemctl status sshd --no-pager
```

Expected results:
- PID 1 is `systemd`
- `/sbin/init` resolves to a systemd binary
- Ethernet has the baked IPv4 address
- SSH is reachable after setting a non-empty root password

## Outcome
- systemd now owns PID 1 after a clean rebuild.
- BusyBox remains available without controlling init.
- Ethernet IPv4 configuration is persistent across reflashes.
- Direct SSH bring-up is simpler once the root password is set.
