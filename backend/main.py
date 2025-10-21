"""
Main FastAPI application entry point - Modular Architecture
Single source of truth for application initialization
"""
import logging
from bson.objectid import ObjectId
from fastapi import FastAPI
from fastapi.responses import JSONResponse as FastAPIJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import json as json_lib

# Core imports
from core.config import settings
from core.database import init_database, close_database, get_database
from core.rate_limiting import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# API routers
from api import auth, user, subscription, ai, analytics, auto_notes, mock_tests, dashboard_analytics, gamification

# Middleware
from middleware.csrf import CSRFMiddleware
from middleware.security_headers import SecurityHeadersMiddleware

# Services for dependency injection
from services.auth_service import AuthService
from services.subscription_service import SubscriptionService
from services.unified_subscription_service import UnifiedSubscriptionService
from services.ai_service import AIService
import dependencies

# Logging configuration
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Custom JSONResponse that handles MongoDB ObjectId serialization
class JSONResponse(FastAPIJSONResponse):
    """Custom JSON response handler for MongoDB ObjectId"""
    def render(self, content: any) -> bytes:
        return json_lib.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=lambda obj: str(obj) if isinstance(obj, ObjectId) else obj,
        ).encode("utf-8")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    Single entry point for the entire application
    """
    
    # Validate configuration
    validation_errors = settings.validate()
    if validation_errors:
        logger.error("❌ Critical configuration errors detected:")
        for error in validation_errors:
            logger.error(f"   - {error}")
        raise RuntimeError("Application configuration invalid. Check .env file.")
    
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔐 Debug mode: {settings.DEBUG}")
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        default_response_class=JSONResponse
    )
    
    # Add rate limiter state and exception handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    
    # =============================================================================
    # MIDDLEWARE CONFIGURATION
    # =============================================================================
    
    # Security Headers Middleware (MUST be first to apply to all responses)
    logger.info("🛡️ Configuring Security Headers...")
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("   - HSTS, CSP, X-Frame-Options, and other security headers enabled")
    
    # Session Middleware (MUST be before CORS for cookie handling)
    logger.info("🍪 Configuring SessionMiddleware...")
    is_https = settings.BACKEND_URL.startswith('https://')
    cookie_domain = settings.SESSION_COOKIE_DOMAIN
    
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.JWT_SECRET,
        same_site=settings.SESSION_COOKIE_SAMESITE,
        https_only=is_https,
        max_age=settings.SESSION_EXPIRY_DAYS * 24 * 60 * 60,  # Convert days to seconds
        domain=cookie_domain  # FIX: Add missing domain parameter
    )
    logger.info(f"   - same_site: {settings.SESSION_COOKIE_SAMESITE}")
    logger.info(f"   - https_only: {is_https}")
    logger.info(f"   - domain: {cookie_domain or 'auto (no restriction)'}")
    logger.info(f"   - BACKEND_URL: {settings.BACKEND_URL}")
    
    # CORS Middleware
    logger.info("🌐 Configuring CORS...")
    cors_origins = settings.CORS_ORIGINS
    logger.info(f"   - Allowed origins: {cors_origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=cors_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "Cache-Control",
            "Cookie"
        ],
        expose_headers=["X-CSRF-Token", "Set-Cookie"]
    )

    
    # CSRF Middleware - ENABLED for production security
    logger.info("🛡️ Configuring CSRF Protection...")
    app.add_middleware(
        CSRFMiddleware,
        exempt_paths=[
            "/api/auth/google/login",
            "/api/auth/google/callback",
            "/api/auth/session",
            "/api/health",
            "/docs",
            "/openapi.json",
            "/api/subscription/razorpay-webhook",  # Webhook must be exempt
            "/api/subscription/razorpay/create-order",  # FIX: Razorpay payment endpoints (JWT-authenticated)
            "/api/subscription/razorpay/verify-payment",  # FIX: Razorpay payment endpoints (JWT-authenticated)
            "/api/subscription/check-access",  # FIX: Exempt subscription checks (JWT-authenticated)
            "/api/subscription/track-usage",  # FIX: Exempt usage tracking (JWT-authenticated)
            "/api/ai/chat/sessions",  # FIX: Exempt AI chat sessions (JWT-authenticated)
            "/api/ai/dual-response",  # FIX: Exempt AI dual response (JWT-authenticated)
        ]
    )
    logger.info("   - CSRF protection enabled for POST/PUT/PATCH/DELETE requests")

    
    # =============================================================================
    # STARTUP EVENT
    # =============================================================================
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize database and services on startup"""
        logger.info("⚡ Application startup initiated...")
        
        # Initialize database
        db = await init_database()
        
        # Initialize services and inject dependencies
        logger.info("🔧 Initializing services...")
        auth_service = AuthService(db, settings.JWT_SECRET)
        subscription_service = SubscriptionService(db)  # Legacy
        unified_subscription_service = UnifiedSubscriptionService(db)  # New unified service
        ai_service = AIService(
            db,
            settings.EMERGENT_LLM_KEY,
            subscription_service=subscription_service
        )
        
        # Set global dependencies
        dependencies.db = db
        dependencies.auth_service = auth_service
        dependencies.subscription_service = subscription_service  # Legacy
        dependencies.unified_subscription_service = unified_subscription_service  # New
        dependencies.ai_service = ai_service
        
        logger.info("✅ Unified Subscription Service initialized")
        
        logger.info("✅ All services initialized successfully")
        logger.info(f"🎯 Server ready at {settings.BACKEND_URL}")
    
    # =============================================================================
    # SHUTDOWN EVENT
    # =============================================================================
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up resources on shutdown"""
        logger.info("🛑 Application shutdown initiated...")
        await close_database()
        logger.info("✅ Shutdown complete")
    
    # =============================================================================
    # REGISTER ROUTERS
    # =============================================================================
    
    logger.info("📡 Registering API routers...")
    
    app.include_router(auth.router, prefix="/api", tags=["Authentication"])
    app.include_router(user.router, prefix="/api", tags=["User"])
    app.include_router(subscription.router, prefix="/api", tags=["Subscription"])
    app.include_router(ai.router, prefix="/api", tags=["AI Tutor"])
    app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
    app.include_router(auto_notes.router, prefix="/api", tags=["Auto Notes"])
    app.include_router(mock_tests.router, prefix="/api", tags=["Mock Tests"])
    app.include_router(dashboard_analytics.router, prefix="/api", tags=["Dashboard Analytics"])
    app.include_router(gamification.router, prefix="/api", tags=["Gamification"])
    
    logger.info("✅ All routers registered")
    
    # =============================================================================
    # HEALTH CHECK ENDPOINTS
    # =============================================================================
    
    @app.get("/api/health", tags=["System"])
    async def health_check():
        """Health check endpoint for monitoring and load balancers"""
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    @app.get("/", tags=["System"])
    async def root():
        """Root endpoint with API information"""
        return {
            "message": f"Welcome to {settings.APP_NAME} API",
            "version": settings.VERSION,
            "docs": f"{settings.BACKEND_URL}/docs",
            "health": f"{settings.BACKEND_URL}/api/health"
        }
    
    return app


# =============================================================================
# APPLICATION INSTANCE
# =============================================================================

# Create the application instance
app = create_app()


# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🔥 Starting development server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )