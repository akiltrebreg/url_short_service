from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis
import os

from .routes import router
from .tasks import start_scheduler

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

    # Запуск планировщика задач
    start_scheduler()

app.include_router(router)
