# Cross-Session Memory System (Phase 2)

## Overview

Phase 2 of the memory system enables the AI Tutor to remember and adapt across **different learning sessions**, creating a truly personalized learning companion that grows smarter with every interaction.

## What Makes This Special

Unlike Phase 1 (session memory) which only remembers within a single chat session, Phase 2 tracks:

- ✅ **Topics mastered** across all sessions
- ✅ **Weak areas** where student struggles
- ✅ **Learning preferences** discovered over time
- ✅ **Study streaks** and motivation tracking
- ✅ **Personalized welcome back** messages
- ✅ **Intelligent recommendations** based on learning history

## How It Works

### 1. Learning Profile Structure

Each user has a comprehensive learning profile stored in their user document:

```json
{
  "learning_profile": {
    "user_id": "uuid",

    // Topics mastered
    "topics_mastered": [
      {
        "topic": "atomic_orbitals",
        "subject": "Chemistry",
        "mastery_level": 0.85,  // 0.0 to 1.0
        "times_reviewed": 5,
        "last_reviewed": "2025-01-10T...",
        "metaphors_used": ["cricket", "cooking"]
      }
    ],

    // Weak areas
    "weak_areas": [
      {
        "topic": "integration_by_parts",
        "subject": "Mathematics",
        "struggle_count": 3,
        "last_struggled": "2025-01-09T...",
        "common_mistakes": ["Forgot to use LIATE rule"],
        "needs_revision": true
      }
    ],

    // Recent sessions
    "recent_sessions": [
      {
        "session_id": "uuid",
        "date": "2025-01-10T...",
        "topics_covered": ["quantum_numbers", "orbitals"],
        "messages_count": 8,
        "subjects": ["Chemistry"],
        "summary": "Discussed 2 topics"
      }
    ],

    // Preferences
    "preferences": {
      "preferred_metaphors": {"cricket": 15, "cooking": 8},
      "preferred_visual_types": {"hierarchy": 10, "flow": 5},
      "learning_pace": "moderate",
      "depth_preference": "standard"
    },

    // Stats
    "total_sessions": 12,
    "total_questions_asked": 45,
    "total_topics_explored": 18,
    "current_streak_days": 5,
    "longest_streak_days": 7,
    "last_active_date": "2025-01-10T..."
  }
}
```

### 2. Automatic Learning Tracking

Every time a student asks a question, the system automatically:

```
User asks question about "quantum numbers"
           ↓
AI generates response with cricket metaphor
           ↓
System tracks:
  ✅ Topic: quantum_numbers (Chemistry)
  ✅ Metaphor used: cricket
  ✅ Visual type: hierarchy
  ✅ Mastery score: 0.6 (default)
           ↓
Learning profile updated:
  - topics_mastered[quantum_numbers].times_reviewed += 1
  - topics_mastered[quantum_numbers].mastery_level updated
  - preferences.preferred_metaphors[cricket] += 1
  - total_questions_asked += 1
```

### 3. Mastery Level Calculation

Mastery levels use **Exponential Moving Average** to balance history with recent performance:

```python
new_mastery = (current_mastery * 0.7) + (performance_score * 0.3)
```

**Examples:**
- First encounter: mastery = 0.6 (default performance)
- Second encounter (good understanding):
  - mastery = (0.6 * 0.7) + (0.8 * 0.3) = 0.66
- Third encounter (mastery shown):
  - mastery = (0.66 * 0.7) + (0.9 * 0.3) = 0.732 ✅ Mastered!

## API Endpoints

### 1. Get Learning Profile

```http
GET /api/ai/learning-profile
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "user_id": "uuid",
    "topics_mastered": [...],
    "weak_areas": [...],
    "preferences": {...},
    "total_sessions": 12,
    "current_streak_days": 5
  }
}
```

### 2. Welcome Back Message

```http
GET /api/ai/learning-profile/welcome-back
Authorization: Bearer <token>
```

**Response (Returning User):**
```json
{
  "success": true,
  "is_new_user": false,
  "welcome_data": {
    "has_history": true,
    "streak_days": 5,
    "total_sessions": 12,
    "last_session": {
      "topics": ["quantum_numbers", "orbitals"],
      "date": "2025-01-10T...",
      "summary": "Discussed 2 topics"
    },
    "current_focus": "electron_configuration",
    "needs_revision": ["integration_by_parts"],
    "suggested_topics": ["aufbau_principle", "hunds_rule"]
  }
}
```

