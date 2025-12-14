"""
Streaming AI Response Endpoint
Sends responses progressively like ChatGPT, not all at once
"""
import logging
import json
import asyncio
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from models.core import User
from dependencies import get_current_user, get_database
from utils.streaming_cleanup import safe_streaming_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/stream", tags=["AI Streaming"])


class StreamingRequest(BaseModel):
    message: str
    session_id: str
    subject: str = "General"
    exam_mode: Optional[str] = None  # Will be resolved dynamically


async def generate_streaming_response(
    message: str,
    session_id: str,
    subject: str,
    user: User,
    db: Any
) -> str:
    """
    Generator that yields response chunks progressively
    
    Format:
    data: {"type": "start", "metadata": {...}}
    data: {"type": "greeting", "text": "Hey! Let me help..."}
    data: {"type": "chunk", "text": "Force is..."}
    data: {"type": "section", "section_type": "main", "title": "The Cool Part"}
    data: {"type": "chunk", "text": "more content..."}
    data: {"type": "complete"}
    """
    try:
        # Import AI service
        from services.ai_service import AIService
        from agents.response_adapter import ResponseAdapter
        import os
        
        # Initialize AI service
        emergent_llm_key = os.environ.get('OPENAI_API_KEY')
        ai_service = AIService(db, emergent_llm_key=emergent_llm_key)
        
        # Send start signal with metadata
        yield f"data: {json.dumps({'type': 'start', 'metadata': {'subject': subject, 'timestamp': str(asyncio.get_event_loop().time())}})}\n\n"
        
        # Get full response from AI service (we'll chunk it)
        # In future, integrate with streaming LLM APIs
        from agents.supervisor import SupervisorAgent
        
        supervisor = SupervisorAgent(config={"emergent_llm_key": emergent_llm_key})
        
        # Resolve exam mode dynamically
        exam_mode = await resolve_exam_mode(
            request_exam_mode=None,  # Not in this flow
            user_id=user.user_id,
            db_client=db
        )
        
        # Build context
        agentic_context = {
            "subject": subject,
            "session_id": session_id,
            "user_id": user.user_id,
            "exam_mode": exam_mode,
            "student_profile": {
                "name": user.full_name.split()[0] if user.full_name else "",
                "level": "class_12",
                "interests": ["cricket", "gaming"],
                "board": "CBSE"
            }
        }
        
        # Get agentic response
        agentic_response = await supervisor.run(message, agentic_context)
        
        # Convert to neuro-symbolic format
        result = ResponseAdapter.adapt_agentic_to_neuro_symbolic(
            agentic_response=agentic_response,
            query=message,
            subject=subject,
            intent=agentic_response.get('intent'),
            user_id=user.user_id,
            student_profile=agentic_context.get('student_profile')
        )
        
        # Extract components
        default_view = result['response']['default_view']
        progressive_sections = result['response'].get('progressive_sections', {})
        template_metadata = result['response'].get('template_metadata', {})
        
        # ========== USE CONTENT CHUNKER FOR STRUCTURED SECTIONS ==========
        from services.content_chunker import ContentChunker, format_for_streaming
        
        mentor_content = agentic_response.get('mentor', {}).get('content', '')
        professor_content = agentic_response.get('professor', {}).get('content', '')
        
        # Chunk content into structured sections
        chunked_sections = ContentChunker.chunk_response(
            mentor_content=mentor_content,
            professor_content=professor_content,
            subject=subject,
            question=message
        )
        
        # Format for streaming
        stream_sections = format_for_streaming(chunked_sections)
        
        # Stream each section progressively
        for section_data in stream_sections:
            section_type = section_data['type']
            content = section_data['content']
            
            # Send section start signal
            yield f"data: {json.dumps({'type': 'section_start', 'section_type': section_type})}\n\n"
            await asyncio.sleep(0.1)
            
            # Stream content in chunks (word by word for typing effect)
            words = content.split(' ')
            chunk_size = 3  # words per chunk
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i+chunk_size]
                chunk_text = ' '.join(chunk_words)
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk_text + ' ', 'section': section_type})}\n\n"
                await asyncio.sleep(0.04)  # Faster typing for better UX
            
            # Send section complete signal
            yield f"data: {json.dumps({'type': 'section_complete', 'section_type': section_type})}\n\n"
            await asyncio.sleep(0.2)  # Pause between sections
        
        
        # Send complete signal
        yield f"data: {json.dumps({'type': 'complete', 'metadata': template_metadata})}\n\n"
        
    except asyncio.CancelledError:
        # Client disconnected - cleanup gracefully
        logger.warning(f"Stream cancelled for user {user.user_id}")
        # Don't yield error - connection is already closed
        
    except Exception as e:
        logger.error(f"❌ Streaming generation error: {e}", exc_info=True)
        try:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        except:
            pass  # Connection might be closed
            
    finally:
        # Ensure cleanup happens
        logger.info(f"Streaming cleanup for user {user.user_id}")


@router.post("/generate")
async def stream_ai_response(
    request: StreamingRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Stream AI response progressively with proper cleanup.
    
    Returns Server-Sent Events (SSE) stream
    """
    # Generate unique stream ID for tracking
    stream_id = f"stream_{user.user_id}_{uuid.uuid4().hex[:8]}"
    
    # Wrap generator with safety features
    safe_generator = safe_streaming_generator(
        generate_streaming_response(
            message=request.message,
            session_id=request.session_id,
            subject=request.subject,
            user=user,
            db=db
        ),
        stream_id=stream_id,
        timeout=120.0  # 2 minute timeout
    )
    
    return StreamingResponse(
        safe_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "X-Stream-ID": stream_id  # For debugging
        }
    )

