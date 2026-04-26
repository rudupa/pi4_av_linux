# Task 02: Convert av_services to a Buildroot Package

## Goal
Move from copying source code into the image to building `av_services` as a first-class Buildroot package.

## What was performed
1. Updated Buildroot package metadata under `br2_external/package/av_services/`.
2. Used CMake package infrastructure in `av_services.mk`:
   - `$(eval $(cmake-package))`
3. Pointed package source to local submodule content.
4. Added required package dependency wiring (`libcurl`) for cross-build.

## Outcome
- `av_services` now compiles during image generation using Buildroot cross-compilation.
