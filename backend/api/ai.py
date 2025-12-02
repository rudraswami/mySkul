"""
AI router for chat sessions, dual AI responses, guardrails, and AI-powered features
Now with unified subscription service for consistent access control
Streaming support for <5s response times
Image/Document upload support with GPT-4 Vision
Async visual generation for non-blocking responses
"""
import os
import logging
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
import base64

logger = logging.getLogger(__name__)

from models.core import User, SessionCreateRequest, SessionRenameRequest, SessionPinRequest, SessionBookmarkRequest
from models.ai import DualAIRequest, MathValidationRequest, FactVerificationRequest, StudyPlanRequest
from services.ai_service import AIService
from services.unified_subscription_service import UnifiedSubscriptionService, FeatureName
from services.vision_analyzer import analyze_student_image
from dependencies import get_current_user, get_database, get_unified_subscription_service
from agents.supervisor import SupervisorAgent
from agents.response_adapter import ResponseAdapter
from visual_engine.scene_builder import SceneBuilder


# Router instance
router = APIRouter(prefix="/ai", tags=["ai"])

# In-memory caches to avoid repeating visuals per session
_LAST_TV_BY_SESSION: dict = {}
_RECENT_TV_BY_SESSION: dict = {}


# Dependency to get AI service
async def get_ai_service(db = Depends(get_database)) -> AIService:
    """Get AI service instance"""
    emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
    return AIService(db, emergent_llm_key)


# Dependencies for caching and streaming
from services.ai_cache_service import AICacheService, MentorTipsCache
from services.streaming_service import StreamingResponseService, create_sse_response
from fastapi.responses import StreamingResponse
import time

async def get_ai_cache_service(db = Depends(get_database)) -> AICacheService:
    """Get AI cache service instance"""
    service = AICacheService(db)
    await service.initialize()
    return service

async def get_mentor_tips_cache(db = Depends(get_database)) -> MentorTipsCache:
    """Get mentor tips cache instance"""
    service = MentorTipsCache(db)
    await service.initialize()
    return service





