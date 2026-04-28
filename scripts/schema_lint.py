#!/usr/bin/env python3
import json
from pathlib import Path
from jsonschema.validators import Draft202012Validator

root = Path("contracts/schemas")
errors = 0
for p in root.glob("*.json"):
    try:
        obj = json.loads(p.read_text())
        Draft202012Validator.check_schema(obj)
        print(f"ok: {p}")
    except Exception as e:
        print(f"error: {p}: {e}")
        errors += 1
if errors:
    raise SystemExit(1)
