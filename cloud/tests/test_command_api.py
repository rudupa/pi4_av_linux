from fastapi.testclient import TestClient
from cloud.command_api.main import app


def test_rbac_blocks_without_token():
    c = TestClient(app)
    r = c.post("/cmd/reset", json={"cmd_id": "x1", "payload": {}})
    assert r.status_code == 403
