from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import logging
import uuid
from pathlib import Path
import bcrypt
import jwt

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI Chat Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
JWT_SECRET = os.environ.get('JWT_SECRET', 'dhruv-ai-secret-key-2025')

app = FastAPI(title="Dhruv AI API", description="AI-Powered Competitive Exam Preparation Platform")
api_router = APIRouter(prefix="/api")

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============= DATA MODELS =============

class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: str
    password_hash: str
    exam_type: str  # JEE, NEET, UPSC
    grade: Optional[str] = None
    target_year: int
    parent_email: Optional[str] = None
    subscription_type: str = "free"  # free, basic, premium, family
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    exam_type: str
    grade: Optional[str] = None
    target_year: int
    parent_email: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class StudyProgress(BaseModel):
    progress_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    chapter: str
    concept: str
    mastery_level: float = 0.0  # 0-100%
    time_spent: int = 0  # minutes
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    questions_attempted: int = 0
    questions_correct: int = 0

class ChatSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    message: str
    response: str
    reasoning: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    feedback: Optional[str] = None  # helpful, not_helpful
    confidence: Optional[float] = None

class MockTest(BaseModel):
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    exam_type: str
    subject: str
    test_name: str
    questions: List[Dict[str, Any]]
    answers: Dict[str, Any] = {}
    score: Optional[float] = None
    time_taken: Optional[int] = None  # seconds
    completed_at: Optional[datetime] = None
    analysis: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StudyPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    exam_type: str
    target_date: datetime
    subjects: List[Dict[str, Any]]
    daily_goals: Dict[str, Any]
    weekly_targets: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DoubtQuery(BaseModel):
    query: str
    subject: Optional[str] = None
    context: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    subject: str

# ============= UTILITY FUNCTIONS =============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(' ')[1]
    payload = verify_jwt_token(token)
    user = await db.users.find_one({"user_id": payload['user_id']})
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

# ============= AI INTEGRATION =============

async def get_ai_tutor_response(user_message: str, subject: str, session_id: str) -> tuple[str, str]:
    """Get response from AI tutor with reasoning"""
    
    system_message = f"""You are Dhruv AI, an expert tutor for {subject} competitive exam preparation in India. 

Your core principles:
1. ACCURACY FIRST: Provide only verified, accurate information
2. STEP-BY-STEP EXPLANATIONS: Break down complex concepts into digestible steps
3. EXAM-FOCUSED: Tailor responses to competitive exam requirements (JEE/NEET/UPSC)
4. ENCOURAGE LEARNING: Ask follow-up questions to ensure understanding
5. CITE SOURCES: Reference specific principles, formulas, or laws when explaining

Always structure your responses as:
1. Direct answer to the question
2. Step-by-step explanation
3. Key principles/formulas involved
4. Tips for exam preparation
5. A follow-up question to check understanding

Be encouraging but maintain academic rigor. If asked about non-academic topics, politely redirect to studies."""

    try:
        # Initialize AI chat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        # Create user message
        user_msg = UserMessage(text=user_message)
        
        # Get AI response
        response = await chat.send_message(user_msg)
        
        # Generate reasoning (simplified for now)
        reasoning = f"Applied {subject} principles and pedagogical best practices to provide accurate, step-by-step explanation suitable for competitive exam preparation."
        
        return response, reasoning
        
    except Exception as e:
        logger.error(f"AI tutor error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI tutor temporarily unavailable")

# ============= API ENDPOINTS =============

@api_router.post("/auth/register")
async def register_user(user_data: UserCreate):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    password_hash = hash_password(user_data.password)
    user = User(
        **user_data.dict(exclude={'password'}),
        password_hash=password_hash
    )
    
    # Save to database
    await db.users.insert_one(user.dict())
    
    # Create JWT token
    token = create_jwt_token(user.user_id, user.email)
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "exam_type": user.exam_type
        }
    }

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    """Login user"""
    
    # Find user
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = User(**user_doc)
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    token = create_jwt_token(user.user_id, user.email)
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "exam_type": user.exam_type,
            "subscription_type": user.subscription_type
        }
    }

@api_router.get("/user/profile")
async def get_user_profile(user: User = Depends(get_current_user)):
    """Get user profile"""
    return {
        "user_id": user.user_id,
        "full_name": user.full_name,
        "email": user.email,
        "exam_type": user.exam_type,
        "grade": user.grade,
        "target_year": user.target_year,
        "subscription_type": user.subscription_type
    }

