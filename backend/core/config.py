"""
Centralized configuration management for Dhruv AI application
All environment variables are loaded and validated here
"""
import os
import secrets
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
ROOT_DIR = Path(__file__).parent.parent
env_file = ROOT_DIR / '.env'

if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment variables from {env_file}")
else:
    print("ℹ️  .env file not found - using environment variables from container")


class Settings:
    """Application settings loaded from environment variables"""
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    APP_NAME: str = "Dhruv AI"
    APP_DESCRIPTION: str = "AI-Powered Competitive Exam Preparation Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # =============================================================================
    # SERVER SETTINGS
    # =============================================================================
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8001")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    MONGO_URL: str = os.getenv("MONGO_URL", "")
    DB_NAME: str = os.getenv("DB_NAME", "dhruv_ai")
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "168"))  # 7 days
    
    # Generate CSRF secret if not provided
    CSRF_SECRET: str = os.getenv("CSRF_SECRET", secrets.token_hex(32))
    
    # Session settings
    SESSION_COOKIE_NAME: str = "dhruv_ai_session"
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "none")
    SESSION_COOKIE_DOMAIN: str = os.getenv("SESSION_COOKIE_DOMAIN", ".emergent.host")
    SESSION_EXPIRY_DAYS: int = int(os.getenv("SESSION_EXPIRY_DAYS", "7"))
    
    # =============================================================================
    # CORS SETTINGS
    # =============================================================================
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        origins_str = os.getenv("CORS_ORIGINS", "")
        if not origins_str:
            return [
                self.FRONTEND_URL,
                "http://localhost:3000",
                "http://localhost:8001"
            ]
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    # =============================================================================
    # AI / LLM SETTINGS
    # =============================================================================
    EMERGENT_LLM_KEY: str = os.getenv("EMERGENT_LLM_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4000"))
    
    # =============================================================================
    # OAUTH SETTINGS
    # =============================================================================
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # =============================================================================
    # PAYMENT SETTINGS
    # =============================================================================
    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Razorpay
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    
    # =============================================================================
    # SUBSCRIPTION LIMITS
    # =============================================================================
    # Free Tier
    FREE_TIER_AI_MENTOR_LIMIT: int = int(os.getenv("FREE_TIER_AI_MENTOR_LIMIT", "5"))
    FREE_TIER_MOCK_TEST_LIMIT: int = int(os.getenv("FREE_TIER_MOCK_TEST_LIMIT", "2"))
    FREE_TIER_AUTO_NOTES_LIMIT: int = int(os.getenv("FREE_TIER_AUTO_NOTES_LIMIT", "3"))
    
    # Basic Tier
    BASIC_TIER_AI_MENTOR_LIMIT: int = int(os.getenv("BASIC_TIER_AI_MENTOR_LIMIT", "50"))
    BASIC_TIER_MOCK_TEST_LIMIT: int = int(os.getenv("BASIC_TIER_MOCK_TEST_LIMIT", "10"))
    BASIC_TIER_AUTO_NOTES_LIMIT: int = int(os.getenv("BASIC_TIER_AUTO_NOTES_LIMIT", "20"))
    
    # Premium Tier (unlimited = -1)
    PREMIUM_TIER_AI_MENTOR_LIMIT: int = int(os.getenv("PREMIUM_TIER_AI_MENTOR_LIMIT", "-1"))
    PREMIUM_TIER_MOCK_TEST_LIMIT: int = int(os.getenv("PREMIUM_TIER_MOCK_TEST_LIMIT", "-1"))
    PREMIUM_TIER_AUTO_NOTES_LIMIT: int = int(os.getenv("PREMIUM_TIER_AUTO_NOTES_LIMIT", "-1"))
    
    # =============================================================================
    # FILE UPLOAD SETTINGS
    # =============================================================================
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".m4a", ".ogg", ".webm"]
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    
    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # =============================================================================
    # VALIDATION
    # =============================================================================
    def validate(self) -> List[str]:
        """
        Validate critical environment variables
        Returns list of missing/invalid variables
        """
        errors = []
        
        # Required for security
        if not self.JWT_SECRET:
            errors.append("JWT_SECRET is required for authentication")
        
        # Required for database
        if not self.MONGO_URL:
            errors.append("MONGO_URL is required for database connection")
        
        # Required for AI functionality
        if not self.EMERGENT_LLM_KEY:
            errors.append("EMERGENT_LLM_KEY is required for AI features")
        
        # Warn about CSRF secret (auto-generated if missing)
        if not os.getenv("CSRF_SECRET"):
            print("⚠️  CSRF_SECRET not in .env - using auto-generated value")
            print("   Add CSRF_SECRET to .env for production consistency")
        
        # Warn about OAuth if missing
        if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET:
            print("⚠️  Google OAuth credentials not configured")
            print("   Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET for Google login")
        
        return errors
    
    def get_subscription_limits(self, tier: str) -> dict:
        """Get subscription limits for a given tier"""
        limits = {
            "free": {
                "ai_mentor": self.FREE_TIER_AI_MENTOR_LIMIT,
                "mock_tests": self.FREE_TIER_MOCK_TEST_LIMIT,
                "auto_notes": self.FREE_TIER_AUTO_NOTES_LIMIT,
            },
            "basic": {
                "ai_mentor": self.BASIC_TIER_AI_MENTOR_LIMIT,
                "mock_tests": self.BASIC_TIER_MOCK_TEST_LIMIT,
                "auto_notes": self.BASIC_TIER_AUTO_NOTES_LIMIT,
            },
            "premium": {
                "ai_mentor": self.PREMIUM_TIER_AI_MENTOR_LIMIT,
                "mock_tests": self.PREMIUM_TIER_MOCK_TEST_LIMIT,
                "auto_notes": self.PREMIUM_TIER_AUTO_NOTES_LIMIT,
            },
        }
        return limits.get(tier.lower(), limits["free"])


# Create global settings instance
settings = Settings()

# Validate settings on import
validation_errors = settings.validate()
if validation_errors:
    print("\n❌ CRITICAL CONFIGURATION ERRORS:")
    for error in validation_errors:
        print(f"   - {error}")
    print("\nApplication may not function correctly. Please check your .env file.\n")
