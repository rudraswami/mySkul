"""FastAPI modular routers package"""
# Explicit re-exports for type checking
from . import (
    auth as auth,
    user as user,
    subscription as subscription,
    ai as ai,
    analytics as analytics,
    auto_notes as auto_notes,
    mock_tests as mock_tests,
)

__all__ = [
    "auth",
    "user",
    "subscription",
    "ai",
    "analytics",
    "auto_notes",
    "mock_tests",
]