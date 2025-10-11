# AI Tutor 2.x Selective Refactor Plan

**Date**: October 2025  
**Objective**: Remove legacy/duplicate code while preserving AI Tutor 2.4 modular architecture

---

## Current State Analysis

### Backend Routes (Duplicates Detected)

**✅ KEEP - Modular Routes** (`/app/backend/api/ai.py`):
- `POST /api/ai/dual-response` - Primary AI Tutor endpoint (with subscription check)
- `POST /api/ai/mentor-only` - Mentor-only mode
- `POST /api/ai/professor-only` - Professor-only mode
- `GET /api/ai/available-contexts` - Context management
- `POST /api/ai/dual-study-plan` - Study plan generation
- `GET /api/ai/chat/sessions` - Session management
- `POST /api/ai/chat/sessions` - Create session
- `GET /api/ai/chat/{session_id}/messages` - Get messages
- **Status**: Modern, modular, uses AIService with subscription integration

**❌ REMOVE - Legacy Routes** (`/app/backend/server.py`):
- Line ~5081: `send_chat_message()` - Old chat endpoint
- Line ~7088: `@api_router.post("/ai/dual-response")` - Duplicate endpoint
- **Reason**: Superseded by modular api/ai.py routes

### Frontend Components

**✅ KEEP - AI Tutor 2.4 Components**:
- `/app/frontend/src/components/AITutor.js` - Main component (125KB, recently updated)
- `/app/frontend/src/components/AIResponseCardV2.js` - Enhanced response card
- `/app/frontend/src/components/UpgradeModal.js` - Subscription modal
- `/app/frontend/src/components/microlesson/` - All 8 micro-lesson components:
  - `ResponseComposer.js` - Orchestrator ✅
  - `LatexRenderer.js` - Math rendering ✅
  - `MentorCard.js` - Structured mentor UI ✅
  - `ConceptCard.js`, `FormulaCard.js`, `TipCard.js` ✅
  - `MotivationalFooter.js`, `PracticeActions.js` ✅

**❌ REMOVE - Legacy Components**:
- `/app/frontend/src/components/AITutor20.js` - Old beta version (17KB)
- `/app/frontend/src/components/SimpleAITutor20.js` - Debug component (3.9KB)
- **Reason**: Functionality merged into main AITutor.js

**🔄 EVALUATE - Utility Components**:
- `/app/frontend/src/components/FormattedAIResponse.js` (42KB)
  - Check if still used or superseded by ResponseComposer
  - May contain legacy formatting logic

### Backend Services

**✅ KEEP**:
- `/app/backend/services/ai_service.py` - Core AI service with subscription
- `/app/backend/services/subscription_service.py` - Subscription logic
- `/app/backend/utils/response_parser.py` - Text sanitization
- `/app/backend/utils/mentor_splitter.py` - Mentor structuring
- `/app/backend/utils/sentiment_analyzer.py` - Sentiment detection
- `/app/backend/utils/svg_generator.py` - Visual generation

**✅ KEEP - Models**:
- `/app/backend/models/ai.py` - Request/response schemas
- `/app/backend/models/subscription.py` - Subscription schemas

---

## Refactor Execution Plan

### Phase 1: Backend Cleanup

**Task 1.1**: Remove duplicate AI routes from `server.py`
- [x] Identify duplicate `/api/ai/dual-response` endpoint
- [ ] Remove legacy `send_chat_message()` function
- [ ] Remove duplicate route registration
- [ ] Verify main.py routes to api/ai.py only

**Task 1.2**: Consolidate AI endpoints under `/api/ai/*`
- [ ] Verify all AI routes use modular api/ai.py router
- [ ] Ensure consistent error handling
- [ ] Confirm subscription integration in all routes

### Phase 2: Frontend Cleanup

**Task 2.1**: Remove legacy AITutor components
- [ ] Delete `AITutor20.js` (superseded by AITutor.js)
- [ ] Delete `SimpleAITutor20.js` (debug component)
- [ ] Update imports if referenced elsewhere

**Task 2.2**: Evaluate FormattedAIResponse.js
- [ ] Check usage across codebase
- [ ] If used, keep; if not, remove
- [ ] Ensure ResponseComposer is primary renderer

**Task 2.3**: Verify frontend hooks
- [ ] Confirm useAITutor.js is used
- [ ] Check for duplicate API calls
- [ ] Ensure LatexRenderer used everywhere

### Phase 3: Verification

**Task 3.1**: Backend verification
- [ ] All AI routes under `/api/ai/*`
- [ ] No duplicate endpoints
- [ ] Subscription checks in place
- [ ] Text sanitization applied

**Task 3.2**: Frontend verification
- [ ] Single AITutor component
- [ ] All responses use ResponseComposer
- [ ] LatexRenderer for all math
- [ ] UpgradeModal integrated

**Task 3.3**: Integration testing
- [ ] Test AI Tutor end-to-end
- [ ] Verify subscription limits work
- [ ] Check math rendering
- [ ] Test upgrade modal flow

---

## Risk Mitigation

1. **Backup**: Git commit before changes
2. **Incremental**: Remove one file at a time
3. **Test**: Check after each removal
4. **Rollback**: Keep git history clean for easy revert

---

## Expected Outcome

**Files to Delete**: 3-4 files
**Lines of Code Removed**: ~2,000-3,000 lines
**Duplicate Routes Removed**: 2-3 endpoints
**Unified Architecture**: All AI routes under /api/ai/*

**Preserved**:
- ✅ AI Tutor 2.4 micro-lesson system
- ✅ Subscription integration
- ✅ Text sanitization pipeline
- ✅ Math rendering (KaTeX)
- ✅ All recent modular updates
