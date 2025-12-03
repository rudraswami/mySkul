"""
LLM Call Timeout Wrapper
========================

Prevents LLM API calls from hanging indefinitely.
Adds timeout protection to all LLM interactions.

Usage:
    from utils.llm_timeout import with_timeout
    
    response = await with_timeout(
        llm_client.chat.completions.create(...),
        timeout=30.0
    )
"""

import asyncio
import logging
from typing import Any, Coroutine, TypeVar, Optional
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Default timeouts (in seconds)
DEFAULT_LLM_TIMEOUT = 30.0  # 30 seconds for standard calls
LONG_LLM_TIMEOUT = 60.0     # 60 seconds for complex generation
STREAMING_TIMEOUT = 120.0   # 2 minutes for streaming responses


class LLMTimeoutError(Exception):
    """Raised when an LLM call exceeds timeout"""
    pass


async def with_timeout(
    coro: Coroutine[Any, Any, T],
    timeout: float = DEFAULT_LLM_TIMEOUT,
    error_message: Optional[str] = None
) -> T:
    """
    Execute coroutine with timeout protection.
    
    Args:
        coro: The coroutine to execute
        timeout: Timeout in seconds
        error_message: Custom error message
    
    Returns:
        Result from coroutine
    
    Raises:
        LLMTimeoutError: If timeout exceeded
    
    Example:
        >>> response = await with_timeout(
        ...     client.chat.completions.create(...),
        ...     timeout=30.0
        ... )
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        msg = error_message or f"LLM call exceeded timeout of {timeout}s"
        logger.error(f"⏱️ {msg}")
        raise LLMTimeoutError(msg)


def timeout_decorator(timeout: float = DEFAULT_LLM_TIMEOUT):
    """
    Decorator to add timeout protection to async functions.
    
    Usage:
        @timeout_decorator(timeout=30.0)
        async def call_llm():
            return await client.chat.completions.create(...)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await with_timeout(
                func(*args, **kwargs),
                timeout=timeout,
                error_message=f"{func.__name__} exceeded timeout of {timeout}s"
            )
        return wrapper
    return decorator


# Convenience functions for common timeout scenarios

async def llm_call_with_timeout(
    llm_func,
    *args,
    timeout: float = DEFAULT_LLM_TIMEOUT,
    **kwargs
) -> Any:
    """
    Call LLM function with standard timeout.
    
    Example:
        >>> response = await llm_call_with_timeout(
        ...     client.chat.completions.create,
        ...     model="gpt-4",
        ...     messages=[...]
        ... )
    """
    return await with_timeout(
        llm_func(*args, **kwargs),
        timeout=timeout,
        error_message=f"LLM call exceeded {timeout}s timeout"
    )


async def streaming_llm_with_timeout(
    llm_func,
    *args,
    timeout: float = STREAMING_TIMEOUT,
    **kwargs
) -> Any:
    """
    Call streaming LLM function with extended timeout.
    """
    return await with_timeout(
        llm_func(*args, **kwargs),
        timeout=timeout,
        error_message=f"Streaming LLM call exceeded {timeout}s timeout"
    )


