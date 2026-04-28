#!/usr/bin/env bash
set -euo pipefail
echo "[smoke] checking python entrypoints"
python3 -m pi4.src.main --help >/dev/null
python3 - <<PY
import yaml
cfg=yaml.safe_load(open("pi4/config/runtime.yaml"))
assert cfg["mqtt"]["topic_state"]
print("config ok")
PY
echo "[smoke] ok"
