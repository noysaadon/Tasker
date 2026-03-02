from typing import Any, Dict, Callable

def validate_sum(params: Dict[str, Any]) -> None:
    if "a" not in params or "b" not in params:
        raise ValueError("sum task requires parameters: a, b")
    if not isinstance(params["a"], (int, float)) or not isinstance(params["b"], (int, float)):
        raise ValueError("a and b must be numbers")

def validate_chatgpt(params: Dict[str, Any]) -> None:
    if "prompt" not in params or not isinstance(params["prompt"], str) or not params["prompt"].strip():
        raise ValueError("chatgpt task requires a non-empty 'prompt' string")

def validate_custom(params: Dict[str, Any]) -> None:
    if "text" not in params or not isinstance(params["text"], str):
        raise ValueError("word_count task requires 'text' string")

def validate_boom(params: Dict[str, Any]) -> None:
    return

TASK_VALIDATORS: dict[str, Callable[[Dict[str, Any]], None]] = {
    "sum": validate_sum,
    "chatgpt": validate_chatgpt,
    "word_count": validate_custom,
    "boom": validate_boom,
}