@api_router.post("/chat/message")
async def send_chat_message(chat_request: ChatRequest, user: User = Depends(get_current_user)):
    """Send message to AI tutor"""
    
    # Create or get chat session
    session_id = chat_request.session_id or str(uuid.uuid4())
    
    if not chat_request.session_id:
        # Create new session
        session = ChatSession(
            session_id=session_id,
            user_id=user.user_id,
            subject=chat_request.subject,
            title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
        )
        await db.chat_sessions.insert_one(session.dict())
    
    # Get AI response
    try:
        ai_response, reasoning = await get_ai_tutor_response(
            chat_request.message, 
            chat_request.subject, 
            session_id
        )
        
        # Save chat message
        chat_message = ChatMessage(
            session_id=session_id,
            user_id=user.user_id,
            message=chat_request.message,
            response=ai_response,
            reasoning=reasoning,
            confidence=0.95  # High confidence for demonstration
        )
        
        await db.chat_messages.insert_one(chat_message.dict())
        
        return {
            "session_id": session_id,
            "message": chat_request.message,
            "response": ai_response,
            "reasoning": reasoning,
            "timestamp": chat_message.timestamp
        }
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@api_router.get("/chat/sessions")
async def get_chat_sessions(user: User = Depends(get_current_user)):
    """Get user's chat sessions"""
    
    sessions = await db.chat_sessions.find(
        {"user_id": user.user_id}
    ).sort("last_updated", -1).to_list(50)
    
    return {"sessions": sessions}

@api_router.get("/chat/{session_id}/messages")
async def get_chat_messages(session_id: str, authorization: str = None):
    """Get messages from a chat session"""
    user = await get_current_user(authorization)
    
    messages = await db.chat_messages.find(
        {"session_id": session_id, "user_id": user.user_id}
    ).sort("timestamp", 1).to_list(100)
    
    return {"messages": messages}

@api_router.post("/progress/update")
async def update_progress(progress: StudyProgress, authorization: str = None):
    """Update study progress"""
    user = await get_current_user(authorization)
    progress.user_id = user.user_id
    
    # Check if progress record exists
    existing = await db.study_progress.find_one({
        "user_id": user.user_id,
        "subject": progress.subject,
        "chapter": progress.chapter,
        "concept": progress.concept
    })
    
    if existing:
        # Update existing record
        await db.study_progress.update_one(
            {"progress_id": existing["progress_id"]},
            {"$set": progress.dict()}
        )
    else:
        # Create new record
        await db.study_progress.insert_one(progress.dict())
    
    return {"message": "Progress updated successfully"}

@api_router.get("/progress/summary")
async def get_progress_summary(authorization: str = None):
    """Get user's overall progress summary"""
    user = await get_current_user(authorization)
    
    # Aggregate progress data
    pipeline = [
        {"$match": {"user_id": user.user_id}},
        {"$group": {
            "_id": "$subject",
            "avg_mastery": {"$avg": "$mastery_level"},
            "total_time": {"$sum": "$time_spent"},
            "concepts_studied": {"$sum": 1},
            "questions_attempted": {"$sum": "$questions_attempted"},
            "accuracy": {
                "$multiply": [
                    {"$divide": ["$questions_correct", "$questions_attempted"]},
                    100
                ]
            }
        }}
    ]
    
    progress_summary = await db.study_progress.aggregate(pipeline).to_list(10)
    
    return {"progress": progress_summary}

@api_router.get("/dashboard/analytics")
async def get_dashboard_analytics(authorization: str = None):
    """Get comprehensive analytics for dashboard"""
    user = await get_current_user(authorization)
    
    # Get recent activity
    recent_progress = await db.study_progress.find(
        {"user_id": user.user_id}
    ).sort("last_accessed", -1).limit(5).to_list(5)
    
    # Get chat sessions count
    chat_sessions_count = await db.chat_sessions.count_documents(
        {"user_id": user.user_id}
    )
    
    # Get total study time
    total_time_pipeline = [
        {"$match": {"user_id": user.user_id}},
        {"$group": {"_id": None, "total_time": {"$sum": "$time_spent"}}}
    ]
    
    total_time_result = await db.study_progress.aggregate(total_time_pipeline).to_list(1)
    total_study_time = total_time_result[0]["total_time"] if total_time_result else 0
    
    return {
        "recent_progress": recent_progress,
        "total_study_time": total_study_time,
        "chat_sessions_count": chat_sessions_count,
        "current_streak": 7,  # Placeholder
        "weekly_goals_progress": 75,  # Placeholder
    }

@api_router.post("/doubt/resolve")
async def resolve_doubt(doubt_query: DoubtQuery, authorization: str = None):
    """Quick doubt resolution without chat session"""
    user = await get_current_user(authorization)
    
    try:
        # Create a temporary session for doubt resolution
        session_id = f"doubt_{uuid.uuid4()}"
        
        ai_response, reasoning = await get_ai_tutor_response(
            doubt_query.query,
            doubt_query.subject or "General",
            session_id
        )
        
        return {
            "question": doubt_query.query,
            "answer": ai_response,
            "reasoning": reasoning,
            "subject": doubt_query.subject
        }
        
    except Exception as e:
        logger.error(f"Doubt resolution error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resolve doubt")

# Health check endpoint
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@api_router.get("/")
async def root():
    return {"message": "Dhruv AI API - Empowering Education with AI"}

# Include router in main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)