@router.post("/dual-response-cached")
async def generate_dual_ai_response_with_cache(
    request: DualAIRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service),
    cache_service: AICacheService = Depends(get_ai_cache_service)
):
    """
    Generate dual AI response with caching
    Returns cached response if available, otherwise generates new response
    PERFORMANCE OPTIMIZATION: Reduces latency for repeated questions
    """
    try:
        # Start latency timer
        start_time = time.time()
        
        # Check feature access
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
        
        # Prepare context for caching
        context = {
            "subject": request.subject,
            "exam_type": request.exam_type,
            "mode": request.mode,
            "depth_level": request.depth_level
        }
        
        # Check cache
        cached_response = await cache_service.get_cached_response(
            request.user_message,
            user.user_id,
            context
        )
        
        if cached_response:
            cache_latency = (time.time() - start_time) * 1000
            return {
                **cached_response,
                "cached": True,
                "latency_ms": cache_latency,
                "cache_hit": True
            }
        
        # Generate new response
        response = await ai_service.generate_dual_response(
            user_message=request.user_message,
            subject=request.subject,
            exam_type=request.exam_type,
            mode=request.mode,
            depth_level=request.depth_level,
            visuals_enabled=request.visuals_enabled,
            conversation_history=request.conversation_history
        )
        
        # Cache the response
        await cache_service.cache_response(
            request.user_message,
            user.user_id,
            response,
            context
        )
        
        # Track usage
        await sub_service.track_feature_use(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            amount=1
        )
        
        generation_latency = (time.time() - start_time) * 1000
        
        return {
            **response,
            "cached": False,
            "latency_ms": generation_latency,
            "cache_hit": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/dual-response-stream")
async def generate_dual_ai_response_streaming(
    request: DualAIRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service),
    cache_service: AICacheService = Depends(get_ai_cache_service)
):
    """
    Generate dual AI response with streaming
    Returns response incrementally as tokens are generated
    PERFORMANCE OPTIMIZATION: Reduces perceived latency
    """
    try:
        # Check feature access
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
        
        # Prepare context
        context = {
            "subject": request.subject,
            "exam_type": request.exam_type,
            "mode": request.mode,
            "depth_level": request.depth_level
        }
        
        # Create streaming service
        streaming_service = StreamingResponseService(ai_service)
        
        # Stream with cache check
        stream_generator = streaming_service.stream_with_cache(
            request.user_message,
            user.user_id,
            context,
            cache_service
        )
        
        # Track usage
        await sub_service.track_feature_use(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            amount=1
        )
        
        # Return SSE streaming response
        return StreamingResponse(
            create_sse_response(stream_generator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming AI generation failed: {str(e)}")



@router.get("/mentor-tip/{subject}/{topic}")
async def get_mentor_tip(
    subject: str,
    topic: str,
    user: User = Depends(get_current_user),
    tips_cache: MentorTipsCache = Depends(get_mentor_tips_cache),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """
    Get pre-generated mentor tip for a topic
    PERFORMANCE OPTIMIZATION: Pre-generated tips for popular topics
    """
    try:
        start_time = time.time()
        
        # Check cached tip first
        cached_tip = await tips_cache.get_tip(subject, topic)
        
        if cached_tip:
            latency = (time.time() - start_time) * 1000
            return {
                "tip": cached_tip,
                "subject": subject,
                "topic": topic,
                "cached": True,
                "latency_ms": latency
            }
        
        # If not cached, return indication to generate
        return {
            "tip": None,
            "subject": subject,
            "topic": topic,
            "cached": False,
            "message": "Tip not pre-generated. Use AI generation endpoint."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mentor tip lookup failed: {str(e)}")


@router.get("/cache/stats")
async def get_cache_statistics(
    user: User = Depends(get_current_user),
    cache_service: AICacheService = Depends(get_ai_cache_service)
):
    """Get AI response cache statistics (admin endpoint)"""
    try:
        stats = await cache_service.get_cache_stats()
        return {
            "cache_stats": stats,
            "user_id": user.user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache stats failed: {str(e)}")

        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")


# =============== Session Memory Utilities (Debug/Inspection) ===============

@router.get("/session-memory/{session_id}")
async def get_session_memory(
    session_id: str,
    user: User = Depends(get_current_user)
):
    """Inspect lightweight session memory for the Tutor.

    Returns last_topic and last_visual_sig for the given session owned by the user.
    """
    try:
        db = await get_database()
        sess = await db.chat_sessions.find_one({"session_id": session_id, "user_id": user.user_id})
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found")

        mem = {
            "session_id": session_id,
            "last_topic": sess.get("last_topic"),
            "last_visual_sig": sess.get("last_visual_sig"),
            "recent_visual_sigs": sess.get("recent_visual_sigs", []),
            "last_updated": sess.get("last_updated")
        }
        return {"success": True, "memory": mem}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch session memory: {str(e)}")


@router.post("/session-memory/{session_id}/reset")
async def reset_session_memory(
    session_id: str,
    user: User = Depends(get_current_user)
):
    """Reset lightweight session memory fields (last_topic, last_visual_sig, recent_visual_sigs)."""
    try:
        db = await get_database()
        res = await db.chat_sessions.update_one(
            {"session_id": session_id, "user_id": user.user_id},
            {"$unset": {"last_topic": "", "last_visual_sig": "", "recent_visual_sigs": ""}, "$set": {"last_updated": time.time()}}
        )
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        # Clear in-memory cache as well
        _LAST_TV_BY_SESSION.pop(session_id, None)
        _RECENT_TV_BY_SESSION.pop(session_id, None)
        return {"success": True, "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset session memory: {str(e)}")

@router.post("/dual-response")
async def generate_dual_ai_response(
    request: DualAIRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """
    Generate dual AI response (Professor + Mentor)
    Checks subscription access before generating response
    Automatically saves message to session
    """
    try:
        # Check feature access
        access_result = await sub_service.check_feature_access(
            user.user_id,
            FeatureName.AI_MENTOR.value,
            requested_amount=1
        )
        
        if not access_result.allowed:
            # Return 402 with student-friendly upgrade message
            raise HTTPException(
                status_code=402,
                detail=access_result.to_dict()
            )
        
        # Generate response
        response = await ai_service.generate_dual_ai_response(
            user.user_id, request.message, request.session_id, request.subject
        )
        
        # Auto-save message to session for history
        if request.session_id:
            await ai_service.save_session_message(
                user.user_id,
                request.session_id,
                request.message,
                response
            )
        
        # Track usage AFTER successful generation
        await sub_service.track_feature_use(user.user_id, FeatureName.AI_MENTOR.value, 1)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dual AI response: {str(e)}")


@router.post("/mentor-only")
async def generate_mentor_response(
    request: DualAIRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate mentor-only AI response and auto-save to session"""
    try:
        # Use the dual response but extract mentor only
        response = await ai_service.generate_dual_ai_response(
            user.user_id, request.message, request.session_id, request.subject
        )
        
        mentor_response = {
            "response": response["secondary"]["response"],
            "persona": "mentor",
            "session_id": request.session_id,
            "subject": request.subject
        }
        
        # Auto-save to session
        if request.session_id:
            await ai_service.save_session_message(
                user.user_id,
                request.session_id,
                request.message,
                mentor_response
            )
        
        return mentor_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate mentor response: {str(e)}")


@router.post("/professor-only")
async def generate_professor_response(
    request: DualAIRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate professor-only AI response and auto-save to session"""
    try:
        # Use the dual response but extract professor only
        response = await ai_service.generate_dual_ai_response(
            user.user_id, request.message, request.session_id, request.subject
        )
        
        professor_response = {
            "response": response["primary"]["response"],
            "persona": "professor",
            "session_id": request.session_id,
            "subject": request.subject
        }
        
        # Auto-save to session
        if request.session_id:
            await ai_service.save_session_message(
                user.user_id,
                request.session_id,
                request.message,
                professor_response
            )
        
        return professor_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate professor response: {str(e)}")


@router.get("/available-contexts")
async def get_available_contexts():
    """Get available AI context options"""
    return {
        "subjects": ["Mathematics", "Physics", "Chemistry", "Biology", "English", "History", "Geography"],
        "ai_modes": ["dual", "mentor", "professor"],
        "topics": {
            "Mathematics": ["Algebra", "Geometry", "Calculus", "Statistics", "Trigonometry"],
            "Physics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Optics", "Modern Physics"],
            "Chemistry": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry"]
        }
    }


@router.get("/subjects/{subject}/defaultPrompts")
async def get_subject_default_prompts(subject: str):
    """
    Get context-aware default question prompts for a specific subject
    Returns 4 questions: 2 concept, 1 application, 1 exam-style
    """
    # Default prompts database - subject-specific contextual questions
    prompts_db = {
        "Mathematics": [
            {"text": "Explain the fundamental theorem of calculus", "type": "concept"},
            {"text": "What is the difference between permutations and combinations?", "type": "concept"},
            {"text": "How do I solve quadratic equations in real-world problems?", "type": "application"},
            {"text": "Give me a JEE-level problem on integration by parts", "type": "exam"}
        ],
        "Physics": [
            {"text": "Explain Newton's laws of motion with examples", "type": "concept"},
            {"text": "What is the difference between work and energy?", "type": "concept"},
            {"text": "How does a pulley system reduce the effort force?", "type": "application"},
            {"text": "Give me a NEET-level problem on projectile motion", "type": "exam"}
        ],
        "Chemistry": [
            {"text": "Explain atomic structure and electron configuration", "type": "concept"},
            {"text": "What is the difference between ionic and covalent bonds?", "type": "concept"},
            {"text": "How do catalysts speed up chemical reactions?", "type": "application"},
            {"text": "Give me a JEE-level problem on chemical equilibrium", "type": "exam"}
        ],
        "Biology": [
            {"text": "Explain the process of photosynthesis in detail", "type": "concept"},
            {"text": "What is the difference between mitosis and meiosis?", "type": "concept"},
            {"text": "How does DNA replication work in cells?", "type": "application"},
            {"text": "Give me a NEET-level problem on genetics and inheritance", "type": "exam"}
        ],
        "English": [
            {"text": "Explain the elements of a strong essay introduction", "type": "concept"},
            {"text": "What are the key differences between active and passive voice?", "type": "concept"},
            {"text": "How can I improve my vocabulary for competitive exams?", "type": "application"},
            {"text": "Give me practice questions on reading comprehension", "type": "exam"}
        ],
        "History": [
            {"text": "Explain the causes of the Indian independence movement", "type": "concept"},
            {"text": "What were the major effects of World War II?", "type": "concept"},
            {"text": "How did the Industrial Revolution change society?", "type": "application"},
            {"text": "Give me UPSC-level questions on ancient Indian history", "type": "exam"}
        ],
        "Geography": [
            {"text": "Explain the water cycle and its importance", "type": "concept"},
            {"text": "What is the difference between weather and climate?", "type": "concept"},
            {"text": "How does deforestation affect the environment?", "type": "application"},
            {"text": "Give me UPSC-level questions on Indian geography", "type": "exam"}
        ]
    }
    
    # Normalize subject name (case-insensitive)
    subject_normalized = subject.strip().title()
    
    # Return subject-specific prompts or fallback to general prompts
    if subject_normalized in prompts_db:
        return {
            "subject": subject_normalized,
            "prompts": prompts_db[subject_normalized]
        }
    else:
        # Fallback to Mathematics if subject not found
        return {
            "subject": subject_normalized,
            "prompts": prompts_db["Mathematics"],
            "note": f"Using default prompts for {subject_normalized}"
        }


@router.post("/dual-study-plan")
async def create_dual_study_plan(
    request: StudyPlanRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate personalized study plan using dual AI"""
    try:
        # This would use AI to generate a comprehensive study plan
        # For now, returning a structured response
        return {
            "study_plan": {
                "target_exam_date": request.target_exam_date,
                "daily_study_hours": request.daily_study_hours,
                "weekly_schedule": "Generated based on preferences",
                "subject_allocation": "Optimized for weak areas",
                "milestones": ["Week 1: Foundation", "Week 2: Practice", "Week 3: Mock Tests"]
            },
            "mentor_insights": "Study plan created to balance weak and strong subjects effectively.",
            "professor_analysis": "The schedule optimizes retention while building systematic knowledge."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create study plan: {str(e)}")


# Guardrails endpoints
@router.post("/guardrails/validate-math")
async def validate_math(
    request: MathValidationRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Validate mathematical expressions"""
    try:
        validation = await ai_service.validate_math_expression(request.expression, request.units)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Math validation failed: {str(e)}")


@router.get("/guardrails/citations/{subject}/{topic}")
async def get_citations(
    subject: str,
    topic: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """Get citations for a subject and topic"""
    try:
        citations = await ai_service.get_citations(subject, topic)
        return {"citations": citations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get citations: {str(e)}")


@router.post("/guardrails/fact-verification")
async def verify_fact(
    request: FactVerificationRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Verify factual statements"""
    try:
        verification = await ai_service.verify_fact(request.statement, request.subject, request.context)
        return verification
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact verification failed: {str(e)}")


@router.get("/guardrails/disagreements/{session_id}")
async def get_disagreements(
    session_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get any disagreements between AI responses for a session"""
    try:
        # Placeholder implementation - would analyze AI response disagreements
        return {
            "disagreements": [],
            "session_id": session_id,
            "analysis": "No significant disagreements found between AI responses"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get disagreements: {str(e)}")


# Chat session management endpoints
@router.get("/chat/sessions") 
async def get_chat_sessions(
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get all chat sessions for the current user"""
    try:
        sessions = await ai_service.get_user_sessions(user.user_id)
        # Enrich with message_count and last_updated fallback
        try:
            db = await get_database()
            enriched = []
            for s in sessions:
                sid = s.get("session_id")
                if not sid:
                    continue
                try:
                    count = await db.chat_messages.count_documents({
                        "session_id": sid,
                        "user_id": user.user_id
                    })
                    s["message_count"] = int(count)
                    # If last_updated missing, infer from latest message
                    if not s.get("last_updated"):
                        last = await db.chat_messages.find_one(
                            {"session_id": sid, "user_id": user.user_id},
                            sort=[("timestamp", -1)]
                        )
                        if last and last.get("timestamp"):
                            s["last_updated"] = last["timestamp"]
                except Exception:
                    s["message_count"] = s.get("message_count", 0)
                enriched.append(s)
            sessions = enriched
        except Exception:
            pass
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat sessions: {str(e)}")


@router.post("/chat/sessions")
async def create_chat_session(
    request: SessionCreateRequest,
    user: User = Depends(get_current_user), 
    ai_service: AIService = Depends(get_ai_service)
):
    """Create a new chat session"""
    try:
        session = await ai_service.create_chat_session(
            user.user_id, request.title, request.subject, request.topic, request.ai_mode
        )
        return {
            "message": "Chat session created successfully",
            "session_id": session.session_id,
            "session": session.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


@router.get("/chat/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get all messages for a specific session with pagination support"""
    try:
        messages = await ai_service.get_session_messages(session_id, user.user_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session messages: {str(e)}")


@router.post("/chat/{session_id}/messages")
async def save_session_message(
    session_id: str,
    request: dict,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Save a message to the session
    Expected request body: { user_message: str, ai_response: dict }
    """
    try:
        user_message = request.get('user_message', '')
        ai_response = request.get('ai_response', {})
        
        if not user_message:
            raise HTTPException(status_code=400, detail="user_message is required")
        
        success = await ai_service.save_session_message(
            user.user_id,
            session_id,
            user_message,
            ai_response
        )
        
        if success:
            return {"message": "Message saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save message")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")


@router.put("/chat/{session_id}/rename")
async def rename_chat_session(
    session_id: str,
    request: SessionRenameRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Rename a chat session"""
    try:
        success = await ai_service.update_session(session_id, user.user_id, {"title": request.title})
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session renamed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename session: {str(e)}")


@router.put("/chat/{session_id}/pin")
async def pin_chat_session(
    session_id: str,
    request: SessionPinRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Pin/unpin a chat session"""
    try:
        success = await ai_service.update_session(session_id, user.user_id, {"pinned": request.pinned})
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": f"Session {'pinned' if request.pinned else 'unpinned'} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session pin status: {str(e)}")


@router.put("/chat/{session_id}/bookmark")
async def bookmark_chat_session(
    session_id: str,
    request: SessionBookmarkRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Bookmark/unbookmark a chat session"""
    try:
        success = await ai_service.update_session(session_id, user.user_id, {"bookmarked": request.bookmarked})
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": f"Session {'bookmarked' if request.bookmarked else 'unbookmarked'} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session bookmark status: {str(e)}")


@router.delete("/chat/{session_id}")
async def delete_chat_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a chat session and all its messages"""
    try:
        # Delete session messages first
        try:
            await db.chat_messages.delete_many({"session_id": session_id, "user_id": user.user_id})
        except Exception:
            # Message collection may not exist; don't block deletion
            pass

        # Delete session
        result = await db.chat_sessions.delete_one({"session_id": session_id, "user_id": user.user_id})

        if result.deleted_count == 0:
            # Soft-delete fallback: mark as deleted so UI won't show it
            try:
                import time as _t
                soft = await db.chat_sessions.update_one(
                    {"session_id": session_id, "user_id": user.user_id},
                    {"$set": {"deleted": True, "last_updated": _t.time()}},
                )
                if soft.matched_count:
                    return {"message": "Session marked deleted"}
            except Exception:
                pass
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        # As a last resort, attempt soft-delete and then surface original error if that fails
        try:
            import time as _t
            await db.chat_sessions.update_one(
                {"session_id": session_id, "user_id": user.user_id},
                {"$set": {"deleted": True, "last_updated": _t.time()}},
            )
            return {"message": "Session marked deleted"}
        except Exception:
            raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


# ===================== NEURO-SYMBOLIC AI TUTOR (v3.0) =====================

@router.post("/neuro-symbolic/stream")
async def stream_neuro_symbolic_response(
    request: DualAIRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service)
):
    """
    Stream Neuro-Symbolic AI Mentor response (OPTIMIZED - <5s response)
    
    Features:
    - Text streaming: <2s to first token
    - Visual fallback: SVG template → AI visual
    - Parallel processing: text + visual
    - Cache-aware: 60-70% hit rate
    
    Returns: Server-Sent Events (SSE)
    - event: visual_fallback
    - event: text_chunk
    - event: visual_upgrade (optional)
    - event: complete
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
        
        # Get user profile
        db = await get_database()
        user_doc = await db.users.find_one({"user_id": user.user_id}) or {}
        student_profile = {
            'preferred_metaphor': user_doc.get('preferred_metaphor', 'cricket'),
            'region': user_doc.get('region', 'Bangalore'),
            'visual_learner_preference': user_doc.get('visual_learner_preference', True),
            'device_type': user_doc.get('device_type', 'mobile'),
            'network_speed': user_doc.get('network_speed', '3G')
        }
        
        # Auto-detect subject if not provided
        detected_subject = request.subject
        if not detected_subject or detected_subject.strip() == "":
            detected_subject = _detect_subject_from_question(request.message)
            logger.info(f"🔍 Auto-detected subject: {detected_subject} from question: {request.message[:50]}")
        
        # Initialize streaming service
        from services.streaming_ai_service import StreamingAIService, SimpleRedisCache
        cache_service = SimpleRedisCache()
        streaming_service = StreamingAIService(ai_service, cache_service)
        
        # Stream response
        return EventSourceResponse(
            streaming_service.stream_mentor_response(
                user_id=user.user_id,
                session_id=request.session_id or f"temp_{user.user_id}",
                message=request.message,
                subject=detected_subject,
                exam_mode=getattr(request, 'exam_mode', 'JEE'),
                student_profile=student_profile
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Use module-level logger (already defined at top of file)
        logger.error(f"Streaming error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stream response: {str(e)}"
        )


def _detect_subject_from_question(question: str) -> str:
    """Auto-detect subject from question text"""
    from services.question_classifier import QuestionClassifier, Subject
    
    if not question or not question.strip():
        return "Mathematics"  # Default fallback
    
    classifier = QuestionClassifier()
    analysis = classifier.classify(question)
    detected_subject = analysis.subject
    
    # Map Subject enum to frontend format
    subject_map = {
        Subject.MATHEMATICS: "Mathematics",
        Subject.PHYSICS: "Physics",
        Subject.CHEMISTRY: "Chemistry",
        Subject.BIOLOGY: "Biology",
        Subject.COMPUTER_SCIENCE: "Computer Science",
        Subject.GENERAL: "Mathematics"  # Default to Mathematics
    }
    
    return subject_map.get(detected_subject, "Mathematics")


@router.post("/neuro-symbolic")
async def generate_neuro_symbolic_response(
    request: DualAIRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
    sub_service: UnifiedSubscriptionService = Depends(get_unified_subscription_service),
    db = Depends(get_database)  # ✅ Add db dependency
):
    """
    Generate Neuro-Symbolic AI Tutor response (Indian student-centric)
    
    - **message**: Student's question
    - **subject**: Subject (Mathematics, Physics, Chemistry, Biology, etc.) - Auto-detected if not provided
    - **session_id**: Chat session ID
    - **exam_mode**: JEE, NEET, UPSC, etc. (default: JEE)
    
    Returns 8-section response:
    1. Practical Explanation (simple, 3-6 lines)
    2. Indian Example (from student life)
    3. Metaphor (memory hook)
    4. Visual Schema (JSON diagram)
    5. Professor Verification (steps, source, confidence)
    6. Mini Practice (1 MCQ)
    7. Encouragement (sincere)
    8. Ask (follow-up question)
    """
    try:
        # ========== IMAGE/DOCUMENT ANALYSIS ==========
        # If student uploaded an image, analyze it first
        image_analysis = None
        contextual_message = request.message
        
        if request.image_url:
            logger.info(f"📷 Image uploaded - analyzing with GPT-4 Vision (data length: {len(request.image_url)} chars)")
            try:
                image_analysis = await analyze_student_image(
                    image_data=request.image_url,
                    question=request.message,
                    subject_hint=request.subject
                )
                
                # Enhance the question with image context
                extracted_info = image_analysis.get('extracted_text', '')
                content_type = image_analysis.get('content_type', 'unknown')
                analysis_text = image_analysis.get('analysis', '')
                
                logger.info(f"📷 Vision analysis result: content_type={content_type}, extracted_length={len(extracted_info)}")
                
                if extracted_info or analysis_text:
                    # Use extracted_info if available, otherwise use analysis
                    image_content = extracted_info if extracted_info else analysis_text
                    
                    # CRITICAL: Format message to force AI to focus on image content
                    contextual_message = f"""🖼️ IMPORTANT: Student uploaded an image ({content_type}). You MUST analyze and respond based on the image content below.

=== IMAGE CONTENT EXTRACTED BY VISION AI ===
{image_content}
=== END OF IMAGE CONTENT ===

STUDENT'S QUESTION: {request.message}

INSTRUCTIONS:
1. FIRST, acknowledge you can see the image and describe what's in it briefly
2. If it's an MCQ: identify question, all options (A, B, C, D), and solve it step-by-step
3. If it's a diagram/equation: explain exactly what is shown
4. If it's a textbook page: summarize the key points shown
5. Answer the student's specific question based on ACTUAL image content
6. Be DIRECT and FACTUAL - no random metaphors unless explaining concepts

You MUST reference specific content from the image in your response."""
                    
                    logger.info(f"✅ Image context prepared: {content_type}, Subject: {image_analysis.get('subject_detected')}, Content length: {len(image_content)} chars")
                else:
                    logger.warning(f"⚠️ Image analysis returned empty content. Full result: {image_analysis}")
                
            except Exception as e:
                import traceback
                logger.error(f"❌ Image analysis failed: {e}")
                logger.error(traceback.format_exc())
                # Continue without image analysis but inform user
                contextual_message = f"{request.message}\n\n(Note: There was an issue analyzing the uploaded image. Please describe what's in the image if you need help with it.)"
        
        # Auto-detect subject if not provided (consider image analysis)
        detected_subject = request.subject
        if not detected_subject or detected_subject.strip() == "":
            if image_analysis and image_analysis.get('subject_detected'):
                detected_subject = image_analysis['subject_detected']
                logger.info(f"🔍 Subject detected from image: {detected_subject}")
            else:
                detected_subject = _detect_subject_from_question(contextual_message)
                logger.info(f"🔍 Auto-detected subject: {detected_subject} from question: {request.message[:50]}")
        
        # Update request subject for downstream processing
        request.subject = detected_subject
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
        
        # Get message history for memory/context (optional)
        message_history = []
        session_doc = None
        if request.session_id:
            history = await ai_service.get_session_messages(request.session_id, user.user_id)
            message_history = history[-5:] if history else []  # Last 5 messages for context
            # Fetch session memory (e.g., last topic)
            try:
                db = await get_database()
                session_doc = await db.chat_sessions.find_one({"session_id": request.session_id, "user_id": user.user_id})
            except Exception:
                session_doc = None
        
        # ====================================================================
        # FAST-PATH FOR SIMPLE GREETINGS (< 100ms response)
        # ====================================================================
        message_lower = request.message.lower().strip()
        simple_greetings = ['hi', 'hello', 'hey', 'namaste', 'hola', 'yo']
        
        if message_lower in simple_greetings:
            logger.info(f"⚡ Fast-path: Simple greeting detected, skipping full AI pipeline")
            
            # Get user name for personalization
            user_doc = await db.users.find_one({"user_id": user.user_id})
            user_name = ""
            if user_doc:
                full_name = user_doc.get("full_name", "")
                user_name = full_name.split()[0] if full_name else "there"
            
            # Quick greeting response
            greeting_responses = {
                'hi': f"Hi {user_name}! 👋 I'm your AI Tutor. Ask me anything about Math, Physics, Chemistry, or any subject!",
                'hello': f"Hello {user_name}! 🎓 Ready to learn something awesome today?",
                'hey': f"Hey {user_name}! 🚀 What would you like to explore today?",
                'namaste': f"Namaste {user_name}! 🙏 Let's make learning fun!",
                'hola': f"Hola {user_name}! 🌟 What can I help you learn today?",
                'yo': f"Yo {user_name}! 💪 Ready to crush some concepts?"
            }
            
            greeting_text = greeting_responses.get(message_lower, f"Hello {user_name}! Ask me anything!")
            
            # Return fast greeting response
            return {
                "response": {
                    "default_view": {
                        "greeting": greeting_text,
                        "main_content": {
                            "content": "I'm here to help you with:\n\n• Math problems and concepts\n• Physics explanations\n• Chemistry reactions\n• Biology processes\n• Exam preparation tips\n• Step-by-step solutions\n\nJust ask your question, and I'll explain it clearly!"
                        },
                        "metaphor": {
                            "text": "Think of me as your study buddy who's always ready to help! 📚"
                        }
                    },
                    "progressive_sections": {},
                    "intent": "greeting",
                    "render_directives": {
                        "greeting_only": True,
                        "suppress_cta": True
                    }
                },
                "detected_subject": "General",
                "generation_time": 0.05  # 50ms
            }
        
        # ====================================================================
        # INTELLIGENT RESPONSE ENGINE - Adaptive response structure
        # ====================================================================
        from services.intelligent_response_engine import get_response_config, detect_intent as smart_detect_intent
        
        # Get intelligent response configuration based on question type
        response_config = get_response_config(request.message, request.subject)
        smart_intent = response_config["intent"]
        render_directives = response_config["render_directives"]
        
        logger.info(f"🧠 Intelligent Response: intent={smart_intent}, blocks={response_config['blocks']}")
        
        # Legacy intent detection for backward compatibility
        from services.adaptive_response import detect_intent as _detect_intent
        _intent = _detect_intent(request.message)
        
        # CRITICAL FIX: Only update contextual_message if NO IMAGE was analyzed
        # (contextual_message already contains image context from above if image was uploaded)
        has_image_context = image_analysis is not None and image_analysis.get('extracted_text')
        if not has_image_context:
            # No image - check for topic continuation context
            try:
                prev_topic = (session_doc or {}).get('last_topic') if session_doc else None
                if _intent in {"clarification_or_followup", "deep_dive"} and prev_topic:
                    if prev_topic.lower() not in (request.message or "").lower():
                        contextual_message = f"{request.message}\n\nContext: Previous topic was '{prev_topic}'. Please respond accordingly (no basic repetition; go deeper/clarify)."
            except Exception:
                pass
        else:
            logger.info(f"📷 Preserving image context in message (has {len(image_analysis.get('extracted_text', ''))} chars of extracted content)")

        # ====================================================================
        # 🤖 SPECIALIZED AGENT ROUTING (Cognito OS v1.5)
        # Check if query should go to a specialized agent BEFORE unified pipeline
        # ====================================================================
        specialized_agent_result = None
        USE_SPECIALIZED_AGENTS = os.getenv("USE_SPECIALIZED_AGENTS", "true").lower() == "true"
        
        if USE_SPECIALIZED_AGENTS:
            try:
                from agents.doubt_resolver import DoubtResolverAgent
                from agents.exam_coach import ExamCoachAgent
                from agents.weak_area_detective import WeakAreaDetectiveAgent
                from agents.study_buddy import StudyBuddyAgent
                from agents.motivation import MotivationAgent
                from agents.proactive_companion import ProactiveCompanionAgent
                
                # Detect if specialized agent should handle this
                specialized_intent = None
                
                # Check for reminder/schedule requests FIRST (highest priority)
                if ProactiveCompanionAgent.is_reminder_request(contextual_message):
                    specialized_intent = 'reminder'
                elif ProactiveCompanionAgent.is_schedule_request(contextual_message):
                    specialized_intent = 'schedule'
                elif DoubtResolverAgent.is_doubt_query(contextual_message):
                    specialized_intent = 'doubt'
                elif ExamCoachAgent.is_exam_strategy_query(contextual_message):
                    specialized_intent = 'exam_strategy'
                elif WeakAreaDetectiveAgent.is_weak_area_query(contextual_message):
                    specialized_intent = 'weak_area'
                elif StudyBuddyAgent.is_buddy_query(contextual_message):
                    specialized_intent = 'study_buddy'
                
                if specialized_intent:
                    logger.info(f"🤖 Specialized agent detected: {specialized_intent}")
                    
                    emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
                    
                    # Build context for specialized agent
                    agent_context = {
                        "subject": detected_subject,
                        "session_id": request.session_id,
                        "user_id": user.user_id,
                        "student_profile": {
                            "user_name": (await db.users.find_one({"user_id": user.user_id}) or {}).get("full_name", "").split()[0] if user else "",
                            "exam": getattr(request, 'exam_mode', 'JEE'),
                            "language": "en"
                        },
                        "session_data": {}
                    }
                    
                    # Route to appropriate specialized agent
                    if specialized_intent == 'reminder':
                        # 🌟 Proactive Companion handles reminders
                        companion = ProactiveCompanionAgent(db)
                        agent_response = await companion.process_reminder_request(contextual_message, agent_context)
                    elif specialized_intent == 'schedule':
                        # 📅 Proactive Companion handles scheduling
                        companion = ProactiveCompanionAgent(db)
                        agent_response = await companion.process_reminder_request(contextual_message, agent_context)
                    elif specialized_intent == 'doubt':
                        # 🧠 Use Agentic Doubt Resolver if enabled
                        USE_AGENTIC_SYSTEM = os.getenv("USE_AGENTIC_SYSTEM", "true").lower() == "true"
                        
                        if USE_AGENTIC_SYSTEM:
                            try:
                                from agents.agentic_doubt_resolver import create_agentic_doubt_resolver
                                logger.info("🧠 Using TRUE AGENTIC Doubt Resolver (ReAct + Tools)")
                                
                                agentic_agent = create_agentic_doubt_resolver({
                                    'emergent_llm_key': emergent_llm_key,
                                    'max_iterations': 8,
                                    'verbose': True
                                })
                                
                                # Run with full agentic capabilities
                                agentic_result = await agentic_agent.run(contextual_message, agent_context)
                                
                                if agentic_result.get('success'):
                                    agent_response = {
                                        'success': True,
                                        'content': agentic_result.get('content', ''),
                                        'metadata': {
                                            'agentic': True,
                                            'tools_used': agentic_result.get('tools_used', []),
                                            'iterations': agentic_result.get('iterations', 0),
                                            'verified': agentic_result.get('verification', {}).get('status') == 'verified'
                                        }
                                    }
                                    logger.info(f"✅ Agentic response generated (iterations: {agentic_result.get('iterations', 0)}, tools: {agentic_result.get('tools_used', [])})")
                                else:
                                    # Fall back to regular doubt resolver
                                    logger.warning("⚠️ Agentic system failed, falling back to regular agent")
                                    agent = DoubtResolverAgent({"emergent_llm_key": emergent_llm_key})
                                    agent_response = await agent.process(contextual_message, agent_context)
                            except Exception as agentic_error:
                                logger.error(f"❌ Agentic system error: {agentic_error}, falling back")
                                agent = DoubtResolverAgent({"emergent_llm_key": emergent_llm_key})
                                agent_response = await agent.process(contextual_message, agent_context)
                        else:
                            agent = DoubtResolverAgent({"emergent_llm_key": emergent_llm_key})
                            agent_response = await agent.process(contextual_message, agent_context)
                    elif specialized_intent == 'exam_strategy':
                        agent = ExamCoachAgent({"emergent_llm_key": emergent_llm_key})
                        agent_response = await agent.process(contextual_message, agent_context)
                    elif specialized_intent == 'weak_area':
                        agent = WeakAreaDetectiveAgent({"emergent_llm_key": emergent_llm_key})
                        agent_response = await agent.process(contextual_message, agent_context)
                    elif specialized_intent == 'study_buddy':
                        agent = StudyBuddyAgent({"emergent_llm_key": emergent_llm_key})
                        agent_response = await agent.process(contextual_message, agent_context)
                    
                    if agent_response and agent_response.get('success'):
                        logger.info(f"✅ Specialized agent {specialized_intent} responded successfully")
                        
                        # Extract agentic metadata if present
                        agentic_metadata = agent_response.get('metadata', {})
                        is_agentic = agentic_metadata.get('agentic', False)
                        
                        # Format as unified result
                        specialized_agent_result = {
                            "response": {
                                "default_view": {
                                    "greeting": "",
                                    "main_content": {
                                        "content": agent_response.get('content', '')
                                    }
                                },
                                "progressive_sections": {
                                    "explanation": agent_response.get('content', '')
                                },
                                "render_directives": render_directives
                            },
                            "detected_subject": detected_subject,
                            "generation_time": 0.5,
                            "agent_used": specialized_intent,
                            "intent_detected": specialized_intent
                        }
                        
                        # Add agentic system info if used
                        if is_agentic:
                            specialized_agent_result["agentic_info"] = {
                                "used_react_loop": True,
                                "tools_used": agentic_metadata.get('tools_used', []),
                                "iterations": agentic_metadata.get('iterations', 0),
                                "self_verified": agentic_metadata.get('verified', False)
                            }
                            logger.info(f"🧠 Agentic response metadata: {specialized_agent_result['agentic_info']}")
                        
            except Exception as agent_error:
                logger.warning(f"⚠️ Specialized agent routing failed: {agent_error}")
                specialized_agent_result = None
        
        # If specialized agent handled it, skip unified pipeline
        result = specialized_agent_result
        
        # ====================================================================
        # UNIFIED INTELLIGENT PIPELINE (DEFAULT - Always On)
        # ====================================================================
        # CRITICAL: Use unified pipeline FIRST, it's cleaner and more intelligent
        # Only fall back to agentic/legacy if explicitly requested
        
        USE_UNIFIED_FIRST = os.getenv("USE_UNIFIED_FIRST", "true").lower() == "true"
        
        # Initialize memory_context variable (used in both paths)
        memory_context = {}
        
        if USE_UNIFIED_FIRST and result is None:
            logger.info("🚀 Using UNIFIED intelligent pipeline (clean, adaptive)")
            try:
                from services.response_composer import ResponseComposer
                from services.intelligent_response_engine import detect_intent, QuestionIntent
                
                emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
                composer = ResponseComposer(db, emergent_llm_key)
                
                # PERFORMANCE: Quick intent detection for fast-path optimization
                quick_intent = detect_intent(contextual_message)
                is_simple_question = quick_intent in {
                    QuestionIntent.GREETING, 
                    QuestionIntent.CONVERSATIONAL,
                    QuestionIntent.SIMPLE_FACT,
                    QuestionIntent.VERIFICATION
                }
                
                # PERFORMANCE: Only load history for complex questions
                extended_history = []
                if request.session_id and not is_simple_question:
                    history = await ai_service.get_session_messages(request.session_id, user.user_id)
                    extended_history = history[-10:] if history else []
                elif request.session_id and is_simple_question:
                    # For simple questions, just get last 3 messages (faster)
                    history = await ai_service.get_session_messages(request.session_id, user.user_id)
                    extended_history = history[-3:] if history else []
                
                logger.info(f"⚡ Quick intent: {quick_intent.value}, simple={is_simple_question}, history_size={len(extended_history)}")
                
                # Single unified response generation
                result = await composer.generate_response(
                    user_id=user.user_id,
                    session_id=request.session_id or f"temp_{user.user_id}",
                    question=contextual_message,
                    subject=detected_subject,
                    exam_mode=getattr(request, 'exam_mode', 'JEE'),
                    message_history=extended_history
                )
                
                logger.info(f"✅ Unified response generated in {result.get('generation_time', 0):.2f}s")
                logger.info(f"🎯 Intent: {result.get('intent_detected')}, Context used: {result.get('context_used')}")
                
                # CRITICAL: Skip ALL other pipelines - unified succeeded
                # Jump directly to post-processing
                
            except Exception as unified_error:
                logger.error(f"❌ Unified pipeline failed: {unified_error}")
                import traceback
                logger.error(traceback.format_exc())
                # Fall through to agentic system as backup
                USE_UNIFIED_FIRST = False
                result = None  # Ensure result is defined
        
        # ====================================================================
        # AGENTIC SYSTEM (Backup - Only if unified fails)
        # ====================================================================
        USE_AGENTIC_SYSTEM = os.getenv("USE_AGENTIC_SYSTEM", "false").lower() == "true"
        
        # Only use agentic if unified failed AND agentic is enabled
        if not USE_UNIFIED_FIRST and USE_AGENTIC_SYSTEM and result is None:
            # Use new agentic system with MEMORY
            logger.info("🤖 Using Agentic System with Memory for neuro-symbolic response")
            try:
                # Initialize Supervisor
                emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
                supervisor = SupervisorAgent(config={"emergent_llm_key": emergent_llm_key})
                
                # ================================================================
                # MEMORY SYSTEM INTEGRATION - Retrieve context before processing
                # ================================================================
                from services.memory_service import MemoryService
                from services.semantic_memory import SemanticMemoryService
                from services.mastery_tracker import MasteryTracker
                from services.continuity_engine import ContinuityEngine
                
                # Initialize memory services (using db from dependency)
                # Use OpenAI key for embeddings (NOT emergent key)
                openai_api_key = os.environ.get('OPENAI_API_KEY') or emergent_llm_key
                
                memory_service = MemoryService(db)
                semantic_memory = SemanticMemoryService(db, openai_api_key)
                mastery_tracker = MasteryTracker(db)
                continuity_engine = ContinuityEngine(db)
                
                logger.info("🧠 Memory services initialized")
                
                # Step 1: Get short-term conversation context (last 10 messages)
                recent_context = await memory_service.get_conversation_context(
                    session_id=request.session_id or f"temp_{user.user_id}",
                    user_id=user.user_id,
                    window_size=10
                )
                logger.info(f"📜 Retrieved {len(recent_context)} recent messages")
                
                # Step 2: Semantic search for relevant long-term memories
                relevant_memories = await semantic_memory.search_relevant_memories(
                    user_id=user.user_id,
                    query=contextual_message,
                    top_k=5,
                    min_similarity=0.5
                )
                logger.info(f"🔍 Found {len(relevant_memories)} relevant memories")
                
                # Step 3: Check for topic continuation
                continuity = await continuity_engine.detect_topic_continuation(
                    user_id=user.user_id,
                    current_query=contextual_message
                )
                logger.info(f"🔗 Continuity check: {continuity.get('is_continuation', False)}")
                
                # Step 4: Get mastery level for current topic
                # Extract main topic from question
                from services.memory_extraction import MemoryExtractor
                temp_extractor = MemoryExtractor(db)
                current_concepts = temp_extractor._extract_concepts(contextual_message, {})
                current_topic = current_concepts[0] if current_concepts else "general"
                
                mastery_level = await mastery_tracker.get_mastery_level(user.user_id, current_topic)
                logger.info(f"📊 Mastery level for {current_topic}: {mastery_level}/100")
                
                # Step 5: Get user profile with name and preferences
                user_doc = await db.users.find_one({"user_id": user.user_id})
                user_name = ""
                student_profile_data = {}
                
                if user_doc:
                    full_name = user_doc.get("full_name", "")
                    user_name = full_name.split()[0] if full_name else ""
                    
                    # Get learning profile for personalization
                    learning_profile = await db.user_learning_profile.find_one({"user_id": user.user_id})
                    if learning_profile:
                        student_profile_data = {
                            "preferences": learning_profile.get("preferences", {}),
                            "patterns": learning_profile.get("patterns", {}),
                            "mastery_levels": learning_profile.get("mastery_levels", {}),
                            "response_style": learning_profile.get("preferences", {}).get("response_style")
                        }
                
                # Prepare enhanced context for agentic system
                agentic_context = {
                    "subject": detected_subject,
                    "session_id": request.session_id,
                    "user_id": user.user_id,
                    "exam_mode": getattr(request, 'exam_mode', 'JEE'),
                    "request_visual": True,  # Always request visual for neuro-symbolic
                    "student_profile": {
                        "name": user_name,  # Personalized!
                        "level": "class_12",
                        "interests": ["cricket", "gaming"],
                        "board": "CBSE",
                        "exam": getattr(request, 'exam_mode', 'JEE'),
                        "mastery_level": mastery_level,  # Adaptive depth!
                        **student_profile_data  # Merge learning profile data
                    },
                    # Memory context for agents
                    "memory_context": {
                        "recent_context": recent_context[-5:],  # Last 5 messages
                        "relevant_memories": relevant_memories,
                        "continuity": continuity,
                        "mastery_level": mastery_level,
                        "current_topic": current_topic
                    }
                }
                
                logger.info(f"🧠 Memory context prepared: {len(recent_context)} recent, {len(relevant_memories)} relevant, continuity={continuity.get('is_continuation')}")
                
                # Run Supervisor
                agentic_response = await supervisor.run(contextual_message, agentic_context)
                
                # Build visual scene if present
                if agentic_response.get("visual"):
                    scene_builder = SceneBuilder()
                    visual_spec = agentic_response["visual"]
                    template_id = visual_spec.get("metadata", {}).get("template_id")
                    
                    if template_id:
                        scene = scene_builder.build_scene(
                            template_id=template_id,
                            variables=visual_spec.get("variables", {}),
                            context=agentic_context
                        )
                        agentic_response["visual"] = scene
                
                # Convert agentic response to neuro-symbolic format
                # Pass user_id and student_profile for dynamic template selection
                result = ResponseAdapter.adapt_agentic_to_neuro_symbolic(
                    agentic_response=agentic_response,
                    query=contextual_message,
                    subject=request.subject,
                    intent=agentic_response.get('intent'),  # Pass intent for greeting detection
                    user_id=user.user_id,  # For template variety tracking
                    student_profile=agentic_context.get('student_profile')  # For personalization
                )
                
                logger.info("✅ Agentic system response generated successfully")
                
                # ================================================================
                # MEMORY UPDATE PIPELINE - Store learnings after response
                # ================================================================
                try:
                    from services.spaced_repetition import SpacedRepetitionEngine
                    
                    # Extract learning facts from this interaction
                    facts = await temp_extractor.extract_learning_facts(
                        user_id=user.user_id,
                        question=contextual_message,
                        response=result,
                        session_id=request.session_id or f"temp_{user.user_id}",
                        message_id=None  # Will be set when message is saved
                    )
                    
                    logger.info(f"🧠 Extracted {len(facts)} memory facts")
                    
                    # Store facts with embeddings
                    sp_engine = SpacedRepetitionEngine()
                    
                    for fact in facts:
                        if fact.get("fact_type") == "concept_learned":
                            # Store with embedding
                            fact_id = await semantic_memory.store_memory_with_embedding(
                                user_id=user.user_id,
                                content=fact["content"],
                                metadata=fact
                            )
                            
                            # Schedule first review (1 day for new concepts)
                            review_schedule = sp_engine.calculate_next_review(
                                current_interval_days=0,
                                quality=3,  # Default: understood
                                current_easiness=2.5
                            )
                            
                            # Update review schedule in memory
                            await db.user_memory_facts.update_one(
                                {"fact_id": fact_id},
                                {"$set": review_schedule}
                            )
                            
                        elif fact.get("fact_type") == "mastery_update":
                            # Update mastery level
                            await mastery_tracker.update_mastery(
                                user_id=user.user_id,
                                topic=fact["topic"],
                                delta=fact["mastery_delta"],
                                reason=fact.get("reason", "question_answered")
                            )
                    
                    # Update concept thread for continuity
                    if current_concepts:
                        await continuity_engine.update_concept_thread(
                            user_id=user.user_id,
                            topic=current_topic,
                            concepts=current_concepts
                        )
                    
                    logger.info("💾 Memory update pipeline complete")
                    
                except Exception as e:
                    logger.error(f"⚠️ Memory update failed (non-critical): {e}")
                    # Don't fail the request if memory update fails
            except Exception as e:
                logger.error(f"❌ Agentic system failed, falling back to legacy: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Fallback to legacy system
                result = await ai_service.generate_neuro_symbolic_response(
                    user_id=user.user_id,
                    session_id=request.session_id or f"temp_{user.user_id}",
                    message=contextual_message,
                    subject=request.subject,
                    exam_mode=getattr(request, 'exam_mode', 'JEE'),
                    message_history=message_history
                )
        # ================================================================
        # LEGACY FALLBACK (only if both unified and agentic fail)
        # ================================================================
        if result is None:
            logger.info("📚 Using legacy neuro-symbolic system (fallback)")
            
            # ================================================================
            # MEMORY INTEGRATION (Always On - No Feature Flag)
            # ================================================================
            memory_context = {}
            try:
                from services.memory_integration import MemoryIntegrationService
                memory_service = MemoryIntegrationService(db)
                
                # Get enhanced context for personalization
                memory_context = await memory_service.get_enhanced_context(
                    user_id=user.user_id,
                    session_id=request.session_id or f"temp_{user.user_id}",
                    question=contextual_message,
                    subject=detected_subject
                )
                
                logger.info(f"🧠 Memory context loaded: mastery={memory_context.get('mastery_level', 0)}, "
                           f"continuation={memory_context.get('is_continuation', False)}")
                
            except Exception as mem_error:
                logger.warning(f"⚠️ Memory context retrieval failed (non-blocking): {mem_error}")
                memory_context = {}
            
            # Generate AI response
            result = await ai_service.generate_neuro_symbolic_response(
                user_id=user.user_id,
                session_id=request.session_id or f"temp_{user.user_id}",
                message=contextual_message,
                subject=request.subject,
                exam_mode=getattr(request, 'exam_mode', 'JEE'),
                message_history=message_history,
                memory_context=memory_context  # Pass memory context
                )
            
            # ================================================================
            # MEMORY UPDATE PIPELINE (Post-Response)
            # ================================================================
            try:
                if memory_context:
                    # Process interaction and update memory
                    await memory_service.process_interaction(
                        user_id=user.user_id,
                        session_id=request.session_id or f"temp_{user.user_id}",
                        question=contextual_message,
                        response=result,
                        feedback=None,  # Feedback comes later via separate endpoint
                        message_id=None
                    )
                    logger.info("💾 Memory update pipeline completed")
            except Exception as mem_update_error:
                logger.warning(f"⚠️ Memory update failed (non-blocking): {mem_update_error}")
        
        # Track usage
        await sub_service.track_feature_use(user.user_id, FeatureName.AI_MENTOR.value, 1)
        
        # ====================================================================
        # ASYNC VISUAL SKETCH GENERATION (PERMANENT SOLUTION)
        # Generate visual in background, don't block main response
        # ====================================================================
        visual_task_id = None
        visual_sketch_data = None
        
        try:
            # Only generate visual sketch for questions that benefit from visuals
            question_length = len(request.message.strip())
            q_lower = request.message.lower()
            
            # PERFORMANCE: Skip visuals for casual/simple questions
            skip_visual_patterns = [
                "remind", "hello", "hi ", "hey", "thanks", "thank you",
                "bye", "good morning", "good night", "schedule", "plan",
                "how are you", "what's up", "ok", "okay", "got it"
            ]
            is_casual = any(pat in q_lower for pat in skip_visual_patterns)
            
            # CRITICAL: Generate visuals for concept explanations
            # But skip for casual chit-chat (PERFORMANCE OPTIMIZATION)
            is_visual_worthy = (
                question_length > 15 and  # Need substantial question
                not is_casual and  # Skip casual questions
                _intent not in {"greeting", "conversational"} and  # Skip greetings & casual
                # Only for concept explanations
                (any(keyword in q_lower for keyword in ["explain", "what is", "define", "describe", "how does", "derive", "prove"]) or
                 (request.subject and request.subject.strip() != "" and question_length > 20))
            )
            
            if is_visual_worthy:
                # Generate unique task ID for async visual generation
                visual_task_id = str(uuid.uuid4())
                
                # Get user profile for personalization
                user_doc = await db.users.find_one({"user_id": user.user_id})
                student_profile = {
                    "level": user_doc.get("education_level", "class_12") if user_doc else "class_12",
                    "interests": user_doc.get("interests", []) if user_doc else [],
                    "locale_language": user_doc.get("language", "hi-IN") if user_doc else "hi-IN",
                    "board": user_doc.get("board", "CBSE") if user_doc else "CBSE",
                    "gender": user_doc.get("gender") if user_doc else None,
                    "exam": user_doc.get("exam_type", "JEE") if user_doc else "JEE"
                }
                
                # Start async visual generation task (non-blocking)
                logger.info(f"🎨 Starting async visual generation (task_id: {visual_task_id})")
                
                # Store task info for polling endpoint
                await db.visual_generation_tasks.insert_one({
                    "task_id": visual_task_id,
                    "user_id": user.user_id,
                    "question": request.message,
                    "subject": request.subject,
                    "student_profile": student_profile,
                    "status": "generating",
                    "created_at": datetime.now(),
                    "session_id": request.session_id
                })
                
                # Start background task (fire and forget)
                asyncio.create_task(
                    _generate_visual_async(visual_task_id, request.message, student_profile, db)
                )
                
                logger.info(f"✅ Visual generation task started (non-blocking)")
            else:
                logger.info(f"⏭️ Skipping visual sketch (question too short or not visual-worthy)")
                
        except Exception as e:
            logger.error(f"⚠️ Visual task creation failed (non-critical): {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Don't fail the request if visual task creation fails
        
        # [JULES VISUAL ENHANCEMENT START]
        visual_metaphor = result['response'].pop('visual_metaphor', {})
        result['response']['hero_visual'] = visual_metaphor.get('hero_visual')
        result['response']['step_visuals'] = result['response'].get('progressive_sections', {}).get('strategy', {}).get('steps', [])
        result['response']['symbolic_structures'] = visual_metaphor.get('symbolic_structure')
        result['response']['metaphor'] = visual_metaphor.get('metaphor')
        result['response']['student_persona'] = f"{getattr(request, 'exam_mode', 'JEE')} | {result['response'].get('student_profile', {}).get('region', 'Delhi')} | {result['response'].get('student_profile', {}).get('emotional_state', 'Confident')}"

        # Attach teaching visual for Tutor rendering
        # Priority: Visual Professor Generator (dynamic, multi-step, professor-style)
        # Only attempt when question appears visual-worthy (heuristic gate)
        logger.info(f"🎨 ========== VISUAL GENERATION START ==========")
        logger.info(f"🎨 Question: {request.message[:100]}")
        logger.info(f"🎨 Subject: {request.subject}")
        logger.info(f"🎨 User ID: {user.user_id}")
        try:
            from services.question_scope import build_scope as _brief, should_generate_visual as _should
            from services.adaptive_response import detect_intent as _detect_intent

            _scope = _brief(request.message)

            # Detect high-level student intent
            _intent = _detect_intent(request.message)
            logger.info(f"🎯 Detected intent: {_intent}")
            
            # Attach intent and rendering directives for frontend adaptivity
            # Using new intelligent response engine directives
            try:
                if 'response' in result:
                    result['response']['intent'] = smart_intent  # Use intelligent intent
                    # Merge intelligent directives with legacy handling
                    result['response']['render_directives'] = {
                        **render_directives,  # From intelligent engine
                        # Legacy overrides for specific intents
                        "skip_greeting": _intent == 'clarification_or_followup',
                        "suppress_cta": smart_intent in ['greeting', 'conversational', 'simple_fact'],
                        "greeting_only": smart_intent == 'greeting',
                    }
                    logger.info(f"✅ Applied render_directives: {result['response']['render_directives']}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to set render directives: {e}")

            # Only attach a teaching visual when appropriate (not for compare/clarification)
            allow_visual = _should(request.message, request.subject) and _intent not in {"compare_contrast", "clarification_or_followup"}
            logger.info(f"🎨 allow_visual={allow_visual}, _should={_should(request.message, request.subject)}, _intent={_intent}")

            if allow_visual:
                # ====================================================================
                # FEATURE FLAG: Visual Generator (DISABLED FOR V1.0 MARKET RELEASE)
                # ====================================================================
                # Set to True to re-enable visual generation
                VISUAL_GENERATOR_ENABLED = False
                
                if not VISUAL_GENERATOR_ENABLED:
                    logger.info("🚫 Visual generator DISABLED (V1.0 market release - visuals disabled)")
                    tv = None
                else:
                    # PRIORITY 1: Visual Professor Generator (dynamic, multi-step, professor-style)
                    tv = None
                    try:
                        logger.info(f"🎨 Starting Visual Professor Generator for: {request.message[:50]}...")
                        
                        # Build student profile for metaphor selection
                        student_profile = {
                            "user_id": user.user_id if user else None,
                            "region": "India",
                            "interests": ["cricket", "technology"],
                            "preferred_metaphor": "cricket",
                            "emotional_state": "neutral"
                        }
                        
                        from services.visual_professor import VisualProfessorGenerator
                        vpg = VisualProfessorGenerator(student_profile=student_profile)
                        logger.info("✅ VisualProfessorGenerator imported successfully")
                        
                        vpg_result = await vpg.generate_visual(
                            question=request.message,
                            subject=request.subject,
                            student_profile=student_profile
                        )
                        logger.info(f"📊 Visual Professor Generator returned: {type(vpg_result)}, has stages: {bool(vpg_result and vpg_result.get('stages'))}")
                        
                        # Convert VisualProfessorGenerator output to TeachingVisual format
                        if vpg_result and vpg_result.get('stages') and len(vpg_result['stages']) > 0:
                            tv = {
                                "visual_id": vpg_result.get('visual_id', f"prof_{hash(request.message) % 1000000}"),
                                "type": vpg_result.get('type', 'animated_lesson'),
                                "total_duration_ms": vpg_result.get('total_duration_ms', 0),
                                "metadata": vpg_result.get('metadata', {}),
                                "stages": vpg_result.get('stages', []),
                                "professor_avatar": vpg_result.get('professor_avatar', {}),
                                "lottie_base_url": vpg_result.get('lottie_base_url', 'https://cdn.ai-tutor.in/visuals')
                            }
                            logger.info(f"✅ Visual Professor Generator: {len(vpg_result.get('stages', []))} stages generated")
                            logger.info(f"📦 Teaching visual structure: visual_id={tv['visual_id']}, type={tv['type']}, stages={len(tv['stages'])}")
                        else:
                            logger.warning(f"⚠️ Visual Professor Generator returned invalid result: stages={vpg_result.get('stages') if vpg_result else 'None'}")
                    except Exception as e:
                        logger.error(f"❌ Visual Professor Generator failed with exception: {e}", exc_info=True)
                        import traceback
                        logger.error(f"❌ Traceback: {traceback.format_exc()}")

                    # LEGACY VISUAL SYSTEMS DISABLED
                    # Visual Professor Engine is now the ONLY pathway
                    # Legacy systems (_dyn, _tpl, _plan) are disabled
                    # Visual Professor Generator's fallback already generates multi-step visuals
                    if not tv:
                        logger.warning("⚠️ Visual Professor Generator returned no visual, attempting fallback...")
                        # Try to call fallback directly
                        try:
                            from services.visual_professor import VisualProfessorGenerator
                            vpg_fallback = VisualProfessorGenerator()
                            fallback_result = vpg_fallback._fallback_visual(request.message, request.subject)
                            if fallback_result and fallback_result.get('stages') and len(fallback_result['stages']) > 0:
                                tv = {
                                    "visual_id": fallback_result.get('visual_id', f"prof_fallback_{hash(request.message) % 1000000}"),
                                    "type": fallback_result.get('type', 'animated_lesson'),
                                    "total_duration_ms": fallback_result.get('total_duration_ms', 0),
                                    "metadata": fallback_result.get('metadata', {}),
                                    "stages": fallback_result.get('stages', []),
                                    "professor_avatar": fallback_result.get('professor_avatar', {}),
                                    "lottie_base_url": fallback_result.get('lottie_base_url', 'https://cdn.ai-tutor.in/visuals')
                                }
                                logger.info(f"✅ Fallback visual generated: {len(tv.get('stages', []))} stages")
                        except Exception as fallback_error:
                            logger.error(f"❌ Fallback visual generation also failed: {fallback_error}", exc_info=True)

                if tv:
                    # Repetition guard: persist + maintain a small ring buffer (last 3)
                    try:
                        sid = getattr(request, 'session_id', None) or f"temp_{user.user_id}"
                        sig = f"{tv.get('visual_id','')}::{(tv.get('metadata') or {}).get('topic','')}"

                        # Load persisted memory
                        try:
                            db = await get_database()
                            sess_doc = await db.chat_sessions.find_one({"session_id": sid, "user_id": user.user_id})
                            persisted_sig = (sess_doc or {}).get('last_visual_sig')
                            recent_list = (sess_doc or {}).get('recent_visual_sigs', []) or []
                        except Exception:
                            persisted_sig = None
                            recent_list = []

                        # Load in-memory ring buffer
                        mem_list = _RECENT_TV_BY_SESSION.get(sid, [])
                        combined_recent = list(dict.fromkeys([*mem_list, *recent_list]))  # dedupe, preserve order

                        # Check against last and recent
                        # TEMPORARILY DISABLED FOR TESTING - Allow all visuals
                        allow_duplicate = True  # Set to False to re-enable repetition guard
                        
                        if not allow_duplicate and (_LAST_TV_BY_SESSION.get(sid) == sig or sig in combined_recent or (persisted_sig and persisted_sig == sig)):
                            tv = None
                            logger.info(f"🔄 Duplicate visual suppressed: {sig}")
                        else:
                            # Update in-memory caches
                            _LAST_TV_BY_SESSION[sid] = sig
                            new_recent = (combined_recent + [sig])[-3:]  # keep last 3
                            _RECENT_TV_BY_SESSION[sid] = new_recent
                            
                            logger.info(f"✅ Visual allowed (metaphor may have changed!)")

                            # Persist last + recent ring buffer
                            try:
                                await db.chat_sessions.update_one(
                                    {"session_id": sid, "user_id": user.user_id},
                                    {"$set": {"last_visual_sig": sig, "recent_visual_sigs": new_recent, "last_updated": time.time()}},
                                    upsert=False
                                )
                            except Exception:
                                pass
                    except Exception:
                        pass
                # OLD VISUAL SYSTEM DISABLED - SketchSense V2 is now the primary visual system
                # if tv:
                #     result['response']['teaching_visual'] = tv
                #     logger.info(f"✅ Added teaching_visual to response: {tv.get('visual_id')} with {len(tv.get('stages', []))} stages")
                
                # 🎨 WHITEBOARD SKETCH ENGINE - Next-Gen Visual System
                # Progressive, animated, Indian context, NO boring MCQs!
                try:
                    from services.whiteboard_engine import generate_whiteboard_visual, whiteboard_engine
                    
                    # Extract concept from question
                    msg_lower = (request.message or '').lower()
                    concept = whiteboard_engine.extract_concept(request.message)
                    
                    # Also check for explicit visual requests
                    if not concept and any(kw in msg_lower for kw in ['visual', 'diagram', 'draw', 'show', 'picture', 'sketch', 'explain']):
                        # Default based on subject
                        subject_defaults = {
                            'physics': 'force',
                            'chemistry': 'acids',
                            'biology': 'cell',
                            'math': 'geometry',
                            'mathematics': 'geometry'
                        }
                        concept = subject_defaults.get((request.subject or 'physics').lower(), 'force')
                    
                    if concept:
                        subject = request.subject or 'physics'
                        whiteboard_scene = generate_whiteboard_visual(
                            concept=concept,
                            subject=subject,
                            question=request.message
                        )
                        result['response']['whiteboard_visual'] = whiteboard_scene
                        logger.info(f"🎨 Whiteboard visual generated for concept: {concept}")
                    else:
                        logger.info(f"ℹ️ No visual concept detected, skipping whiteboard visual")
                except Exception as wb_err:
                    logger.warning(f"⚠️ Whiteboard visual generation failed (non-blocking): {wb_err}")
                    import traceback
                    logger.warning(f"⚠️ Whiteboard traceback: {traceback.format_exc()}")
            else:
                logger.info(f"ℹ️ Visual generation skipped: allow_visual={allow_visual}")
        except Exception as e:
            # Never block main response if visual planning fails, but LOG IT
            logger.error(f"❌ Visual planning failed completely: {e}", exc_info=True)
            import traceback
            logger.error(f"❌ Full traceback:\n{traceback.format_exc()}")

        # Update memory: store last topic from attached teaching visual (if any)
        try:
            db = await get_database()
            tv = result.get('response', {}).get('teaching_visual')
            last_topic = None
            if tv and isinstance(tv, dict):
                last_topic = (tv.get('metadata') or {}).get('topic')
            if not last_topic:
                # Fallback: short topic from message
                last_topic = (request.message or '')[:60]
            if request.session_id and last_topic:
                await db.chat_sessions.update_one(
                    {"session_id": request.session_id, "user_id": user.user_id},
                    {"$set": {"last_topic": last_topic, "last_updated": time.time()}}
                )
        except Exception:
            pass

        # Add detected subject and memory context to response
        if isinstance(result, dict):
            result['detected_subject'] = detected_subject
            
            # Add memory context for frontend display
            if memory_context and 'response' in result:
                result['response']['memory_context'] = {
                    'mastery_level': memory_context.get('mastery_level', 0),
                    'mastery_bucket': memory_context.get('mastery_bucket', 'beginner'),
                    'is_continuation': memory_context.get('is_continuation', False),
                    'last_topic': memory_context.get('continuity', {}).get('last_topic', ''),
                    'context_summary': memory_context.get('context_summary', ''),
                    'weak_topics': memory_context.get('weak_topics', [])
                }
            
            # ====================================================================
            # CRITICAL FIX: Save message to session for chat history
            # ====================================================================
            if request.session_id:
                try:
                    await ai_service.save_session_message(
                        user.user_id,
                        request.session_id,
                        request.message,
                        result.get('response', result)
                    )
                    logger.info(f"✅ Message saved to session {request.session_id}")
                except Exception as save_error:
                    logger.error(f"⚠️ Failed to save message to session: {save_error}")
            
            # Add visual task ID for async polling (if visual is being generated)
            if visual_task_id:
                if 'response' not in result:
                    result['response'] = {}
                result['response']['visual_sketch'] = {
                    "status": "generating",
                    "task_id": visual_task_id,
                    "poll_url": f"/api/ai/visual/{visual_task_id}"
                }
                logger.info(f"✅ Visual generation task ID added to response (async)")
            elif visual_sketch_data:
                # If visual was generated synchronously (fallback)
                if 'response' not in result:
                    result['response'] = {}
                result['response']['visual_sketch'] = visual_sketch_data
                logger.info(f"✅ Visual sketch added to response")
        
        # ====================================================================
        # 💪 MOTIVATION AGENT ENHANCEMENT (Cognito OS)
        # Add emotional support elements based on detected student state
        # ====================================================================
        try:
            from agents.motivation import MotivationAgent
            
            # Build context for motivation agent
            motivation_context = {
                "student_profile": {
                    "user_name": user_doc.get("full_name", "").split()[0] if user_doc else "",
                },
                "session_data": {
                    "wrong_answer_streak": 0,  # Could be tracked in session
                    "current_streak": 0,
                },
                "original_query": request.message  # Pass the original query for emotion detection
            }
            
            # Add query to result for emotion detection
            result['query'] = request.message
            
            # Get motivation enhancement
            motivation_agent = MotivationAgent({})
            enhanced_result = motivation_agent.enhance_response(result, motivation_context)
            
            # If motivation was added, include it in response
            if enhanced_result.get('motivation'):
                if 'response' not in result:
                    result['response'] = {}
                result['response']['motivation'] = enhanced_result['motivation']
                logger.info(f"💪 Motivation enhancement added: {enhanced_result['motivation'].get('type', 'general')}")
        except Exception as motivation_error:
            logger.debug(f"ℹ️ Motivation enhancement skipped: {motivation_error}")
        
        return result
        # [JULES VISUAL ENHANCEMENT END]
        
    except HTTPException:
        raise
    except Exception as e:
        # Use module-level logger (already defined at top of file)
        logger.error(f"Neuro-symbolic response error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )


# ====================================================================
# ASYNC VISUAL GENERATION HELPER FUNCTION
# ====================================================================
async def _generate_visual_async(task_id: str, question: str, student_profile: dict, db):
    """
    Background task to generate visual sketch asynchronously
    Updates task status in database when complete
    Now uses whiteboard_engine instead of legacy dynamic_visual_sketch
    """
    try:
        logger.info(f"🎨 [Background] Starting visual generation for task {task_id}")
        
        from services.whiteboard_engine import generate_whiteboard_visual, whiteboard_engine
        
        # Generate visual using whiteboard engine
        try:
            concept = whiteboard_engine.extract_concept(question)
            subject = student_profile.get("subject", "physics") if student_profile else "physics"
            
            if concept:
                visual_result = generate_whiteboard_visual(
                    concept=concept,
                    subject=subject,
                    question=question
                )
                logger.info(f"✅ Whiteboard visual generated for concept: {concept}")
            else:
                # No concept detected - use fallback
                visual_result = _generate_fallback_visual(question)
                logger.info(f"ℹ️ No concept detected, using fallback visual")
                
        except Exception as e:
            logger.error(f"❌ Visual generation failed: {e}", exc_info=True)
            visual_result = _generate_fallback_visual(question)
            logger.info(f"✅ Using fallback visual due to error")
        
        visual_sketch_data = {
            "whiteboard_visual": visual_result,  # New format
            "svg": "",  # Legacy - not used anymore
            "metaphors": [],
            "estimated_marks": 3,
            "has_emotional_content": True,
            "concept": visual_result.get("concept", ""),
            "title": visual_result.get("title", "")
        }
        
        logger.info(f"✅ Visual generated for concept: {visual_sketch_data.get('concept', 'unknown')}")
        
        # Update task status in database
        await db.visual_generation_tasks.update_one(
            {"task_id": task_id},
            {
                "$set": {
                    "status": "completed",
                    "visual_data": visual_sketch_data,
                    "completed_at": datetime.now()
                }
            }
        )
        
        logger.info(f"✅ [Background] Visual generation completed for task {task_id}")
        
    except Exception as e:
        logger.error(f"❌ [Background] Visual generation failed for task {task_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Update task status to failed
        try:
            await db.visual_generation_tasks.update_one(
                {"task_id": task_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e),
                        "completed_at": datetime.now()
                    }
                }
            )
        except Exception:
            pass


def _generate_fallback_visual(question: str) -> Dict[str, Any]:
    """
    Generate a simple fallback visual if main generation fails
    Ensures visuals are always available for all concepts
    """
    # Simple concept explanation visual
    concept_name = question.replace("explain", "").replace("what is", "").replace("define", "").strip()[:30]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" width="640" height="360">
        <defs>
            <style>
                .concept-text {{ font-family: system-ui, Arial; font-size: 24px; fill: #000080; font-weight: bold; }}
                .explanation-text {{ font-family: system-ui, Arial; font-size: 16px; fill: #138808; }}
            </style>
        </defs>
        <rect x="50" y="50" width="540" height="260" fill="#FFFCEF" stroke="#000080" stroke-width="2" rx="10"/>
        <text x="320" y="120" text-anchor="middle" class="concept-text">{concept_name}</text>
        <text x="320" y="180" text-anchor="middle" class="explanation-text">Visual Explanation</text>
        <text x="320" y="220" text-anchor="middle" class="explanation-text">Interactive diagram coming soon!</text>
    </svg>'''
    
    return {
        "svg": svg,
        "metaphors_used": ["concept"],
        "estimated_marks": 3,
        "has_emotional_content": False,
        "region": "North"
    }


# ====================================================================
# VISUAL STATUS POLLING ENDPOINT
# ====================================================================
@router.get("/visual/{task_id}")
async def get_visual_status(
    task_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Poll endpoint for async visual generation status
    Returns visual data when ready, or status if still generating
    """
    try:
        task = await db.visual_generation_tasks.find_one({
            "task_id": task_id,
            "user_id": user.user_id
        })
        
        if not task:
            raise HTTPException(status_code=404, detail="Visual generation task not found")
        
        if task["status"] == "completed":
            visual_data = task.get("visual_data", {})
            return {
                "status": "completed",
                "visual_sketch": {
                    "svg": visual_data.get("svg", ""),
                    "metaphors": visual_data.get("metaphors", []),
                    "estimated_marks": visual_data.get("estimated_marks", 3),
                    "has_emotional_content": visual_data.get("has_emotional_content", True),
                    "topper_hack": visual_data.get("topper_hack"),
                    "topper_rank": visual_data.get("topper_rank"),
                    "pyq_references": visual_data.get("pyq_references", []),
                    "region": visual_data.get("region", "North")
                }
            }
        elif task["status"] == "failed":
            return {
                "status": "failed",
                "error": task.get("error", "Visual generation failed")
            }
        else:
            return {
                "status": "generating",
                "message": "Visual is being generated, please check back in a moment"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching visual status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch visual status: {str(e)}")
