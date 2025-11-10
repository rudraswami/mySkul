# AI Tutor Memory System

## Overview

The AI Tutor now has a comprehensive memory system that maintains conversation context across turns, making interactions feel more natural and intelligent - just like a real mentor who remembers what you've discussed.

## Features

### 1. Session Memory (Short-term)

While the student is in an active session, the system now:

- ✅ **Tracks every conversation turn** with rich metadata
- ✅ **Remembers topics discussed** in the current session
- ✅ **Recalls metaphors used** to avoid repetition
- ✅ **Tracks visuals shown** to maintain visual continuity
- ✅ **Builds structured memory context** injected into LLM prompts
- ✅ **Detects follow-up questions** and maintains context

### 2. Memory Context Structure

For each message exchange, the system stores:

```json
{
  "user_message": "Explain atomic orbitals",
  "topic": "atomic_orbitals",
  "metaphor": "cricket",
  "metaphor_text": "Like cricket field positions",
  "visual_type": "hierarchy",
  "practical_explanation": "Atomic orbitals are regions..."
}
```

### 3. Conversation Continuity

The memory system enables natural continuity:

**Example 1: Follow-up Questions**
```
Student: "Explain atomic orbitals"
AI: [Explains with cricket metaphor]

Student: "What about d orbitals?"
AI: "Building on the atomic orbital concept we just discussed..."
    [Continues naturally without re-explaining basics]
```

**Example 2: Progressive Learning**
```
Student: "Explain quantum numbers"
AI: [Explains n, l, m, s with visuals]

Student: "Continue"
AI: "Now that you know quantum numbers, let's see how they relate to..."
    [Progresses naturally based on what was covered]
```

### 4. Session Metadata

Each chat session now tracks:

```json
{
  "session_id": "uuid",
  "last_topic": "quantum_mechanics",
  "last_metaphor": "cricket",
  "topics_covered": ["atomic_orbitals", "quantum_numbers", "aufbau_principle"],
  "message_count": 5,
  "last_updated": "2025-01-10T..."
}
```

## Implementation Details

### Files Modified/Created

1. **`utils/memory_builder.py`** (NEW)
   - `MemoryContextBuilder` class
   - Builds structured memory from conversation history
   - Extracts topics, metaphors, visuals, concepts
   - Generates memory context string for LLM injection

2. **`prompts/neuro_symbolic_mentor_v2.py`**
   - Added `memory_context` parameter to `get_mentor_prompt_v2()`
   - Memory context injected into system prompt after student profile
   - LLM now sees previous conversation history

3. **`services/ai_service.py`**
   - Integrated `MemoryContextBuilder` into `generate_neuro_symbolic_response()`
   - Memory built before each response generation
   - Message documents now include memory metadata:
     - `topic`: Detected topic from the question
     - `metaphor`: Metaphor category used
     - `metaphor_text`: Actual metaphor text
     - `visual_type`: Type of visual shown
     - `practical_explanation`: Brief summary of explanation
   - Session updates now track:
     - `last_topic`: Last discussed topic
     - `last_metaphor`: Last metaphor used
     - `topics_covered`: Array of all topics covered (unique)
     - `message_count`: Number of messages in session

4. **`api/ai.py`**
   - Updated `/session-memory/{session_id}/reset` endpoint
   - Now clears all memory-related fields including:
     - `last_topic`, `last_metaphor`
     - `topics_covered`
     - `message_count`

### Memory Context Format

When conversation history exists, the LLM receives:

```
═══════════════════════════════════════════════════
📝 **CONVERSATION MEMORY** (Use this to maintain continuity)
═══════════════════════════════════════════════════

**Previous Questions in this Session:**
  1. "Explain atomic orbitals"
  2. "What about d orbitals?"
  3. "How do they fill up?"

**Last Topic Discussed:** electron_configuration

**Concepts Already Explained:**
  1. Atomic orbitals are regions where electrons are most likely...
  2. d orbitals have more complex shapes with 5 different...
  3. Electrons fill orbitals following the Aufbau principle...

**Instructions for Using Memory:**
- DON'T repeat explanations already given
- If student says "continue" or "next", build upon previous topic
- If student references earlier concepts, acknowledge them
- If student asks for clarification, refer back to what was already discussed
- Progress naturally from previous topics
═══════════════════════════════════════════════════
```

## API Usage

### Get Session Memory

