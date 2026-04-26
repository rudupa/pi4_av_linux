# Task 06: Build and Validate the Image

## Goal
Produce a complete Raspberry Pi 4 image with integrated AV services and verify artifacts.

## What was performed
1. Applied project defconfig:
   - `make defconfig`
2. Built full image:
   - `make build`
3. Rebuilt after package updates to ensure latest changes were included.
4. Verified expected outputs under Buildroot output directories.

## Outcome
- Build completed successfully with `av_services` integrated.
- Image artifacts include package output and rootfs updates.
