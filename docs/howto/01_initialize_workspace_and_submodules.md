# Task 01: Initialize Workspace and Submodules

## Goal
Prepare the Buildroot workspace and ensure `external/av_services` is available as a git submodule.

## What was performed
1. Cloned and opened the `pi4_linux` workspace.
2. Initialized and synced submodules:
   - `make submodules`
   - `make submodules-update`
3. Verified submodule checkout state from `external/av_services`.

## Outcome
- Buildroot project root and external layer were ready.
- `av_services` source became available to package from the local tree.
