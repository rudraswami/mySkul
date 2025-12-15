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
    print(f"[OK] Loaded environment variables from {env_file}")
else:
    print("[INFO] .env file not found - using environment variables from container")


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

    # Visual engine feature flags
    VISUAL_ENGINE_MODE: str = os.getenv("VISUAL_ENGINE_MODE", "universal")  # universal|legacy
    VISUAL_ENGINE_STRICT: bool = os.getenv("VISUAL_ENGINE_STRICT", "true").lower() == "true"
    
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
    SESSION_EXPIRY_DAYS: int = int(os.getenv("SESSION_EXPIRY_DAYS", "7"))
    
    @property
    def SESSION_COOKIE_DOMAIN(self) -> Optional[str]:
        """
        Extract cookie domain from BACKEND_URL automatically
        Returns None for localhost (allows cookie to work on any local port)
        """
        # Check if explicitly set in environment
        explicit_domain = os.getenv("SESSION_COOKIE_DOMAIN")
        if explicit_domain:
            return explicit_domain
        
        # Auto-detect from BACKEND_URL
        if "localhost" in self.BACKEND_URL or "127.0.0.1" in self.BACKEND_URL:
            return None  # No domain restriction for localhost
        
        # Extract domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(self.BACKEND_URL)
        hostname = parsed.hostname
        
        if hostname and "." in hostname:
            # For emergent.host, dhruv.ai, etc., use parent domain
            parts = hostname.split(".")
            if len(parts) >= 2:
                return f".{'.'.join(parts[-2:])}"  # e.g., .emergent.host
        
        return None  # Fallback to no domain restriction
    
    # =============================================================================
    # CORS SETTINGS
    # =============================================================================
    CORS_ALLOW_ALL_SUBDOMAINS: bool = os.getenv("CORS_ALLOW_ALL_SUBDOMAINS", "false").lower() == "true"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """
        Parse CORS origins from comma-separated string
        Automatically includes frontend URL and localhost for development
        """
        origins = []
        
        # Parse explicit origins from environment
        origins_str = os.getenv("CORS_ORIGINS", "")
        if origins_str:
            for origin in origins_str.split(","):
                origin = origin.strip()
                if origin:
                    origins.append(origin)
        
        # Always include configured frontend URL
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        
        # Include localhost for development
        if self.DEBUG or self.ENVIRONMENT == "development":
            for local_origin in ["http://localhost:3000", "http://localhost:8001", "http://127.0.0.1:3000"]:
                if local_origin not in origins:
                    origins.append(local_origin)
        
        # Add subdomain wildcard if enabled (for preview environments)
        if self.CORS_ALLOW_ALL_SUBDOMAINS:
            from urllib.parse import urlparse
            parsed = urlparse(self.FRONTEND_URL)
            if parsed.hostname and "." in parsed.hostname:
                # Extract parent domain
                parts = parsed.hostname.split(".")
                if len(parts) >= 2:
                    parent_domain = ".".join(parts[-2:])
                    # Note: Actual wildcard regex would need middleware implementation
                    # For now, we'll document this limitation
                    pass
        
        return origins
    
    # =============================================================================
    # AI / LLM SETTINGS
    # =============================================================================
    EMERGENT_LLM_KEY: str = os.getenv("EMERGENT_LLM_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # BASE MODEL - gpt-4.1-mini for all reasoning (STRICT)
    BASE_MODEL: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    
    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")  # Unified to gpt-4.1-mini
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4000"))
    
    # =============================================================================
    # GEMINI PRO - PRIMARY REASONING MODEL (Lightning fast, deeply intelligent)
    # =============================================================================
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyCvZFnJiADdLqvMZ0lAtgRzKtJxJkMKglo")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # For NETRA v4 visual reasoning
    GEMINI_PRO_MODEL: str = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")  # Deep reasoning
    GEMINI_VISUAL_MODEL: str = os.getenv("GEMINI_VISUAL_MODEL", "gemini-2.0-flash-exp")  # For image generation
    USE_GEMINI_PRIMARY: bool = os.getenv("USE_GEMINI_PRIMARY", "false").lower() == "true"  # Disabled - using gpt-4.1-mini
    
    # =============================================================================
    # DEEPSEEK & VISION MODEL SETTINGS
    # =============================================================================
    # DeepSeek - Fallback reasoning model (70B for deep thinking)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "sk-288b009e0be14411a1c11b4649c360be")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # Kimi-VL - PRIMARY Vision model (OCR, diagrams, formulas, textbook pages)
    KIMI_VISION_API_KEY: str = os.getenv("KIMI_VISION_API_KEY", "sk-aEzUhSMy0Izz6bUnbJiwtpBxDADeI94vByaUTqOvOV6y2EP9")
    KIMI_VISION_MODEL: str = os.getenv("KIMI_VISION_MODEL", "moonshot-v1-8k-vision-preview")
    KIMI_VISION_BASE_URL: str = os.getenv("KIMI_VISION_BASE_URL", "https://api.moonshot.ai/v1")
    
    # Qwen-VL - SECONDARY Vision model (fallback)
    QWEN_VL_API_KEY: str = os.getenv("QWEN_VL_API_KEY", "")
    QWEN_VL_MODEL: str = os.getenv("QWEN_VL_MODEL", "qwen-vl-max")
    QWEN_VL_BASE_URL: str = os.getenv("QWEN_VL_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # Model routing flags - All disabled, using gpt-4.1-mini exclusively
    USE_DEEPSEEK_REASONING: bool = os.getenv("USE_DEEPSEEK_REASONING", "false").lower() == "true"
    USE_KIMI_VISION: bool = os.getenv("USE_KIMI_VISION", "false").lower() == "true"
    USE_QWEN_VISION: bool = os.getenv("USE_QWEN_VISION", "false").lower() == "true"
    
    # =============================================================================
    # 🤖 AGENTIC SYSTEM SETTINGS - TRUE AGENT BEHAVIOR
    # =============================================================================
    # Enable the full agentic system (ReAct loop, tools, planning)
    USE_AGENTIC_SYSTEM: bool = os.getenv("USE_AGENTIC_SYSTEM", "true").lower() == "true"
    
    # Enable action intent detection (reminders, notifications, etc.)
    ENABLE_ACTION_DETECTION: bool = os.getenv("ENABLE_ACTION_DETECTION", "true").lower() == "true"
    
    # Enable background scheduler for processing reminders/notifications
    ENABLE_BACKGROUND_SCHEDULER: bool = os.getenv("ENABLE_BACKGROUND_SCHEDULER", "true").lower() == "true"
    
    # Agent configuration
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    AGENT_VERBOSE_LOGGING: bool = os.getenv("AGENT_VERBOSE_LOGGING", "true").lower() == "true"
    
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
    # Free Tier - Updated to match planConfig_ai_tutor.json (January 17, 2025)
    # Free Tier - Daily/Monthly limits
    FREE_TIER_AI_MENTOR_LIMIT: int = int(os.getenv("FREE_TIER_AI_MENTOR_LIMIT", "10"))  # 10/day
    FREE_TIER_MOCK_TEST_LIMIT: int = int(os.getenv("FREE_TIER_MOCK_TEST_LIMIT", "2"))  # 2/month
    FREE_TIER_AUTO_NOTES_LIMIT: int = int(os.getenv("FREE_TIER_AUTO_NOTES_LIMIT", "5"))  # 5/month
    FREE_TIER_MEMORY_HOURS: int = int(os.getenv("FREE_TIER_MEMORY_HOURS", "24"))  # 24 hours
    
    # Basic Tier - Daily/Monthly limits
    BASIC_TIER_AI_MENTOR_LIMIT: int = int(os.getenv("BASIC_TIER_AI_MENTOR_LIMIT", "50"))  # 50/day
    BASIC_TIER_MOCK_TEST_LIMIT: int = int(os.getenv("BASIC_TIER_MOCK_TEST_LIMIT", "10"))  # 10/month
    BASIC_TIER_AUTO_NOTES_LIMIT: int = int(os.getenv("BASIC_TIER_AUTO_NOTES_LIMIT", "25"))  # 25/month
    BASIC_TIER_MEMORY_DAYS: int = int(os.getenv("BASIC_TIER_MEMORY_DAYS", "7"))  # 7 days
    
    # Premium Tier (unlimited = -1)
    PREMIUM_TIER_AI_MENTOR_LIMIT: int = int(os.getenv("PREMIUM_TIER_AI_MENTOR_LIMIT", "-1"))
    PREMIUM_TIER_MOCK_TEST_LIMIT: int = int(os.getenv("PREMIUM_TIER_MOCK_TEST_LIMIT", "-1"))
    PREMIUM_TIER_AUTO_NOTES_LIMIT: int = int(os.getenv("PREMIUM_TIER_AUTO_NOTES_LIMIT", "-1"))
    PREMIUM_TIER_MEMORY_DAYS: int = int(os.getenv("PREMIUM_TIER_MEMORY_DAYS", "-1"))  # Unlimited
    
    # =============================================================================
    # FILE UPLOAD SETTINGS
    # =============================================================================
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".m4a", ".ogg", ".webm"]
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    
    # =============================================================================
    # REDIS SETTINGS (Optional - for production caching)
    # =============================================================================
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    RATE_LIMIT_STORAGE_URI: str = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")
    
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
        
        # Required for security - CRITICAL
        if not self.JWT_SECRET:
            errors.append("JWT_SECRET is required for authentication (CRITICAL)")
        elif len(self.JWT_SECRET) < 32:
            errors.append("JWT_SECRET must be at least 32 characters for security")
        
        # Required for database - CRITICAL
        if not self.MONGO_URL:
            errors.append("MONGO_URL is required for database connection (CRITICAL)")
        
        # Required for AI functionality - CRITICAL
        if not self.EMERGENT_LLM_KEY:
            errors.append("EMERGENT_LLM_KEY is required for AI features (CRITICAL)")
        
        # Warn about CSRF secret (auto-generated if missing)
        if not os.getenv("CSRF_SECRET"):
            print("[WARNING]  CSRF_SECRET not in .env - using auto-generated value")
            print("   Add CSRF_SECRET to .env for production consistency")
        
        # Warn about OAuth if missing
        if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET:
            print("[WARNING]  Google OAuth credentials not configured")
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
    print("\n[ERROR] CRITICAL CONFIGURATION ERRORS:")
    for error in validation_errors:
        print(f"   - {error}")
    print("\nApplication may not function correctly. Please check your .env file.\n")
