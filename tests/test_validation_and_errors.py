import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def poll(uuid: str, attempts: int = 50, sleep_s: float = 0.2):
    for _ in range(attempts):
        r = client.get("/get-task-output", params={"task_uuid": uuid})
        assert r.status_code == 200
        data = r.json()
        if data["status"] in ("SUCCESS", "FAILED"):
            return data
        time.sleep(sleep_s)
    raise AssertionError("Task did not reach terminal state")

def test_invalid_task_name_returns_400():
    r = client.post("/run-task", json={"task_name": "nope", "task_parameters": {}})
    assert r.status_code == 400

def test_invalid_sum_params_returns_400():
    r = client.post("/run-task", json={"task_name": "sum", "task_parameters": {"a": 1}})
    assert r.status_code == 400

def test_unknown_uuid_returns_404():
    r = client.get("/get-task-output", params={"task_uuid": "00000000-0000-0000-0000-000000000000"})
    assert r.status_code == 404

def test_failure_task_sets_failed_status():
    r = client.post("/run-task", json={"task_name": "boom", "task_parameters": {}})
    assert r.status_code == 200
    uuid = r.json()["uuid"]

    out = poll(uuid)
    assert out["status"] == "FAILED"
    assert "Intentional failure" in (out["error"] or "")