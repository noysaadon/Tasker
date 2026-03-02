from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import RunTaskRequest, RunTaskResponse, GetTaskOutputResponse, WordCountResponse, WordCountRequest
from app.services import create_and_enqueue_task
from app.models import Task
from app.cache import get_cached_output, set_cached_output

app = FastAPI(title="Tasker")

@app.post("/run-task", response_model=RunTaskResponse)
def run_task(req: RunTaskRequest, db: Session = Depends(get_db)):
    try:
        task_uuid = create_and_enqueue_task(db, req.task_name, req.task_parameters)
        return RunTaskResponse(uuid=task_uuid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get-task-output", response_model=GetTaskOutputResponse)
def get_task_output(task_uuid: str = Query(...), db: Session = Depends(get_db)):
    cached = get_cached_output(task_uuid)
    if cached is not None:
        return GetTaskOutputResponse(**cached)

    task = db.get(Task, task_uuid)
    if not task:
        raise HTTPException(status_code=404, detail="task_uuid not found")

    payload = {
        "task_uuid": task.uuid,
        "status": task.status,
        "task_output": task.output,
        "error": task.error,
    }

    if task.output is not None or task.status in ("SUCCESS", "FAILED"):
        set_cached_output(task_uuid, payload)

    return GetTaskOutputResponse(**payload)

@app.post("/word-count", response_model=WordCountResponse)
def word_count(req: WordCountRequest):
    words = [w for w in req.text.strip().split() if w]
    return WordCountResponse(words=len(words), chars=len(req.text))