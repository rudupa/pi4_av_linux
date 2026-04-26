# Buildroot Package Integration: Foundation vs AV Runtime

## Evolution of av_services package integration

The av_services package went through two stages of integration in this repo.

---

## Stage 1: Foundation — source copy

The earliest approach copied av_services source into the image without building it.

| Aspect | Approach |
|---|---|
| Source handling | Copied into rootfs as source tree |
| Binary | Not cross-compiled |
| Config files | Not installed |
| Startup | Not managed |
| Defconfig symbol | Not present |

---

## Stage 2: Cross-build BSP package (pre-AV runtime)

av_services was converted to a proper Buildroot cmake-package.

`av_services.mk` key additions:
```make
AV_SERVICES_SITE_METHOD = local
AV_SERVICES_DEPENDENCIES = libcurl
$(eval $(cmake-package))
```

`Config.in` additions:
```
select BR2_PACKAGE_LIBCURL
select BR2_PACKAGE_LIBCURL_FORCE_TLS
select BR2_PACKAGE_OPENSSL
select BR2_PACKAGE_LIBCURL_OPENSSL
```

| Aspect | Stage 2 |
|---|---|
| Source handling | Cross-compiled by Buildroot CMake infra |
| Binaries | Installed to `/usr/local/bin/av-core-*` |
| Config files | Installed to `/etc/av-core/` |
| Runtime dirs | `/var/lib/av-core/ota`, `/var/log/av-core` |
| Startup | Single SysV init script `S99avcore` |
| Defconfig symbol | `BR2_PACKAGE_AV_SERVICES=y` |

---

## Stage 3: Full AV Runtime Stack (current)

On top of Stage 2, the following were added for a production-grade runtime.

### Init system upgrade
| Item | Before | After |
|---|---|---|
| PID 1 | BusyBox init | systemd |
| Defconfig | (implicit) | `BR2_INIT_SYSTEMD=y` |
| Packages added | — | systemd, journald, networkd, resolved |

### Service granularity
| Before | After |
|---|---|
| One script manages all services | One unit file per service |
| Sequential start | Parallel start via dependency graph |
| No per-service restart policy | `Restart=on-failure` per unit |
| No watchdog | `WatchdogSec=` per unit |

### New unit files installed
```
/usr/lib/systemd/system/av-core-orchestrator.service
/usr/lib/systemd/system/av-core-gateway.service
/usr/lib/systemd/system/av-core-health.service
/usr/lib/systemd/system/av-core-logger.service
/usr/lib/systemd/system/av-core-ota.service
```

### Diagnostic tooling added
```
BR2_PACKAGE_HTOP=y
BR2_PACKAGE_LSHW=y
BR2_PACKAGE_MAN_DB=y
BR2_PACKAGE_OPENSSH=y
BR2_PACKAGE_PCIUTILS=y
BR2_PACKAGE_SCREEN=y
BR2_PACKAGE_STRACE=y
BR2_PACKAGE_USBUTILS=y
BR2_PACKAGE_UTIL_LINUX=y
BR2_PACKAGE_UTIL_LINUX_BINARIES=y
```

---

## File change summary

| File | Change |
|---|---|
| `configs/pi4_64_defconfig` | Added `BR2_INIT_SYSTEMD=y`, systemd packages, diagnostics packages |
| `br2_external/package/av_services/av_services.mk` | Added `AV_SERVICES_INSTALL_INIT_SYSTEMD` hook alongside existing SysV hook |
| `br2_external/package/av_services/Config.in` | Updated help text to reflect dual init support |
| `br2_external/package/av_services/*.service` | Five new systemd unit files added |
