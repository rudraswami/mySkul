# 🎛️ Sketchy Interactive Controls

**Purpose:** Hand-drawn controls with ZERO HTML inputs

## Components

### `SketchSlider.jsx`
RoughJS-based slider (NO `<input type="range">`).

**Features:**
- Rail: RoughJS line (slightly bowed)
- Thumb: RoughJS circle with wobble
- Label: Handwriting font
- Drag: Pointer events (mouse + touch)
- Animation: Framer Motion

**Usage:**
```jsx
<SketchSlider
  label="Force"
  value={force}
  min={0}
  max={100}
  onChange={setForce}
  color={NOTEBOOK_THEME.markerBlue}
/>
```

### `SketchToggle.jsx`
Hand-drawn switch (wobbly, organic).

### `SketchButton.jsx`
Sketchy button with hover effects.

### `SketchKnob.jsx`
Rotary control (optional, for advanced interactions).

---

## Design Principles

1. **Pure SVG** - No HTML inputs visible
2. **RoughJS aesthetic** - Wobbly, hand-drawn
3. **Accessible** - Hidden HTML inputs for screen readers
4. **Responsive** - Touch + mouse unified
5. **Animated** - Smooth Framer Motion transitions

---

**Status:** 🚧 Phase 2 (After renderer)
**Dependencies:** primitives/
**Replaces:** 
- `components/visuals/InteractiveControls.js` (HTML sliders)
- `sketch/UniversalSketchCanvasV6.jsx` SketchSlider (HTML)

