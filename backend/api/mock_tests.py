"""
Mock Tests router for test generation, submission, and performance tracking
"""
from fastapi import APIRouter, HTTPException, Depends, Query
import logging
import traceback
import uuid
from typing import Dict, Any

from models.core import User
from models.mock_tests import TestGenerationRequest, TestGenerationResponse, ErrorResponse
from services.mock_tests_service import MockTestsService
from dependencies import get_current_user, get_database, get_unified_subscription_service

# Logger setup
logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(prefix="/mock-tests", tags=["mock-tests"])


# Dependency to get mock-tests service
async def get_mock_tests_service(db = Depends(get_database)) -> MockTestsService:
    """Get mock-tests service instance"""
    return MockTestsService(db)


@router.get("/library")
async def get_test_library(
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service),
    skip: int = Query(0, ge=0, description="Number of tests to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of tests to return (max 100)")
):
    """
    Get test library for the user with pagination
    
    - **skip**: Number of tests to skip (for pagination)
    - **limit**: Number of tests to return (default 20, max 100)
    """
    try:
        tests = await service.get_user_tests(user.user_id)
        total = len(tests)
        paginated_tests = tests[skip:skip + limit]
        
        return {
            "tests": paginated_tests,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get test library: {str(e)}")


@router.get("/library/recent")
async def get_recent_tests(
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get recent tests for the user"""
    try:
        tests = await service.get_user_tests(user.user_id)
        # Return only the 5 most recent
        recent_tests = tests[:5] if tests else []
        return {"tests": recent_tests, "total": len(recent_tests)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent tests: {str(e)}")


@router.get("/library/high-scores")
async def get_high_score_tests(
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get tests with high scores"""
    try:
        tests = await service.get_user_tests(user.user_id)
        # Filter submitted tests and sort by score (if available)
        submitted_tests = [t for t in tests if t.get('status') == 'submitted']
        return {"tests": submitted_tests[:5], "total": len(submitted_tests)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get high score tests: {str(e)}")


@router.get("/dashboard")
async def get_dashboard(
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get dashboard statistics"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Dashboard requested for user: {user.user_id}")
        
        stats = await service.get_dashboard_stats(user.user_id)
        logger.info(f"Dashboard stats retrieved: {stats}")
        return stats
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard error for user {user.user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")


@router.get("/performance-trends")
async def get_performance_trends(
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get performance trends for the user"""
    try:
        trends = await service.get_performance_trends(user.user_id)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance trends: {str(e)}")


@router.get("/subjects")
async def get_subjects(
    exam_type: str = Query(default="JEE", description="Exam type (JEE, NEET, etc.)"),  # Default to JEE if not provided
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get available subjects for an exam type (defaults to JEE)"""
    try:
        subjects = await service.get_available_subjects(user.user_id, exam_type)
        return {"subjects": subjects, "exam_type": exam_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subjects: {str(e)}")


@router.get("/bookmarked-questions")
async def get_bookmarked_questions(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    PATCH: Get all bookmarked questions from test attempts
    Returns questions that user has bookmarked across all tests
    """
    try:
        # Find all test attempts with bookmarked questions
        attempts = await db.test_attempts.find({
            "student_id": user.user_id
        }).to_list(length=None)
        
        bookmarked = []
        for attempt in attempts:
            responses = attempt.get("responses", [])
            for response in responses:
                if response.get("bookmarked", False):
                    bookmarked.append({
                        "test_id": attempt.get("test_id"),
                        "question_id": response.get("question_id"),
                        "question": response.get("question", ""),
                        "subject": response.get("subject", ""),
                        "topic": response.get("topic", ""),
                        "user_answer": response.get("user_answer"),
                        "correct_answer": response.get("correct_answer"),
                        "is_correct": response.get("is_correct", False),
                        "bookmarked_at": attempt.get("submitted_at")
                    })
        
        return {
            "bookmarked_questions": bookmarked,
            "total": len(bookmarked)
        }
    except Exception as e:
        print(f"Error fetching bookmarked questions: {e}")
        # Return empty list instead of error for graceful degradation
        return {
            "bookmarked_questions": [],
            "total": 0
        }


@router.get("/{test_id}/detailed-review")
async def get_detailed_review(
    test_id: str,
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get detailed review for a test"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Detailed review requested for test: {test_id}, user: {user.user_id}")
        
        test = await service.get_test(test_id, user.user_id)
        if not test:
            logger.warning(f"Test not found: {test_id} for user: {user.user_id}")
            raise HTTPException(status_code=404, detail="Test not found")
        
        attempts = await service.get_test_attempts(test_id, user.user_id)
        logger.info(f"Retrieved {len(attempts)} attempts for test: {test_id}")
        
        return {
            "test": test,
            "attempts": attempts,
            "latest_attempt": attempts[0] if attempts else None
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Detailed review error for test {test_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get detailed review: {str(e)}")


@router.get("/resume")
async def get_resume_tests(
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get tests that can be resumed"""
    try:
        tests = await service.get_user_tests(user.user_id)
        # Filter active tests that haven't been submitted
        active_tests = [t for t in tests if t.get('status') == 'active']
        return {"tests": active_tests, "total": len(active_tests)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resume tests: {str(e)}")


@router.post("/generate", response_model=TestGenerationResponse)
async def generate_mock_test(
    request: TestGenerationRequest,
    user: User = Depends(get_current_user),
    db = Depends(get_database),
    sub_service = Depends(get_unified_subscription_service)
):
    """
    Generate a new mock test based on user parameters with comprehensive validation
    
    **Validations**:
    - exam_type: Required, non-empty string
    - subjects: Required, must have at least 1 subject
    - difficulty_level: 1=easy, 2=medium, 3=hard (accepts int or string)
    - num_questions: Between 3 and 100
    - test_type: One of [full_length, chapter_wise, subject_wise, adaptive]
    
    **Error Codes**:
    - 400: Validation error (invalid parameters)
    - 402: Subscription limit reached
    - 500: Internal server error (database, AI service, etc.)
    """
    # Generate trace ID for debugging
    trace_id = str(uuid.uuid4())
    
    try:
        from datetime import datetime, timezone
        from services.unified_subscription_service import FeatureName
        
        logger.info(f"[{trace_id}] Test generation started for user {user.user_id}")
        logger.info(f"[{trace_id}] Request: exam_type={request.exam_type}, subjects={request.subjects}, "
                   f"difficulty={request.difficulty_level}, num_questions={request.num_questions}")
        
        # ==================== STEP 1: Validate Subscription Access ====================
        try:
            access_result = await sub_service.check_feature_access(
                user.user_id,
                FeatureName.MOCK_TESTS.value,
                requested_amount=1
            )
            
            if not access_result.allowed:
                logger.warning(f"[{trace_id}] Subscription limit reached for user {user.user_id}")
                raise HTTPException(
                    status_code=402,
                    detail=access_result.to_dict()
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[{trace_id}] Subscription check failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error_code": "SUBSCRIPTION_CHECK_FAILED",
                    "message": "Failed to verify subscription access",
                    "trace_id": trace_id
                }
            )
        
        # ==================== STEP 2: Generate Test ID ====================
        test_id = str(uuid.uuid4())
        logger.info(f"[{trace_id}] Generated test_id: {test_id}")
        
        # ==================== STEP 3: Generate Questions using Agentic System ====================
        try:
            # Ensure subjects list is not empty (should be validated by Pydantic, but double-check)
            if not request.subjects:
                raise ValueError("subjects list cannot be empty")
            
            from services.agentic_test_generator import AgenticTestGenerator
            from services.test_blueprint_generator import TestBlueprintGenerator
            import os
            
            emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY') or os.environ.get('EMERGENT_API_KEY')
            if not emergent_llm_key:
                logger.warning(f"[{trace_id}] EMERGENT_LLM_KEY missing. Using deterministic fallback generator.")
                blueprint = TestBlueprintGenerator().generate_blueprint(
                    exam_type=request.exam_type,
                    subjects=request.subjects,
                    num_questions=min(request.num_questions, 100),
                    difficulty_level=request.difficulty_level,
                    test_type=request.test_type,
                    chapters=request.chapters,
                    focus_areas=request.focus_areas
                )
                questions = []
                for i in range(min(request.num_questions, 100)):
                    subject = request.subjects[i % len(request.subjects)]
                    questions.append({
                        "question_id": str(uuid.uuid4()),
                        "question_number": i + 1,
                        "subject": subject,
                        "topic": "General",
                        "question_text": f"Placeholder {request.exam_type} question {i + 1} - {subject}",
                        "options": [
                            "A) Placeholder option",
                            "B) Placeholder option",
                            "C) Placeholder option",
                            "D) Placeholder option"
                        ],
                        "correct_answer": "A",
                        "marks": 1,
                        "difficulty": request.difficulty_level,
                        "explanation": "This is a fallback question generated because the AI question engine is unavailable.",
                        "metadata": {"fallback": True}
                    })
                quality_report = {
                    "requested_questions": request.num_questions,
                    "generated_questions": len(questions),
                    "validated_questions": len(questions),
                    "fallback_mode": True
                }
            else:
                agentic_config = {
                    "emergent_llm_key": emergent_llm_key
                }
                test_generator = AgenticTestGenerator(config=agentic_config)
                logger.info(f"[{trace_id}] Using Agentic Test Generator")

                test_result = await test_generator.generate_test(
                    exam_type=request.exam_type,
                    subjects=request.subjects,
                    num_questions=min(request.num_questions, 100),
                    difficulty_level=request.difficulty_level,
                    test_type=request.test_type,
                    chapters=request.chapters if hasattr(request, 'chapters') else None,
                    focus_areas=request.focus_areas if hasattr(request, 'focus_areas') else None,
                    user_id=user.user_id
                )

                questions = test_result["questions"]
                blueprint = test_result.get("blueprint", {})
                quality_report = test_result.get("quality_report", {})
                logger.info(f"[{trace_id}] Agentic generation complete: {len(questions)} questions")
            
            if not questions:
                raise ValueError("Failed to generate any questions")
            
            logger.info(f"[{trace_id}] Generated {len(questions)} questions")
            
        except Exception as e:
            logger.error(f"[{trace_id}] Question generation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error_code": "QUESTION_GENERATION_FAILED",
                    "message": f"Failed to generate questions: {str(e)}",
                    "trace_id": trace_id
                }
            )
        
        # ==================== STEP 4: Create Test Document ====================
        try:
            time_limit_minutes = blueprint.get("time_limit_minutes", 180)
            title = f"{request.exam_type} {request.test_type.replace('_', ' ').title()} Test"

            test_doc = {
                "test_id": test_id,
                "user_id": user.user_id,
                "student_id": user.user_id,  # Backward compatibility
                "exam_type": request.exam_type,
                "test_type": request.test_type,
                "subjects": request.subjects,
                "difficulty_level": request.difficulty_level,
                "num_questions": len(questions),
                "generation_mode": request.generation_mode,
                "status": "active",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "time_limit_minutes": time_limit_minutes,
                "time_limit": time_limit_minutes,
                "questions": questions,
                "total_marks": len(questions),  # 1 mark per question
                "title": title,
                "test_name": title,
                "trace_id": trace_id,
                "created_by": "api_v2",
                "blueprint": blueprint,
                "quality_report": quality_report,
                "question_schema_version": "v2"
            }
            
            logger.info(f"[{trace_id}] Test document created with {len(questions)} questions")
            
        except Exception as e:
            logger.error(f"[{trace_id}] Test document creation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error_code": "TEST_DOCUMENT_CREATION_FAILED",
                    "message": f"Failed to create test document: {str(e)}",
                    "trace_id": trace_id
                }
            )
        
        # ==================== STEP 5: Save to Database ====================
        try:
            result = await db.mock_tests.insert_one(test_doc)
            logger.info(f"[{trace_id}] Test saved to database with _id: {result.inserted_id}")
            
        except Exception as e:
            logger.error(f"[{trace_id}] Database insertion failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error_code": "DATABASE_INSERTION_FAILED",
                    "message": "Failed to save test to database",
                    "details": {"error": str(e)},
                    "trace_id": trace_id
                }
            )
        
        # ==================== STEP 6: Track Usage ====================
        try:
            await sub_service.track_feature_use(user.user_id, FeatureName.MOCK_TESTS.value, 1)
            logger.info(f"[{trace_id}] Feature usage tracked for user {user.user_id}")
        except Exception as e:
            # Don't fail the request if usage tracking fails, just log it
            logger.error(f"[{trace_id}] Usage tracking failed (non-critical): {str(e)}")
        
        # ==================== STEP 7: Return Response ====================
        # Remove MongoDB _id before returning
        if "_id" in test_doc:
            del test_doc["_id"]
        
        logger.info(f"[{trace_id}] Test generation completed successfully")
        
        return TestGenerationResponse(
            success=True,
            test_id=test_id,
            test=test_doc,
            message="Mock test generated successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (402, 400, etc.)
        raise
        
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"[{trace_id}] Unexpected error in test generation: {str(e)}", exc_info=True)
        logger.error(f"[{trace_id}] Full traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during test generation",
                "details": {"error": str(e)},
                "trace_id": trace_id
            }
        )


# Note: Complex endpoints like /submit, /retake, /bookmark-question
# remain in server.py for now as they involve heavy AI processing and subscription logic.
# These can be migrated incrementally in future iterations.
