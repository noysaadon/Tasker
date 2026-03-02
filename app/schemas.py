from pydantic import BaseModel, Field
from typing import Any, Dict

class RunTaskRequest(BaseModel):
    task_name: str = Field(..., min_length=1)
    task_parameters: Dict[str, Any] = Field(default_factory=dict)

class RunTaskResponse(BaseModel):
    uuid: str

class GetTaskOutputResponse(BaseModel):
    task_uuid: str
    status: str
    task_output: Dict[str, Any] | None = None
    error: str | None = None