**Response (New User):**
```json
{
  "success": true,
  "is_new_user": true,
  "message": "Welcome! Let's start your learning journey! 🚀"
}
```

### 3. Learning Insights

```http
GET /api/ai/learning-profile/insights
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "insights": [
    {
      "type": "progress",
      "message": "Great progress! You've mastered 12 topics",
      "topics": ["atomic_orbitals", "quantum_numbers", "..."],
      "confidence": 0.9
    },
    {
      "type": "weakness",
      "message": "Let's strengthen: integration_by_parts, thermodynamics",
      "topics": ["integration_by_parts", "thermodynamics"],
      "confidence": 0.8
    },
    {
      "type": "motivation",
      "message": "Amazing! 5 day learning streak! Keep it going! 🔥",
      "topics": [],
      "confidence": 1.0
    }
  ]
}
```

### 4. Topics Mastered

```http
GET /api/ai/learning-profile/topics-mastered
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "topics_mastered": [
    {
      "topic": "atomic_orbitals",
      "subject": "Chemistry",
      "mastery_level": 0.85,
      "times_reviewed": 5,
      "last_reviewed": "2025-01-10T..."
    }
  ],
  "count": 12
}
```

### 5. Weak Areas

```http
GET /api/ai/learning-profile/weak-areas
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "weak_areas": [
    {
      "topic": "integration_by_parts",
      "subject": "Mathematics",
      "struggle_count": 3,
      "last_struggled": "2025-01-09T...",
      "common_mistakes": ["Forgot to use LIATE rule"],
      "needs_revision": true
    }
  ],
  "count": 2
}
```

## User Experience Examples

### Example 1: Welcome Back

**Day 1:**
```
User logs in for the first time
AI: "Welcome! Let's start your learning journey! 🚀"
User asks about atomic orbitals
AI explains with cricket metaphor
[Profile created, first topic tracked]
```

**Day 2:**
```
User logs in
GET /api/ai/learning-profile/welcome-back
AI: "Welcome back! Yesterday we discussed atomic orbitals.
     Ready to explore electron configuration next?"
```

**Day 6:**
```
User logs in
GET /api/ai/learning-profile/welcome-back
AI: "Amazing! You're on a 5-day streak! 🔥
     Last time we covered quantum numbers.
     Want to tackle the Aufbau principle today?"
```

### Example 2: Intelligent Recommendations

```
User has mastered:
- atomic structure
- quantum numbers
- orbital shapes

System recommends logically:
- electron configuration
- aufbau principle
- hund's rule
(Natural progression from mastered topics)
```

### Example 3: Weak Area Focus

```
User struggled 3 times with integration by parts
Profile shows: weak_area = "integration_by_parts"

When user asks about calculus:
AI: "I notice integration by parts has been tricky.
     Let's break it down with a fresh approach..."
[Automatically provides extra care and simpler explanations]
```

## Implementation Architecture

```
┌─────────────────────────────────────────────────────┐
│  User asks question in any session                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  AI Service generates response                       │
│  - Detects topic (e.g., "quantum_numbers")          │
│  - Uses metaphor (e.g., "cricket")                   │
│  - Shows visual (e.g., "hierarchy")                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Learning Profile Service (Automatic Tracking)       │
│  1. update_topic_mastery()                           │
│     - Find or create topic entry                     │
│     - Update mastery level (EMA)                     │
│     - Increment times_reviewed                       │
│     - Track metaphor used                            │
│                                                       │
│  2. update_preferences()                             │
│     - Track metaphor usage count                     │
│     - Track visual type preferences                  │
│                                                       │
│  3. Background: Session summary                      │
│     - Aggregate session topics                       │
│     - Calculate streak                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  User Document Updated in MongoDB                    │
│  users.learning_profile = {...updated data}         │
└─────────────────────────────────────────────────────┘

Next session:
┌─────────────────────────────────────────────────────┐
│  User returns (new session)                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  GET /learning-profile/welcome-back                  │
│  - Fetch learning_profile from users collection      │
│  - Analyze: last topics, weak areas, streak          │
│  - Generate personalized welcome message             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Frontend shows welcome card:                        │
│  "Welcome back! 5-day streak! 🔥                    │
│   Last time: quantum numbers                         │
│   Suggested next: electron configuration"            │
└─────────────────────────────────────────────────────┘
```

