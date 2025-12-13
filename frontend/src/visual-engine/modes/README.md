# 🎨 Visual Modes - 8 Master Renderers

Complete implementations of all 8 visual modes for different types of educational content.

---

## Overview

Each mode is optimized for a specific type of learning content:

| Mode | Icon | Best For | Examples |
|------|------|----------|----------|
| **Scene** | 🎬 | Physics, real-world scenarios | Forces, motion, cricket |
| **Comparison** | ⚖️ | X vs Y, pros/cons | AC vs DC, plant vs animal |
| **Process** | 🔄 | Step-by-step flows | Algorithms, photosynthesis |
| **Cycle** | ♻️ | Circular processes | Water cycle, Krebs cycle |
| **Structure** | 🏗️ | Anatomy, diagrams | Heart, atom, cell |
| **Graph** | 📊 | Math functions, data | y=x², trig functions |
| **Timeline** | ⏰ | History, chronology | Evolution, historical events |
| **Hierarchy** | 🌳 | Trees, classification | Taxonomy, org charts |

---

## Usage

### Automatic Mode Selection (via ModeRouter)

```javascript
import { ModeRouter } from './visual-engine/modes';

<ModeRouter blueprint={blueprint} animationState={animationState} />
```

The router automatically selects the correct mode based on `blueprint.mode`.

### Manual Mode Selection

```javascript
import { SceneMode, ComparisonMode } from './visual-engine/modes';

// Use specific mode
<SceneMode blueprint={blueprint} />
<ComparisonMode blueprint={blueprint} />
```

---

## Mode Details

### 1. 🎬 Scene Mode

**Purpose:** Physical scenarios with objects, forces, and motion

**Blueprint Structure:**
```javascript
{
  mode: 'SCENE',
  items: [
    { id: 'ball', type: 'circle', position: {x, y}, radius: 30 }
  ],
  arrows: [
    { from: 'ball', to: 'force', label: 'F' }
  ],
  figures: [
    { x: 100, y: 180, pose: 'pushing' }
  ]
}
```

**Best For:**
- Force diagrams
- Motion scenarios
- Real-world physics
- Cricket/sports metaphors

---

### 2. ⚖️ Comparison Mode

**Purpose:** Side-by-side comparison of two concepts

**Blueprint Structure:**
```javascript
{
  mode: 'COMPARISON',
  items: [
    { id: 'left1', position: {x: 100, y: 150} }, // Left side
    { id: 'right1', position: {x: 300, y: 150} } // Right side
  ],
  comparisons: [
    { text: 'Difference: ...', x: 200, y: 280 }
  ]
}
```

**Features:**
- Center divider line
- "VS" label
- Symmetric layout
- Comparison callouts

---

### 3. 🔄 Process Mode

**Purpose:** Step-by-step sequential processes

**Blueprint Structure:**
```javascript
{
  mode: 'PROCESS',
  items: [
    { id: 'step1', label: 'Input', position: {x: 60, y: 150} },
    { id: 'step2', label: 'Process', position: {x: 200, y: 150} },
    { id: 'step3', label: 'Output', position: {x: 340, y: 150} }
  ],
  arrows: [
    { from: 'step1', to: 'step2' },
    { from: 'step2', to: 'step3' }
  ]
}
```

**Features:**
- Step numbers (1, 2, 3)
- Flow arrows
- Sequential reveal
- Progress tracking

---

### 4. ♻️ Cycle Mode

**Purpose:** Circular loops and repeating processes

**Blueprint Structure:**
```javascript
{
  mode: 'CYCLE',
  centerX: 200,
  centerY: 150,
  items: [
    // Arranged in circle automatically
    { id: 'stage1', label: 'Evaporation', position: {x, y} },
    { id: 'stage2', label: 'Condensation', position: {x, y} }
  ],
  arrows: [
    { from: 'stage1', to: 'stage2' },
    { from: 'stage2', to: 'stage1' } // Completes cycle
  ]
}
```

**Features:**
- Circular layout
- Curved arrows
- Cycle direction indicator (↻)
- Center label (optional)

---

