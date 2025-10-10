"""
Main FastAPI application with modular architecture
"""
import os
import logging
import secrets
from pathlib import Path
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from fastapi.responses import JSONResponse as FastAPIJSONResponse
import json as json_lib

# Import modular components
from api import auth, user
from services.auth_service import AuthService
import dependencies

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Custom JSONResponse that handles MongoDB ObjectId serialization
class JSONResponse(FastAPIJSONResponse):
    def render(self, content: any) -> bytes:
        return json_lib.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=lambda obj: str(obj) if isinstance(obj, ObjectId) else obj,
        ).encode("utf-8")

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


def validate_critical_env_vars():
    """Validate critical environment variables on startup - fail fast if missing"""
    required_vars = {
        'JWT_SECRET': 'JWT signing secret is required for authentication security',
        'MONGO_URL': 'MongoDB connection URL is required',
        'DB_NAME': 'Database name is required',
        'EMERGENT_LLM_KEY': 'Emergent LLM API key is required for AI functionality'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"{var}: {description}")
    
    # Generate CSRF secret if not provided
    if not os.environ.get('CSRF_SECRET'):
        csrf_secret = secrets.token_hex(32)
        os.environ['CSRF_SECRET'] = csrf_secret
        logger.warning(f"CSRF_SECRET not found - generated temporary secret: {csrf_secret[:16]}...")
        logger.warning("Add CSRF_SECRET to your .env file for production use")
    
    if missing_vars:
        logger.error("CRITICAL: Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        logger.error("Application startup aborted for security reasons.")
        raise RuntimeError("Missing critical environment variables")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Validate environment variables before starting
    validate_critical_env_vars()
    
    # Create FastAPI app
    app = FastAPI(
        title="Dhruv AI API", 
        description="AI-Powered Competitive Exam Preparation Platform"
    )
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Initialize services
    jwt_secret = os.environ['JWT_SECRET']
    auth_service = AuthService(db, jwt_secret)
    
    # Set dependencies
    dependencies.db = db
    dependencies.auth_service = auth_service
    
    # Security Middleware Configuration
    cors_origins = os.environ.get('CORS_ORIGINS', '').split(',')
    if not cors_origins or cors_origins == ['']:
        logger.error("CORS_ORIGINS environment variable is required for security")
        raise RuntimeError("CORS_ORIGINS must be explicitly configured")

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Content-Type", 
            "Authorization", 
            "X-Requested-With",
            "X-CSRF-Token",
            "Cache-Control"
        ],
        expose_headers=["X-CSRF-Token"]
    )

    # TODO: Add CSRF protection back after implementing proper token flow
    # CSRF Protection - Temporarily disabled for initial cookie auth implementation  
    # app.add_middleware(
    #     CSRFMiddleware,
    #     secret=os.environ['CSRF_SECRET'],
    #     cookie_name="csrftoken",
    #     header_name="x-csrftoken"
    # )
    
    # Register routers with API prefix
    app.include_router(auth.router, prefix="/api")
    app.include_router(user.router, prefix="/api")
    
    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint for monitoring"""
        return {"status": "healthy", "service": "dhruv-ai-backend"}
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_db_client():
        client.close()
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)