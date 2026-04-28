import json
from pathlib import Path
from jsonschema import validate


def test_perception_schema_roundtrip():
    schema = json.loads((Path("contracts/schemas/perception_objects_v1.json")).read_text())
    sample = {
        "schema_version": 1,
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "source": "pc",
        "sequence_id": 1,
        "objects": [{
            "id": "1", "class": "vehicle", "confidence": 0.9,
            "bbox": [1,2,3,4], "range_m": 10.0, "rel_velocity_mps": 0.1,
            "source_flags": ["camera"], "track_state": "tracked"
        }]
    }
    validate(instance=sample, schema=schema)
