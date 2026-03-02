import json
import redis
from app.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_key(task_uuid: str) -> str:
    return f"task_output:{task_uuid}"

def get_cached_output(task_uuid: str):
    raw = redis_client.get(cache_key(task_uuid))
    return json.loads(raw) if raw else None

def set_cached_output(task_uuid: str, payload: dict):
    redis_client.setex(cache_key(task_uuid), settings.CACHE_TTL_SECONDS, json.dumps(payload))