```http
GET /api/ai/session-memory/{session_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session_id": "uuid",
  "last_topic": "quantum_mechanics",
  "topics_covered": ["atomic_orbitals", "quantum_numbers"],
  "message_count": 5,
  "last_updated": "2025-01-10T..."
}
```

### Reset Session Memory

```http
POST /api/ai/session-memory/{session_id}/reset
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "session_id": "uuid",
  "message": "Session memory cleared. Ready for a fresh start!"
}
```

## Benefits

### For Students:

1. **No Repetition**: AI won't re-explain concepts already covered
2. **Natural Flow**: Conversations feel like talking to a real tutor
3. **Progressive Learning**: Each topic builds on previous ones
4. **Contextual Responses**: AI understands "continue", "explain more", etc.

### For Learning:

1. **Better Retention**: Concepts build upon each other naturally
2. **Reduced Cognitive Load**: No need to repeat context
3. **Personalized Path**: AI adapts to what you've already learned
4. **Efficient Learning**: Faster progression through topics

## Technical Architecture

```
┌─────────────────────────────────────────────────────┐
│              User asks question                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│   1. Fetch last 5 messages from chat_messages       │
│      collection (message_history)                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│   2. MemoryContextBuilder.build_memory_context()    │
│      - Extracts topics, metaphors, concepts          │
│      - Builds structured memory context string       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│   3. get_mentor_prompt_v2(..., memory_context)      │
│      - Memory injected into system prompt            │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│   4. LLM generates response with memory awareness   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│   5. Save message with memory metadata:              │
│      - topic, metaphor, metaphor_text                │
│      - visual_type, practical_explanation            │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│   6. Update session with learning artifacts:         │
│      - last_topic, last_metaphor                     │
│      - topics_covered[], message_count               │
└─────────────────────────────────────────────────────┘
```

## Testing

### Test Case 1: Basic Memory

1. Start new session
2. Ask: "Explain atomic orbitals"
3. Check: Response includes explanation
4. Ask: "What about d orbitals?"
5. ✅ Verify: Response references previous explanation, doesn't repeat basics

### Test Case 2: Continuation

1. Start new session
2. Ask: "Explain quantum numbers"
3. Ask: "Continue"
4. ✅ Verify: Response progresses from quantum numbers naturally

### Test Case 3: Memory Reset

1. Have ongoing session with 5+ messages
2. Call `/session-memory/{id}/reset`
3. Ask new question
4. ✅ Verify: AI treats it as fresh start, no memory references

## Future Enhancements (Phase 2)

### Cross-Session Memory

Store learning history across sessions:

```json
{
  "user_id": "uuid",
  "learning_history": {
    "topics_mastered": ["atomic_orbitals", "quantum_numbers"],
    "weak_areas": ["integration_by_parts"],
    "preferred_metaphors": ["cricket", "cooking"],
    "learning_pace": "moderate",
    "last_session_summary": "Covered electron configuration"
  }
}
```

**Features:**
- Welcome back messages: "Last time we covered atomic orbitals. Ready to continue?"
- Intelligent topic suggestions based on what was learned
- Avoid re-teaching mastered concepts
- Focus on weak areas automatically

## Troubleshooting

### Memory not working?

1. **Check message history is being fetched**:
   - Look for log: `🧠 Memory: X messages | Topics: [...]`

2. **Check memory context is built**:
   - Verify `MemoryContextBuilder` is being called
   - Check if `memory_context_str` is not empty

3. **Check prompt injection**:
   - Verify `get_mentor_prompt_v2` receives `memory_context` parameter
   - Check if memory section appears in system prompt

### Memory too verbose?

- Adjust `max_messages` in `MemoryContextBuilder.build_memory_context()`
- Currently set to 5, can reduce to 3 for shorter context

### Want to clear memory for all sessions?

```python
# Admin operation - clear all session memory
await db.chat_sessions.update_many(
    {},
    {
        "$unset": {
            "last_topic": "",
            "last_metaphor": "",
            "topics_covered": ""
        }
    }
)
```

## Performance Impact

- **Latency**: +50-100ms for memory building (negligible)
- **Database**: Uses existing `chat_messages` collection, no new tables
- **Prompt size**: +200-500 tokens for memory context
- **Cost**: Minimal increase in LLM token usage

## Conclusion

The memory system transforms the AI Tutor from a stateless Q&A bot into an intelligent learning companion that remembers, adapts, and guides students through their learning journey naturally and efficiently.
