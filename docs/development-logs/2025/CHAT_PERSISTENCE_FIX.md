# Chat Persistence Fix - ChatGPT-Style Session Persistence

## Problem
When users navigated away from the AI Tutor and returned, all messages disappeared. The chat view reset instead of showing previously saved messages. Specifically, AI responses were not being restored.

## Root Cause Analysis

### Root Cause 1: `currentSession` State Not Persisted (Frontend)

**File**: `frontend/src/components/AITutorNeuroSymbolic.js`

**Line 212 (before fix)**:
```javascript
const [currentSession, setCurrentSession] = useState(null);
```

**Issue**:
1. `currentSession` was initialized as `null` on every component mount
2. When navigating away and back, React unmounts and remounts the component
3. The state resets to `null`, so there's no session ID to load messages from

### Root Cause 2: AI Response Not Stored Correctly (Backend)

**File**: `backend/services/ai_service.py`

**Issue**:
The `save_session_message` function was storing `ai_response.get('response')` but the unified pipeline returns a different structure. The AI response was being saved incompletely, so when loading history, the AI message was missing.

---

## Fixes Applied

### Fix 1: Persist `currentSession` to localStorage (Frontend)

**File**: `frontend/src/components/AITutorNeuroSymbolic.js`

```javascript
// CRITICAL FIX: Persist currentSession to localStorage for ChatGPT-style persistence
const [currentSession, setCurrentSessionState] = useState(() => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('dhruv_ai_current_session') || null;
  }
  return null;
});

// Wrapper to persist session changes to localStorage
const setCurrentSession = useCallback((sessionId) => {
  setCurrentSessionState(sessionId);
  if (typeof window !== 'undefined') {
    if (sessionId) {
      localStorage.setItem('dhruv_ai_current_session', sessionId);
    } else {
      localStorage.removeItem('dhruv_ai_current_session');
    }
  }
}, []);
```

### Fix 2: Restore Session Messages on Mount (Frontend)

```javascript
// CRITICAL FIX: Restore session messages on mount if we have a persisted session
useEffect(() => {
  const restoreSession = async () => {
    const persistedSession = localStorage.getItem('dhruv_ai_current_session');
    if (persistedSession && messages.length === 0) {
      console.log('🔄 Restoring persisted session:', persistedSession);
      await loadSession(persistedSession);
    }
  };
  
  const timeoutId = setTimeout(restoreSession, 100);
  return () => clearTimeout(timeoutId);
}, []);
```

### Fix 3: Store Complete AI Response (Backend)

**File**: `backend/services/ai_service.py`

```python
# CRITICAL FIX: Store the COMPLETE AI response for history restoration
message_dict = {
    'message_id': message_id,
    'session_id': session_id,
    'user_id': user_id,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    
    # FRONTEND-COMPATIBLE STRUCTURE
    'user_message': sanitized_user_message,
    
    # CRITICAL: Store the COMPLETE AI response for history loading
    'ai_response': ai_response,  # Store complete response
    
    # Also store in legacy format for backward compatibility
    'dual_response': ai_response.get('dual_response') if isinstance(ai_response, dict) else None,
    'response': ai_response if isinstance(ai_response, dict) else {'content': str(ai_response)},
    ...
}
```

---

## How It Works Now

### Message Storage Flow
1. User sends message
2. Backend generates AI response via unified pipeline
3. `save_session_message()` stores **complete** AI response in MongoDB
4. Response includes `ai_response` field with full response structure

### Message Restoration Flow
1. Component mounts
2. `currentSession` restored from localStorage
3. `loadSession(sessionId)` called
4. Backend returns messages with `ai_response` field
5. Frontend parses: `msg.dual_response || msg.response || msg.ai_response`
6. AI messages displayed correctly

---

## Files Changed

| File | Change |
|------|--------|
| `frontend/src/components/AITutorNeuroSymbolic.js` | localStorage persistence for session + auto-restore on mount |
| `backend/services/ai_service.py` | Store complete AI response in `ai_response` field |

---

## Testing Checklist

1. ✅ Send a message → Both user and AI messages appear
2. ✅ Navigate to another page (e.g., Home)
3. ✅ Return to AI Tutor → **Both user AND AI messages restored**
4. ✅ Refresh the page → Messages still visible
5. ✅ Logout and login → Messages still visible (same session)
6. ✅ Click "New Chat" → Messages clear, welcome screen appears
7. ✅ Select old chat from sidebar → Old messages restored

---

## localStorage Key

```
Key: dhruv_ai_current_session
Value: <session_id>
```

## MongoDB Document Structure

```json
{
  "message_id": "uuid",
  "session_id": "uuid",
  "user_id": "uuid",
  "timestamp": "ISO date",
  "user_message": "What is the difference between...",
  "ai_response": {
    "default_view": {
      "main_content": { "content": "..." }
    },
    "progressive_sections": { "explanation": "..." }
  },
  "response": { ... },
  "dual_response": null
}
```

The frontend looks for AI content in this order:
1. `msg.dual_response` (legacy)
2. `msg.response` (legacy)
3. `msg.ai_response` (new - complete response)

