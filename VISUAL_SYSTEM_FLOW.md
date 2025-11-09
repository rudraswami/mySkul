# Visual Teaching Engine - System Flow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         STUDENT                                  │
│                    "Explain active voice"                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  MentorResponseV2.js                                      │   │
│  │  - Receives question                                      │   │
│  │  - Sends to backend API                                   │   │
│  │  - Checks for teaching_visual in response                 │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  TeachingVisualPlayer.js                                  │   │
│  │  - Renders animated stages                                │   │
│  │  - Manages playback (play/pause/restart)                  │   │
│  │  - Tracks progress                                        │   │
│  │  - Triggers interactions                                  │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  InteractionLayer.js                                      │   │
│  │  - Quiz, Drag, Slider, Tap, Predict                       │   │
│  │  - Collects student responses                             │   │
│  │  - Provides feedback                                      │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   │                                              │
│                   ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  AnimationEngine.js (D3.js)                               │   │
│  │  - SVG rendering                                          │   │
│  │  - Animation primitives                                   │   │
│  │  - Smooth transitions                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API: visual_teaching.py                                  │   │
│  │  POST /api/visual-teaching/generate                       │   │
│  │  - Receives question                                      │   │
│  │  - Checks for pre-built templates                         │   │
│  │  - Falls back to dynamic generation                       │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   │                                              │
│        ┌──────────┴──────────┐                                  │
│        ▼                     ▼                                  │
│  ┌─────────────┐      ┌─────────────────────────────────────┐  │
│  │  Templates  │      │  Dynamic Generation                  │  │
│  │             │      │                                      │  │
│  │  grammar_   │      │  visual_teaching_engine.py          │  │
│  │  visual_    │      │  ┌────────────────────────────────┐ │  │
│  │  templates  │      │  │ 1. SemanticParser              │ │  │
│  │  .py        │      │  │    - Understand concept type   │ │  │
│  │             │      │  │    - Extract key elements      │ │  │
│  │  - Active/  │      │  └──────────┬─────────────────────┘ │  │
│  │    Passive  │      │             ▼                        │  │
│  │  - Subject- │      │  ┌────────────────────────────────┐ │  │
│  │    Verb     │      │  │ 2. Cultural Metaphor Library   │ │  │
│  │  - Tenses   │      │  │    cultural_metaphor_library.py│ │  │
│  │             │      │  │    - Cricket                    │ │  │
│  │             │      │  │    - Cooking                    │ │  │
│  │             │      │  │    - Trains                     │ │  │
│  │             │      │  │    - Bollywood                  │ │  │
│  │             │      │  │    - Festivals, Gaming, etc.    │ │  │
│  │             │      │  └──────────┬─────────────────────┘ │  │
│  │             │      │             ▼                        │  │
│  │             │      │  ┌────────────────────────────────┐ │  │
│  │             │      │  │ 3. SceneGenerator              │ │  │
│  │             │      │  │    - Map to visual pattern     │ │  │
│  │             │      │  │    - Generate animation stages │ │  │
│  │             │      │  │    - Add interactions          │ │  │
│  │             │      │  │    - Add cultural elements     │ │  │
│  │             │      │  └──────────┬─────────────────────┘ │  │
│  └─────────────┘      └─────────────┼─────────────────────────┘  │
│                                     │                            │
│                                     ▼                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  TeachingVisual Object                                    │   │
│  │  - visual_id                                              │   │
│  │  - type: "animated_lesson"                                │   │
│  │  - stages: [Stage1, Stage2, ...]                          │   │
│  │  - total_duration_ms                                      │   │
│  │  - interaction_points: [1, 3, 4]                          │   │
│  │  - metadata: {subject, topic, metaphor, complexity}       │   │
│  └────────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  MongoDB (Analytics)                                      │   │
│  │  - visual_analytics collection                            │   │
│  │  - visual_interactions collection                         │   │
│  │  - Tracks: views, completions, quiz scores, time spent    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                      JSON Response
                             │
                             ▼
                  [Back to Frontend]
```

---

## Detailed Flow: Active/Passive Voice Example

```
STEP 1: Student Question
─────────────────────────
Student: "Explain active and passive voice"
    ↓
Frontend: MentorResponseV2 sends to backend
    ↓
POST /api/visual-teaching/generate
    {
      "question": "Explain active and passive voice",
      "subject": "English",
      "complexity": "medium"
    }


STEP 2: Backend Processing
───────────────────────────
API receives request
    ↓
Checks keywords: "active", "passive", "voice" found!
    ↓
