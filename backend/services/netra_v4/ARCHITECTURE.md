# 🔮 NETRA v4.0 - Visual Intelligence Architecture

## Overview

NETRA v4.0 is the visual intelligence module that generates unique, rich, educational visuals for any student question.

## Core Architecture

```
User Question
    ↓
┌─────────────────────────────────────┐
│      NETRA ORCHESTRATOR             │
│   (coordinates all components)       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   VISUAL STRATEGY RESOLVER          │
│   ────────────────────────────      │
│   Model: Gemini 2.5 Flash           │
│   Purpose:                          │
│     - Analyze concept               │
│     - Determine intent              │
│     - Choose visual style           │
│     - Create visual metaphor        │
│     - Compose DALL-E 3 prompt       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   DALL-E 3 IMAGE GENERATOR          │
│   ────────────────────────────      │
│   Model: dall-e-3                   │
│   API: OpenAI Images API            │
│   Purpose:                          │
│     - Generate actual image         │
│     - Rich, contextual visuals      │
│     - Unique per concept            │
│   Output: Base64 PNG (1792x1024)    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   TEACHING METADATA GENERATOR       │
│   ────────────────────────────      │
│   Model: Gemini 2.5 Flash           │
│   Purpose:                          │
│     - Create hotspots               │
│     - Generate teaching steps       │
│     - Add annotations               │
│     - Key takeaways                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   VISUAL NORMALIZER                 │
│   ────────────────────────────      │
│   Purpose:                          │
│     - Validate image quality        │
│     - Package response              │
│     - Quality checks                │
└─────────────────────────────────────┘
    ↓
Frontend Renderer
```

## API Keys Used

| Component | API Key | Model |
|-----------|---------|-------|
| Strategy Resolver | `GEMINI_API_KEY` | `gemini-2.5-flash` |
| Image Generator | `OPENAI_API_KEY` | `dall-e-3` |
| Teaching Metadata | `GEMINI_API_KEY` | `gemini-2.5-flash` |

## Cost Analysis

### Per Visual Generation

| Component | Cost | Notes |
|-----------|------|-------|
| Gemini (Strategy) | ~$0.001 | 3 API calls, ~2000 tokens each |
| **DALL-E 3** | **$0.040** | 1792x1024, standard quality |
| Gemini (Teaching) | ~$0.001 | 1 API call, ~1500 tokens |
| **Total** | **~$0.042** | Per visual |

### Monthly Estimates

| Usage Level | Visuals/Month | Monthly Cost |
|-------------|---------------|--------------|
| Light (10/day) | 300 | ~$12.60 |
| Moderate (50/day) | 1,500 | ~$63.00 |
| Heavy (200/day) | 6,000 | ~$252.00 |

## Why DALL-E 3?

1. **Quality**: Best-in-class for educational illustrations
2. **Prompt Understanding**: Native understanding of complex educational concepts
3. **No Fallbacks**: Generates rich scenes, not diagrams
4. **Consistency**: Same API key as GPT-4 models (OPENAI_API_KEY)
5. **Reliability**: 99.9% uptime, enterprise-grade

## Key Design Decisions

### 1. No PIL Fallbacks
Previous implementation used PIL to draw generic circles/boxes as a "fallback". This is completely removed. If DALL-E 3 fails, we return an error - no fake visuals.

### 2. Rich Prompts from Gemini
Gemini 2.5 Flash analyzes the concept and creates detailed, scene-based prompts that guide DALL-E 3 to generate memorable visuals.

### 3. Visual Metaphors
Every concept is mapped to a real-world visual metaphor (e.g., "tug of war" for Newton's third law) to ensure visuals are relatable and memorable.

### 4. Anti-Generic Directives
Prompts explicitly instruct DALL-E 3 to NOT generate:
- Abstract diagrams
- Flowcharts
- Generic circles and arrows
- Text labels in images

### 5. Teaching Layer
Gemini generates interactive teaching elements (hotspots, steps) that overlay on the image for guided learning.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| DALL-E 3 API error | Return error response, no fallback |
| Content policy rejection | Return error, don't retry |
| Timeout (60s) | Return timeout error, suggest retry |
| Gemini failure | Use fallback prompts, continue generation |
| Invalid image | Return validation error |

## Frontend Integration

The frontend receives:
```javascript
{
  netra_v4: true,
  image_base64: "...",  // Full DALL-E 3 image
  image_format: "png",
  width: 1792,
  height: 1024,
  teaching: {
    hotspots: [...],
    steps: [...],
    key_takeaways: [...]
  },
  metadata: {
    concept: "...",
    intent: "...",
    style: "..."
  }
}
```

The `SmartBoard` component renders this with `NetraV4ImageRenderer`, displaying the full AI-generated image with optional teaching overlays.

## Performance

| Metric | Target | Typical |
|--------|--------|---------|
| Total Generation Time | <15s | 8-12s |
| Strategy Resolution | <3s | 1-2s |
| DALL-E 3 Generation | <10s | 5-8s |
| Teaching Metadata | <3s | 1-2s |

## Quality Bar

Every generated visual must:
- ✅ Be visually rich and engaging
- ✅ Show the concept in action (not as abstract symbols)
- ✅ Create an "aha moment" for students
- ✅ Be unique to the specific question
- ✅ Use real-world visual metaphors
- ❌ NOT be generic diagrams with circles/arrows
- ❌ NOT contain text labels or annotations
- ❌ NOT look like a flowchart or org chart


































