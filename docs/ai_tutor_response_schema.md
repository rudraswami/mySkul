# AI Tutor Response Schema

**Version**: 2.4  
**Last Updated**: October 2025  
**Maintainer**: Dhruv AI Engineering Team

## Overview

This document defines the canonical JSON schema for AI Tutor dual responses. All backend endpoints returning AI-generated educational content must conform to this structure.

## Schema Version History

- **v2.4** (Oct 2025): Added mentor_sections with structured emotional support
- **v2.3** (Sept 2025): Introduced micro_lesson_sections for progressive disclosure
- **v2.0** (Aug 2025): Dual AI system (Professor + Mentor personas)
- **v1.0** (June 2025): Single AI response

---

## Root Response Object

```json
{
  "primary": { /* Professor Response */ },
  "secondary": { /* Mentor Response */ },
  "visual": { /* Visual Generation Data */ },
  "sentiment_analysis": { /* User Sentiment */ },
  "quick_actions": [ /* Contextual Actions */ ],
  "motivational_footer": { /* Footer Data */ },
  "session_id": "string",
  "subject": "string",
  "timestamp": "ISO8601 string",
  "persona_blend": { /* Persona Weights */ }
}
```

---

## 1. Primary Response (Professor AI)

**Purpose**: Provides detailed, logical, exam-focused explanations.

### Schema

```json
{
  "type": "professor",
  "response": "string (full text response)",
  "confidence": 0.95,
  "progressive_sections": {
    "foundation": "string",
    "step_by_step": "string",
    "real_life": "string",
    "key_points": "string"
  },
  "micro_lesson_sections": {
    "concept_overview": "string (2-3 sentences)",
    "key_formula": ["string (LaTeX)", "..."],
    "step_by_step": "string (numbered steps)",
    "real_life_analogy": "string (practical example)",
    "mentor_tip": "string (strategic advice)",
    "visual_prompt": "string (for visual generation)"
  },
  "weight": 0.7
}
```

### Field Definitions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `type` | string | Always "professor" | Required |
| `response` | string | Full text response from GPT-5 | Required, sanitized |
| `confidence` | float | AI confidence score | 0.0 - 1.0 |
| `progressive_sections` | object | Legacy progressive disclosure sections | Optional |
| `micro_lesson_sections` | object | Structured micro-lesson content | Required |
| `micro_lesson_sections.concept_overview` | string | Core concept summary | 2-3 sentences, <300 chars |
| `micro_lesson_sections.key_formula` | array[string] | LaTeX formulas | Max 3 formulas, LaTeX format |
| `micro_lesson_sections.step_by_step` | string | Detailed explanation with steps | May contain numbered lists |
| `micro_lesson_sections.real_life_analogy` | string | Practical application example | <500 chars |
| `micro_lesson_sections.mentor_tip` | string | Strategic study advice | <400 chars |
| `micro_lesson_sections.visual_prompt` | string | Prompt for visual generation | <200 chars |
| `weight` | float | Professor persona weight | 0.5 - 1.0 |

### Example

```json
{
  "type": "professor",
  "response": "Understanding trigonometric identities is vital...",
  "confidence": 0.95,
  "micro_lesson_sections": {
    "concept_overview": "Trigonometric identities are mathematical equations involving trigonometric functions that are true for all values of the variables. They are fundamental tools in simplifying expressions and solving equations.",
    "key_formula": [
      "\\sin^2 \\theta + \\cos^2 \\theta = 1",
      "1 + \\tan^2 \\theta = \\sec^2 \\theta",
      "1 + \\cot^2 \\theta = \\csc^2 \\theta"
    ],
    "step_by_step": "1. Start with the Pythagorean theorem applied to the unit circle\n2. Derive primary identity from x² + y² = 1\n3. Divide by cos²θ to get tan²θ identity\n4. Divide by sin²θ to get cot²θ identity",
    "real_life_analogy": "Think of these identities as shortcuts in navigation. Just as GPS uses coordinate systems to find optimal routes, trigonometric identities help mathematicians find the shortest path to solutions.",
    "mentor_tip": "Master the primary Pythagorean identity first. Once you understand how it's derived from the unit circle, all other identities become logical extensions. Practice converting between different forms.",
    "visual_prompt": "Unit circle diagram showing sin and cos relationships"
  },
  "weight": 0.7
}
```

---

## 2. Secondary Response (Mentor AI)

**Purpose**: Provides motivational support, strategic guidance, and confidence building.

### Schema

```json
{
  "type": "mentor",
  "response": "string (full mentor response)",
  "mentor_sections": {
    "motivation_spark": "string (1-2 sentences)",
    "simplified_recap": "string (bullet points)",
    "confidence_tips": "string (actionable advice)",
    "encouragement": "string (closing quote)"
  },
  "confidence": 0.9,
  "weight": 0.3
}
```

