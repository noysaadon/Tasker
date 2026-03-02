import json
import httpx
from sqlalchemy.orm import Session
from app.config import settings
from app.db import SessionLocal
from app.models import Task, TaskStatus
from app.cache import set_cached_output
from worker.celery_app import celery_app

def db_session() -> Session:
    return SessionLocal()

def task_sum(params: dict) -> dict:
    return {"result": params["a"] + params["b"]}

def task_word_count(params: dict) -> dict:
    text = params["text"]
    words = [w for w in text.strip().split() if w]
    return {"words": len(words), "chars": len(text)}

async def task_chatgpt(params: dict) -> dict:
    prompt = params.get("prompt", "")

    # MOCK MODE
    if not settings.OPENAI_ENABLED:
       return {"answer": f"[MOCK] Echo: {prompt[:120]}"}

    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENAI_MODEL,
        "input": params["prompt"]
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.openai.com/v1/responses",
            headers=headers,
            json=payload,
        )
        if r.status_code >= 400:
            raise RuntimeError(
                f"OpenAI error {r.status_code}: {r.text}"
            )
              
        data = r.json()

    text = None
    try:
        text = data["output"][0]["content"][0]["text"]
    except Exception:
        text = json.dumps(data)

    return {"answer": text}

def task_boom(params: dict) -> dict:
    raise RuntimeError("Intentional failure (boom task)")

@celery_app.task(name="worker.tasks.execute_task")
def execute_task(task_uuid: str) -> None:
    db = db_session()
    task = None
    try:
        task = db.get(Task, task_uuid)
        if not task:
            return

        task.status = TaskStatus.RUNNING.value
        db.commit()

        if task.name == "sum":
            output = task_sum(task.parameters)
        elif task.name == "word_count":
            output = task_word_count(task.parameters)
        elif task.name == "chatgpt":
            import asyncio
            output = asyncio.run(task_chatgpt(task.parameters))
        elif task.name == "boom":
            output = task_boom(task.parameters)
        else:
            raise RuntimeError(f"Unsupported task: {task.name}")

        task.status = TaskStatus.SUCCESS.value
        task.output = output
        task.error = None
        db.commit()

        payload = {"task_uuid": task.uuid, "status": task.status, "task_output": task.output, "error": None}
        set_cached_output(task.uuid, payload)

    except Exception as e:
        if task:
            task.status = TaskStatus.FAILED.value
            task.error = str(e)
            db.commit()
            payload = {"task_uuid": task.uuid, "status": task.status, "task_output": task.output, "error": task.error}
            set_cached_output(task.uuid, payload)
    finally:
        db.close()
