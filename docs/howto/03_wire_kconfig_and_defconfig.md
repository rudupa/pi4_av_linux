# Task 03: Wire Kconfig and Defconfig

## Goal
Ensure package selection and transitive dependencies are enabled from Buildroot configuration.

## What was performed
1. Updated `br2_external/package/av_services/Config.in` with package symbol and selects:
   - `BR2_PACKAGE_LIBCURL`
   - `BR2_PACKAGE_LIBCURL_FORCE_TLS`
   - `BR2_PACKAGE_OPENSSL`
   - `BR2_PACKAGE_LIBCURL_OPENSSL`
2. Enabled package in `configs/pi4_64_defconfig`:
   - `BR2_PACKAGE_AV_SERVICES=y`

## Outcome
- Package and TLS-related dependencies are selected through configuration.
- `defconfig` consistently reproduces a build with `av_services` enabled.
