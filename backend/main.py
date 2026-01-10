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
from core.database import init_database, close_database
from core.rate_limiting import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# API routers
from api import (
    auth,
    user,
    subscription,
    ai,
    analytics,
    auto_notes,
    mock_tests,
    dashboard_analytics,
    gamification,
)
from api import metaphors
from api import visual_teaching
from api import streaming_ai

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
        logger.error("Critical configuration errors detected:")
        for error in validation_errors:
            logger.error(f"   - {error}")
        raise RuntimeError("Application configuration invalid. Check .env file.")

    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

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
    # CRITICAL: In Starlette, add_middleware() inserts at index 0.
    # Therefore: LAST added = FIRST in list = OUTERMOST (processes request first)
    # 
    # We add in this order so the final stack is:
    #   CORS (outermost) → RequestID → SecurityHeaders → CSRF → Session (innermost)
    # =============================================================================

    # 1. Session Middleware (will be innermost)
    logger.info("Configuring SessionMiddleware...")
    is_https = settings.BACKEND_URL.startswith('https://')
    cookie_domain = settings.SESSION_COOKIE_DOMAIN

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.JWT_SECRET,
        same_site=settings.SESSION_COOKIE_SAMESITE,
        https_only=is_https,
        max_age=settings.SESSION_EXPIRY_DAYS * 24 * 60 * 60,  # Convert days to seconds
        domain=cookie_domain
    )
    logger.info(f"   - same_site: {settings.SESSION_COOKIE_SAMESITE}")
    logger.info(f"   - https_only: {is_https}")
    logger.info(f"   - domain: {cookie_domain or 'auto (no restriction)'}")

    # 2. CSRF Middleware
    logger.info("Configuring CSRF Protection...")
    app.add_middleware(
        CSRFMiddleware,
        exempt_paths=[
            "/api/auth/google/login",
            "/api/auth/google/callback",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/logout",
            "/api/auth/session",
            "/api/health",
            "/docs",
            "/openapi.json",
            "/api/subscription/razorpay-webhook",
            "/api/subscription/razorpay/create-order",
            "/api/subscription/razorpay/verify-payment",
            "/api/subscription/check-access",
            "/api/subscription/track-usage",
            "/api/ai/chat/sessions",
            "/api/ai/dual-response",
            "/api/ai/mentor-only",
            "/api/ai/professor-only",
            "/api/ai/neuro-symbolic",
            "/api/mock-tests/generate",
            "/api/agentic/query",
            "/api/agentic/doubt",
            "/api/agentic/tools",
            "/api/agentic/health",
            "/api/study-planner/today",
            "/api/study-planner/generate",
            "/api/study-planner/complete-block",
            "/api/study-planner/history",
            "/api/study-planner/recommendations",
            "/api/notifications",
            "/api/notifications/unread-count",
            "/api/notifications/mark-read",
            "/api/notifications/mark-all-read",
            "/api/netra/parse-concept",
            "/api/netra/health",
            "/api/netra/v4/generate",
            "/api/netra/v4/generate-simple",
            "/api/netra/v4/analyze",
            "/api/netra/v4/health",
            "/api/netra/v4/metrics",
            "/api/newsletter/subscribe",
            "/api/newsletter/unsubscribe",
            "/api/analytics/feedback",
            "/api/analytics/wellness-check",
            "/api/analytics/track-session",
        ],
    )
    logger.info("   - CSRF protection enabled for POST/PUT/PATCH/DELETE requests")
    
    # 3. Security Headers Middleware
    logger.info("Configuring Security Headers...")
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("   - Security headers enabled")

    # 4. Request ID Middleware
    logger.info("Configuring Request ID Middleware...")
    from middleware.request_id import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)
    logger.info("   - Request ID tracing enabled")

    # 5. CORS Middleware - MUST be LAST (becomes outermost, processes first)
    logger.info("Configuring CORS (LAST - outermost)...")
    cors_origins = settings.CORS_ORIGINS
    logger.info(f"   - FRONTEND_URL: {settings.FRONTEND_URL}")
    logger.info(f"   - Allowed origins ({len(cors_origins)}): {cors_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=cors_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "Cache-Control",
            "Cookie",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
        expose_headers=["X-CSRF-Token", "Set-Cookie", "Content-Length"],
        max_age=600,
    )

    # =============================================================================
    # STARTUP EVENT
    # =============================================================================

    @app.on_event("startup")
    async def startup_event():
        """Initialize database and services on startup"""
        logger.info("Application startup initiated...")

        # Initialize database
        db = await init_database()
        
        # ================================================================
        # CRITICAL: Ensure essential indexes exist (fast, idempotent)
        # This prevents slow queries that cause timeouts
        # ================================================================
        try:
            logger.info("🔍 Checking essential database indexes...")
            
            # User profile index (critical for memory queries)
            await db.user_learning_profile.create_index(
                "user_id", 
                unique=True, 
                background=True,
                name="idx_profile_user"
            )
            
            # Chat messages index (critical for conversation context)
            await db.chat_messages.create_index(
                [("session_id", 1), ("user_id", 1), ("timestamp", -1)],
                background=True,
                name="idx_messages_session_user_time"
            )
            
            logger.info("✅ Essential indexes verified")
        except Exception as e:
            # Don't fail startup, just warn
            logger.warning(f"⚠️ Index check failed (may already exist): {e}")

        # Initialize services and inject dependencies
        logger.info("Initializing services...")
        auth_service = AuthService(db, settings.JWT_SECRET)
        unified_subscription_service = UnifiedSubscriptionService(db)
        subscription_service = SubscriptionService(db)  # New unified service
        ai_service = AIService(
            db,
            settings.OPENAI_API_KEY,
            subscription_service=subscription_service,
        )

        # Set global dependencies
        dependencies.db = db
        dependencies.auth_service = auth_service
        dependencies.subscription_service = subscription_service  # Legacy
        dependencies.unified_subscription_service = unified_subscription_service  # New
        dependencies.ai_service = ai_service

        logger.info("Unified Subscription Service initialized")
        
        # 🕐 Start Background Scheduler for TRUE AGENTIC BEHAVIOR
        # This processes scheduled reminders, notifications, streak warnings
        try:
            from services.background_scheduler import start_background_scheduler
            await start_background_scheduler(db)
            logger.info("🕐 Background scheduler started - Agentic actions enabled!")
        except Exception as e:
            logger.error(f"Failed to start background scheduler: {e}")
            logger.warning("⚠️ Scheduled reminders/notifications will NOT work!")
        
        logger.info("All services initialized successfully")
        logger.info(f"Server ready at {settings.BACKEND_URL}")

    # =============================================================================
    # SHUTDOWN EVENT
    # =============================================================================

    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up resources on shutdown"""
        logger.info("Application shutdown initiated...")
        
        # Stop background scheduler
        try:
            from services.background_scheduler import stop_background_scheduler
            await stop_background_scheduler()
            logger.info("Background scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
        
        await close_database()
        logger.info("Shutdown complete")

    # =============================================================================
    # REGISTER ROUTERS
    # =============================================================================

    logger.info("Registering API routers...")

    app.include_router(auth.router, prefix="/api", tags=["Authentication"])
    app.include_router(user.router, prefix="/api", tags=["User"])
    app.include_router(subscription.router, prefix="/api", tags=["Subscription"])
    app.include_router(ai.router, prefix="/api", tags=["AI Tutor"])
    app.include_router(streaming_ai.router, prefix="/api", tags=["AI Tutor Streaming"])
    
    # Unified AI Tutor (NEW - Clean Pipeline)
    try:
        from api import ai_unified
        app.include_router(ai_unified.router, prefix="/api", tags=["AI Tutor Unified"])
        logger.info("Unified AI Tutor router registered")
    except Exception as e:
        logger.warning(f"Could not load unified AI router: {e}")
    
    # 🧠 AI Sathi v2.0 - Intelligent Multi-Agent Pipeline (RECOMMENDED)
    try:
        from api import ai_v2
        app.include_router(ai_v2.router, prefix="/api", tags=["AI Sathi v2"])
        logger.info("🧠 AI Sathi v2.0 router registered - Intelligent routing active")
    except Exception as e:
        logger.warning(f"Could not load AI v2 router: {e}")
    
    # 🧠 Agentic AI System (True Agents with ReAct Loop)
    try:
        from api import agentic
        app.include_router(agentic.router, prefix="/api", tags=["Agentic AI"])
        logger.info("🧠 Agentic AI router registered")
    except Exception as e:
        logger.warning(f"Could not load Agentic AI router: {e}")
    
    app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
    app.include_router(auto_notes.router, prefix="/api", tags=["Auto Notes"])
    app.include_router(mock_tests.router, prefix="/api", tags=["Mock Tests"])
    app.include_router(dashboard_analytics.router, prefix="/api", tags=["Dashboard Analytics"])
    app.include_router(gamification.router, prefix="/api", tags=["Gamification"])
    app.include_router(metaphors.router, prefix="/api", tags=["Metaphors"])
    app.include_router(visual_teaching.router, tags=["Visual Teaching"])
    
    # SketchSense V2 Visual Engine (Enhancement Layer)
    try:
        from api import sketchsense
        app.include_router(sketchsense.router, prefix="/api", tags=["SketchSense V2"])
        logger.info("🎨 SketchSense V2 router registered")
    except Exception as e:
        logger.warning(f"Could not load SketchSense V2 router: {e}")
    
    # Magic Notebook Engine V6 (Visual Engine)
    try:
        from api.routes import ai_visual_engine
        app.include_router(ai_visual_engine.router, prefix="/api", tags=["Magic Notebook V6"])
        logger.info("✨ Magic Notebook Engine V6 router registered")
    except Exception as e:
        logger.warning(f"Magic Notebook Engine V6 router not available: {e}")
    
    # 🔮 NETRA - Intelligent Visual Reasoning Engine (v7.0) - Legacy
    try:
        from api import netra
        app.include_router(netra.router, tags=["NETRA Visual Engine"])
        logger.info("🔮 NETRA Visual Reasoning Engine registered")
    except Exception as e:
        logger.warning(f"NETRA Visual Engine not available: {e}")
    
    # 🔮 NETRA v4.0 - Visual Intelligence Orchestrator (NEW - Game Changer)
    try:
        from api import netra_v4
        app.include_router(netra_v4.router, tags=["NETRA v4 Visual Intelligence"])
        logger.info("🔮 NETRA v4.0 Visual Intelligence Orchestrator registered")
    except Exception as e:
        logger.warning(f"NETRA v4.0 not available: {e}")
    
    # Memory & Learning Dashboard (NEW)
    try:
        from api import memory_dashboard
        app.include_router(memory_dashboard.router, prefix="/api", tags=["Memory & Learning"])
        logger.info("Memory dashboard router registered")
    except Exception as e:
        logger.warning(f"Could not load memory dashboard router: {e}")

    # Diagnostic endpoints for visual testing (dev only)
    if settings.DEBUG or settings.ENVIRONMENT == "development":
        try:
            from api import diagnostic

            app.include_router(diagnostic.router, prefix="/api", tags=["Diagnostic"])
            logger.info("Diagnostic router registered (dev)")
        except Exception as e:
            logger.warning(f"Could not load diagnostic router: {e}")
        
        # Neuro-Symbolic AI endpoints (Phase 1 of Cognitive OS)
        try:
            from api import neuro_symbolic
            app.include_router(neuro_symbolic.router, prefix="/api", tags=["Neuro-Symbolic AI"])
            logger.info("🧠 Neuro-Symbolic AI router registered")
        except Exception as e:
            logger.warning(f"Could not load neuro-symbolic router: {e}")
    
    # Cognitive Model API (Student Intelligence - Always enabled)
    try:
        from api import cognitive
        app.include_router(cognitive.router, prefix="/api", tags=["Cognitive Model"])
        logger.info("🧠 Cognitive Model router registered")
    except Exception as e:
        logger.warning(f"Could not load cognitive router: {e}")
    
    # 🔔 Notifications API (CRITICAL for reminders to work!)
    try:
        from api import notifications
        app.include_router(notifications.router, prefix="/api", tags=["Notifications"])
        logger.info("🔔 Notifications router registered")
    except Exception as e:
        logger.warning(f"Could not load notifications router: {e}")
    
    # 🔌 WebSocket API (Real-time notification delivery)
    try:
        from api import websocket as ws_api
        app.include_router(ws_api.router, tags=["WebSocket"])
        logger.info("🔌 WebSocket router registered")
        
        # Initialize WebSocket manager
        from services.websocket_manager import init_websocket_manager
        init_websocket_manager()
        logger.info("🔌 WebSocket manager initialized")
    except Exception as e:
        logger.warning(f"Could not load WebSocket router: {e}")

    # 📧 Newsletter API (Landing page subscription)
    try:
        from api import newsletter
        app.include_router(newsletter.router, prefix="/api", tags=["Newsletter"])
        logger.info("📧 Newsletter router registered")
    except Exception as e:
        logger.warning(f"Could not load newsletter router: {e}")

    # 📚 Study Planner API (AI-powered daily planning)
    try:
        from api import study_planner
        app.include_router(study_planner.router, prefix="/api", tags=["Study Planner"])
        logger.info("📚 Study Planner router registered")
    except Exception as e:
        logger.warning(f"Could not load study planner router: {e}")

    logger.info("All routers registered")

    # =============================================================================
    # HEALTH CHECK ENDPOINTS
    # =============================================================================

    @app.get("/api/health", tags=["System"])
    async def health_check():
        """Health check endpoint for monitoring and load balancers"""
        from dependencies import get_database
        from datetime import datetime, timezone
        
        # Check database connectivity
        db_status = "healthy"
        try:
            db = await get_database()
            await db.command("ping")
        except Exception as e:
            db_status = f"unhealthy: {str(e)[:50]}"
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "service": settings.APP_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "database": db_status,
                "api": "healthy"
            }
        }

    @app.get("/", tags=["System"])
    async def root():
        """Root endpoint with API information"""
        return {
            "message": f"Welcome to {settings.APP_NAME} API",
            "version": settings.VERSION,
            "docs": f"{settings.BACKEND_URL}/docs",
            "health": f"{settings.BACKEND_URL}/api/health",
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

    logger.info(f"Starting development server on {settings.HOST}:{settings.PORT}")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
