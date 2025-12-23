"""
AI Streaming Response Service
Enables incremental token streaming for faster perceived latency
"""
import asyncio
import logging
import re
from typing import AsyncGenerator, Optional, Dict, Any
import json

logger = logging.getLogger(__name__)


# =============================================================================
# STREAMING CHUNK SANITIZER
# =============================================================================
# CRITICAL: Every streamed chunk must be UI-safe.
# Same forbidden patterns as _sanitize_response_for_student().

# Forbidden patterns that indicate internal traces
FORBIDDEN_STREAMING_PATTERNS = [
    '"thought":', '"action":', '"action_input":', '"tool_calls":',
    '"routing":', '"confidence":', '"observation":',
    'Student asked:', 'Traceback (', 'Action:', 'Thought:',
    '"hybrid_reasoning":', '"orchestration":'
]

def _sanitize_streaming_chunk(chunk: str) -> str:
    """
    Sanitize a streaming chunk before sending to client.
    
    FAST PATH: O(1) substring checks, only slow path if patterns found.
    IDEMPOTENT: Running twice produces same result.
    
    This ensures no internal JSON/tool traces leak through SSE.
    """
    if not chunk or not isinstance(chunk, str):
        return chunk or ''
    
    # FAST PATH: Quick check for forbidden patterns
    chunk_lower = chunk.lower()
    needs_sanitization = any(
        pattern.lower() in chunk_lower 
        for pattern in FORBIDDEN_STREAMING_PATTERNS
    )
    
    if not needs_sanitization:
        # Also check for suspicious JSON-like structures
        if '{"' not in chunk and '"}' not in chunk:
            return chunk  # Fast path - clean chunk
    
    # SLOW PATH: Sanitize the chunk
    sanitized = chunk
    
    # Remove JSON blocks with internal keys (handles nested braces)
    # Use a more aggressive approach: find { ... } blocks containing forbidden keys
    def remove_json_with_forbidden_keys(text: str) -> str:
        """Remove JSON objects containing forbidden keys, handling nesting."""
        result = []
        i = 0
        while i < len(text):
            if text[i] == '{':
                # Find matching closing brace
                brace_count = 1
                start = i
                j = i + 1
                while j < len(text) and brace_count > 0:
                    if text[j] == '{':
                        brace_count += 1
                    elif text[j] == '}':
                        brace_count -= 1
                    j += 1
                
                # Extract the JSON-like block
                block = text[start:j]
                block_lower = block.lower()
                
                # Check if block contains forbidden keys
                has_forbidden = any(
                    key in block_lower 
                    for key in ['"thought"', '"action"', '"action_input"', '"confidence"', 
                                '"observation"', '"routing"', '"tool_calls"', 
                                '"hybrid_reasoning"', '"orchestration"']
                )
                
                if has_forbidden:
                    # Skip this block
                    i = j
                    continue
                else:
                    # Keep this block
                    result.append(block)
                    i = j
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)
    
    sanitized = remove_json_with_forbidden_keys(sanitized)
    
    # Remove ReAct transcript patterns
    react_pattern = r'(?:^|\n)\s*(?:Thought|Action|Observation|Action Input):\s*[^\n]*(?:\n|$)'
    sanitized = re.sub(react_pattern, '\n', sanitized, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove "Student asked:" debug lines
    sanitized = re.sub(r'Student asked:[^\n]*\n?', '', sanitized, flags=re.IGNORECASE)
    
    # Remove Traceback lines
    sanitized = re.sub(r'Traceback \(most recent call last\)[^\n]*\n?', '', sanitized)
    
    # Remove standalone trace keys like "thought": ...
    trace_pattern = r'(?:^|\n)\s*"(?:thought|action|action_input)":\s*[^\n]+(?:\n|$)'
    sanitized = re.sub(trace_pattern, '\n', sanitized, flags=re.IGNORECASE | re.MULTILINE)
    
    # Clean up orphaned braces at start of line
    sanitized = re.sub(r'^\s*\{\s*$', '', sanitized, flags=re.MULTILINE)
    sanitized = re.sub(r'^\s*\}\s*$', '', sanitized, flags=re.MULTILINE)
    
    # Clean up multiple newlines
    sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
    
    return sanitized.strip() if sanitized else ''


class StreamingResponseService:
    """Service for streaming AI responses token by token"""
    
    def __init__(self, ai_service):
        self.ai_service = ai_service
    
    async def stream_response(
        self,
        user_message: str,
        context: Dict[str, Any],
        chunk_size: int = 20
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI response in chunks
        
        Args:
            user_message: User's question
            context: Context (subject, mode, etc.)
            chunk_size: Number of tokens per chunk
        
        Yields:
            Chunks of the response as they're generated
            
        CRITICAL: Every chunk is sanitized to prevent internal trace leaks.
        """
        try:
            # Generate full response (in future, this would call streaming API)
            response = await self.ai_service.generate_response(
                user_message,
                context
            )
            
            # SANITIZE: Get content and sanitize BEFORE chunking
            content = response.get("response", "")
            content = _sanitize_streaming_chunk(content)
            
            words = content.split()
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                
                # SANITIZE each chunk as extra safety
                chunk = _sanitize_streaming_chunk(chunk)
                
                # Skip empty chunks
                if not chunk.strip():
                    continue
                
                # Format as SSE (Server-Sent Events)
                yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                
                # Small delay to simulate streaming
                await asyncio.sleep(0.05)
            
            # Send done signal
            yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    async def stream_with_cache(
        self,
        user_message: str,
        user_id: str,
        context: Dict[str, Any],
        cache_service
    ) -> AsyncGenerator[str, None]:
        """
        Stream response with cache check
        
        If cached, stream the cached response
        If not cached, generate and stream, then cache
        
        CRITICAL: Every chunk is sanitized to prevent internal trace leaks.
        """
        try:
            # Check cache first
            cached = await cache_service.get_cached_response(
                user_message,
                user_id,
                context
            )
            
            if cached:
                # SANITIZE: Sanitize cached content before streaming
                content = cached.get("response", "")
                content = _sanitize_streaming_chunk(content)
                words = content.split()
                
                for i in range(0, len(words), 30):  # Larger chunks for cached
                    chunk = " ".join(words[i:i + 30])
                    chunk = _sanitize_streaming_chunk(chunk)
                    
                    # Skip empty chunks
                    if not chunk.strip():
                        continue
                    
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False, 'cached': True})}\n\n"
                    await asyncio.sleep(0.02)  # Faster streaming for cached
                
                yield f"data: {json.dumps({'chunk': '', 'done': True, 'cached': True})}\n\n"
            else:
                # Generate and stream new response (already sanitized in stream_response)
                response_chunks = []
                
                async for chunk_data in self.stream_response(user_message, context):
                    response_chunks.append(chunk_data)
                    yield chunk_data
                
                # Cache the full response (store sanitized version)
                full_response = "".join([
                    json.loads(chunk.replace("data: ", "").strip()).get("chunk", "")
                    for chunk in response_chunks
                    if "chunk" in chunk
                ])
                
                await cache_service.cache_response(
                    user_message,
                    user_id,
                    {"response": full_response},
                    context
                )
                
        except Exception as e:
            logger.error(f"Streaming with cache error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"


def create_sse_response(generator: AsyncGenerator):
    """
    Create Server-Sent Events response for FastAPI
    
    Usage:
        return StreamingResponse(
            create_sse_response(stream_generator),
            media_type="text/event-stream"
        )
    """
    async def event_generator():
        try:
            async for chunk in generator:
                yield chunk
        except asyncio.CancelledError:
            logger.info("Client disconnected from stream")
        except Exception as e:
            logger.error(f"Stream generator error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return event_generator()
