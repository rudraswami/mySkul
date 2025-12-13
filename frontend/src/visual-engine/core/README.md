# 🎨 Core Rendering Engine

**Purpose:** The foundation of Magic Notebook Engine V6

## Components

### `UniversalSketchRenderer.jsx`
The main SVG renderer that draws all visuals using RoughJS + Framer Motion.

**Responsibilities:**
- SVG canvas management
- Layer ordering (background → shapes → connections → labels → doodles)
- Animation timing coordination
- Blueprint consumption
- Mode routing

### `MagicNotebookEngine.jsx`
The top-level orchestrator that connects all systems.

**Responsibilities:**
- Receives question or blueprint
- Coordinates ConceptBreaker → SceneComposer → Renderer
- Manages narrative flow
- Handles user interactions
- Provides public API

### `EngineContext.jsx`
React Context for sharing state across the engine.

**Shared State:**
- Current blueprint
- Animation phase
- Interactive values
- Validator feedback
- Narrative beat

### `BlueprintSchema.js`
JSON schema definition and validation for blueprints.

**Blueprint Structure:**
```javascript
{
  mode: 'SCENE' | 'PROCESS' | 'CYCLE' | ...,
  items: [...],      // Shapes to draw
  arrows: [...],     // Connections
  labels: [...],     // Text
  highlights: [...], // Emphasis
  doodles: [...],    // Decorations
  figures: [...],    // Stick figures
  controls: [...],   // Interactive elements
  beats: [...]       // 5-beat narrative
}
```

### `types.js`
JSDoc type definitions for TypeScript-like autocomplete.

---

**Status:** 🚧 Under Construction (Phase 1)
**Dependencies:** primitives/, narrative/, controls/

