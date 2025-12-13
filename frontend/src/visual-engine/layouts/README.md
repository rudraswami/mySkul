# 📐 Layout Algorithms

Automatic positioning algorithms for visual elements.

## Available Layouts

### 1. **Grid Layout** (`GridLayout.js`)
Regular grid arrangement for items.

**Best for:** Periodic tables, comparison grids, structured data

```javascript
import { gridLayout } from './layouts';

const positions = gridLayout(items, {
  columns: 3,
  spacing: 80,
  alignment: 'center',
});
```

### 2. **Circular Layout** (`CircularLayout.js`)
Radial arrangement around a center point.

**Best for:** Cycles, circular processes, hub-and-spoke diagrams

```javascript
import { circularLayout, hubLayout } from './layouts';

const positions = circularLayout(items, {
  radius: 100,
  startAngle: -90,
  clockwise: true,
});

// Or hub with center node
const hubPositions = hubLayout(items, centerItem, { radius: 120 });
```

### 3. **Flow Layout** (`FlowLayout.js`)
Left-to-right or top-to-bottom sequential flow.

**Best for:** Process steps, timelines, sequential logic

```javascript
import { flowLayout, zigzagLayout } from './layouts';

const positions = flowLayout(items, {
  direction: 'horizontal',
  spacing: 80,
});

// Or zigzag pattern
const zigzagPositions = zigzagLayout(items, { amplitude: 50 });
```

### 4. **Tree Layout** (`TreeLayout.js`)
Hierarchical tree structure using Reingold-Tilford algorithm.

**Best for:** Taxonomies, org charts, classification hierarchies

```javascript
import { treeLayout, balancedTreeLayout } from './layouts';

const positions = treeLayout(items, {
  orientation: 'vertical',
  levelSpacing: 80,
  siblingSpacing: 60,
});

// Or balanced tree
const balancedPositions = balancedTreeLayout(items);
```

### 5. **Force-Directed Layout** (`ForceDirectedLayout.js`)
Physics-based layout using attraction/repulsion forces.

**Best for:** Concept maps, network diagrams, organic layouts

```javascript
import { forceDirectedLayout } from './layouts';

const positions = forceDirectedLayout(items, connections, {
  iterations: 50,
  repulsionStrength: 100,
  attractionStrength: 0.1,
});
```

## Usage with SceneComposer

The SceneComposer automatically selects the appropriate layout based on mode:

```javascript
import { SceneComposer } from './intelligence';

const composer = new SceneComposer();
const blueprint = composer.compose(conceptData);
// Positions are automatically calculated based on mode
```

## Mode → Layout Mapping

- **SCENE** → Flow Layout
- **COMPARISON** → Grid Layout
- **PROCESS** → Flow Layout
- **CYCLE** → Circular Layout
- **STRUCTURE** → Hub Layout
- **GRAPH** → Flow Layout
- **TIMELINE** → Flow Layout
- **HIERARCHY** → Tree Layout

## Creating Custom Layouts

All layout functions follow the same signature:

```javascript
function customLayout(items, options = {}) {
  const { canvasWidth, canvasHeight, spacing } = options;
  const positions = {};
  
  items.forEach((item, index) => {
    positions[item.id] = {
      x: /* calculate x */,
      y: /* calculate y */,
    };
  });
  
  return positions;
}
```
