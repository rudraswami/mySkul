"""Configuration helpers for the job orchestration layer."""
from __future__ import annotations

import os
from functools import lru_cache

from redis import asyncio as redis_asyncio


@lru_cache
def get_redis_client():
    """Return a Redis asyncio client configured from environment variables."""
    url = os.environ.get("REDIS_URL")
    if not url:
        raise RuntimeError("REDIS_URL must be configured before creating the job orchestrator")

    return redis_asyncio.from_url(
        url,
        decode_responses=True,
        health_check_interval=int(os.environ.get("REDIS_HEALTHCHECK_SECONDS", "30")),
    )
