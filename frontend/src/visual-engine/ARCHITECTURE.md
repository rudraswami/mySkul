# 🎨 Druv AI Visual Builder Engine - Architecture

## Overview

The Visual Builder Engine is a complete replacement for static SVG diagrams. It creates **animated, interactive, scene-based visuals** that feel like a professor demonstrating concepts.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DRUV AI VISUAL ENGINE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐                                                   │
│  │   TOON Template  │ ◄── Concept definitions (force.toon.js, etc.)    │
│  │   Library        │                                                   │
│  └────────┬─────────┘                                                   │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────┐                                                   │
│  │   TOON Parser    │ ◄── Converts TOON → Scene Config                 │
│  │   (core)         │                                                   │
│  └────────┬─────────┘                                                   │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────┐    ┌──────────────────┐                          │
│  │  Animation       │    │  Indian Context  │                          │
│  │  Timeline        │◄──►│  (hinglish,      │                          │
│  │  Controller      │    │   analogies)     │                          │
│  └────────┬─────────┘    └──────────────────┘                          │
│           │                                                             │
│           ▼                                                             │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │                    SCENE RENDERER                          │         │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │         │
│  │  │Background│ │  Props  │ │ Actors  │ │ Labels  │         │         │
│  │  │ Layer   │ │  Layer  │ │ Layer   │ │ Layer   │         │         │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │         │
│  │                                                            │         │
│  │  ┌─────────────────────────────────────────────────┐      │         │
│  │  │              Vector Arrows (Animated)            │      │         │
│  │  └─────────────────────────────────────────────────┘      │         │
│  └───────────────────────────────────────────────────────────┘         │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────┐                                                   │
│  │  Interaction     │ ◄── Tap, Long Press, Swipe handlers              │
│  │  Engine          │                                                   │
│  └──────────────────┘                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## TOON Format (Teaching Object Oriented Notation)

TOON is our custom DSL for defining visual teaching scenes:

```javascript
{
  topic: "Force (बल)",
  
  scene: "cricket_pitch",  // Background type
  
  actors: [
    { id: "professor", type: "professor", position: {x: 0.1, y: 0.5} }
  ],
  
  props: [
    { id: "ball", type: "cricket_ball", position: {x: 0.35, y: 0.45} }
  ],
  
  animations: [
    { id: "throw", target: "ball", type: "throw", trigger: "auto" }
  ],
  
  labels: [
    { target: "ball", text: "FORCE", textHi: "बल" }
  ],
  
  steps: [
    { title: "Step 1", animations: ["throw"], duration: 2000 }
  ],
  
  analogy: "Bowler applies force → ball accelerates!"
}
```

---

## Components

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| `TOONParser` | `core/TOONParser.js` | Converts TOON → Scene config |
| `AnimationTimeline` | `core/AnimationTimeline.js` | Controls animation sequencing |
| `VisualScene` | `components/VisualScene.jsx` | Main wrapper component |
| `SceneRenderer` | `components/SceneRenderer.jsx` | SVG rendering engine |

### Layer Components

| Component | Purpose |
|-----------|---------|
| `BackgroundLayer` | Scene backgrounds (cricket, classroom, lab, street, village, space) |
| `PropsLayer` | Objects (ball, bat, auto, mango, box, etc.) |
| `ActorLayer` | Professor avatar with gestures |
| `LabelsLayer` | Text, formulas, Hinglish annotations |
| `VectorArrow` | Animated force/motion arrows |

### UI Components

| Component | Purpose |
|-----------|---------|
| `ControlBar` | Play/pause, step navigation |
| `StepIndicator` | Visual progress indicator |
| `InteractiveVisualCard` | Drop-in replacement for static visual |

---

## Animation Types

| Type | Description | Example |
|------|-------------|---------|
| `throw` | Projectile motion | Ball thrown by bowler |
| `push/pull` | Linear force | Box pushed on surface |
| `fall` | Gravity drop | Mango falling from tree |
| `move` | Point-to-point | Auto moving on road |
| `rotate` | Spinning | Ball spin |
| `vector_grow` | Arrow animation | Force vector appearing |
| `gesture` | Actor gesture | Professor pointing |

---

## Indian Context System

### Regional Props

```javascript
{
  north: { vehicle: 'auto_rickshaw', fruit: 'mango', drink: 'chai' },
  south: { vehicle: 'auto_rickshaw', fruit: 'coconut', drink: 'filter_coffee' },
  east:  { vehicle: 'auto_rickshaw', fruit: 'mango', sport: 'football' },
  west:  { vehicle: 'auto_rickshaw', fruit: 'chikoo', food: 'dhokla' },
}
```

