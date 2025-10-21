"""
Mock Tests router for test generation, submission, and performance tracking
"""
from fastapi import APIRouter, HTTPException, Depends, Query

from models.core import User
from services.mock_tests_service import MockTestsService
from dependencies import get_current_user, get_database, get_unified_subscription_service

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


@router.post("/generate")
async def generate_mock_test(
    request: dict,
    user: User = Depends(get_current_user),
    db = Depends(get_database),
    sub_service = Depends(get_unified_subscription_service)
):
    """
    Generate a new mock test based on user parameters
    
    Request body:
    {
        "exam_type": str (JEE, NEET, etc.),
        "test_type": str (full_length, subject_wise, etc.),
        "subjects": list[str],
        "difficulty_level": str (easy, medium, hard),
        "num_questions": int,
        "generation_mode": str (standard, adaptive, etc.)
    }
    """
    try:
        import uuid
        from datetime import datetime, timezone
        from services.unified_subscription_service import FeatureName
        
        # Extract parameters
        exam_type = request.get('exam_type', 'JEE')
        test_type = request.get('test_type', 'full_length')
        subjects = request.get('subjects', [])
        difficulty_raw = request.get('difficulty_level', 'medium')
        num_questions = request.get('num_questions', 75)
        generation_mode = request.get('generation_mode', 'standard')
        
        # PATCH: Handle integer difficulty_level from frontend (1=easy, 2=medium, 3=hard)
        if isinstance(difficulty_raw, int):
            difficulty_map = {1: 'easy', 2: 'medium', 3: 'hard'}
            difficulty = difficulty_map.get(difficulty_raw, 'medium')
        else:
            difficulty = difficulty_raw if difficulty_raw in ['easy', 'medium', 'hard'] else 'medium'
        
        # PATCH: Use dependency-injected sub_service instead of manual initialization
        # Check subscription access - NO initialize() call needed
        access_result = await sub_service.check_feature_access(
            user.user_id,
            FeatureName.MOCK_TESTS.value,
            requested_amount=1
        )
        
        if not access_result.allowed:
            raise HTTPException(
                status_code=402,
                detail=access_result.to_dict()
            )
        
        # Generate test ID
        test_id = str(uuid.uuid4())
        
        # Create test document
        test_doc = {
            "test_id": test_id,
            "user_id": user.user_id,
            "student_id": user.user_id,  # For backward compatibility
            "exam_type": exam_type,
            "test_type": test_type,
            "subjects": subjects,
            "difficulty_level": difficulty,
            "num_questions": num_questions,
            "generation_mode": generation_mode,
            "status": "active",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "time_limit_minutes": 180,  # 3 hours default
            "questions": [],  # Would be populated by AI in full implementation
            "total_marks": num_questions,  # 1 mark per question
            "title": f"{exam_type} {test_type.replace('_', ' ').title()} Test"
        }
        
        # For now, generate simple placeholder questions
        # In production, this would call AI service to generate real questions
        questions = []
        for i in range(min(num_questions, 10)):  # Limit to 10 for demo
            questions.append({
                "question_id": str(uuid.uuid4()),
                "question_number": i + 1,
                "subject": subjects[i % len(subjects)] if subjects else "General",
                "question_text": f"Sample question {i + 1} for {exam_type}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "marks": 1,
                "difficulty": difficulty
            })
        
        test_doc["questions"] = questions
        test_doc["num_questions"] = len(questions)
        test_doc["total_marks"] = len(questions)
        
        # Save to database
        await db.mock_tests.insert_one(test_doc)
        
        # Track usage
        await sub_service.track_feature_use(user.user_id, FeatureName.MOCK_TESTS.value, 1)
        
        # Return test
        del test_doc["_id"]  # Remove MongoDB _id
        
        return {
            "success": True,
            "test": test_doc,
            "test_id": test_id,
            "message": "Mock test generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"❌ Test generation CRITICAL error: {str(e)}")
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        logger.error(f"❌ Request data: {request}")
        raise HTTPException(status_code=500, detail=f"Failed to generate test: {str(e)}")


# Note: Complex endpoints like /submit, /retake, /bookmark-question
# remain in server.py for now as they involve heavy AI processing and subscription logic.
# These can be migrated incrementally in future iterations.
