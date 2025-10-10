"""
Test script to validate modular FastAPI structure
"""
import sys
import os
import asyncio
sys.path.append('/app/backend')

# Test imports
try:
    from models.core import User, UserCreate, UserLogin
    print("✅ Core models imported successfully")
    
    from models.subscription import SubscriptionPlan, UsageTracking
    print("✅ Subscription models imported successfully")
    
    from services.auth_service import AuthService
    print("✅ Auth service imported successfully")
    
    from api.auth import router as auth_router
    print("✅ Auth router imported successfully")
    
    from main import create_app
    print("✅ Main app creator imported successfully")
    
    # Test creating app
    app = create_app()
    print("✅ FastAPI app created successfully")
    
    print("\n🎉 MODULAR STRUCTURE VALIDATION: ALL TESTS PASSED!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()