### Hinglish Labels

All labels support dual text (English + Hindi):
```javascript
{ text: "FORCE", textHi: "बल" }
{ text: "More Force → More Speed!", textHi: "ज़्यादा बल → ज़्यादा तेज़!" }
```

---

## Usage

### Basic Usage

```jsx
import { VisualScene } from './visual-engine';
import { forceTOON } from './visual-engine/templates/force.toon';

// With TOON template
<VisualScene toon={forceTOON} autoPlay={true} />

// Auto-generate from concept
<VisualScene concept="force" context={{ language: 'hinglish' }} />
```

### Integration with AI Tutor

```jsx
import InteractiveVisualCard from './visual-engine/components/InteractiveVisualCard';

// In MentorResponseV2.js
<InteractiveVisualCard
  question={userQuestion}
  subject="Physics"
  studentProfile={profile}
  fallbackSvg={staticSvg}  // Fallback if no interactive template
  embedded={true}
  onInteraction={handleInteraction}
/>
```

---

## Adding New Concepts

### Step 1: Create TOON Template

Create `templates/newconcept.toon.js`:

```javascript
export const newConceptTOON = {
  topic: "New Concept",
  scene: "classroom",
  actors: [...],
  props: [...],
  animations: [...],
  labels: [...],
  steps: [...],
  analogy: "Real-world explanation...",
};
```

### Step 2: Register Template

In `utils/conceptToTOON.js`:

```javascript
import { newConceptTOON } from '../templates/newconcept.toon';

const TEMPLATES = {
  // ... existing
  'new concept': newConceptTOON,
};
```

### Step 3: Add Props (if needed)

In `components/PropsLayer.jsx`:

```javascript
const propComponents = {
  // ... existing
  new_object: ({ style }) => (
    <g>
      {/* SVG elements */}
    </g>
  ),
};
```

---

## File Structure

```
frontend/src/visual-engine/
├── index.js                    # Main exports
├── README.md                   # Overview
├── ARCHITECTURE.md             # This file
├── core/
│   ├── TOONParser.js           # TOON → Scene config
│   ├── AnimationTimeline.js    # Animation controller
│   └── InteractionEngine.js    # (To be implemented)
├── components/
│   ├── VisualScene.jsx         # Main component
│   ├── SceneRenderer.jsx       # SVG renderer
│   ├── BackgroundLayer.jsx     # Backgrounds
│   ├── PropsLayer.jsx          # Objects library
│   ├── ActorLayer.jsx          # Professor avatar
│   ├── LabelsLayer.jsx         # Text/formulas
│   ├── VectorArrow.jsx         # Force arrows
│   ├── ControlBar.jsx          # Playback controls
│   ├── StepIndicator.jsx       # Progress dots
│   └── InteractiveVisualCard.jsx # Integration
├── templates/
│   ├── force.toon.js           # Force concept
│   ├── motion.toon.js          # Motion concept
│   ├── gravity.toon.js         # Gravity concept
│   └── (more to add...)
└── utils/
    ├── conceptToTOON.js        # Auto TOON generation
    └── indianContext.js        # Cultural helpers
```

---

## Migration Plan

### Current State
- Static SVG generated by `dynamic_visual_sketch.py`
- No animations, no interactivity
- Basic diagrams

### Target State
- Animated scene-based visuals
- Interactive (tap, swipe, long-press)
- Professor avatar explaining
- Hinglish labels
- Step-by-step progression

### Migration Steps

1. **Phase 1** (Done): Create Visual Engine architecture
2. **Phase 2**: Implement core components (VisualScene, SceneRenderer)
3. **Phase 3**: Create TOON templates for Physics concepts
4. **Phase 4**: Integrate with AI Tutor (`InteractiveVisualCard`)
5. **Phase 5**: Replace static visual calls with new engine
6. **Phase 6**: Add more concepts (Chemistry, Biology, Math)

---

## Performance

- **SVG-based**: Lightweight, no heavy 3D rendering
- **Framer Motion**: Optimized React animations
- **Lazy loading**: Templates loaded on demand
- **Mobile-first**: Touch gestures, responsive sizing

---

## Future Enhancements

- [ ] React Native version using React Native Skia
- [ ] Voice-over support (professor speaking)
- [ ] AI-generated TOON from any concept
- [ ] Student interaction tracking
- [ ] A/B testing different visualizations







