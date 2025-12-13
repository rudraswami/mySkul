# 🎬 Narrative Engine (5-Beat Teaching System)

**Purpose:** Orchestrates cinematic teaching flow with hand drawing

## Components

### `NarrativeEngine.js`
The conductor that coordinates all animations, hand movement, and text.

**5-Beat Structure:**
```
Beat 1 (0-2s): Setup - "Let me show you..."
Beat 2 (2-4s): Main Concept - Draw core idea
Beat 3 (4-6s): Connection - "See how this relates..."
Beat 4 (6-8s): Insight - Highlight key point
Beat 5 (8-10s): Memory Hook - "Now you'll never forget!"
```

**Controls:**
- Drawing sequence order
- Hand movement timing
- Text bubble appearance
- Highlight moments
- Pause/emphasis

### `DrawingHand.jsx`
Animated hand overlay that follows strokes.

**Poses:**
- `idle` - Relaxed hand
- `drawing` - Pen to paper
- `pointing` - Index finger extended

**Features:**
- Follows stroke paths
- Rotates based on direction
- Pauses at key nodes
- Synchronized with drawing animation

### `TextBubble.jsx`
Speech bubble with typewriter effect.

**Features:**
- RoughJS border (hand-drawn)
- Typewriter animation (character-by-character)
- Tail points to element or hand
- Handwriting font

### `RevealSequencer.js`
Enhanced version of existing `sketch/RevealSequenceEngine.js`.

**Enhancements:**
- 5-beat integration
- Hand coordination
- Pause system
- Emphasis triggers

### `HandMotionPath.js`
Calculates smooth motion paths for the hand.

**Algorithm:**
- Bezier curve generation
- Path smoothing
- Direction calculation (for rotation)
- Easing functions

### `assets/`
Hand SVG files in different poses.

---

**Status:** 🚧 Phase 4 (After hand system)
**Dependencies:** core/, primitives/, sketch/RevealSequenceEngine.js

