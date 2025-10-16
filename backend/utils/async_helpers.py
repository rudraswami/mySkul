"""
Async Error Handling Utilities
Provides consistent error handling for async functions
"""
import logging
import functools
from typing import Callable, Any
import asyncio

logger = logging.getLogger(__name__)


def handle_async_errors(
    default_return=None,
    log_errors=True,
    reraise=False
):
    """
    Decorator to handle async function errors consistently
    
    Usage:
        @handle_async_errors(default_return={}, log_errors=True)
        async def my_function():
            # function code
    
    Args:
        default_return: Value to return on error
        log_errors: Whether to log the error
        reraise: Whether to re-raise the exception after handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True
                    )
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def ensure_awaited(coro):
    """
    Ensure a coroutine is awaited, even if called without await
    
    This is a safety wrapper to catch common mistakes
    """
    if asyncio.iscoroutine(coro):
        logger.warning(f"Coroutine {coro} was not awaited. Auto-awaiting now.")
        return asyncio.create_task(coro)
    return coro


class AsyncContextManager:
    """
    Context manager for async operations with cleanup
    
    Usage:
        async with AsyncContextManager(setup_func, cleanup_func):
            # operations
    """
    def __init__(self, setup_func=None, cleanup_func=None):
        self.setup_func = setup_func
        self.cleanup_func = cleanup_func
        self.resources = None
    
    async def __aenter__(self):
        if self.setup_func:
            self.resources = await self.setup_func()
        return self.resources
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.cleanup_func:
            try:
                await self.cleanup_func(self.resources)
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
        
        # Don't suppress exceptions
        return False


async def run_with_timeout(coro, timeout_seconds: float):
    """
    Run an async function with a timeout
    
    Args:
        coro: Coroutine to run
        timeout_seconds: Timeout in seconds
    
    Returns:
        Result or raises TimeoutError
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(f"Operation timed out after {timeout_seconds}s")
        raise


async def run_sequential(*coros):
    """
    Run coroutines sequentially (one after another)
    Ensures dependent operations execute in order
    
    Returns:
        List of results
    """
    results = []
    for coro in coros:
        try:
            result = await coro
            results.append(result)
        except Exception as e:
            logger.error(f"Sequential execution error: {e}")
            results.append(None)
    return results


async def run_parallel(*coros, return_exceptions=True):
    """
    Run coroutines in parallel
    Safe for independent operations
    
    Args:
        *coros: Coroutines to run
        return_exceptions: If True, returns exceptions instead of raising
    
    Returns:
        List of results
    """
    try:
        results = await asyncio.gather(*coros, return_exceptions=return_exceptions)
        return results
    except Exception as e:
        logger.error(f"Parallel execution error: {e}")
        if return_exceptions:
            return [None] * len(coros)
        raise


class AsyncRetry:
    """
    Retry decorator for async functions
    
    Usage:
        @AsyncRetry(max_attempts=3, delay=1.0)
        async def my_function():
            # code
    """
    def __init__(self, max_attempts=3, delay=1.0, backoff=2.0):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
    
    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = self.delay
            last_exception = None
            
            for attempt in range(self.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_attempts} failed for {func.__name__}: {e}"
                    )
                    
                    if attempt < self.max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= self.backoff
            
            logger.error(f"All {self.max_attempts} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper


# Race condition prevention utilities
class AsyncLock:
    """
    Async lock for preventing race conditions
    
    Usage:
        lock = AsyncLock()
        async with lock:
            # critical section
    """
    def __init__(self):
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        await self._lock.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()
        return False


# Global locks for common operations
upload_lock = AsyncLock()
session_lock = AsyncLock()
