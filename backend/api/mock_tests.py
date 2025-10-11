"""
Mock Tests router for test generation, submission, and performance tracking
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List

from models.core import User
from models.mock_tests import (
    TestGenerationRequest, TestSubmissionRequest, TestRetakeRequest,
    BookmarkQuestionRequest
)
from services.mock_tests_service import MockTestsService
from dependencies import get_current_user, get_database

# Router instance
router = APIRouter(prefix="/mock-tests", tags=["mock-tests"])


# Dependency to get mock-tests service
async def get_mock_tests_service(db = Depends(get_database)) -> MockTestsService:
    """Get mock-tests service instance"""
    return MockTestsService(db)


@router.get("/library")
async def get_test_library(
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get test library for the user"""
    try:
        tests = await service.get_user_tests(user.user_id)
        return {"tests": tests, "total": len(tests)}
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
        stats = await service.get_dashboard_stats(user.user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


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
    exam_type: str,
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get available subjects for an exam type"""
    try:
        subjects = await service.get_available_subjects(user.user_id, exam_type)
        return {"subjects": subjects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subjects: {str(e)}")


@router.get("/{test_id}/detailed-review")
async def get_detailed_review(
    test_id: str,
    user: User = Depends(get_current_user),
    service: MockTestsService = Depends(get_mock_tests_service)
):
    """Get detailed review for a test"""
    try:
        test = await service.get_test(test_id, user.user_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        attempts = await service.get_test_attempts(test_id, user.user_id)
        
        return {
            "test": test,
            "attempts": attempts,
            "latest_attempt": attempts[0] if attempts else None
        }
    except HTTPException:
        raise
    except Exception as e:
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


# Note: Complex endpoints like /generate, /submit, /retake, /bookmark-question
# remain in server.py for now as they involve heavy AI processing and subscription logic.
# These can be migrated incrementally in future iterations.
