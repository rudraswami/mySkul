"""Factory helpers for creating the shared job orchestrator instance."""
from __future__ import annotations

from functools import lru_cache

from .config import get_redis_client
from .handlers import HANDLERS
from .manager import JobOrchestrator
from .storage import RedisJobStore


@lru_cache
def get_orchestrator() -> JobOrchestrator:
    redis = get_redis_client()
    store = RedisJobStore(redis)
    return JobOrchestrator(store=store, handlers=HANDLERS)
