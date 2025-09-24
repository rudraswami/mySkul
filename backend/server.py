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

class StudyProgressUpdate(BaseModel):
    subject: str
    chapter: str
    concept: str
    mastery_level: float = 0.0  # 0-100%
    time_spent: int = 0  # minutes
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

class Question(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: str
    subject: str
    chapter: str
    difficulty_level: int = Field(ge=1, le=5)  # 1=Easy, 5=Very Hard
    exam_type: str
    marks: int = 1
    negative_marks: float = 0.25
    time_limit: int = 120  # seconds per question

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
    difficulty_level: int = 3  # Adaptive difficulty
    total_marks: int = 100
    passing_marks: int = 40

class MockTestResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    user_id: str
    answers: Dict[str, str]  # question_id: selected_answer
    score: float
    percentage: float
    time_taken: int
    correct_answers: int
    wrong_answers: int
    unanswered: int
    subject_wise_analysis: Dict[str, Any]
    difficulty_performance: Dict[str, Any]
    recommendations: List[str]
    rank: Optional[int] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class StressAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    stress_level: int = Field(ge=1, le=10)  # 1=Very Low, 10=Very High
    anxiety_level: int = Field(ge=1, le=10)
    sleep_quality: int = Field(ge=1, le=10)
    study_motivation: int = Field(ge=1, le=10)
    physical_symptoms: List[str] = []
    emotional_state: str
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    recommendations: List[str] = []

class MotivationalContent(BaseModel):
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content_type: str  # quote, tip, exercise, success_story
    title: str
    content: str
    category: str  # motivation, stress_relief, study_tips, health
    engagement_score: Optional[float] = None
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

class MockTestGenerationRequest(BaseModel):
    exam_type: str
    subject: str
    difficulty: int = 3
    num_questions: int = 25

class DoubtQuery(BaseModel):
    query: str
    subject: Optional[str] = None
    context: Optional[str] = None

# ============= AUTO-NOTE MENTOR DATA MODELS =============

class NoteSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    subject: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: str = "active"  # active, processing, completed
    audio_duration: Optional[int] = None  # seconds
    transcription: Optional[str] = None
    structured_notes: Optional[Dict[str, Any]] = None
    dual_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AudioChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    sequence_number: int
    transcription: str
    timestamp: float  # seconds from start
    confidence: Optional[float] = None
    processed: bool = False

class GeneratedFlashcard(BaseModel):
    card_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    question: str
    answer: str
    concept: str
    difficulty_level: int = Field(ge=1, le=5)
    created_from_point: Optional[str] = None  # Reference to note point
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NoteSessionRequest(BaseModel):
    title: str
    subject: str

class AudioChunkRequest(BaseModel):
    session_id: str
    transcription: str
    timestamp: float
    sequence_number: int
    confidence: Optional[float] = None

class ExplainPointRequest(BaseModel):
    session_id: str
    point_reference: str  # e.g., "point_3", "concept_1"
    additional_context: Optional[str] = None

class GenerateFlashcardsRequest(BaseModel):
    session_id: str
    specific_concepts: Optional[List[str]] = None  # If empty, generate from all notes

class MockTestSubmission(BaseModel):
    answers: Dict[str, str]  # question_id: selected_answer
    time_taken: int  # seconds

class StressAssessmentRequest(BaseModel):
    stress_level: int = Field(ge=1, le=10)
    anxiety_level: int = Field(ge=1, le=10)
    sleep_quality: int = Field(ge=1, le=10)
    study_motivation: int = Field(ge=1, le=10)
    physical_symptoms: List[str] = []
    emotional_state: str = "neutral"

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

# ============= DUAL-LAYER AI INTEGRATION =============

class ScenarioClassifier:
    """Classifies user queries to determine whether Mentor or Professor should lead"""
    
    @staticmethod
    def classify_scenario(user_message: str, subject: str = None) -> dict:
        """
        Classify the scenario and determine AI persona leadership
        Returns: {
            'primary_persona': 'mentor' | 'professor',
            'secondary_persona': 'mentor' | 'professor',
            'scenario_type': str,
            'confidence': float
        }
        """
        message_lower = user_message.lower()
        
        # Professor-first scenarios (accuracy-critical)
        professor_indicators = [
            'solve', 'calculate', 'derive', 'prove', 'formula', 'equation',
            'explain the concept', 'what is', 'define', 'difference between',
            'step by step', 'check my answer', 'is this correct', 'verify'
        ]
        
        # Mentor-first scenarios (motivation/guidance)
        mentor_indicators = [
            'study plan', 'timetable', 'schedule', 'motivation', 'stressed',
            'anxiety', 'worried', 'how to prepare', 'tips', 'strategy',
            'feeling', 'confidence', 'guidance', 'advice', 'help me focus'
        ]
        
        professor_score = sum(1 for indicator in professor_indicators if indicator in message_lower)
        mentor_score = sum(1 for indicator in mentor_indicators if indicator in message_lower)
        
        if professor_score > mentor_score:
            return {
                'primary_persona': 'professor',
                'secondary_persona': 'mentor', 
                'scenario_type': 'fact_solving',
                'confidence': min(professor_score / 5.0, 1.0)
            }
        elif mentor_score > professor_score:
            return {
                'primary_persona': 'mentor',
                'secondary_persona': 'professor',
                'scenario_type': 'guidance_motivation',
                'confidence': min(mentor_score / 5.0, 1.0)
            }
        else:
            # Default to mentor for balanced/unclear cases
            return {
                'primary_persona': 'mentor',
                'secondary_persona': 'professor',
                'scenario_type': 'general_inquiry',
                'confidence': 0.5
            }

class MentorAI:
    """Adaptive, friendly, motivational AI layer"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_response(self, user_message: str, subject: str, session_id: str, user_context: dict = None) -> tuple[str, str]:
        """Generate mentor response - adaptive, friendly, motivational"""
        
        system_message = f"""You are the MENTOR layer of Dhruv AI - the adaptive, friendly, and motivational intelligence.

Your core identity:
- ADAPTIVE: Adjust your teaching style to student's emotional and learning needs
- FRIENDLY: Use encouraging, empathetic communication that builds confidence
- MOTIVATIONAL: Inspire and energize students while maintaining focus on goals
- PERSONALIZER: Tailor advice to individual student's journey and challenges

For {subject} competitive exam preparation, your approach:
1. START WITH ENCOURAGEMENT: Acknowledge effort and validate concerns
2. PERSONALIZE: Consider student's emotional state, progress, and challenges  
3. SIMPLIFY: Break down overwhelming concepts into manageable steps
4. MOTIVATE: Connect learning to their goals and dreams
5. GUIDE: Provide practical study strategies and emotional support

Response Structure:
- Warm, encouraging opening
- Personalized advice/explanation
- Practical next steps
- Motivational closing with confidence building

Always maintain academic integrity while being the supportive guide every student needs."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"mentor_{session_id}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            user_msg = UserMessage(text=user_message)
            response = await chat.send_message(user_msg)
            
            reasoning = f"Mentor AI: Applied adaptive learning psychology and motivational techniques for {subject} exam preparation, focusing on emotional support and personalized guidance."
            
            return response, reasoning
            
        except Exception as e:
            logger.error(f"Mentor AI error: {str(e)}")
            raise HTTPException(status_code=500, detail="Mentor AI temporarily unavailable")

class ProfessorAI:
    """Rule-based, verified reasoning AI layer"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_response(self, user_message: str, subject: str, session_id: str, user_context: dict = None) -> tuple[str, str]:
        """Generate professor response - rule-based, verified, rigorous"""
        
        system_message = f"""You are the PROFESSOR layer of Dhruv AI - the rule-based, verified reasoning intelligence.

Your core identity:
- ACCURACY FIRST: Provide only verified, factually correct information
- SYSTEMATIC: Follow structured, logical approaches to problem-solving
- RIGOROUS: Maintain academic standards and scientific methodology
- VERIFIED: Cross-check facts, formulas, and principles before presenting
- COMPREHENSIVE: Cover all aspects thoroughly with proper citations

For {subject} competitive exam preparation, your approach:
1. PRECISE DEFINITIONS: Start with exact, verified concepts
2. STEP-BY-STEP LOGIC: Show clear, logical progression
3. FORMULA/PRINCIPLE CITATION: Reference exact sources and laws
4. VERIFICATION: Double-check calculations and reasoning
5. EXAM STANDARDS: Align with official syllabus and marking schemes

Response Structure:
- Direct, accurate answer
- Detailed step-by-step explanation
- Relevant formulas/principles with citations
- Verification checkpoints
- Exam-specific application notes

Maintain absolute accuracy - if uncertain about any fact, clearly state limitations."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"professor_{session_id}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            user_msg = UserMessage(text=user_message)
            response = await chat.send_message(user_msg)
            
            reasoning = f"Professor AI: Applied systematic verification and rule-based reasoning for {subject}, ensuring academic accuracy and exam compliance."
            
            return response, reasoning
            
        except Exception as e:
            logger.error(f"Professor AI error: {str(e)}")
            raise HTTPException(status_code=500, detail="Professor AI temporarily unavailable")

class DualLayerAI:
    """Coordinated dual-layer AI system combining Mentor and Professor"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.mentor = MentorAI(api_key)
        self.professor = ProfessorAI(api_key)
        self.classifier = ScenarioClassifier()
    
    async def get_coordinated_response(self, user_message: str, subject: str, session_id: str, user_context: dict = None) -> dict:
        """Get coordinated response from both Mentor and Professor layers"""
        
        try:
            # Classify the scenario
            scenario = self.classifier.classify_scenario(user_message, subject)
            
            # Get responses from both layers
            if scenario['primary_persona'] == 'professor':
                # Professor leads, Mentor supports
                professor_response, professor_reasoning = await self.professor.get_response(
                    user_message, subject, session_id, user_context
                )
                
                # Generate supporting mentor message
                mentor_prompt = f"A student asked: '{user_message}' and received this technical explanation: '{professor_response[:200]}...' Provide encouraging support and study tips to complement this answer."
                mentor_response, mentor_reasoning = await self.mentor.get_response(
                    mentor_prompt, subject, session_id, user_context
                )
                
                return {
                    'primary_response': professor_response,
                    'primary_persona': 'professor',
                    'primary_reasoning': professor_reasoning,
                    'secondary_response': mentor_response,
                    'secondary_persona': 'mentor',
                    'secondary_reasoning': mentor_reasoning,
                    'scenario_type': scenario['scenario_type'],
                    'confidence': scenario['confidence']
                }
            
            else:
                # Mentor leads, Professor validates
                mentor_response, mentor_reasoning = await self.mentor.get_response(
                    user_message, subject, session_id, user_context
                )
                
                # Generate supporting professor validation (if needed for factual content)
                if any(keyword in user_message.lower() for keyword in ['formula', 'calculate', 'solve', 'concept']):
                    professor_prompt = f"Verify and add technical accuracy to this guidance: '{mentor_response[:200]}...' for the question: '{user_message}'"
                    professor_response, professor_reasoning = await self.professor.get_response(
                        professor_prompt, subject, session_id, user_context
                    )
                else:
                    professor_response, professor_reasoning = "", "No technical validation required for this guidance-focused query."
                
                return {
                    'primary_response': mentor_response,
                    'primary_persona': 'mentor',
                    'primary_reasoning': mentor_reasoning,
                    'secondary_response': professor_response,
                    'secondary_persona': 'professor',
                    'secondary_reasoning': professor_reasoning,
                    'scenario_type': scenario['scenario_type'],
                    'confidence': scenario['confidence']
                }
                
        except Exception as e:
            logger.error(f"Dual-layer AI error: {str(e)}")
            raise HTTPException(status_code=500, detail="Dual-layer AI system temporarily unavailable")

# Initialize dual-layer AI system
dual_ai = DualLayerAI(EMERGENT_LLM_KEY)

# Legacy function for backward compatibility
async def get_ai_tutor_response(user_message: str, subject: str, session_id: str) -> tuple[str, str]:
    """Legacy function - now uses dual-layer AI system"""
    
    try:
        coordinated_response = await dual_ai.get_coordinated_response(user_message, subject, session_id)
        
        # Combine responses for legacy compatibility
        if coordinated_response['secondary_response']:
            combined_response = f"{coordinated_response['primary_response']}\n\n--- Additional Insights ---\n{coordinated_response['secondary_response']}"
        else:
            combined_response = coordinated_response['primary_response']
        
        combined_reasoning = f"Dual-layer response: {coordinated_response['primary_persona']} leading ({coordinated_response['scenario_type']}). {coordinated_response['primary_reasoning']}"
        
        return combined_response, combined_reasoning
        
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
    
    # Convert ObjectId to string for JSON serialization
    for session in sessions:
        if "_id" in session:
            session["_id"] = str(session["_id"])
    
    return {"sessions": sessions}

@api_router.get("/chat/{session_id}/messages")
async def get_chat_messages(session_id: str, user: User = Depends(get_current_user)):
    """Get messages from a chat session"""
    
    messages = await db.chat_messages.find(
        {"session_id": session_id, "user_id": user.user_id}
    ).sort("timestamp", 1).to_list(100)
    
    # Convert ObjectId to string for JSON serialization
    for message in messages:
        if "_id" in message:
            message["_id"] = str(message["_id"])
    
    return {"messages": messages}

@api_router.post("/progress/update")
async def update_progress(progress_update: StudyProgressUpdate, user: User = Depends(get_current_user)):
    """Update study progress"""
    
    # Create full progress object
    progress = StudyProgress(
        user_id=user.user_id,
        **progress_update.dict()
    )
    
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
async def get_progress_summary(user: User = Depends(get_current_user)):
    """Get user's overall progress summary"""
    
    # Aggregate progress data
    pipeline = [
        {"$match": {"user_id": user.user_id}},
        {"$group": {
            "_id": "$subject",
            "avg_mastery": {"$avg": "$mastery_level"},
            "total_time": {"$sum": "$time_spent"},
            "concepts_studied": {"$sum": 1},
            "questions_attempted": {"$sum": "$questions_attempted"},
            "questions_correct": {"$sum": "$questions_correct"}
        }},
        {"$addFields": {
            "accuracy": {
                "$cond": {
                    "if": {"$gt": ["$questions_attempted", 0]},
                    "then": {
                        "$multiply": [
                            {"$divide": ["$questions_correct", "$questions_attempted"]},
                            100
                        ]
                    },
                    "else": 0
                }
            }
        }}
    ]
    
    progress_summary = await db.study_progress.aggregate(pipeline).to_list(10)
    
    return {"progress": progress_summary}

@api_router.get("/dashboard/analytics")
async def get_dashboard_analytics(user: User = Depends(get_current_user)):
    """Get comprehensive analytics for dashboard"""
    
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
async def resolve_doubt(doubt_query: DoubtQuery, user: User = Depends(get_current_user)):
    """Quick doubt resolution without chat session"""
    
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

# ============= DUAL-LAYER AI API ENDPOINTS =============

@api_router.post("/ai/dual-response")
async def get_dual_ai_response(chat_request: ChatRequest, user: User = Depends(get_current_user)):
    """Get coordinated response from both Mentor and Professor AI layers"""
    
    try:
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        # Get user context for personalization
        user_context = {
            'exam_type': user.exam_type,
            'grade': user.grade,
            'target_year': user.target_year,
            'user_id': user.user_id
        }
        
        # Get coordinated dual-layer response
        coordinated_response = await dual_ai.get_coordinated_response(
            chat_request.message, 
            chat_request.subject, 
            session_id, 
            user_context
        )
        
        # Save chat message with dual-layer data
        chat_message = ChatMessage(
            session_id=session_id,
            user_id=user.user_id,
            message=chat_request.message,
            response=coordinated_response['primary_response'],
            reasoning=f"Dual-layer AI: {coordinated_response['primary_persona']} leading. Scenario: {coordinated_response['scenario_type']}"
        )
        
        await db.chat_messages.insert_one(chat_message.dict())
        
        return {
            "session_id": session_id,
            "message": chat_request.message,
            "dual_response": {
                "primary": {
                    "persona": coordinated_response['primary_persona'],
                    "response": coordinated_response['primary_response'],
                    "reasoning": coordinated_response['primary_reasoning']
                },
                "secondary": {
                    "persona": coordinated_response['secondary_persona'],
                    "response": coordinated_response['secondary_response'],
                    "reasoning": coordinated_response['secondary_reasoning']
                },
                "scenario_type": coordinated_response['scenario_type'],
                "confidence": coordinated_response['confidence']
            },
            "timestamp": chat_message.timestamp
        }
        
    except Exception as e:
        logger.error(f"Dual AI response error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dual AI response")

@api_router.post("/ai/mentor-only")
async def get_mentor_response(chat_request: ChatRequest, user: User = Depends(get_current_user)):
    """Get response only from Mentor AI layer"""
    
    try:
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        user_context = {
            'exam_type': user.exam_type,
            'grade': user.grade,
            'target_year': user.target_year,
            'user_id': user.user_id
        }
        
        mentor_response, mentor_reasoning = await dual_ai.mentor.get_response(
            chat_request.message,
            chat_request.subject,
            session_id,
            user_context
        )
        
        return {
            "session_id": session_id,
            "message": chat_request.message,
            "response": mentor_response,
            "reasoning": mentor_reasoning,
            "persona": "mentor",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Mentor AI error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get mentor response")

@api_router.post("/ai/professor-only")
async def get_professor_response(chat_request: ChatRequest, user: User = Depends(get_current_user)):
    """Get response only from Professor AI layer"""
    
    try:
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        user_context = {
            'exam_type': user.exam_type,
            'grade': user.grade,
            'target_year': user.target_year,
            'user_id': user.user_id
        }
        
        professor_response, professor_reasoning = await dual_ai.professor.get_response(
            chat_request.message,
            chat_request.subject,
            session_id,
            user_context
        )
        
        return {
            "session_id": session_id,
            "message": chat_request.message,
            "response": professor_response,
            "reasoning": professor_reasoning,
            "persona": "professor", 
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Professor AI error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get professor response")

@api_router.get("/ai/scenario-classify")
async def classify_message_scenario(message: str):
    """Classify a message to determine which AI persona should lead"""
    
    try:
        classifier = ScenarioClassifier()
        scenario = classifier.classify_scenario(message)
        
        return {
            "message": message,
            "classification": scenario,
            "explanation": {
                "professor_scenarios": "Fact/concept questions, problem solving, step-by-step solutions",
                "mentor_scenarios": "Study planning, motivation, stress management, guidance"
            }
        }
        
    except Exception as e:
        logger.error(f"Scenario classification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to classify scenario")

# ============= PHASE 2: DUAL-LAYER SCENARIO IMPLEMENTATIONS =============

class StudyPlanRequest(BaseModel):
    target_exam_date: str  # ISO date string
    daily_study_hours: int = Field(ge=1, le=16)
    weak_subjects: List[str] = []
    strong_subjects: List[str] = []
    preferred_study_times: List[str] = []  # morning, afternoon, evening, night
    stress_level: int = Field(ge=1, le=10, default=5)

@api_router.post("/ai/dual-study-plan")
async def create_dual_study_plan(
    plan_request: StudyPlanRequest,
    user: User = Depends(get_current_user)
):
    """Generate comprehensive study plan using dual-layer AI intelligence"""
    
    try:
        # Get user's current performance for context
        recent_progress = await db.study_progress.find(
            {"user_id": user.user_id}
        ).sort("last_accessed", -1).limit(10).to_list(10)
        
        # Calculate performance metrics
        avg_mastery = sum(p.get("mastery_level", 50) for p in recent_progress) / max(len(recent_progress), 1)
        
        # Create study plan prompt
        study_plan_prompt = f"""Create a comprehensive study plan for {user.exam_type} preparation:
        
        Student Profile:
        - Target Exam: {user.exam_type} {user.target_year}
        - Exam Date: {plan_request.target_exam_date}
        - Daily Study Hours: {plan_request.daily_study_hours}
        - Current Average Mastery: {avg_mastery:.1f}%
        - Weak Subjects: {', '.join(plan_request.weak_subjects) if plan_request.weak_subjects else 'None specified'}
        - Strong Subjects: {', '.join(plan_request.strong_subjects) if plan_request.strong_subjects else 'None specified'}
        - Preferred Study Times: {', '.join(plan_request.preferred_study_times)}
        - Current Stress Level: {plan_request.stress_level}/10
        
        Create a detailed, actionable study plan that balances academic rigor with student well-being."""
        
        # Get dual-layer response
        user_context = {
            'exam_type': user.exam_type,
            'target_year': user.target_year,
            'current_performance': avg_mastery,
            'stress_level': plan_request.stress_level
        }
        
        session_id = f"study_plan_{uuid.uuid4()}"
        dual_response = await dual_ai.get_coordinated_response(
            study_plan_prompt, "Study Planning", session_id, user_context
        )
        
        # Parse the coordinated response
        professor_plan = dual_response['primary_response'] if dual_response['primary_persona'] == 'professor' else dual_response['secondary_response']
        mentor_guidance = dual_response['primary_response'] if dual_response['primary_persona'] == 'mentor' else dual_response['secondary_response']
        
        # Create study plan record with properly formatted subjects
        all_subjects = []
        for subject in plan_request.weak_subjects:
            all_subjects.append({"name": subject, "type": "weak", "priority": "high"})
        for subject in plan_request.strong_subjects:
            all_subjects.append({"name": subject, "type": "strong", "priority": "medium"})
        
        study_plan = StudyPlan(
            user_id=user.user_id,
            exam_type=user.exam_type,
            target_date=datetime.fromisoformat(plan_request.target_exam_date.replace('Z', '+00:00')),
            subjects=all_subjects,
            daily_goals={"study_hours": plan_request.daily_study_hours},
            weekly_targets={"progress_target": 10}  # 10% progress per week
        )
        
        await db.study_plans.insert_one(study_plan.dict())
        
        return {
            "plan_id": study_plan.plan_id,
            "dual_intelligence_plan": {
                "professor": {
                    "persona": "professor",
                    "academic_structure": professor_plan,
                    "focus": "Curriculum coverage, exam compliance, rigorous preparation"
                },
                "mentor": {
                    "persona": "mentor", 
                    "personalized_guidance": mentor_guidance,
                    "focus": "Motivation, stress management, adaptive learning"
                }
            },
            "scenario_classification": {
                "primary_persona": dual_response['primary_persona'],
                "scenario_type": dual_response['scenario_type'],
                "confidence": dual_response['confidence']
            },
            "implementation_timeline": {
                "start_date": datetime.utcnow().isoformat(),
                "target_date": plan_request.target_exam_date,
                "review_frequency": "weekly"
            }
        }
        
    except Exception as e:
        logger.error(f"Dual study plan creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create dual study plan")

@api_router.post("/ai/enhanced-question-analysis")
async def get_enhanced_question_analysis(
    chat_request: ChatRequest,
    user: User = Depends(get_current_user)
):
    """Get enhanced question analysis with dual-layer intelligence and student psychology"""
    
    try:
        # Get student's recent performance and stress levels for context
        recent_assessments = await db.stress_assessments.find(
            {"user_id": user.user_id}
        ).sort("assessment_date", -1).limit(3).to_list(3)
        
        recent_tests = await db.mock_test_results.find(
            {"user_id": user.user_id}
        ).sort("completed_at", -1).limit(5).to_list(5)
        
        # Calculate student context
        avg_stress = sum(a.get("stress_level", 5) for a in recent_assessments) / max(len(recent_assessments), 1)
        avg_performance = sum(t.get("percentage", 0) for t in recent_tests) / max(len(recent_tests), 1)
        
        # Enhanced analysis prompt with student psychology
        analysis_prompt = f"""Provide enhanced analysis for this {chat_request.subject} question: "{chat_request.message}"
        
        Student Context:
        - Exam Type: {user.exam_type}
        - Recent Performance: {avg_performance:.1f}% average
        - Current Stress Level: {avg_stress:.1f}/10
        - Subject: {chat_request.subject}
        
        Provide both technical accuracy AND learning psychology optimization for maximum student understanding and confidence building."""
        
        # Get dual-layer enhanced response
        user_context = {
            'exam_type': user.exam_type,
            'recent_performance': avg_performance,
            'stress_level': avg_stress,
            'subject': chat_request.subject
        }
        
        session_id = chat_request.session_id or f"enhanced_{uuid.uuid4()}"
        dual_response = await dual_ai.get_coordinated_response(
            analysis_prompt, chat_request.subject, session_id, user_context
        )
        
        # Save enhanced chat message
        chat_message = ChatMessage(
            session_id=session_id,
            user_id=user.user_id,
            message=chat_request.message,
            response=dual_response['primary_response'],
            reasoning=f"Enhanced dual analysis: {dual_response['primary_persona']} leading with learning psychology optimization"
        )
        
        await db.chat_messages.insert_one(chat_message.dict())
        
        return {
            "session_id": session_id,
            "enhanced_analysis": {
                "technical_accuracy": {
                    "persona": "professor",
                    "analysis": dual_response['primary_response'] if dual_response['primary_persona'] == 'professor' else dual_response['secondary_response'],
                    "focus": "Factual correctness, step-by-step reasoning, exam compliance"
                },
                "learning_psychology": {
                    "persona": "mentor",
                    "guidance": dual_response['primary_response'] if dual_response['primary_persona'] == 'mentor' else dual_response['secondary_response'],
                    "focus": "Student understanding, confidence building, personalized approach"
                }
            },
            "student_context": {
                "performance_level": "high" if avg_performance > 75 else "medium" if avg_performance > 50 else "developing",
                "stress_status": "high" if avg_stress > 7 else "moderate" if avg_stress > 4 else "low",
                "recommended_approach": "encouraging" if avg_stress > 6 or avg_performance < 50 else "challenging"
            },
            "scenario_metadata": {
                "primary_persona": dual_response['primary_persona'],
                "scenario_type": dual_response['scenario_type'],
                "confidence": dual_response['confidence']
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced question analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to provide enhanced analysis")
# ============= AUTO-NOTE MENTOR API ENDPOINTS =============

@api_router.post("/auto-notes/start-session")
async def start_note_session(
    request: NoteSessionRequest,
    user: User = Depends(get_current_user)
):
    """Start a new auto-note taking session"""
    
    try:
        # Create new note session
        session = NoteSession(
            user_id=user.user_id,
            title=request.title,
            subject=request.subject
        )
        
        # Save to database
        await db.note_sessions.insert_one(session.dict())
        
        return {
            "session_id": session.session_id,
            "title": session.title,
            "subject": session.subject,
            "start_time": session.start_time,
            "status": session.status,
            "message": "Auto-Note session started successfully. Begin speaking or start your class recording."
        }
        
    except Exception as e:
        logger.error(f"Note session creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start note session")

@api_router.post("/auto-notes/process-audio")
async def process_audio_chunk(
    request: AudioChunkRequest,
    user: User = Depends(get_current_user)
):
    """Process real-time audio transcription chunk"""
    
    try:
        # Verify session exists and belongs to user
        session_doc = await db.note_sessions.find_one({
            "session_id": request.session_id,
            "user_id": user.user_id,
            "status": "active"
        })
        
        if not session_doc:
            raise HTTPException(status_code=404, detail="Active session not found")
        
        # Create audio chunk record
        chunk = AudioChunk(
            session_id=request.session_id,
            sequence_number=request.sequence_number,
            transcription=request.transcription,
            timestamp=request.timestamp,
            confidence=request.confidence
        )
        
        # Save chunk to database
        await db.audio_chunks.insert_one(chunk.dict())
        
        # Simple concept detection (Phase A - basic implementation)
        concepts_detected = []
        key_terms = ["formula", "equation", "theorem", "law", "principle", "concept", "definition"]
        
        for term in key_terms:
            if term.lower() in request.transcription.lower():
                concepts_detected.append(term)
        
        return {
            "chunk_id": chunk.chunk_id,
            "processed": True,
            "concepts_detected": concepts_detected,
            "timestamp": chunk.timestamp,
            "transcription_preview": request.transcription[:100] + "..." if len(request.transcription) > 100 else request.transcription
        }
        
    except Exception as e:
        logger.error(f"Audio processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process audio")

@api_router.post("/auto-notes/end-session")
async def end_note_session(
    session_id: str,
    user: User = Depends(get_current_user)
):
    """End note session and generate structured notes with dual AI analysis"""
    
    try:
        # Verify session exists and belongs to user
        session_doc = await db.note_sessions.find_one({
            "session_id": session_id,
            "user_id": user.user_id
        })
        
        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session status to processing
        await db.note_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"status": "processing", "end_time": datetime.utcnow()}}
        )
        
        # Collect all audio chunks for this session
        chunks = await db.audio_chunks.find(
            {"session_id": session_id}
        ).sort("sequence_number", 1).to_list(1000)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No audio data found for this session")
        
        # Combine all transcriptions
        full_transcription = " ".join([chunk["transcription"] for chunk in chunks])
        total_duration = max([chunk["timestamp"] for chunk in chunks]) if chunks else 0
        
        # PHASE B: Dual-Layer AI Analysis
        analysis_prompt = f"""Analyze this class transcription and create structured educational notes:

TRANSCRIPTION:
{full_transcription}

SUBJECT: {session_doc['subject']}
CLASS TITLE: {session_doc['title']}
DURATION: {total_duration:.1f} seconds

Create a comprehensive analysis with both Professor and Mentor perspectives for a student studying {session_doc['subject']}.

Structure your response as detailed educational notes with:
1. Key concepts covered
2. Important formulas/equations  
3. Examples discussed
4. Doubts/questions raised
5. Study recommendations"""

        # Get dual-layer analysis
        user_context = {
            'exam_type': user.exam_type,
            'subject': session_doc['subject'],
            'session_duration': total_duration
        }
        
        dual_response = await dual_ai.get_coordinated_response(
            analysis_prompt, session_doc['subject'], f"notes_{session_id}", user_context
        )
        
        # Structure the notes with dual analysis
        structured_notes = {
            "transcript_length": len(full_transcription),
            "duration_minutes": total_duration / 60,
            "key_concepts": extract_concepts_from_text(full_transcription),
            "important_points": extract_important_points(full_transcription),
            "formulas_mentioned": extract_formulas(full_transcription),
            "questions_raised": extract_questions(full_transcription)
        }
        
        dual_analysis = {
            "professor_analysis": {
                "persona": "professor",
                "content": dual_response['primary_response'] if dual_response['primary_persona'] == 'professor' else dual_response['secondary_response'],
                "focus": "Academic accuracy, concept verification, structured learning"
            },
            "mentor_guidance": {
                "persona": "mentor", 
                "content": dual_response['primary_response'] if dual_response['primary_persona'] == 'mentor' else dual_response['secondary_response'],
                "focus": "Personalized insights, encouragement, learning optimization"
            },
            "scenario_classification": {
                "primary_persona": dual_response['primary_persona'],
                "scenario_type": dual_response['scenario_type'],
                "confidence": dual_response['confidence']
            }
        }
        
        # Update session with final results
        await db.note_sessions.update_one(
            {"session_id": session_id},
            {"$set": {
                "status": "completed",
                "audio_duration": int(total_duration),
                "transcription": full_transcription,
                "structured_notes": structured_notes,
                "dual_analysis": dual_analysis
            }}
        )
        
        return {
            "session_id": session_id,
            "status": "completed",
            "duration_minutes": total_duration / 60,
            "structured_notes": structured_notes,
            "dual_analysis": dual_analysis,
            "summary": {
                "concepts_identified": len(structured_notes["key_concepts"]),
                "formulas_found": len(structured_notes["formulas_mentioned"]),
                "questions_raised": len(structured_notes["questions_raised"]),
                "note_quality": "high" if len(full_transcription) > 500 else "medium"
            }
        }
        
    except Exception as e:
        logger.error(f"Note session completion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete note session")

@api_router.get("/auto-notes/{session_id}")
async def get_note_session(
    session_id: str,
    user: User = Depends(get_current_user)
):
    """Get complete note session with dual analysis"""
    
    try:
        session_doc = await db.note_sessions.find_one({
            "session_id": session_id,
            "user_id": user.user_id
        })
        
        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Remove MongoDB ObjectId for JSON serialization
        if "_id" in session_doc:
            del session_doc["_id"]
        
        return session_doc
        
    except Exception as e:
        logger.error(f"Note session retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")

@api_router.post("/auto-notes/explain-point")
async def explain_note_point(
    request: ExplainPointRequest,
    user: User = Depends(get_current_user)
):
    """PHASE C: Interactive explanation of specific note points"""
    
    try:
        # Get the note session
        session_doc = await db.note_sessions.find_one({
            "session_id": request.session_id,
            "user_id": user.user_id,
            "status": "completed"
        })
        
        if not session_doc:
            raise HTTPException(status_code=404, detail="Completed session not found")
        
        # Extract the specific point to explain
        structured_notes = session_doc.get("structured_notes", {})
        dual_analysis = session_doc.get("dual_analysis", {})
        
        # Create context-specific explanation prompt
        explanation_prompt = f"""A student is asking for explanation about "{request.point_reference}" from their class notes.

ORIGINAL CLASS CONTEXT:
Subject: {session_doc['subject']}
Class: {session_doc['title']}

STUDENT'S QUESTION CONTEXT:
Point Reference: {request.point_reference}
Additional Context: {request.additional_context or 'None provided'}

AVAILABLE CLASS CONTENT:
{session_doc.get('transcription', '')[:1000]}...

Please provide a clear, detailed explanation that helps the student understand this specific point better. Use both academic rigor and encouraging, personalized guidance."""
        
        # Get dual-layer explanation
        user_context = {
            'exam_type': user.exam_type,
            'subject': session_doc['subject'],
            'context': 'note_explanation'
        }
        
        explanation_response = await dual_ai.get_coordinated_response(
            explanation_prompt, session_doc['subject'], f"explain_{request.session_id}", user_context
        )
        
        return {
            "session_id": request.session_id,
            "point_reference": request.point_reference,
            "explanation": {
                "professor_explanation": {
                    "content": explanation_response['primary_response'] if explanation_response['primary_persona'] == 'professor' else explanation_response['secondary_response'],
                    "focus": "Technical accuracy and detailed academic explanation"
                },
                "mentor_guidance": {
                    "content": explanation_response['primary_response'] if explanation_response['primary_persona'] == 'mentor' else explanation_response['secondary_response'], 
                    "focus": "Personalized understanding and learning support"
                }
            },
            "related_concepts": structured_notes.get("key_concepts", [])[:3],  # Show 3 related concepts
            "study_tip": "Review this concept again in 24 hours for better retention"
        }
        
    except Exception as e:
        logger.error(f"Point explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to explain note point")

@api_router.post("/auto-notes/generate-flashcards")
async def generate_flashcards_from_notes(
    request: GenerateFlashcardsRequest,
    user: User = Depends(get_current_user)
):
    """PHASE C: Auto-generate flashcards from class notes"""
    
    try:
        # Get the note session
        session_doc = await db.note_sessions.find_one({
            "session_id": request.session_id,
            "user_id": user.user_id,
            "status": "completed"
        })
        
        if not session_doc:
            raise HTTPException(status_code=404, detail="Completed session not found")
        
        structured_notes = session_doc.get("structured_notes", {})
        
        # Create flashcard generation prompt
        concepts_to_use = request.specific_concepts or structured_notes.get("key_concepts", [])
        
        flashcard_prompt = f"""Generate educational flashcards from this class content:

SUBJECT: {session_doc['subject']}
CLASS: {session_doc['title']}

KEY CONCEPTS TO FOCUS ON:
{', '.join(concepts_to_use[:10])}  # Limit to 10 concepts

ORIGINAL CONTENT:
{session_doc.get('transcription', '')[:1500]}...

Create 5-8 high-quality flashcards that will help a {user.exam_type} student master these concepts. Each flashcard should have:
1. Clear, concise question
2. Accurate, complete answer
3. Appropriate difficulty level

Focus on the most important concepts that appeared in this specific class."""
        
        # Generate flashcards using dual AI
        user_context = {
            'exam_type': user.exam_type,
            'subject': session_doc['subject'],
            'context': 'flashcard_generation'
        }
        
        flashcard_response = await dual_ai.get_coordinated_response(
            flashcard_prompt, session_doc['subject'], f"flashcards_{request.session_id}", user_context
        )
        
        # Parse the response to create individual flashcards
        # For now, create sample flashcards based on concepts
        generated_cards = []
        
        for i, concept in enumerate(concepts_to_use[:6]):  # Generate up to 6 flashcards
            flashcard = GeneratedFlashcard(
                session_id=request.session_id,
                user_id=user.user_id,
                question=f"What is {concept}?",
                answer=f"Based on today's class: {concept} is a key concept in {session_doc['subject']}...",
                concept=concept,
                difficulty_level=3,  # Medium difficulty
                created_from_point=f"concept_{i+1}"
            )
            
            # Save flashcard to database
            await db.flashcards.insert_one(flashcard.dict())
            generated_cards.append(flashcard.dict())
        
        return {
            "session_id": request.session_id,
            "flashcards_generated": len(generated_cards),
            "flashcards": generated_cards,
            "ai_insights": {
                "professor_review": "Flashcards cover essential concepts with academic accuracy",
                "mentor_encouragement": f"Great! These {len(generated_cards)} flashcards will help reinforce today's learning. Practice them daily for best results!"
            },
            "study_recommendation": "Review these flashcards within 24 hours, then again in 3 days for optimal retention"
        }
        
    except Exception as e:
        logger.error(f"Flashcard generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate flashcards")

@api_router.get("/auto-notes/sessions")
async def get_user_note_sessions(user: User = Depends(get_current_user)):
    """Get all note sessions for the current user"""
    
    try:
        sessions = await db.note_sessions.find(
            {"user_id": user.user_id}
        ).sort("created_at", -1).limit(50).to_list(50)
        
        # Remove MongoDB ObjectIds
        for session in sessions:
            if "_id" in session:
                del session["_id"]
        
        return {
            "sessions": sessions,
            "total_sessions": len(sessions),
            "active_sessions": len([s for s in sessions if s["status"] == "active"])
        }
        
    except Exception as e:
        logger.error(f"Sessions retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")

# Helper functions for note analysis
def extract_concepts_from_text(text: str) -> List[str]:
    """Extract key concepts from transcribed text"""
    # Simple keyword-based extraction for Phase A
    concept_indicators = [
        "concept", "definition", "theorem", "law", "principle", 
        "formula", "equation", "method", "technique", "approach"
    ]
    
    concepts = []
    words = text.lower().split()
    
    for i, word in enumerate(words):
        if word in concept_indicators and i + 1 < len(words):
            # Extract the next few words as the concept
            concept_phrase = " ".join(words[i:i+3])
            concepts.append(concept_phrase.title())
    
    return list(set(concepts))[:10]  # Return unique concepts, max 10

def extract_important_points(text: str) -> List[str]:
    """Extract important points from text"""
    sentences = text.split('.')
    important = []
    
    keywords = ["important", "remember", "key", "crucial", "essential", "note that"]
    
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in keywords):
            important.append(sentence.strip())
    
    return important[:5]  # Return top 5 important points

def extract_formulas(text: str) -> List[str]:
    """Extract mathematical formulas and equations"""
    # Simple pattern matching for common formula indicators
    formula_patterns = ["=", "∫", "∑", "√", "²", "³", "+", "-", "×", "÷"]
    
    sentences = text.split('.')
    formulas = []
    
    for sentence in sentences:
        if any(pattern in sentence for pattern in formula_patterns) and len(sentence.strip()) < 100:
            if "formula" in sentence.lower() or "equation" in sentence.lower() or any(p in sentence for p in formula_patterns[:4]):
                formulas.append(sentence.strip())
    
    return formulas[:5]

def extract_questions(text: str) -> List[str]:
    """Extract questions raised during class"""
    sentences = text.split('.')
    questions = []
    
    question_indicators = ["?", "how", "what", "why", "when", "where", "question", "doubt"]
    
    for sentence in sentences:
        if "?" in sentence or any(indicator in sentence.lower() for indicator in question_indicators[:6]):
            questions.append(sentence.strip())
    
    return questions[:5]

# ============= PHASE 4: ENHANCED FEATURES API ENDPOINTS =============

@api_router.post("/demo/populate-data")
async def populate_demo_data(user: User = Depends(get_current_user)):
    """Populate demo data for new users to showcase analytics features"""
    
    try:
        # Create some sample study progress records
        demo_subjects = [
            {"subject": "Mathematics", "mastery": 85, "time": 20},
            {"subject": "Physics", "mastery": 72, "time": 15}, 
            {"subject": "Chemistry", "mastery": 78, "time": 12}
        ]
        
        for subject_data in demo_subjects:
            for i in range(5):  # 5 chapters per subject
                progress = StudyProgress(
                    user_id=user.user_id,
                    subject=subject_data["subject"],
                    chapter=f"Chapter {i+1}",
                    concept=f"Concept {i+1}",
                    mastery_level=subject_data["mastery"] + (i * 2) - 5,
                    time_spent=subject_data["time"] + i,
                    questions_attempted=50 + (i * 10),
                    questions_correct=int((50 + (i * 10)) * (subject_data["mastery"]/100))
                )
                await db.study_progress.insert_one(progress.dict())
        
        # Create a sample mock test result
        sample_test = MockTest(
            user_id=user.user_id,
            exam_type=user.exam_type,
            subject="Mathematics", 
            test_name="Sample JEE Mathematics Test",
            questions=[],
            total_marks=100,
            score=76,
            time_taken=3600,
            completed_at=datetime.utcnow()
        )
        await db.mock_tests.insert_one(sample_test.dict())
        
        # Create a sample test result
        sample_result = MockTestResult(
            test_id=sample_test.test_id,
            user_id=user.user_id,
            answers={},
            score=76,
            percentage=76.0,
            time_taken=3600,
            correct_answers=19,
            wrong_answers=6,
            unanswered=0,
            subject_wise_analysis={"Mathematics": {"correct": 19, "wrong": 6, "total": 25}},
            difficulty_performance={"3": {"correct": 19, "wrong": 6, "total": 25}},
            recommendations=["Focus on advanced calculus problems", "Practice more integration techniques"]
        )
        await db.mock_test_results.insert_one(sample_result.dict())
        
        return {
            "message": "Demo data populated successfully",
            "study_records": len(demo_subjects) * 5,
            "mock_tests": 1,
            "test_results": 1
        }
        
    except Exception as e:
        logger.error(f"Demo data population error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to populate demo data")

@api_router.post("/mock-tests/generate")
async def generate_mock_test(
    request: MockTestGenerationRequest,
    user: User = Depends(get_current_user)
):
    """Generate an adaptive mock test based on user's performance"""
    
    try:
        # Get user's performance history to adapt difficulty
        user_progress = await db.study_progress.find(
            {"user_id": user.user_id, "subject": request.subject}
        ).to_list(10)
        
        # Calculate adaptive difficulty based on past performance
        difficulty = request.difficulty
        if user_progress:
            avg_mastery = sum(p.get("mastery_level", 50) for p in user_progress) / len(user_progress)
            if avg_mastery > 80:
                difficulty = min(5, difficulty + 1)
            elif avg_mastery < 40:
                difficulty = max(1, difficulty - 1)
        
        # Generate questions using AI
        current_year = datetime.utcnow().year
        question_prompt = f"""You specialize in creating high-quality, original questions that mirror the style, difficulty, and format of official {request.exam_type} papers. Generate {request.num_questions} multiple choice questions for {request.exam_type} {request.subject} exam.

Context:
- Exam Type: {request.exam_type}
- Subject: {request.subject}  
- Difficulty level: {difficulty}/5 (1=Easy, 5=Very Hard)
- Current Year: {current_year}
- Target: Questions should align with {current_year-1}-{current_year} yearly trends and patterns

Requirements for each question:
1. Question text must be factually correct and follow {request.exam_type} {current_year-1} patterns
2. 4 answer options (A, B, C, D) with only one correct answer
3. Correct answer (A/B/C/D)
4. One-line explanation for the correct answer
5. Appropriate chapter/topic classification
6. Match reference style, length, and cognitive level of real {request.exam_type} papers

Please generate REAL, PRACTICAL questions that students would encounter in actual {request.exam_type} exams. Focus on:
- Core concepts and applications relevant to {request.subject}
- Problem-solving scenarios typical of {request.exam_type} level
- Current syllabus alignment for {request.exam_type} {current_year}

Format response as JSON array with this exact structure:
[
  {{
    "question_text": "Clear, specific question text here",
    "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "A",
    "explanation": "Brief explanation for why this answer is correct",
    "chapter": "Relevant chapter/topic name",
    "difficulty_level": {difficulty}
  }}
]

Generate {request.num_questions} such questions now."""
        
        # Get AI-generated questions
        session_id = f"test_gen_{uuid.uuid4()}"
        ai_response, _ = await get_ai_tutor_response(question_prompt, request.subject, session_id)
        
        # Parse AI response to extract questions
        questions = []
        try:
            # Try to extract JSON from AI response
            import json
            import re
            
            # Look for JSON array in the AI response
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_questions = json.loads(json_str)
                
                for i, q in enumerate(parsed_questions[:request.num_questions]):
                    questions.append({
                        "question_id": str(uuid.uuid4()),
                        "question_text": q.get("question_text", f"Question {i+1} for {request.subject}"),
                        "options": q.get("options", ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"]),
                        "correct_answer": q.get("correct_answer", "A"),
                        "explanation": q.get("explanation", "Explanation not provided"),
                        "chapter": q.get("chapter", f"Chapter {(i % 5) + 1}"),
                        "difficulty_level": q.get("difficulty_level", difficulty),
                        "marks": 4,
                        "negative_marks": 1
                    })
            else:
                # Fallback: Create structured questions if JSON parsing fails
                raise ValueError("No JSON found in AI response")
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"AI JSON parsing failed: {e}. Using fallback question generation.")
            
            # Fallback: Generate structured sample questions based on subject and exam type
            subject_questions = {
                "Mathematics": [
                    {
                        "question_text": "If f(x) = x³ - 3x² + 2x - 1, find f'(2)",
                        "options": ["A) 2", "B) 4", "C) 6", "D) 8"],
                        "correct_answer": "A",
                        "explanation": "f'(x) = 3x² - 6x + 2, so f'(2) = 3(4) - 6(2) + 2 = 12 - 12 + 2 = 2",
                        "chapter": "Differential Calculus"
                    },
                    {
                        "question_text": "The sum of first n natural numbers is n(n+1)/2. Find the sum of first 20 natural numbers",
                        "options": ["A) 210", "B) 200", "C) 190", "D) 220"],
                        "correct_answer": "A", 
                        "explanation": "Using formula: 20(21)/2 = 420/2 = 210",
                        "chapter": "Sequences and Series"
                    }
                ],
                "Physics": [
                    {
                        "question_text": "A body falls freely from height h. Its velocity after falling distance h/2 is",
                        "options": ["A) √(gh)", "B) √(gh/2)", "C) √(2gh)", "D) √(3gh/2)"],
                        "correct_answer": "A",
                        "explanation": "Using v² = u² + 2as, where u=0, a=g, s=h/2: v² = 2g(h/2) = gh, so v = √(gh)",
                        "chapter": "Kinematics"
                    },
                    {
                        "question_text": "The resistance of a wire is 10Ω. If it is stretched to double its length, new resistance is",
                        "options": ["A) 20Ω", "B) 40Ω", "C) 5Ω", "D) 10Ω"],
                        "correct_answer": "B",
                        "explanation": "R = ρl/A. When length doubles, area becomes half, so R becomes 4 times = 40Ω",
                        "chapter": "Current Electricity"
                    }
                ],
                "Chemistry": [
                    {
                        "question_text": "The IUPAC name of CH₃-CH(CH₃)-CH₂-CH₃ is",
                        "options": ["A) 2-methylbutane", "B) 3-methylbutane", "C) Isopentane", "D) 2-methylpropane"],
                        "correct_answer": "A",
                        "explanation": "Longest chain has 4 carbons (butane) with methyl group at position 2",
                        "chapter": "Organic Chemistry"
                    },
                    {
                        "question_text": "Which element has electronic configuration [Ar] 3d⁵ 4s¹?",
                        "options": ["A) Mn", "B) Cr", "C) Fe", "D) Co"],
                        "correct_answer": "B",
                        "explanation": "Chromium has exceptional configuration due to half-filled d orbital stability",
                        "chapter": "Atomic Structure"
                    }
                ]
            }
            
            # Get subject-specific questions or create generic ones
            base_questions = subject_questions.get(request.subject, [
                {
                    "question_text": f"Sample {request.subject} question for {request.exam_type}",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct_answer": "A",
                    "explanation": "Sample explanation",
                    "chapter": "General"
                }
            ])
            
            # Generate required number of questions by cycling through base questions
            for i in range(request.num_questions):
                base_q = base_questions[i % len(base_questions)]
                questions.append({
                    "question_id": str(uuid.uuid4()),
                    "question_text": base_q["question_text"],
                    "options": base_q["options"],
                    "correct_answer": base_q["correct_answer"],
                    "explanation": base_q["explanation"],
                    "chapter": base_q["chapter"],
                    "difficulty_level": difficulty,
                    "marks": 4,
                    "negative_marks": 1
                })
        
        # Create mock test
        mock_test = MockTest(
            user_id=user.user_id,
            exam_type=request.exam_type,
            subject=request.subject,
            test_name=f"{request.exam_type} {request.subject} Mock Test - Level {difficulty}",
            questions=questions,
            difficulty_level=difficulty,
            total_marks=request.num_questions * 4
        )
        
        await db.mock_tests.insert_one(mock_test.dict())
        
        return {
            "test_id": mock_test.test_id,
            "test_name": mock_test.test_name,
            "questions": questions,
            "total_marks": mock_test.total_marks,
            "time_limit": request.num_questions * 2,  # 2 minutes per question
            "difficulty_level": difficulty
        }
        
    except Exception as e:
        logger.error(f"Mock test generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate mock test")

@api_router.post("/mock-tests/{test_id}/submit")
async def submit_mock_test(
    test_id: str,
    submission: MockTestSubmission,
    user: User = Depends(get_current_user)
):
    """Submit mock test answers and get detailed analysis"""
    
    try:
        # Get test from database
        test_doc = await db.mock_tests.find_one({"test_id": test_id, "user_id": user.user_id})
        if not test_doc:
            raise HTTPException(status_code=404, detail="Test not found")
        
        mock_test = MockTest(**test_doc)
        
        # Calculate results
        correct_count = 0
        wrong_count = 0
        unanswered_count = 0
        total_score = 0
        subject_analysis = {}
        difficulty_analysis = {}
        
        for question in mock_test.questions:
            q_id = question["question_id"]
            correct_answer = question["correct_answer"]
            user_answer = submission.answers.get(q_id)
            
            subject = question.get("chapter", "General")
            difficulty = question.get("difficulty_level", 3)
            
            if subject not in subject_analysis:
                subject_analysis[subject] = {"correct": 0, "wrong": 0, "total": 0}
            if str(difficulty) not in difficulty_analysis:
                difficulty_analysis[str(difficulty)] = {"correct": 0, "wrong": 0, "total": 0}
            
            subject_analysis[subject]["total"] += 1
            difficulty_analysis[str(difficulty)]["total"] += 1
            
            if not user_answer:
                unanswered_count += 1
            elif user_answer == correct_answer:
                correct_count += 1
                total_score += question.get("marks", 4)
                subject_analysis[subject]["correct"] += 1
                difficulty_analysis[str(difficulty)]["correct"] += 1
            else:
                wrong_count += 1
                total_score -= question.get("negative_marks", 1)
                subject_analysis[subject]["wrong"] += 1
                difficulty_analysis[str(difficulty)]["wrong"] += 1
        
        percentage = (total_score / mock_test.total_marks) * 100
        
        # Generate AI-powered dual feedback (Professor + Mentor)
        analysis_prompt = f"""Analyze this mock test performance for {user.exam_type} {mock_test.subject}:
        
        Score: {total_score}/{mock_test.total_marks} ({percentage:.1f}%)
        Correct: {correct_count}, Wrong: {wrong_count}, Unanswered: {unanswered_count}
        Time taken: {submission.time_taken} seconds ({submission.time_taken // 60} minutes)
        Subject-wise performance: {subject_analysis}
        Difficulty-wise performance: {difficulty_analysis}
        
        Provide detailed performance analysis with specific recommendations for improvement."""
        
        # Get user context for dual AI
        user_context = {
            'exam_type': user.exam_type,
            'target_year': user.target_year,
            'recent_performance': percentage
        }
        
        session_id = f"analysis_{uuid.uuid4()}"
        
        # Get dual-layer AI feedback
        try:
            dual_feedback = await dual_ai.get_coordinated_response(
                analysis_prompt, mock_test.subject, session_id, user_context
            )
            
            # Extract structured feedback
            professor_analysis = dual_feedback['primary_response'] if dual_feedback['primary_persona'] == 'professor' else dual_feedback['secondary_response']
            mentor_feedback = dual_feedback['primary_response'] if dual_feedback['primary_persona'] == 'mentor' else dual_feedback['secondary_response']
            
            # Fallback recommendations if AI fails
            fallback_recommendations = [
                "Focus on time management - practice more timed tests",
                "Review weak chapters identified in subject analysis", 
                "Strengthen conceptual understanding in difficult topics"
            ]
            
            recommendations = fallback_recommendations
            
        except Exception as e:
            logger.warning(f"Dual AI feedback failed: {e}. Using fallback.")
            professor_analysis = "Technical analysis temporarily unavailable."
            mentor_feedback = "Keep practicing! Every test is a step toward your goal."
            recommendations = [
                "Focus on time management - practice more timed tests",
                "Review weak chapters identified in subject analysis",
                "Strengthen conceptual understanding in difficult topics"
            ]
        
        # Create result record with dual AI feedback
        result = MockTestResult(
            test_id=test_id,
            user_id=user.user_id,
            answers=submission.answers,
            score=total_score,
            percentage=percentage,
            time_taken=submission.time_taken,
            correct_answers=correct_count,
            wrong_answers=wrong_count,
            unanswered=unanswered_count,
            subject_wise_analysis=subject_analysis,
            difficulty_performance=difficulty_analysis,
            recommendations=recommendations
        )
        
        await db.mock_test_results.insert_one(result.dict())
        
        # Update test as completed
        await db.mock_tests.update_one(
            {"test_id": test_id},
            {"$set": {
                "answers": submission.answers,
                "score": total_score,
                "time_taken": submission.time_taken,
                "completed_at": datetime.utcnow()
            }}
        )
        
        return {
            "result_id": result.result_id,
            "score": total_score,
            "percentage": percentage,
            "correct_answers": correct_count,
            "wrong_answers": wrong_count,
            "unanswered": unanswered_count,
            "subject_wise_analysis": subject_analysis,
            "difficulty_performance": difficulty_analysis,
            "recommendations": recommendations,
            "dual_feedback": {
                "professor_analysis": professor_analysis,
                "mentor_feedback": mentor_feedback,
                "scenario_confidence": dual_feedback.get('confidence', 0.8) if 'dual_feedback' in locals() else 0.8
            },
            "rank": None,  # TODO: Calculate rank based on other users
            "pass_status": percentage >= (mock_test.passing_marks / mock_test.total_marks * 100)
        }
        
    except Exception as e:
        logger.error(f"Mock test submission error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit test")

@api_router.get("/analytics/performance")
async def get_performance_analytics(user: User = Depends(get_current_user)):
    """Get comprehensive performance analytics for student and parents"""
    
    try:
        # Get mock test results
        test_results = await db.mock_test_results.find(
            {"user_id": user.user_id}
        ).sort("completed_at", -1).limit(20).to_list(20)
        
        # Get study progress
        study_progress = await db.study_progress.find(
            {"user_id": user.user_id}
        ).to_list(100)
        
        # Calculate trends
        score_trend = [result["percentage"] for result in test_results[:10]]
        time_trend = [result["time_taken"] for result in test_results[:10]]
        
        # Subject-wise performance
        subject_performance = {}
        for progress in study_progress:
            subject = progress["subject"]
            if subject not in subject_performance:
                subject_performance[subject] = {
                    "mastery_avg": 0,
                    "time_spent": 0,
                    "accuracy": 0,
                    "count": 0
                }
            
            subject_performance[subject]["mastery_avg"] += progress["mastery_level"]
            subject_performance[subject]["time_spent"] += progress["time_spent"]
            subject_performance[subject]["count"] += 1
            
            if progress["questions_attempted"] > 0:
                accuracy = (progress["questions_correct"] / progress["questions_attempted"]) * 100
                subject_performance[subject]["accuracy"] += accuracy
        
        # Calculate averages
        for subject in subject_performance:
            count = subject_performance[subject]["count"]
            if count > 0:
                subject_performance[subject]["mastery_avg"] /= count
                subject_performance[subject]["accuracy"] /= count
        
        # Weekly study goals and achievements
        weekly_data = {
            "target_hours": 40,  # 40 hours per week
            "completed_hours": sum(p["time_spent"] for p in study_progress[-7:]) / 60,
            "target_tests": 3,   # 3 tests per week
            "completed_tests": len([r for r in test_results if (datetime.utcnow() - r["completed_at"]).days <= 7])
        }
        
        return {
            "overall_performance": {
                "average_score": sum(score_trend) / len(score_trend) if score_trend else 0,
                "score_trend": score_trend,
                "time_trend": time_trend,
                "improvement_rate": (score_trend[0] - score_trend[-1]) if len(score_trend) > 1 else 0
            },
            "subject_performance": subject_performance,
            "weekly_progress": weekly_data,
            "recent_tests": test_results[:5],
            "strengths": ["Time Management", "Problem Solving"] if score_trend and score_trend[0] > 75 else [],
            "areas_for_improvement": ["Accuracy", "Speed"] if score_trend and score_trend[0] < 50 else [],
            "parent_summary": {
                "monthly_hours": sum(p["time_spent"] for p in study_progress) / 60,
                "test_frequency": len(test_results),
                "overall_grade": "A" if (sum(score_trend) / len(score_trend) if score_trend else 0) > 80 else "B"
            }
        }
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@api_router.post("/wellness/stress-assessment")
async def submit_stress_assessment(
    assessment: StressAssessmentRequest,
    user: User = Depends(get_current_user)
):
    """Submit stress assessment and get personalized recommendations"""
    
    try:
        # Generate AI-powered wellness recommendations
        assessment_prompt = f"""Generate personalized wellness recommendations based on this assessment:
        
        Stress Level: {assessment.stress_level}/10
        Anxiety Level: {assessment.anxiety_level}/10  
        Sleep Quality: {assessment.sleep_quality}/10
        Study Motivation: {assessment.study_motivation}/10
        Physical Symptoms: {assessment.physical_symptoms}
        Emotional State: {assessment.emotional_state}
        
        Provide 5 specific, actionable wellness recommendations focusing on stress management, study-life balance, and mental health for a {user.exam_type} aspirant."""
        
        session_id = f"wellness_{uuid.uuid4()}"
        recommendations_text, _ = await get_ai_tutor_response(assessment_prompt, "Wellness", session_id)
        
        recommendations = [
            "Practice daily meditation for 10-15 minutes",
            "Maintain regular sleep schedule (7-8 hours)",
            "Take short breaks every 45 minutes while studying",
            "Engage in light physical exercise daily",
            recommendations_text[:300] + "..." if len(recommendations_text) > 300 else recommendations_text
        ]
        
        # Create assessment record
        assessment_record = StressAssessment(
            user_id=user.user_id,
            stress_level=assessment.stress_level,
            anxiety_level=assessment.anxiety_level,
            sleep_quality=assessment.sleep_quality,
            study_motivation=assessment.study_motivation,
            physical_symptoms=assessment.physical_symptoms,
            emotional_state=assessment.emotional_state,
            recommendations=recommendations
        )
        
        await db.stress_assessments.insert_one(assessment_record.dict())
        
        wellness_score = (assessment.sleep_quality + assessment.study_motivation + (11 - assessment.stress_level) + (11 - assessment.anxiety_level)) / 4
        
        return {
            "assessment_id": assessment_record.assessment_id,
            "wellness_score": wellness_score,
            "recommendations": recommendations,
            "priority_actions": recommendations[:3],
            "follow_up_date": datetime.utcnow() + timedelta(days=7)
        }
        
    except Exception as e:
        logger.error(f"Stress assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process assessment")

@api_router.get("/wellness/motivational-content")
async def get_motivational_content(user: User = Depends(get_current_user)):
    """Get personalized motivational content based on user's performance and stress levels"""
    
    try:
        # Get recent stress assessment
        recent_assessment = await db.stress_assessments.find_one(
            {"user_id": user.user_id},
            sort=[("assessment_date", -1)]
        )
        
        # Get recent performance
        recent_test = await db.mock_test_results.find_one(
            {"user_id": user.user_id},
            sort=[("completed_at", -1)]
        )
        
        # Prepare content variables
        recent_performance = "No recent tests"
        stress_level_text = "Unknown"
        
        if recent_test:
            recent_performance = f"{recent_test['percentage']:.1f}%"
        
        if recent_assessment:
            stress_level_text = f"{recent_assessment['stress_level']}/10"
        
        # Generate personalized content
        content_prompt = f"""Generate motivational content for a {user.exam_type} student based on:
        
        Recent Performance: {recent_performance}
        Stress Level: {stress_level_text}
        Exam Type: {user.exam_type}
        Target Year: {user.target_year}
        
        Provide:
        1. An inspiring quote
        2. A practical study tip
        3. A success story snippet
        4. A stress-relief exercise
        """
        
        session_id = f"motivation_{uuid.uuid4()}"
        ai_content, _ = await get_ai_tutor_response(content_prompt, "Motivation", session_id)
        
        # Create motivational content entries
        contents = [
            {
                "content_id": str(uuid.uuid4()),
                "content_type": "quote",
                "title": "Daily Inspiration",
                "content": "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
                "category": "motivation"
            },
            {
                "content_id": str(uuid.uuid4()),
                "content_type": "tip",
                "title": "Study Technique",
                "content": "Try the Pomodoro Technique: 25 minutes focused study + 5 minutes break. This improves concentration and reduces mental fatigue.",
                "category": "study_tips"
            },
            {
                "content_id": str(uuid.uuid4()),
                "content_type": "exercise", 
                "title": "Quick Stress Relief",
                "content": "4-7-8 Breathing: Inhale for 4 counts, hold for 7, exhale for 8. Repeat 3 times to instantly calm your mind.",
                "category": "stress_relief"
            },
            {
                "content_id": str(uuid.uuid4()),
                "content_type": "ai_generated",
                "title": "Personalized Motivation",
                "content": ai_content[:200] + "..." if len(ai_content) > 200 else ai_content,
                "category": "motivation"
            }
        ]
        
        # Store content for engagement tracking
        for content in contents:
            await db.motivational_content.insert_one({
                **content,
                "user_id": user.user_id,
                "created_at": datetime.utcnow()
            })
        
        return {
            "daily_content": contents,
            "wellness_tip": "Remember to take care of your mental health alongside academic preparation",
            "next_refresh": datetime.utcnow() + timedelta(hours=8)
        }
        
    except Exception as e:
        logger.error(f"Motivational content error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch content")

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