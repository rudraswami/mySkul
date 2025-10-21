# Dhruv AI - Repository Summary

**Generated**: Phase 1 - Comprehensive Audit
**Branch**: Current working branch
**Date**: 2025

## Overview
Dhruv AI is an EdTech platform for competitive exam preparation featuring AI Tutor, Mock Tests, and Auto Note Mentor capabilities. The application uses a FastAPI backend with MongoDB and a React frontend.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **Authentication**: Google OAuth 2.0, JWT tokens, Session middleware
- **AI/LLM**: Emergent LLM Key (OpenAI GPT-4o compatible)
- **Payment**: Razorpay (production keys configured)

### Frontend
- **Framework**: React 18
- **State Management**: React Query (@tanstack/react-query), Context API
- **Routing**: React Router v6
- **Styling**: Tailwind CSS, shadcn/ui components
- **API Client**: Axios with interceptors

## Architecture

### Backend Structure
```
backend/
├── api/              # API routers (modular)
├── core/             # Configuration and database
├── dependencies.py   # Dependency injection
├── main.py          # Application entry point
├── middleware/      # CORS, CSRF, Session
├── models/          # Pydantic models
├── services/        # Business logic layer
├── scripts/         # Database initialization
└── utils/           # Helper functions
```

### Frontend Structure  
```
frontend/src/
├── api/              # API client configuration
├── components/       # React components
├── contexts/         # React Context providers
├── hooks/            # Custom React hooks
├── pages/            # Policy pages
├── styles/           # Global CSS
└── utils/            # Helper functions
```

## Core Features

### 1. Authentication
- **Gmail-Only OAuth**: Google OAuth 2.0 integration
- **Profile Setup**: Mandatory after first login
- **Hybrid Auth**: JWT + Session cookies
- **CSRF Protection**: Available but disabled (commented in main.py)

### 2. AI Tutor
- Interactive chat with AI mentor
- Context-aware responses
- Subject-specific tutoring
- Chat history persistence

### 3. Mock Tests
- AI-generated tests
- Multiple exam types (JEE, NEET, etc.)
- Performance tracking
- Detailed review system

### 4. Auto Note Mentor
- Audio/text input processing
- AI-generated study notes
- Session management

### 5. Subscription System
- **UnifiedSubscriptionService**: New unified service
- **SubscriptionService**: Legacy service (being phased out)
- Three tiers: Free, Basic, Premium
- Feature-based access control
- Usage tracking

### 6. Dashboard & Analytics
- Performance metrics
- Study streak tracking
- Gamification (badges, progress)
- Leaderboard

## Dependencies

### Backend (Key Packages)
- fastapi
- motor (MongoDB async)
- pydantic
- emergentintegrations (LLM integration)
- google-auth
- razorpay
- bcrypt
- python-multipart

### Frontend (Key Packages)
- react, react-dom
- react-router-dom
- @tanstack/react-query
- axios
- tailwindcss
- @radix-ui/* (UI components)

## Environment Variables

### Backend (.env)
- MONGO_URL
- JWT_SECRET
- EMERGENT_LLM_KEY
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
- RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
- BACKEND_URL, FRONTEND_URL
- CORS_ORIGINS

### Frontend (.env)
- REACT_APP_BACKEND_URL
- REACT_APP_RAZORPAY_KEY_ID

## Database Collections

### Core Collections
1. **users**: User profiles and authentication
2. **subscriptions**: Subscription data and limits
3. **chat_sessions**: AI Tutor conversations
4. **chat_messages**: Individual messages
5. **mock_tests**: Generated tests
6. **test_attempts**: Test submissions and scores
7. **auto_notes_sessions**: Note generation sessions
8. **wellness_checks**: Student wellness data
9. **gamification_data**: Badges, achievements, progress

### Indexes
- Compound indexes for dashboard queries
- User-based filtering optimized
- Performance trend queries indexed

## API Endpoints (Modular)

### Authentication (`/api/auth/*`)
- Google OAuth login/callback
- Session management
- CSRF token generation

### User (`/api/user/*`)
- Profile CRUD
- Profile completion status

### Subscription (`/api/subscription/*`)
- Current subscription info
- Access checks
- Usage tracking
- Upgrade flow
- Razorpay integration

### AI Tutor (`/api/chat/*`)
- Session management
- Message streaming
- Context management

### Mock Tests (`/api/mock-tests/*`)
- Test generation
- Library/dashboard
- Submission and grading
- Detailed review

### Auto Notes (`/api/auto-notes/*`)
- Session creation
- Content processing
- Session retrieval

### Analytics (`/api/analytics/*`)
- Dashboard analytics
- Subject progress
- Daily goals
- Wellness checks

### Dashboard Analytics (`/api/dashboard/*`)
- Comprehensive dashboard data
- Streak tracking
- Leaderboard

### Gamification (`/api/gamification/*`)
- Progress tracking
- Leaderboard
- Badge management

## Service Worker
- PWA support
- Caching strategy (GET requests only)
- API route bypassing
- Recent version: Forced unregister mechanism added

## Test Files
- **772 test files** found across repository
- Mix of backend curl tests and playwright scripts
- Located in `/tests/`, root, and various subdirectories

## Known Issues (Pre-Audit)
1. CSRF protection disabled
2. Service worker error handling incomplete
3. Legacy files present (*.legacy, *.backup, *.broken)
4. Dual subscription services (migration in progress)
5. Some hardcoded fallback values
6. React Query migration incomplete (AuthContext)

## Documentation
- Limited inline documentation
- No API documentation (FastAPI docs available at /docs)
- Policy pages implemented (Privacy, Terms, Refund, etc.)

## Deployment
- Supervisor for process management
- Kubernetes for orchestration
- Hot reload enabled (dev mode)
- Production environment configured

---

**Next Steps**: See `issues_report.md` for detailed findings and recommendations.