"""
AI Streaming Response Service
Enables incremental token streaming for faster perceived latency
"""
import asyncio
import logging
from typing import AsyncGenerator, Optional, Dict, Any
import json

logger = logging.getLogger(__name__)


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
        """
        try:
            # Generate full response (in future, this would call streaming API)
            response = await self.ai_service.generate_response(
                user_message,
                context
            )
            
            # Simulate streaming by breaking response into chunks
            content = response.get("response", "")
            words = content.split()
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                
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
        """
        try:
            # Check cache first
            cached = await cache_service.get_cached_response(
                user_message,
                user_id,
                context
            )
            
            if cached:
                # Stream cached response faster
                content = cached.get("response", "")
                words = content.split()
                
                for i in range(0, len(words), 30):  # Larger chunks for cached
                    chunk = " ".join(words[i:i + 30])
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False, 'cached': True})}\n\n"
                    await asyncio.sleep(0.02)  # Faster streaming for cached
                
                yield f"data: {json.dumps({'chunk': '', 'done': True, 'cached': True})}\n\n"
            else:
                # Generate and stream new response
                response_chunks = []
                
                async for chunk_data in self.stream_response(user_message, context):
                    response_chunks.append(chunk_data)
                    yield chunk_data
                
                # Cache the full response
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
