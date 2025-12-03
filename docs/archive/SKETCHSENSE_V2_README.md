# SketchSense V2 Visual Engine

> **Enhancement Layer for Druv AI Visual System**
> 
> High-clarity, sketch-style, animated, culturally-relevant visual generator for Indian students.

---

## 🎯 Overview

SketchSense V2 is an **enhancement layer** built on top of the existing Druv AI visual engine. It adds:

- 🎨 **Sketch-style visuals** with hand-drawn feel
- 💡 **Neon highlights** for key concepts
- 🇮🇳 **Indian cultural context** (real-life examples)
- 🎬 **Multi-stage progressive reveals** (5 stages)
- 🎯 **Micro-tests** for engagement
- 🖱️ **Micro-interactions** (tap, slider, reveal)

**Key Principle**: This is an ADDITIVE enhancement - it does NOT replace existing visual functionality.

---

## 📁 File Structure

### Backend (`backend/`)

```
backend/
├── services/
│   └── sketchsense_v2.py        # SketchSense V2 Engine
├── api/
│   └── sketchsense.py           # REST API endpoints
└── tests/
    └── test_sketchsense_v2.py   # Unit tests
```

### Frontend (`frontend/`)

```
frontend/src/
├── visual-engine/
│   ├── core/
│   │   └── SketchSenseStyleSheet.js    # Styles & palettes
│   └── components/
│       └── SketchSenseRenderer.jsx     # Main renderer
├── hooks/
│   └── useSketchSense.js               # React hook
└── components/visual/
    └── SketchSenseDemo.jsx             # Demo component
```

---

## 🚀 Quick Start

### Backend Usage

```python
from services.sketchsense_v2 import create_sketchsense_blueprint

# Create blueprint for a concept
blueprint = create_sketchsense_blueprint(
    concept="force",
    subject="physics",
    question="What is force?"
)

# Result:
# {
#     "style": "sketchsense",
#     "version": "2.0",
#     "stages": {
#         "coreSketch": { "elements": [...] },
#         "animatedInsight": { "animations": [...] },
#         "realLifeExample": { "example": "Diwali rocket pushing up..." },
#         "formulaOverlay": { "formula": "F = ma", "units": "Newton (N)" },
#         "microTest": { "question": "...", "options": [...] }
#     },
#     ...
# }
```

### Frontend Usage

```jsx
import SketchSenseRenderer from './visual-engine/components/SketchSenseRenderer';
import useSketchSense from './hooks/useSketchSense';

function MyComponent() {
  const { blueprint, isReady } = useSketchSense({
    concept: 'force',
    subject: 'physics'
  });

  if (!isReady) return <Loading />;

  return (
    <SketchSenseRenderer
      blueprint={blueprint}
      autoPlay={true}
      showInteractions={true}
      onStageComplete={(stage) => console.log(stage)}
    />
  );
}
```

---

## 📐 Blueprint Schema

### SketchSense Blueprint V2

```typescript
{
  "style": "sketchsense",
  "version": "2.0",
  "stages": {
    "coreSketch": {
      "elements": [
        {
          "id": "concept_node",
          "type": "node" | "arrow" | "label" | "formula",
          "position": { "x": 0.5, "y": 0.4 },
          "style": { "fill": "#FF9933", "stroke": "#000080", "glow": true },
          "content": "Force",
          "hindiContent": "बल"
        }
      ]
    },
    "animatedInsight": {
      "animations": [
        {
          "targetId": "concept_node",
          "type": "draw_stroke" | "fade_in" | "pulse" | "vector_grow",
          "durationMs": 800,
          "delayMs": 0,
          "easing": "easeOut"
        }
      ]
    },
    "realLifeExample": {
      "example": "Diwali rocket pushing up → Newton's 3rd law!",
      "emoji": "🚀",
      "context": "indian"
    },
    "formulaOverlay": {
      "formula": "F = ma",
      "latex": "F = m \\times a",
      "units": "Newton (N)"
    },
    "microTest": {
      "question": "A 2kg object accelerates at 3m/s². What's the force?",
      "questionHi": "2kg वस्तु 3m/s² से त्वरित होती है। बल क्या है?",
      "options": ["5N", "6N", "1N", "9N"],
      "correctIndex": 1,
      "explanation": "F = ma = 2 × 3 = 6N"
    }
  },
  "interaction": {
    "sliders": [],
    "tapHighlights": [{ "type": "tap", "targetId": "concept_node" }],
    "revealOnTap": []
  },
  "style_config": {
    "strokeStyle": "sketch" | "neon" | "chalkboard" | "minimal",
    "neonHighlights": true,
    "colorPalette": "indian",
    "strokeJitter": 2.0,
    "glowIntensity": 0.6
  }
}
```

---

## 🎨 Color Palettes

### Indian Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Saffron | `#FF9933` | Primary concepts, highlights |
| Green | `#138808` | Secondary nodes, success |
| Navy | `#000080` | Text, borders, arrows |
| Maroon | `#800000` | Hindi text |
| Gold | `#FFD700` | Achievements, emphasis |
| Peacock | `#00A86B` | Examples, cards |