### Field Definitions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `type` | string | Always "mentor" | Required |
| `response` | string | Full mentor response | Required, sanitized |
| `mentor_sections` | object | Structured emotional guidance | Required |
| `mentor_sections.motivation_spark` | string | Opening motivational message | 1-2 sentences, <200 chars |
| `mentor_sections.simplified_recap` | string | Bullet-point summary | Newline-separated bullets, <300 chars |
| `mentor_sections.confidence_tips` | string | Actionable study strategies | 2-3 tips, <200 chars |
| `mentor_sections.encouragement` | string | Closing encouragement | 1 sentence, <150 chars |
| `confidence` | float | Mentor confidence score | 0.0 - 1.0 |
| `weight` | float | Mentor persona weight | 0.0 - 0.5 |

### Example

```json
{
  "type": "mentor",
  "response": "I'm here to guide you through this! Memorizing key trigonometric identities...",
  "mentor_sections": {
    "motivation_spark": "You're tackling one of the most powerful tools in mathematics! These identities will serve you in calculus, physics, and engineering.",
    "simplified_recap": "• Pythagorean identities come from the unit circle\n• Reciprocal identities help simplify expressions\n• Co-function identities relate complementary angles\n• Even-odd identities help with symmetry",
    "confidence_tips": "Start by memorizing the three Pythagorean identities. Practice deriving the others from these base forms. Use flashcards and apply them to 5 problems daily.",
    "encouragement": "Remember, every expert was once a beginner. You're building skills that will unlock advanced mathematics! Keep practicing! 🌟"
  },
  "confidence": 0.9,
  "weight": 0.3
}
```

---

## 3. Visual Data

**Purpose**: Contains auto-generated SVG or Gemini image data for visual learning.

### Schema

```json
{
  "type": "svg" | "gemini_image" | "none",
  "content": "string (SVG XML or base64 image data)",
  "mime_type": "string (for images)",
  "generated": boolean
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `type` | enum | "svg", "gemini_image", or "none" |
| `content` | string | SVG XML markup or base64 image data |
| `mime_type` | string | MIME type (only for images, e.g., "image/png") |
| `generated` | boolean | Whether visual was successfully generated |

---

## 4. Sentiment Analysis

**Purpose**: Captures user emotional state and adapts AI tone accordingly.

### Schema

```json
{
  "primary_sentiment": "confusion" | "confidence" | "frustration" | "curiosity" | "neutral",
  "needs_encouragement": boolean,
  "persona_blend": {
    "professor": 0.7,
    "mentor": 0.3
  }
}
```

---

## 5. Quick Actions

**Purpose**: Contextual action buttons displayed to the user.

### Schema

```json
[
  {
    "id": "save_notes",
    "label": "Save to Notes",
    "icon": "bookmark",
    "action": "save_to_notes"
  },
  {
    "id": "practice_similar",
    "label": "Practice Similar",
    "icon": "target",
    "action": "generate_practice"
  }
]
```

---

## 6. Motivational Footer

**Purpose**: Displays user progress and motivational message at the bottom of responses.

### Schema

```json
{
  "message": "string",
  "progress_line": "string",
  "user_stats": {
    "accuracy": 0.85,
    "streak": 7,
    "mastery": 0.65
  }
}
```

---

## Text Sanitization Requirements

All text fields **MUST** be sanitized before persistence or API return:

1. **Remove escape sequences**: `\n` → actual newline, `\"` → `"`
2. **Remove markdown**: `**bold**` → `bold`, `*italic*` → `italic`
3. **Remove checkmarks**: `✅`, `❌` → removed
4. **Preserve LaTeX**: `\[`, `\]`, `\(`, `\)` → preserved for KaTeX
5. **Remove double backslashes**: `\\` → removed (except in LaTeX commands)

---

## Backward Compatibility

- **v2.4 clients** consume `mentor_sections` for structured mentor display
- **v2.3 clients** fall back to `response` field if `mentor_sections` missing
- **v1.0 clients** ignore `secondary` and only use `primary.response`

All new fields are **additive** and optional with sensible defaults.

---

## Validation Rules

1. `primary.micro_lesson_sections` must exist
2. `secondary.mentor_sections` must exist if Mentor weight > 0
3. All text fields must be sanitized
4. LaTeX formulas must be valid KaTeX syntax
5. Confidence scores must be 0.0 - 1.0
6. Weights (professor + mentor) should sum to ~1.0

---

## Error Handling

If any section is missing or invalid:

1. Backend should populate with **safe defaults**
2. Frontend should gracefully hide missing sections
3. Log warning but don't crash

---

## API Endpoint

**POST** `/api/ai/dual-response`

**Request:**
```json
{
  "message": "Explain trigonometric identities",
  "session_id": "uuid",
  "subject": "Mathematics"
}
```

**Response:** Full schema as defined above

---

## See Also

- [Text Sanitization Pipeline](./text_sanitization_pipeline.md)
- [Mentor Micro-Sections Spec](./mentor_microsections_spec.md)
- Backend: `/app/backend/services/ai_service.py`
- Frontend: `/app/frontend/src/components/microlesson/ResponseComposer.js`