## Key Features Explained

### 1. Exponential Moving Average (EMA)

Why EMA instead of simple average?
- ✅ Gives more weight to recent performance
- ✅ Adapts to learning progress naturally
- ✅ Old struggles don't drag down current mastery
- ✅ Encourages continuous learning

### 2. Weak Area Detection

A topic becomes a "weak area" when:
- Student asks about it multiple times
- Questions show confusion or struggle patterns
- Can be manually marked by the system

### 3. Preference Learning

System learns preferences passively:
- Which metaphors resonate most (usage count)
- Which visual types are viewed most
- Preferred learning pace (inferred from interactions)

### 4. Streak Calculation

Streak logic:
- Active day = any question asked
- Consecutive days increment streak
- Miss a day = streak resets to 0
- Longest streak saved for motivation

## Database Schema

The learning profile is stored as an embedded document in the `users` collection:

```javascript
db.users.updateOne(
  { user_id: "user123" },
  {
    $set: {
      "learning_profile.topics_mastered": [...],
      "learning_profile.preferences": {...}
    }
  }
)
```

**Why embedded?**
- ✅ Single query to get user + learning profile
- ✅ No joins needed
- ✅ Atomic updates
- ✅ Simpler architecture

## Testing Scenarios

### Test 1: First-Time User

```
1. New user signs up
2. GET /learning-profile/welcome-back
   ✅ Should return is_new_user: true
3. User asks first question
4. GET /learning-profile
   ✅ Should show 1 topic tracked
```

### Test 2: Returning User

```
1. User with 5 previous sessions
2. GET /learning-profile/welcome-back
   ✅ Should show last_session data
   ✅ Should show current_focus
   ✅ Should show streak_days
```

### Test 3: Mastery Progression

```
1. User asks about "quantum numbers" (first time)
   ✅ Mastery = 0.6
2. User asks again (shows understanding)
   ✅ Mastery = 0.66
3. User asks third time (mastery demonstrated)
   ✅ Mastery = 0.73 (crossed 0.7 threshold!)
4. GET /learning-profile/topics-mastered
   ✅ Should include "quantum_numbers"
```

### Test 4: Weak Area Tracking

```
1. User struggles with "integration_by_parts"
2. Asks 3 times with confusion
3. GET /learning-profile/weak-areas
   ✅ Should show "integration_by_parts" with struggle_count=3
4. GET /learning-profile/insights
   ✅ Should suggest focusing on weak areas
```

## Performance Considerations

- **Latency**: +30-50ms for profile updates (background, non-blocking)
- **Storage**: ~2-5KB per user (negligible)
- **Queries**: Uses existing users collection, no new tables
- **Scalability**: Indexed user_id lookups, O(1) access

## Future Enhancements

### Adaptive Difficulty

```javascript
if (mastery_level > 0.8) {
  // Student has mastered this - give harder problems
  difficulty = "advanced";
} else if (mastery_level < 0.4) {
  // Student struggling - simplify
  difficulty = "beginner";
}
```

### Spaced Repetition

```javascript
if (last_reviewed > 7_days_ago && mastery_level < 0.8) {
  // Suggest reviewing this topic
  recommended_next_topics.push(topic);
}
```

### Learning Path Generation

```javascript
// Generate personalized curriculum
topics_to_learn = [
  ...weak_areas_needing_revision,
  ...logically_next_topics_from_mastered,
  ...exam_specific_important_topics
];
```

## Conclusion

Phase 2 transforms the AI Tutor from a session-aware assistant into a **true learning companion** that:

1. 🧠 **Remembers** everything you've learned
2. 📈 **Tracks** your progress over time
3. 💪 **Identifies** areas needing focus
4. 🎯 **Recommends** what to learn next
5. 🔥 **Motivates** with streaks and insights
6. 🎨 **Adapts** to your learning preferences

It's like having a personal tutor who knows your complete learning history and genuinely cares about your progress! 🚀