### 5. 🏗️ Structure Mode

**Purpose:** Labeled anatomical diagrams

**Blueprint Structure:**
```javascript
{
  mode: 'STRUCTURE',
  items: [
    { id: 'heart', type: 'ellipse', position: {x, y}, color: '#ffcdd2' }
  ],
  callouts: [
    {
      from: {x: 200, y: 150},
      to: {x: 300, y: 100},
      text: 'Left Ventricle',
      side: 'right'
    }
  ]
}
```

**Features:**
- Leader lines
- Callout labels
- Multiple shapes (circle, rect, ellipse)
- Color coding

---

### 6. 📊 Graph Mode

**Purpose:** Mathematical function plots

**Blueprint Structure:**
```javascript
{
  mode: 'GRAPH',
  xAxis: { min: -10, max: 10 },
  yAxis: { min: -10, max: 10 },
  functions: [
    {
      fn: (x) => x * x,
      label: 'y = x²',
      color: '#3B82F6'
    }
  ],
  points: [
    { x: 2, y: 4, label: '(2,4)' }
  ]
}
```

**Features:**
- X/Y axes with arrows
- Grid (optional)
- Function plotting
- Point markers
- Multiple functions

---

### 7. ⏰ Timeline Mode

**Purpose:** Chronological sequences

**Blueprint Structure:**
```javascript
{
  mode: 'TIMELINE',
  orientation: 'horizontal', // or 'vertical'
  events: [
    {
      title: 'Big Bang',
      date: '13.8 billion years ago',
      emoji: '💥',
      color: '#EF4444'
    },
    {
      title: 'Earth Forms',
      date: '4.5 billion years ago',
      emoji: '🌍'
    }
  ]
}
```

**Features:**
- Horizontal or vertical layout
- Event markers
- Date labels
- Emoji icons
- Alternating positions

---

### 8. 🌳 Hierarchy Mode

**Purpose:** Tree structures and classification

**Blueprint Structure:**
```javascript
{
  mode: 'HIERARCHY',
  root: 'root_id',
  items: [
    { id: 'root_id', label: 'Animals', position: {x: 200, y: 50}, level: 0 },
    { id: 'child1', label: 'Mammals', position: {x: 150, y: 120}, level: 1 },
    { id: 'child2', label: 'Birds', position: {x: 250, y: 120}, level: 1 }
  ],
  connections: [
    { from: 'root_id', to: 'child1' },
    { from: 'root_id', to: 'child2' }
  ]
}
```

**Features:**
- Tree layout
- Level indicators
- Size based on level
- Color coding by level
- Parent-child connections

---

## Integration with ConceptBreaker

Modes are automatically selected by ConceptBreaker:

```javascript
import { ConceptBreaker } from './intelligence';
import { ModeRouter } from './modes';

// ConceptBreaker detects mode
const blueprint = await breakConcept('Explain water cycle');
// blueprint.mode = 'CYCLE'

// ModeRouter renders appropriate component
<ModeRouter blueprint={blueprint} />
```

**Mode Detection Logic:**
- Keywords trigger modes (e.g., "vs" → COMPARISON)
- Subject defaults (e.g., physics → SCENE)
- Concept patterns (e.g., "cycle" → CYCLE)

---

## Animation State

All modes support animation state for synchronized reveals:

```javascript
const animationState = {
  items: {
    'ball': { visible: true, progress: 1.0 },
    'force': { visible: false }
  }
};

<ModeRouter blueprint={blueprint} animationState={animationState} />
```

---

## Extending Modes

### Adding a New Mode

1. Create `NewMode.jsx` in `modes/`
2. Export from `index.js`
3. Add to `ModeRouter.jsx` mode map
4. Update `ConceptBreaker.js` detection

---

## Performance

- ✅ **Lazy rendering** - Only visible items render
- ✅ **Memoization** - Primitives are memoized
- ✅ **Progressive reveal** - Items animate sequentially
- ✅ **GPU acceleration** - Transform-based animations

---

## Examples

See `EXAMPLES.jsx` in each mode folder for complete working examples.

---

For implementation details, see individual mode files.
