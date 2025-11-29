# 🎨 Druv AI Visual Builder Engine

## Interactive, Culturally Indian, Professor-Style Visual Teaching System

This engine replaces static SVG diagrams with **animated, interactive scenes** that feel like a professor demonstrating concepts in a lab or playground.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DRUV AI VISUAL ENGINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   TOON      │───▶│   Scene     │───▶│  Animation  │         │
│  │   Parser    │    │   Builder   │    │  Timeline   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                 │                  │                  │
│         ▼                 ▼                  ▼                  │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              SCENE RENDERER (SVG/Canvas)             │       │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │       │
│  │  │Background│ │ Props   │ │ Actors  │ │ Labels  │   │       │
│  │  │ Layer   │ │ Layer   │ │ Layer   │ │ Layer   │   │       │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │       │
│  └─────────────────────────────────────────────────────┘       │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              INTERACTION ENGINE                      │       │
│  │  • Tap → Animate    • Swipe → Next Step             │       │
│  │  • Long Press → Formula   • Tap Prop → Explain      │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
frontend/src/visual-engine/
├── README.md
├── index.js                    # Main exports
├── core/
│   ├── TOONParser.js           # TOON → Scene config
│   ├── SceneBuilder.js         # Builds scene from config
│   ├── AnimationTimeline.js    # Controls animations
│   └── InteractionEngine.js    # Handles user interactions
├── components/
│   ├── SceneRenderer.jsx       # Main scene component
│   ├── BackgroundLayer.jsx     # Scene backgrounds
│   ├── PropsLayer.jsx          # Objects (ball, box, etc.)
│   ├── ActorLayer.jsx          # Professor avatar
│   ├── LabelsLayer.jsx         # Text, formulas
│   ├── VectorArrow.jsx         # Animated arrows
│   └── InteractionOverlay.jsx  # Tap zones
├── assets/
│   ├── backgrounds/            # Cricket pitch, lab, classroom
│   ├── props/                  # Ball, bat, auto, mango
│   ├── actors/                 # Professor avatar states
│   └── icons/                  # Formula symbols
├── animations/
│   ├── motion.js               # Object movement
│   ├── vectors.js              # Force arrows
│   ├── gestures.js             # Professor gestures
│   └── effects.js              # Glow, highlight, etc.
├── templates/
│   ├── force.toon.js           # Force concept template
│   ├── motion.toon.js          # Motion concept template
│   ├── gravity.toon.js         # Gravity concept template
│   └── friction.toon.js        # Friction concept template
└── utils/
    ├── indianContext.js        # Cultural adaptations
    ├── hinglish.js             # Bilingual labels
    └── scaleHelpers.js         # Responsive sizing
```

## Usage

```jsx
import { VisualScene } from './visual-engine';

// From TOON instruction
<VisualScene 
  toon={forceTOON} 
  onInteraction={handleInteraction}
  language="hinglish"
/>

// Or from concept name (auto-generates TOON)
<VisualScene 
  concept="force" 
  context={{ examType: 'JEE', region: 'north' }}
/>
```

## Key Features

- **Scene-based**: Full environments, not just diagrams
- **Animated**: Objects move, vectors grow, professor gestures
- **Interactive**: Tap to animate, swipe to advance
- **Cultural**: Indian metaphors (cricket, auto, mango)
- **Scalable**: Add new concepts via TOON templates
- **Lightweight**: Pure SVG + Framer Motion, no heavy 3D









