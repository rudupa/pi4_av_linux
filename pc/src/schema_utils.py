from __future__ import annotations
import json
from pathlib import Path
from jsonschema import validate

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "contracts" / "schemas"

def validate_schema(name: str, payload: dict) -> None:
    path = SCHEMA_DIR / f"{name}.json"
    schema = json.loads(path.read_text())
    validate(instance=payload, schema=schema)
