"""
Streaming Response Cleanup Utilities
=====================================

Prevents memory leaks in streaming endpoints by:
1. Proper exception handling in generators
2. Resource cleanup on disconnect
3. Timeout protection
4. Connection state monitoring
"""

import asyncio
import logging
from typing import AsyncGenerator, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class StreamingCleanupError(Exception):
    """Raised when streaming cleanup fails"""
    pass


@asynccontextmanager
async def streaming_context(stream_id: str):
    """
    Context manager for streaming operations.
    Ensures proper cleanup even if client disconnects.
    
    Usage:
        async with streaming_context("stream_123"):
            async for chunk in generate_chunks():
                yield chunk
    """
    logger.info(f"[{stream_id}] Streaming started")
    try:
        yield
    except asyncio.CancelledError:
        logger.warning(f"[{stream_id}] Client disconnected - cleaning up")
        raise
    except Exception as e:
        logger.error(f"[{stream_id}] Streaming error: {e}")
        raise
    finally:
        logger.info(f"[{stream_id}] Streaming cleanup complete")


async def safe_streaming_generator(
    generator: AsyncGenerator[str, None],
    stream_id: str,
    timeout: float = 120.0
) -> AsyncGenerator[str, None]:
    """
    Wrap generator with safety features:
    - Timeout protection
    - Exception handling
    - Proper cleanup
    
    Args:
        generator: The async generator to wrap
        stream_id: Unique identifier for logging
        timeout: Maximum streaming duration in seconds
    
    Yields:
        Chunks from generator
    
    Example:
        async def my_generator():
            yield "chunk1"
            yield "chunk2"
        
        safe_gen = safe_streaming_generator(my_generator(), "stream_123")
        async for chunk in safe_gen:
            # Process chunk
    """
    start_time = asyncio.get_event_loop().time()
    chunk_count = 0
    
    try:
        async with streaming_context(stream_id):
            async for chunk in generator:
                # Check timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    logger.warning(f"[{stream_id}] Timeout after {elapsed:.1f}s")
                    yield f"data: {{'type': 'error', 'message': 'Stream timeout'}}\n\n"
                    break
                
                chunk_count += 1
                yield chunk
                
                # Allow other tasks to run (prevent blocking)
                await asyncio.sleep(0)
        
        logger.info(f"[{stream_id}] Completed: {chunk_count} chunks in {elapsed:.2f}s")
        
    except asyncio.CancelledError:
        logger.warning(f"[{stream_id}] Cancelled after {chunk_count} chunks")
        # Don't re-raise - let connection close gracefully
        
    except Exception as e:
        logger.error(f"[{stream_id}] Error after {chunk_count} chunks: {e}")
        yield f"data: {{'type': 'error', 'message': 'Stream error'}}\n\n"
        
    finally:
        # Ensure generator is closed
        try:
            await generator.aclose()
        except Exception as e:
            logger.error(f"[{stream_id}] Error closing generator: {e}")


def create_sse_event(event_type: str, data: Any) -> str:
    """
    Create properly formatted Server-Sent Event.
    
    Args:
        event_type: Event type (e.g., "message", "error", "complete")
        data: Event data (will be JSON serialized)
    
    Returns:
        Formatted SSE string
    
    Example:
        >>> create_sse_event("chunk", {"text": "Hello"})
        'event: chunk\\ndata: {"text": "Hello"}\\n\\n'
    """
    import json
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def stream_with_heartbeat(
    generator: AsyncGenerator[str, None],
    heartbeat_interval: float = 15.0
) -> AsyncGenerator[str, None]:
    """
    Add heartbeat to streaming to keep connection alive.
    
    Args:
        generator: Source generator
        heartbeat_interval: Seconds between heartbeats
    
    Yields:
        Chunks from generator + periodic heartbeats
    """
    last_heartbeat = asyncio.get_event_loop().time()
    
    async for chunk in generator:
        yield chunk
        
        # Send heartbeat if needed
        now = asyncio.get_event_loop().time()
        if now - last_heartbeat > heartbeat_interval:
            yield create_sse_event("heartbeat", {"timestamp": now})
            last_heartbeat = now