Looks for template: get_grammar_visual_template("active_passive_voice")
    ↓
Template found! Returns pre-built visual with:
    - 7 animation stages
    - 28 seconds total duration
    - 4 interaction points
    - Cooking + cricket metaphors
    ↓
Logs to analytics:
    - user_id, visual_id, question
    - subject: "English"
    - topic: "Active and Passive Voice"
    - is_template: True
    - timestamp


STEP 3: Stage Generation (Template)
────────────────────────────────────
Stage 1 (3s):
    narration: "Let's understand using cooking..."
    animations: [scene_setup, fade_in]
    emphasis: "Active = WHO does action!"

Stage 2 (4s):
    narration: "ACTIVE: 'Ravi makes chai'..."
    animations: [split_screen, spotlight, arrow, sentence_build]
    interactions: [tap_to_continue]
    emphasis: "Subject + Verb + Object = ACTIVE!"

Stage 3 (4s):
    narration: "PASSIVE: 'Chai is made by Ravi'..."
    animations: [split_screen_right, object_spotlight, reverse_arrow]
    interactions: [tap_to_continue]

Stage 4 (5s):
    narration: "See the difference?"
    animations: [comparison_arrows, transformation_morph]
    interactions: [quiz: "Which puts DOER first?"]

Stage 5 (5s):
    narration: "Cricket example..."
    animations: [cricket_scene, dual_sentence_build]
    interactions: [drag: "Form passive voice"]

Stage 6 (4s):
    narration: "When to use each..."
    animations: [decision_tree]
    interactions: [predict: "Which voice for..."]

Stage 7 (3s):
    narration: "Great! Remember..."
    animations: [summary_card, celebration]


STEP 4: JSON Response
──────────────────────
{
  "success": true,
  "visual_id": "abc-123",
  "type": "animated_lesson",
  "stages": [
    {
      "stage_id": "stage-1",
      "duration_ms": 3000,
      "narration": "Let's understand...",
      "animations": [...],
      "interactions": null,
      "emphasis": "Active = WHO does action!"
    },
    ...
  ],
  "total_duration_ms": 28000,
  "interaction_points": [1, 3, 4, 5],
  "metadata": {
    "subject": "English",
    "topic": "Active and Passive Voice",
    "cultural_metaphor": "cooking",
    "complexity": "medium"
  }
}


STEP 5: Frontend Rendering
───────────────────────────
MentorResponseV2 receives response
    ↓
Detects: response.teaching_visual exists!
    ↓
Renders TeachingVisualPlayer component
    ↓
Player initializes:
    - Creates AnimationEngine
    - Loads visual data
    - Sets up event listeners
    ↓
Stage 1 begins:
    - Canvas renders kitchen scene
    - Narration bar shows text
    - Progress bar starts
    - Duration: 3 seconds
    ↓
Stage 2 begins:
    - Split screen animation
    - Spotlight on "Ravi"
    - Arrow draws: Ravi → makes → chai
    - Interaction overlay: "Tap to continue"
    - Student taps → records interaction
    - Duration: 4 seconds
    ↓
Stage 3 begins:
    - Right split screen
    - Spotlight on "Chai"
    - Reverse arrow draws
    - Student taps → records interaction
    ↓
Stage 4 begins:
    - Comparison view
    - Transformation morph animation
    - Quiz popup appears
    - Student selects "Active Voice"
    - Correct feedback shown
    - Posts to /api/visual-teaching/feedback
    ↓
... continues through all stages ...
    ↓
Stage 7 completes:
    - Celebration confetti
    - onComplete callback fires
    - Final analytics logged


STEP 6: Analytics Storage
──────────────────────────
MongoDB documents:

visual_analytics:
{
  "user_id": "user-123",
  "visual_id": "abc-123",
  "question": "Explain active and passive voice",
  "subject": "English",
  "visual_type": "animated_lesson",
  "pattern": "split_screen",
  "complexity": "medium",
  "total_duration_ms": 28000,
  "num_stages": 7,
  "num_interactions": 4,
  "is_template": true,
  "timestamp": "2025-01-09T10:30:00Z"
}

