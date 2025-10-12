"""Async worker entrypoint for pipeline job execution."""
from __future__ import annotations

import asyncio
import logging

from jobs.bootstrap import get_orchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger("jobs.worker")


async def main() -> None:
    orchestrator = get_orchestrator()
    LOGGER.info("Job worker booted")
    await orchestrator.run_worker()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Job worker interrupted, shutting down")
