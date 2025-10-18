"""
AI router for chat sessions, dual AI responses, guardrails, and AI-powered features
Now with unified subscription service for consistent access control
"""
import os
from fastapi import APIRouter, HTTPException, Depends

from models.core import User, SessionCreateRequest, SessionRenameRequest, SessionPinRequest, SessionBookmarkRequest
from models.ai import DualAIRequest, MathValidationRequest, FactVerificationRequest, StudyPlanRequest
from services.ai_service import AIService
from services.unified_subscription_service import UnifiedSubscriptionService, FeatureName
from dependencies import get_current_user, get_database, get_unified_subscription_service


# Router instance
router = APIRouter(prefix="/ai", tags=["ai"])


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
    """Generate mentor-only AI response"""
    try:
        # Use the dual response but extract mentor only
        response = await ai_service.generate_dual_ai_response(
            user.user_id, request.message, request.session_id, request.subject
        )
        
        return {
            "response": response["secondary"]["response"],
            "type": "mentor",
            "session_id": request.session_id,
            "subject": request.subject
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate mentor response: {str(e)}")


@router.post("/professor-only")
async def generate_professor_response(
    request: DualAIRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate professor-only AI response"""
    try:
        # Use the dual response but extract professor only
        response = await ai_service.generate_dual_ai_response(
            user.user_id, request.message, request.session_id, request.subject
        )
        
        return {
            "response": response["primary"]["response"],
            "type": "professor", 
            "session_id": request.session_id,
            "subject": request.subject
        }
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
        await db.chat_messages.delete_many({"session_id": session_id, "user_id": user.user_id})
        
        # Delete session
        result = await db.chat_sessions.delete_one({"session_id": session_id, "user_id": user.user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")