visual_interactions (4 documents):
{
  "user_id": "user-123",
  "visual_id": "abc-123",
  "stage_index": 1,
  "interaction_type": "tap_to_continue",
  "user_response": {"timestamp": 1234567890},
  "timestamp": 1234567890
}
{
  "user_id": "user-123",
  "visual_id": "abc-123",
  "stage_index": 3,
  "interaction_type": "quiz",
  "user_response": {
    "selected": 0,
    "correct": true,
    "option": "Active Voice"
  },
  "timestamp": 1234567895
}
...
```

---

## Component Communication

```
┌─────────────────────────────────────────────────────────────────┐
│  MentorResponseV2 (Parent)                                       │
│                                                                  │
│  State:                                                          │
│  - response (from AI)                                            │
│  - animatedTeachingVisual (extracted)                            │
│                                                                  │
│  Renders:                                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ TeachingVisualPlayer                                        │ │
│  │                                                             │ │
│  │ Props:                                                      │ │
│  │ - visualData (stages, animations, interactions)             │ │
│  │ - onComplete (callback when visual finishes)                │ │
│  │ - onInteraction (callback for each interaction)             │ │
│  │                                                             │ │
│  │ State:                                                      │ │
│  │ - currentStage                                              │ │
│  │ - isPlaying                                                 │ │
│  │ - progress                                                  │ │
│  │ - showInteraction                                           │ │
│  │                                                             │ │
│  │ Renders:                                                    │ │
│  │ ┌────────────────────────────────────────────────────────┐ │ │
│  │ │ Canvas (AnimationEngine)                                │ │ │
│  │ │ - Draws SVG animations                                  │ │ │
│  │ │ - Handles transitions                                   │ │ │
│  │ └────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ ┌────────────────────────────────────────────────────────┐ │ │
│  │ │ InteractionLayer (when interaction required)            │ │ │
│  │ │                                                         │ │ │
│  │ │ Props:                                                  │ │ │
│  │ │ - interaction (type, question, options)                 │ │ │
│  │ │ - onResponse (callback with user answer)                │ │ │
│  │ │ - stage (current stage index)                           │ │ │
│  │ │                                                         │ │ │
│  │ │ Renders:                                                │ │ │
│  │ │ - QuizInteraction (if type === 'quiz')                  │ │ │
│  │ │ - DragInteraction (if type === 'drag')                  │ │ │
│  │ │ - SliderInteraction (if type === 'slider')              │ │ │
│  │ │ - PredictionInteraction (if type === 'predict')         │ │ │
│  │ │ - TapToContinue (if type === 'tap_to_continue')         │ │ │
│  │ └────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │ Controls:                                                   │ │
│  │ - Play/Pause button                                         │ │
│  │ - Restart button                                            │ │
│  │ - Skip button                                               │ │
│  │ - Speed controls (0.5x, 1x, 1.5x, 2x)                       │ │
│  │ - Progress bar with stage markers                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Event Flow

```
Component Lifecycle:
════════════════════

1. MOUNT
   - MentorResponseV2 mounts
   - Detects teaching_visual in props
   - Passes to TeachingVisualPlayer
   - Player creates AnimationEngine
   - Engine initializes canvas
   - Loads first stage

2. PLAY
   - User clicks play
   - Engine starts animation loop
   - Progress tracker starts
   - Narration displays
   - Stage animations execute

3. INTERACTION
   - Engine reaches interaction point
   - Pauses animation
   - Shows InteractionLayer overlay
   - User responds (quiz, drag, etc.)
   - Interaction posts to backend
   - Overlay hides
   - Animation resumes to next stage

4. COMPLETE
   - All stages finish
   - onComplete callback fires
   - Final analytics posted
   - Celebration animation
   - Controls show restart option

5. UNMOUNT
   - Cleanup interval timers
   - Destroy animation engine
   - Clear canvas
```

---

## Data Structures

```typescript
// TeachingVisual (Backend → Frontend)
{
  visual_id: string,
  type: "animated_lesson" | "interactive_scene",
  stages: AnimationStage[],
  total_duration_ms: number,
  interaction_points: number[],
  metadata: {
    subject: string,
    topic: string,
    concept_type: string,
    visual_pattern: string,
    complexity: "simple" | "medium" | "complex",
    cultural_metaphor: string,
    grade_level: string
  }
}

// AnimationStage
{
  stage_id: string,
  duration_ms: number,
  narration: string,
  animations: Animation[],
  interactions?: Interaction[],
  emphasis?: string
}

// Animation
{
  type: "scene_setup" | "split_screen" | "spotlight" | ...,
  ...animationSpecificProps
}

// Interaction
{
  type: "quiz" | "drag" | "slider" | "tap_to_continue" | "predict",
  ...interactionSpecificProps
}
```

---

This flow diagram shows how a student question transforms into an animated, interactive teaching experience with cultural relevance and continuous engagement!
