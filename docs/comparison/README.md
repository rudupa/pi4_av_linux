# Comparison Documents

This folder contains side-by-side comparisons of architectural and implementation choices made in this repository.

## Files

1. `busybox_vs_systemd.md`
   BusyBox SysV init vs systemd: feature table, service lifecycle, on-target CLI comparison, and why this repo moved to systemd.

2. `foundation_vs_av_runtime_defconfig.md`
   Defconfig before and after the AV runtime evolution: packages added, their purpose, and what was not added and why.

3. `sysv_init_vs_systemd_service_units.md`
   S99avcore shell script vs per-service systemd unit files: side-by-side code, install hook comparison in av_services.mk, and full unit inventory.

4. `buildroot_foundation_vs_av_package_integration.md`
   Three-stage evolution of av_services package integration: source copy → cross-build BSP → full AV runtime with systemd.
