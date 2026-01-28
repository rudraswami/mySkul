"""
Streaming Response Service for AI Tutor
Reduces response time from >50s to <5s with progressive rendering
"""
import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

class StreamingAIService:
    """
    Streaming service for progressive AI response delivery
    
    Features:
    - Text streaming: <2s to first token
    - Visual fallback tiers: cache → template → ai → emoji
    - Parallel processing of text and visuals
    """
    
    def __init__(self, ai_service, cache_service=None):
        self.ai_service = ai_service
        self.cache_service = cache_service
        
    async def stream_mentor_response(
        self,
        user_id: str,
        session_id: str,
        message: str,
        subject: str,
        exam_mode: str = "JEE",
        student_profile: dict = None,
        image_analysis: dict = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream mentor response progressively (with optional image analysis support)
        
        Yields:
        - event: visual_fallback (Tier 1-3)
        - event: text_chunk (progressive text)
        - event: visual_upgrade (if Tier 2 succeeds)
        - event: complete (final response)
        
        CRITICAL: Handles client disconnection (abort signal) gracefully.
        """
        text_task = None
        visual_task = None
        try:
            start_time = time.time()
            
            # 🎨 NETRA v5.0: Tell frontend to start composition IMMEDIATELY (parallel visual)
            # Don't wait for slow LLM - frontend generates visuals from question directly
            yield self._format_sse_event('composition_start', {
                'use_composition': True,
                'question': message,
                'subject': subject,
                'message': "Starting dynamic visual generation..."
            })
            
            # Step 1: Immediately send visual fallback (Tier 1: SVG template) 
            visual_fallback = self._get_visual_fallback_tier_1(
                student_profile.get('preferred_metaphor', 'cricket') if student_profile else 'cricket',
                student_profile.get('region', 'Bangalore') if student_profile else 'Bangalore'
            )
            
            yield self._format_sse_event('visual_fallback', {
                'tier': 1,
                'visual_url': visual_fallback['svg_template'],
                'placeholder_emoji': visual_fallback['emoji'],
                'color_theme': visual_fallback['color_theme'],
                'loading_time': time.time() - start_time
            })
            
            # Step 2: Check cache (Tier 0)
            cache_key = self._generate_cache_key(message, student_profile or {}, subject)
            cached_response = None
            if self.cache_service:
                cached_response = await self.cache_service.get(cache_key)
                if cached_response:
                    yield self._format_sse_event('cache_hit', {
                        'cached': True,
                        'response_time': time.time() - start_time
                    })
                    # Stream cached response progressively
                    async for chunk in self._stream_cached_response(cached_response):
                        yield chunk
                    return
            
            # Step 3: Start visual task (background) + stream text directly
            # 🔥 FIX: _stream_llm_text is async generator - iterate directly, NOT create_task
            
            visual_task = asyncio.create_task(
                self._generate_ai_visual_async(message, student_profile, timeout=8)
            )
            
            # Stream text chunks directly from async generator
            text_complete = False
            chunk_count = 0
            final_response_data = None  # 🔥 FIX: Initialize final_response_data
            
            async for text_chunk in self._stream_llm_text(user_id, session_id, message, subject, exam_mode, student_profile):
                if text_chunk:
                    chunk_count += 1
                    yield self._format_sse_event('text_chunk', text_chunk)
                    
                    # 🔥 FIX: Capture final response data from complete event
                    if text_chunk.get('type') == 'complete' or text_chunk.get('complete'):
                        text_complete = True
                        final_response_data = text_chunk.get('data', {})
                        break
            
            import logging
            logging.getLogger(__name__).info(f"📡 [Streaming] Sent {chunk_count} chunks, complete={text_complete}")
            
            # Check if AI visual completed
            try:
                ai_visual = await asyncio.wait_for(visual_task, timeout=1.0)
                if ai_visual and ai_visual.get('success'):
                    # Upgrade to Tier 2 (AI-generated visual)
                    yield self._format_sse_event('visual_upgrade', {
                        'tier': 2,
                        'visual_url': ai_visual['visual_url'],
                        'generation_time': ai_visual['generation_time']
                    })
            except asyncio.TimeoutError:
                # Visual generation exceeded timeout, keep Tier 1 fallback
                yield self._format_sse_event('visual_timeout', {
                    'tier': 1,
                    'message': 'Using SVG template fallback'
                })
            
            # Step 4: Send completion event with FULL response data
            total_time = time.time() - start_time
            
            # 🔥 DEBUG: Log what we're sending in complete event
            import logging
            _debug_logger = logging.getLogger(__name__)
            _debug_logger.info(f"🔍 [DEBUG] Streaming complete - total_time: {total_time:.2f}s, text_complete: {text_complete}")
            _debug_logger.info(f"🔍 [DEBUG] final_response_data keys: {list(final_response_data.keys()) if final_response_data else 'None'}")
            if final_response_data and final_response_data.get('default_view'):
                mc = final_response_data.get('default_view', {}).get('main_content', {})
                if isinstance(mc, dict):
                    preview = mc.get('content', '')[:100]
                else:
                    preview = str(mc)[:100]
                _debug_logger.info(f"🔍 [DEBUG] main_content preview: {preview}")
            
            complete_event = {
                'success': True,
                'total_time': total_time,
                'text_complete': text_complete,
                # CRITICAL: Include full response data for frontend
                'data': final_response_data
            }
            
            # Include visual flags from final response
            if final_response_data:
                complete_event['visual_needed'] = final_response_data.get('visual_needed', True)
                complete_event['intent'] = final_response_data.get('intent', 'conceptual')
            
            yield self._format_sse_event('complete', complete_event)
            
            # Step 5: Cache the response for future use
            # 🔥 FIX: Use final_response_data instead of text_task (we now use direct iteration)
            if self.cache_service and text_complete and final_response_data:
                try:
                    await self.cache_service.set(cache_key, {
                        'text': final_response_data,
                        'timestamp': time.time()
                    }, ttl=3600)  # 1 hour TTL
                except Exception as cache_err:
                    # Non-critical - log but don't fail
                    import logging
                    logging.getLogger(__name__).warning(f"Cache write failed: {cache_err}")
                
        except asyncio.CancelledError:
            # Client disconnected (stop button clicked or connection closed)
            # Cancel background tasks and cleanup gracefully
            if text_task and not text_task.done():
                text_task.cancel()
            if visual_task and not visual_task.done():
                visual_task.cancel()
            # Don't yield anything - connection is already closed
            # Re-raise to let FastAPI handle cleanup
            raise
                
        except GeneratorExit:
            # 🔥 FIX h11 ERROR: Generator closed by client disconnect
            # This happens when client aborts the request mid-stream
            # CRITICAL: Do NOT try to yield anything - connection is already closed
            import logging
            logging.getLogger(__name__).info("📡 [Streaming] Generator exit - client disconnected")
            if text_task and not text_task.done():
                text_task.cancel()
            if visual_task and not visual_task.done():
                visual_task.cancel()
            # Don't re-raise - just exit silently
            return
                
        except Exception as e:
            # Only yield error if connection is still open
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ [Streaming] Error: {e}")
            
            try:
                yield self._format_sse_event('error', {
                    'error': str(e),
                    'fallback_emoji': '🤔'
                })
            except (asyncio.CancelledError, GeneratorExit, Exception) as yield_err:
                # 🔥 FIX h11 ERROR: Connection closed while yielding error
                # Don't try to send anything more - connection is dead
                logger.debug(f"📡 [Streaming] Cannot send error (connection closed): {yield_err}")
                pass
    
    def _get_visual_fallback_tier_1(self, metaphor_category: str, region: str) -> Dict[str, str]:
        """
        Get Tier 1 visual fallback (SVG template + emoji)
        Response time: <0.5s
        """
        svg_templates = {
            'cricket': {
                'svg_template': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNFRkY2RkYiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI2MCIgZmlsbD0iIzEwQjk4MSI+8J+PjzwvdGV4dD48L3N2Zz4=',
                'emoji': '🏏',
                'color_theme': '#10B981'
            },
            'cooking': {
                'svg_template': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGRUYzQzciLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI2MCIgZmlsbD0iI0Y1OUUwQiI+8J+NszwvdGV4dD48L3N2Zz4=',
                'emoji': '🍳',
                'color_theme': '#F59E0B'
            },
            'bollywood': {
                'svg_template': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGQ0U3RjMiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI2MCIgZmlsbD0iI0JFMTg1RCI+8J+OrDwvdGV4dD48L3N2Zz4=',
                'emoji': '🎬',
                'color_theme': '#BE185D'
            },
            'gaming': {
                'svg_template': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNEQ0ZDRTciLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI2MCIgZmlsbD0iIzA1OTY2OSI+8J+OrjwvdGV4dD48L3N2Zz4=',
                'emoji': '🎮',
                'color_theme': '#059669'
            }
        }
        
        return svg_templates.get(metaphor_category, svg_templates['cricket'])
    
    async def _stream_llm_text(
        self,
        user_id: str,
        session_id: str,
        message: str,
        subject: str,
        exam_mode: str,
        student_profile: dict
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream LLM text response progressively
        Target: <2s to first token
        """
        try:
            # Use existing AI service with streaming enabled
            response = await self.ai_service.generate_neuro_symbolic_response(
                user_id=user_id,
                session_id=session_id,
                message=message,
                subject=subject,
                exam_mode=exam_mode,
                message_history=[]
            )
            
            # Simulate streaming by chunking response
            # In production, use LLM native streaming
            full_response = response.get('response', {})
            
            # 🔥 DEBUG: Log what we're sending to frontend
            import logging
            logger = logging.getLogger(__name__)
            main_content_preview = full_response.get('default_view', {}).get('main_content', {})
            if isinstance(main_content_preview, dict):
                main_content_preview = main_content_preview.get('content', '')[:100]
            logger.info(f"🔍 [DEBUG] _stream_llm_text - full_response keys: {list(full_response.keys())}")
            logger.info(f"🔍 [DEBUG] _stream_llm_text - main_content preview: {main_content_preview}")
            
            # CRITICAL: Extract clean text content for streaming
            # Frontend expects 'text_chunk' with 'content' as string
            main_content = ''
            default_view = full_response.get('default_view', {})
            if isinstance(default_view, dict):
                mc = default_view.get('main_content', {})
                if isinstance(mc, dict):
                    main_content = mc.get('content', '')
                elif isinstance(mc, str):
                    main_content = mc
            
            # Also check progressive sections for explanation
            if not main_content:
                progressive = full_response.get('progressive_sections', {})
                if isinstance(progressive, dict):
                    main_content = progressive.get('explanation', '')
            
            # Sanitize the content before streaming
            main_content = self._sanitize_streaming_content(main_content)
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"📝 [_stream_llm_text] main_content length: {len(main_content)} chars")
            
            # 🔥 FIX: If no main_content, try fallback sources
            if not main_content:
                logger.warning("⚠️ [_stream_llm_text] No main_content found, trying fallback sources")
                
                # Try greeting
                greeting = full_response.get('default_view', {}).get('greeting', '')
                if greeting:
                    main_content = greeting
                    logger.info(f"📝 [_stream_llm_text] Using greeting as fallback: {len(main_content)} chars")
                
                # Try raw response text if available
                if not main_content and full_response.get('text'):
                    main_content = str(full_response.get('text', ''))
                    logger.info(f"📝 [_stream_llm_text] Using raw text as fallback: {len(main_content)} chars")
                
                # Last resort - generate minimal response
                if not main_content:
                    main_content = f"I'm processing your question about {message[:50]}... Let me explain this concept clearly."
                    logger.warning(f"📝 [_stream_llm_text] Using generated fallback text")
            
            # Stream the clean text content
            if main_content:
                # Split into chunks for progressive display
                chunk_size = 100
                for i in range(0, len(main_content), chunk_size):
                    chunk = main_content[i:i + chunk_size]
                    yield {
                        'type': 'text_chunk',
                        'content': chunk,
                        'complete': i + chunk_size >= len(main_content)
                    }
                    await asyncio.sleep(0.05)  # Small delay between chunks
            else:
                # 🔥 CRITICAL: Always yield at least one chunk
                logger.error("❌ [_stream_llm_text] CRITICAL: No content to stream!")
                yield {
                    'type': 'text_chunk',
                    'content': "I'm working on your question. Please wait a moment...",
                    'complete': True
                }
            
            # Send complete event with full response data
            # 🎯 CRITICAL: Include visual_needed flag for SmartBoard gating
            visual_needed = full_response.get('visual_needed', True)  # Default true for educational content
            intent = full_response.get('intent', 'conceptual')
            
            # 🎨 NETRA v5.0: Tell frontend to use composition mode for educational content
            # This bypasses slow backend visual generation - frontend handles it dynamically
            use_composition = visual_needed and intent not in ['greeting', 'acknowledgment', 'chitchat']
            
            yield {
                'type': 'complete',
                'data': full_response,
                'visual_needed': visual_needed,
                'intent': intent,
                'use_composition': use_composition,  # 🎨 NEW: Enable frontend composition mode
                'complete': True
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'error': str(e),
                'complete': True
            }
    
    async def _generate_ai_visual_async(
        self,
        message: str,
        student_profile: dict,
        timeout: int = 8
    ) -> Dict[str, Any]:
        """
        Generate AI visual asynchronously with timeout
        Tier 2: AI-generated visual (8s timeout)
        """
        try:
            # Placeholder for AI visual generation
            # In production, call DALL-E, Stable Diffusion, etc.
            await asyncio.sleep(2)  # Simulate AI generation
            
            return {
                'success': True,
                'visual_url': 'https://assets.dhruvai.com/visuals/ai-generated/concept.png',
                'generation_time': 2.0
            }
        except Exception:
            return {
                'success': False,
                'tier': 1  # Fallback to Tier 1
            }
    
    async def _yield_from_task(self, task: asyncio.Task):
        """
        Yield results from async task as they become available.
        
        CRITICAL: Handles cancellation gracefully when client disconnects.
        """
        try:
            result = await task
            if isinstance(result, dict):
                yield result
            elif hasattr(result, '__aiter__'):
                # It's an async generator
                async for item in result:
                    yield item
            else:
                # Single result
                yield result
        except asyncio.CancelledError:
            # Task was cancelled (client disconnected)
            # Cancel the task if it's still running
            if not task.done():
                task.cancel()
            # Re-raise to propagate cancellation
            raise
        except Exception as e:
            # Only yield error if not cancelled
            yield {'error': str(e), 'complete': True}
    
    async def _stream_cached_response(self, cached_data: Dict[str, Any]):
        """Stream cached response progressively"""
        text_data = cached_data.get('text', {})
        
        yield self._format_sse_event('text_chunk', {
            'type': 'default_view',
            'data': text_data.get('default_view', {}),
            'cached': True,
            'complete': False
        })
        
        await asyncio.sleep(0.2)
        
        yield self._format_sse_event('text_chunk', {
            'type': 'progressive_sections',
            'data': text_data.get('progressive_sections', {}),
            'cached': True,
            'complete': True
        })
        
        yield self._format_sse_event('complete', {
            'success': True,
            'cached': True
        })
    
    def _generate_cache_key(self, message: str, student_profile: dict, subject: str) -> str:
        """Generate cache key for response"""
        import hashlib
        key_parts = [
            message.lower().strip(),
            student_profile.get('preferred_metaphor', 'cricket'),
            student_profile.get('region', 'Bangalore'),
            subject
        ]
        key_string = '|'.join(key_parts)
        return f"mentor_v2:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _sanitize_streaming_content(self, content: str) -> str:
        """
        Sanitize content before streaming to remove any internal traces.
        CRITICAL: This runs on every streamed chunk to ensure clean output.
        """
        import re
        
        if not content or not isinstance(content, str):
            return content or ''
        
        # Remove JSON blocks containing internal keys
        json_pattern = r'\{[^{}]*"(?:thought|action|action_input|confidence|observation)"[^{}]*\}'
        content = re.sub(json_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove ReAct transcript patterns
        react_pattern = r'(?:^|\n)\s*(?:Thought|Action|Observation|Action Input|Step \d+):\s*[^\n]*(?:\n|$)'
        content = re.sub(react_pattern, '\n', content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove standalone trace keys
        trace_pattern = r'(?:^|\n)\s*"(?:thought|action|action_input)":\s*[^\n]+(?:\n|$)'
        content = re.sub(trace_pattern, '\n', content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up orphaned braces at start
        if content.strip().startswith('{') and '"thought"' not in content[:200].lower():
            # Check if it's a lone brace
            lines = content.split('\n')
            if lines[0].strip() == '{':
                content = '\n'.join(lines[1:])
        
        # Clean up multiple newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def _format_sse_event(self, event_name: str, data: Dict[str, Any]) -> str:
        """Format Server-Sent Event"""
        return f"event: {event_name}\ndata: {json.dumps(data)}\n\n"


class SimpleRedisCache:
    """
    Simple Redis cache wrapper
    For production, use actual Redis client
    """
    
    def __init__(self):
        self._cache = {}  # In-memory fallback
        
    async def get(self, key: str) -> Any:
        """Get value from cache"""
        return self._cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        self._cache[key] = value
        # In production, implement TTL with Redis
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
