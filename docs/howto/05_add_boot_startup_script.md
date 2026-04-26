# Task 05: Add Boot Startup Script

## Goal
Allow AV services to be started and managed automatically at boot.

## What was performed
1. Added BusyBox SysV init script: `br2_external/package/av_services/S99avcore`.
2. Implemented service commands:
   - `start`, `stop`, `restart`, `status`
3. Wired script install through `AV_SERVICES_INSTALL_INIT_SYSV` in `av_services.mk`.

## Outcome
- Script is installed as `/etc/init.d/S99avcore` in the target rootfs.
- `av-core-orchestrator` can be managed via standard init workflow.
