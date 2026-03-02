import uuid as uuid_lib
from sqlalchemy.orm import Session
from app.models import Task, TaskStatus
from app.tasks_registry import TASK_VALIDATORS
from worker.celery_app import celery_app  # celery task

def create_and_enqueue_task(db: Session, task_name: str, task_parameters: dict) -> str:
    if task_name not in TASK_VALIDATORS:
        raise ValueError(f"Unsupported task_name: {task_name}")

    TASK_VALIDATORS[task_name](task_parameters)

    task_uuid = str(uuid_lib.uuid4())
    task = Task(
        uuid=task_uuid,
        name=task_name,
        parameters=task_parameters,
        status=TaskStatus.PENDING.value,
    )
    db.add(task)
    db.commit()

    # decoupled submit: API sends only the task name + args
    celery_app.send_task("worker.tasks.execute_task", args=[task_uuid])
    return task_uuid
