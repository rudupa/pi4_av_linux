# Task 04: Install Binaries and Runtime Layout

## Goal
Install compiled executables and runtime support files into target rootfs.

## What was performed
1. Kept CMake install path for service binaries so Buildroot installs into target filesystem.
2. Added runtime install hook in `av_services.mk` to place default config files in `/etc/av-core`.
3. Created persistent runtime directories during install:
   - `/var/lib/av-core/ota`
   - `/var/log/av-core`

## Outcome
- Target image includes AV executables and expected runtime layout.
- Service config defaults are present out-of-the-box.
