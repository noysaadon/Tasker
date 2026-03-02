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

def test_sum_task_success():
    r = client.post("/run-task", json={"task_name": "sum", "task_parameters": {"a": 10, "b": 25}})
    assert r.status_code == 200
    uuid = r.json()["uuid"]

    out = poll(uuid)
    assert out["status"] == "SUCCESS"
    assert out["task_output"]["result"] == 35

def test_word_count_task_success():
    r = client.post("/run-task", json={"task_name": "word_count", "task_parameters": {"text": "hello world"}})
    assert r.status_code == 200
    uuid = r.json()["uuid"]

    out = poll(uuid)
    assert out["status"] == "SUCCESS"
    assert out["task_output"]["words"] == 2

def test_chatgpt_mock_mode_success():
    r = client.post("/run-task", json={"task_name": "chatgpt", "task_parameters": {"prompt": "test prompt"}})
    assert r.status_code == 200
    uuid = r.json()["uuid"]

    out = poll(uuid)
    assert out["status"] == "SUCCESS"
    assert "[MOCK]" in out["task_output"]["answer"]