### Neon Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Neon Orange | `#FF6B35` | Glowing highlights |
| Neon Green | `#39FF14` | Success glow |
| Neon Blue | `#00D4FF` | Interactive feedback |
| Neon Pink | `#FF1493` | Attention |
| Neon Yellow | `#FFFF00` | Warning, tips |

---

## 🎬 Animation Types

| Type | Description | Duration |
|------|-------------|----------|
| `draw_stroke` | Hand-drawn line animation | 800ms |
| `fade_in` | Smooth opacity transition | 400ms |
| `vector_grow` | Arrow extends from source | 500ms |
| `pulse` | Scale + glow effect | 600ms |
| `flow` | Continuous movement | 1500ms |
| `reveal` | Tap-triggered appearance | 300ms |

---

## 🇮🇳 Indian Real-Life Examples

### Physics
- **Force**: "Diwali rocket pushing up → Newton's 3rd law in action! 🚀"
- **Gravity**: "Mango falling from tree in village → 9.8 m/s² same everywhere! 🥭"
- **Motion**: "Auto-rickshaw accelerating in traffic → F=ma live demo! 🛺"
- **Friction**: "Chappal sliding on wet bathroom floor → reduce friction = slip! 🩴"

### Chemistry
- **Acids/Bases**: "Nimbu paani (acidic) vs sabun paani (basic) → pH scale IRL! 🍋"
- **Reactions**: "Dahi (curd) forming from milk → fermentation reaction! 🥛"

### Biology
- **Photosynthesis**: "Tulsi plant on balcony making food from sunlight! 🌿"
- **Digestion**: "Rajma-chawal journey from plate to energy! 🍛"

---

## 🔌 API Endpoints

### POST `/api/sketchsense/blueprint`

Generate a SketchSense V2 blueprint.

**Request:**
```json
{
  "concept": "force",
  "subject": "physics",
  "question": "What is force?",
  "config": {
    "styleMode": "sketch",
    "showTest": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "blueprint": { ... },
  "concept": "force",
  "subject": "physics",
  "version": "2.0"
}
```

### POST `/api/sketchsense/enhance`

Enhance an existing visual with SketchSense V2 features.

**Request:**
```json
{
  "existing_visual": { "svg": "...", "metaphor": "Family" },
  "concept": "force",
  "subject": "physics"
}
```

### GET `/api/sketchsense/examples`

Get all available Indian real-life examples.

### GET `/api/sketchsense/micro-tests/{subject}`

Get micro-test templates for a subject.

### GET `/api/sketchsense/health`

Health check endpoint.

---

## 🧪 Testing

### Backend Tests

```bash
# Run all SketchSense tests
pytest backend/tests/test_sketchsense_v2.py -v

# Run specific test
pytest backend/tests/test_sketchsense_v2.py::TestSketchSenseV2Engine -v
```

### Frontend Demo

Navigate to the demo component in your app:

```jsx
import SketchSenseDemo from './components/visual/SketchSenseDemo';

// In your routes
<Route path="/sketchsense-demo" element={<SketchSenseDemo />} />
```

---

## ⚡ Performance

| Metric | Target | Implementation |
|--------|--------|----------------|
| Blueprint generation | <50ms | Python dataclasses, caching |
| SVG render | <100ms | Lightweight SVG, no heavy 3D |
| Animation FPS | 60fps | Framer Motion, RAF |
| Bundle size | <20KB | Tree-shakeable exports |

---

## 🔒 Implementation Rules

These rules are critical for Cursor AI and developers:

### ✅ DO

- Enhance existing visual files in small increments
- Add optional modules that can be toggled
- Patch via small, targeted diffs
- Preserve all existing functionality
- Use the enhancement pattern for integration

### ❌ DON'T

- Override full visual files
- Delete existing logic
- Refactor large portions at once
- Replace the core renderer
- Break backwards compatibility

---

## 📚 Related Files

- [`backend/services/visual_engine.py`](backend/services/visual_engine.py) - Original visual engine
- [`backend/services/handdrawn_sketch.py`](backend/services/handdrawn_sketch.py) - SVG sketch generator
- [`frontend/src/visual-engine/ARCHITECTURE.md`](frontend/src/visual-engine/ARCHITECTURE.md) - Frontend visual engine docs

---

## 🗺️ Roadmap

### ✅ Implemented (V2.0)

- [x] SketchSense Blueprint schema
- [x] Multi-stage progressive reveal
- [x] Indian cultural examples
- [x] Micro-test system
- [x] Sketch-style rendering
- [x] Neon highlights
- [x] API endpoints
- [x] React hook integration
- [x] Demo component

### 🚧 Coming Soon (V2.1)

- [ ] Slider-driven real-time value changes
- [ ] Voice-over support (TTS)
- [ ] Regional language support (Tamil, Telugu, etc.)
- [ ] Concept dependency graphs
- [ ] Spaced repetition integration

### 📋 Future (V3.0)

- [ ] AI-generated custom blueprints per question
- [ ] Collaborative visual annotations
- [ ] Student sketch input recognition
- [ ] AR/VR visual experiences

---

## 📄 License

Part of Druv AI Visual Sketch Engine. Internal use only.




