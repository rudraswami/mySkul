"""
AI Unified Router - Clean, Single Pipeline
==========================================
Replaces the fragmented ai.py with a unified, adaptive AI Tutor.

Key Changes:
1. Single LLM call (no dual Professor+Mentor)
2. Adaptive response structure based on intent
3. Natural markdown output (no rigid JSON)
4. Integrated visual engine V2
5. Full conversation context (10 messages, not 5)
"""

import os
import logging
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

from models.core import User
from services.unified_subscription_service import UnifiedSubscriptionService, FeatureName
from services.response_composer import ResponseComposer
from services.conversation_state import ConversationStateManager
from services.vision_analyzer import analyze_student_image
from dependencies import get_current_user, get_database, get_unified_subscription_service

# Router instance
router = APIRouter(prefix="/ai", tags=["ai-unified"])


class UnifiedAIRequest(BaseModel):
    """Request model for unified AI endpoint"""
    message: str = Field(..., min_length=1, max_length=10000)
    subject: Optional[str] = None
    session_id: Optional[str] = None
    exam_mode: str = Field(default="JEE")
    image_url: Optional[str] = None  # Base64 or URL for image analysis


class UnifiedAIResponse(BaseModel):
    """Response model for unified AI endpoint"""
    response: Dict[str, Any]
    visual_data: Optional[Dict[str, Any]] = None
    detected_subject: str
    generation_time: float
    intent: str
    context_used: bool


