"""
Usage Tracking Models for Phase-1 Subscription
Tracks daily and monthly feature usage with auto-reset logic
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid


class UsageCounter(BaseModel):
    """
    Usage counter for a specific feature
    Supports both daily and monthly resets
    """
    user_id: str
    feature: str  # 'ai_mentor', 'mock_tests', 'auto_notes'
    count: int = 0
    reset_period: str  # 'daily' or 'monthly'
    last_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UsageTrackingRecord(BaseModel):
    """
    Complete usage tracking record for a user
    Stores all feature counters in one document
    """
    tracking_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Daily counters (reset every day at midnight UTC)
    daily_ai_questions: int = 0
    daily_ai_questions_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Monthly counters (reset on 1st of each month)
    monthly_mock_tests: int = 0
    monthly_mock_tests_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    monthly_notes: int = 0
    monthly_notes_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadata
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
