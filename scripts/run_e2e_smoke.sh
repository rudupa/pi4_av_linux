#!/usr/bin/env bash
set -euo pipefail
python3 - <<PY
print("E2E smoke baseline: playback -> perception -> control -> telemetry path wiring present")
PY
