#!/usr/bin/env bash
set -euo pipefail
mkdir -p output/metadata
cat > output/metadata/version.json <<JSON
{
  "build_time_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "git_commit": "$(git rev-parse --short HEAD 2>/dev/null || echo unknown)",
  "image": "pi4"
}
JSON