@router.post("/unified", response_model=UnifiedAIResponse)
async def generate_unified_response(
    request: UnifiedAIRequest,
    user: User = Depends(get_current_user),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service),
    db = Depends(get_database)
):
    """
    Unified AI Tutor Endpoint - Single, Adaptive Pipeline
    
    Features:
    - Single LLM call with adaptive prompts
    - Intent-based response structure
    - Visual integration when relevant
    - Full conversation context
    - Natural markdown output
    
    Replaces: /neuro-symbolic with cleaner architecture
    """
    try:
        # Check subscription access
        access_result = await sub_service.check_feature_access(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            requested_amount=1
        )
        
        if not access_result.allowed:
            raise HTTPException(
                status_code=402,
                detail=access_result.to_dict()
            )
        
        # Handle image upload if present
        contextual_message = request.message
        image_analysis = None
        
        if request.image_url:
            logger.info(f"📷 Image uploaded - analyzing with GPT-4 Vision")
            try:
                image_analysis = await analyze_student_image(
                    image_data=request.image_url,
                    question=request.message,
                    subject_hint=request.subject
                )
                
                extracted_info = image_analysis.get('extracted_text', '')
                if extracted_info:
                    contextual_message = f"""IMAGE CONTENT:
{extracted_info}

STUDENT'S QUESTION: {request.message}

Answer based on the image content above. Be direct and accurate."""
                    
            except Exception as e:
                logger.error(f"❌ Image analysis failed: {e}")
        
        # Get message history (increased to 10 from 5)
        message_history = []
        if request.session_id:
            try:
                cursor = db.chat_messages.find({
                    "session_id": request.session_id,
                    "user_id": user.user_id
                }).sort("timestamp", -1).limit(10)
                
                message_history = await cursor.to_list(length=10)
                message_history.reverse()  # Oldest first
            except Exception as e:
                logger.warning(f"Failed to get message history: {e}")
        
        # Initialize ResponseComposer
        emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
        composer = ResponseComposer(db, emergent_llm_key)
        
        # Generate response using unified pipeline
        result = await composer.generate_response(
            user_id=user.user_id,
            session_id=request.session_id or f"temp_{user.user_id}",
            question=contextual_message,
            subject=request.subject,
            exam_mode=request.exam_mode,
            message_history=message_history
        )
        
        # Track usage
        await sub_service.track_feature_use(user.user_id, FeatureName.AI_MENTOR.value, 1)
        
        # Save message to session
        try:
            message_id = str(uuid.uuid4())
            await db.chat_messages.insert_one({
                "message_id": message_id,
                "session_id": request.session_id or f"temp_{user.user_id}",
                "user_id": user.user_id,
                "user_message": request.message,
                "ai_response": result["response"],
                "visual_data": result.get("visual_data"),
                "intent": result.get("intent_detected"),
                "subject": result.get("detected_subject"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.warning(f"Failed to save message: {e}")
        
        return UnifiedAIResponse(
            response=result["response"],
            visual_data=result.get("visual_data"),
            detected_subject=result.get("detected_subject", "General"),
            generation_time=result.get("generation_time", 0),
            intent=result.get("intent_detected", "explanation"),
            context_used=result.get("context_used", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unified AI error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unified/stream")
async def stream_unified_response(
    request: UnifiedAIRequest,
    user: User = Depends(get_current_user),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service),
    db = Depends(get_database)
):
    """
    Streaming version of unified AI endpoint.
    Returns Server-Sent Events for real-time response.
    """
    try:
        # Check subscription access
        access_result = await sub_service.check_feature_access(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            requested_amount=1
        )
        
        if not access_result.allowed:
            raise HTTPException(
                status_code=402,
                detail=access_result.to_dict()
            )
        
        async def event_generator():
            """Generate SSE events for streaming response"""
            try:
                # Get message history
                message_history = []
                if request.session_id:
                    try:
                        cursor = db.chat_messages.find({
                            "session_id": request.session_id,
                            "user_id": user.user_id
                        }).sort("timestamp", -1).limit(10)
                        message_history = await cursor.to_list(length=10)
                        message_history.reverse()
                    except Exception:
                        pass
                
                # Initialize ResponseComposer
                emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
                composer = ResponseComposer(db, emergent_llm_key)
                
                # Generate response
                result = await composer.generate_response(
                    user_id=user.user_id,
                    session_id=request.session_id or f"temp_{user.user_id}",
                    question=request.message,
                    subject=request.subject,
                    exam_mode=request.exam_mode,
                    message_history=message_history
                )
                
                # Stream the response content
                content = result["response"]["default_view"]["main_content"]["content"]
                
                # Send visual data first if available
                if result.get("visual_data"):
                    yield {
                        "event": "visual",
                        "data": str(result["visual_data"])
                    }
                
                # Stream text in chunks
                chunk_size = 50  # Characters per chunk
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i+chunk_size]
                    yield {
                        "event": "text",
                        "data": chunk
                    }
                    await asyncio.sleep(0.02)  # Small delay for streaming effect
                
                # Send completion event
                yield {
                    "event": "complete",
                    "data": str({
                        "intent": result.get("intent_detected"),
                        "subject": result.get("detected_subject"),
                        "generation_time": result.get("generation_time")
                    })
                }
                
                # Track usage
                await sub_service.track_feature_use(user.user_id, FeatureName.AI_MENTOR.value, 1)
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield {
                    "event": "error",
                    "data": str(e)
                }
        
        return EventSourceResponse(event_generator())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Streaming setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FAST-PATH ENDPOINTS (Greetings, Simple Queries)
# ============================================================================

@router.post("/quick")
async def quick_response(
    request: UnifiedAIRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Fast-path for simple queries (greetings, acknowledgments).
    No subscription check, minimal processing.
    """
    message_lower = request.message.lower().strip()
    
    # Fast greeting responses
    greetings = {
        'hi': "Hey! 👋 What would you like to learn today?",
        'hello': "Hello! 🎓 Ready to explore some concepts?",
        'hey': "Hey there! 💡 What's on your mind?",
        'namaste': "Namaste! 🙏 How can I help you today?",
        'thanks': "You're welcome! Feel free to ask more questions! 😊",
        'thank you': "Happy to help! Keep learning! 🚀",
        'ok': "Great! What's next? 📚",
        'okay': "Perfect! Let me know if you have more questions! ✨"
    }
    
    if message_lower in greetings:
        return {
            "response": {
                "default_view": {
                    "main_content": {
                        "content": greetings[message_lower],
                        "type": "greeting"
                    }
                },
                "intent": "greeting"
            },
            "generation_time": 0.01
        }
    
    # Not a simple query, redirect to full endpoint
    raise HTTPException(
        status_code=400,
        detail="Use /unified for complex queries"
    )


# ============================================================================
# CONTEXT ENDPOINTS
# ============================================================================

@router.get("/context/{session_id}")
async def get_conversation_context(
    session_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get conversation context for a session.
    Useful for debugging and frontend state management.
    """
    state_manager = ConversationStateManager(db)
    
    state = await state_manager.get_state(user.user_id, session_id)
    
    return {
        "session_id": session_id,
        "state": state
    }


@router.delete("/context/{session_id}")
async def clear_conversation_context(
    session_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Clear conversation context for a session.
    Useful for starting fresh within same session.
    """
    state_manager = ConversationStateManager(db)
    
    await state_manager.clear_state(user.user_id, session_id)
    
    return {"status": "cleared", "session_id": session_id}


@router.get("/progress")
async def get_learning_progress(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get overall learning progress for user.
    Topics covered, session count, etc.
    """
    state_manager = ConversationStateManager(db)
    
    progress = await state_manager.get_learning_progress(user.user_id)
    
    return progress



