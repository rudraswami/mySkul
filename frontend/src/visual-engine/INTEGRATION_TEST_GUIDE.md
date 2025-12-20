# 🧪 MAGIC NOTEBOOK ENGINE V6 - INTEGRATION TEST GUIDE

## TEST SUITE FOR COMPLETE VALIDATION

---

## 1️⃣ VALIDATOR INTEGRATION TEST

### Test Case 1: Physics Validator - Friction Range

```javascript
// Test in browser console:

// Import validator
import { PhysicsValidator } from './visual-engine/validators';

const validator = new PhysicsValidator();

// Test valid friction
const result1 = validator.validate(0.5, { property: 'friction' });
console.log('✅ Valid friction (0.5):', result1.valid); // Should be true

// Test invalid friction (> 1)
const result2 = validator.validate(1.5, { property: 'friction' });
console.log('❌ Invalid friction (1.5):', result2.valid); // Should be false
console.log('Error message:', result2.results[0]?.message);
// Expected: "Friction = 1.50 is unrealistic. Friction is between 0 (ice) and 1 (rubber). 🧊"

// Test invalid friction (< 0)
const result3 = validator.validate(-0.3, { property: 'friction' });
console.log('❌ Invalid friction (-0.3):', result3.valid); // Should be false
```

### Test Case 2: Math Validator - Division by Zero

```javascript
import { MathValidator } from './visual-engine/validators';

const validator = new MathValidator();

// Test division by zero
const result = validator.validate(5, { 
  operation: 'divide', 
  denominator: 0 
});
console.log('❌ Division by zero:', result.valid); // Should be false
console.log('Error:', result.results[0]?.message);
// Expected: "Cannot divide by zero! 🚫 Division by zero is undefined."

// Test valid division
const result2 = validator.validate(10, { 
  operation: 'divide', 
  denominator: 2 
});
console.log('✅ Valid division:', result2.valid); // Should be true
```

### Test Case 3: SketchSlider with Validation

```jsx
// Test component:
import { SketchSlider } from './visual-engine/controls';
import { useState } from 'react';

function TestSlider() {
  const [friction, setFriction] = useState(0.5);
  
  return (
    <div style={{ padding: '40px' }}>
      <h3>Test: Friction Slider (0-1 valid range)</h3>
      <SketchSlider
        value={friction}
        onChange={setFriction}
        min={-1}
        max={2}
        step={0.1}
        label="Friction Coefficient"
        subject="physics"
        property="friction"
        enableValidation={true}
      />
      <p>Current value: {friction}</p>
      <p>Try dragging to -0.5 or 1.5 to trigger validation error</p>
    </div>
  );
}
```

**Expected Behavior:**
- Values 0-1: ✅ Smooth update, no errors
- Values < 0 or > 1: ❌ Shake animation, error message in console, Ghost Mentor appears

---

## 2️⃣ EIGHT MODES TEST

### Test Mode 1: SCENE (Physics)

**Question:** "Explain Newton's second law"

**Expected Blueprint:**
```json
{
  "mode": "SCENE",
  "concept": "Newton's Second Law",
  "subject": "physics",
  "entities": [
    {"id": "ball", "type": "circle", "label": "Ball"},
    {"id": "force", "type": "circle", "label": "Force"}
  ],
  "metaphor": null
}
```

**Visual Check:**
- ✅ Items positioned horizontally (flow layout)
- ✅ Arrows connecting ball → force
- ✅ Drawing hand follows strokes
- ✅ RoughJS wobbly lines
- ✅ Narrative: 5 beats play sequentially

### Test Mode 2: COMPARISON (X vs Y)

**Question:** "Compare AC vs DC current"

**Expected Blueprint:**
```json
{
  "mode": "COMPARISON",
  "concept": "AC vs DC Current",
  "subject": "physics",
  "entities": [
    {"id": "ac", "label": "AC Current"},
    {"id": "dc", "label": "DC Current"}
  ]
}
```

**Visual Check:**
- ✅ Center divider line
- ✅ "VS" label at top
- ✅ Items split left/right
- ✅ Comparison labels below

### Test Mode 3: CYCLE (Loops)

**Question:** "Explain the water cycle"

**Expected Blueprint:**
```json
{
  "mode": "CYCLE",
  "concept": "Water Cycle",
  "subject": "biology",
  "metaphor": "monsoon"
}
```

**Visual Check:**
- ✅ Circular layout
- ✅ Curved arrows forming loop
- ✅ Cycle direction indicator (↻)
- ✅ Items evenly spaced around center

### Test Mode 4: PROCESS (Steps)

**Question:** "Explain photosynthesis process"

**Expected Blueprint:**
```json
{
  "mode": "PROCESS",
  "concept": "Photosynthesis",
  "subject": "biology"
}
```

**Visual Check:**
- ✅ Step numbers (1, 2, 3)
- ✅ Flow arrows between steps
- ✅ Sequential reveal
- ✅ Left-to-right flow

### Test Mode 5: STRUCTURE (Anatomy)

**Question:** "Show heart structure"

**Expected Blueprint:**
```json
{
  "mode": "STRUCTURE",
  "concept": "Heart Structure",
  "subject": "biology"
}
```

**Visual Check:**
- ✅ Callout labels with leader lines
- ✅ Multiple shapes (circles, ellipses)
- ✅ Color-coded parts
- ✅ Anatomical layout

### Test Mode 6: GRAPH (Math)

**Question:** "Plot y = x²"

**Expected Blueprint:**
```json
{
  "mode": "GRAPH",
  "concept": "Quadratic Function",
  "subject": "math",
  "functions": [{"fn": (x) => x*x, "label": "y = x²"}]
}
```

**Visual Check:**
- ✅ X/Y axes with arrows
- ✅ Grid lines (optional)
- ✅ Function curve drawn
- ✅ Smooth parabola shape

### Test Mode 7: TIMELINE (History)

**Question:** "Timeline of human evolution"

**Expected Blueprint:**
```json
{
  "mode": "TIMELINE",
  "concept": "Human Evolution",
  "subject": "biology"
}
```

**Visual Check:**
- ✅ Horizontal timeline
- ✅ Event markers with dates
- ✅ Alternating positions (above/below)
- ✅ Arrow at end

### Test Mode 8: HIERARCHY (Trees)

**Question:** "Show animal classification hierarchy"

**Expected Blueprint:**
```json
{
  "mode": "HIERARCHY",
  "concept": "Animal Classification",
  "subject": "biology"
}
```

**Visual Check:**
- ✅ Tree structure
- ✅ Parent-child connections
- ✅ Root node larger
- ✅ Level indicators

---

## 3️⃣ METAPHOR ENGINE TEST

### Test 1: Cricket Metaphor

**Question:** "Explain centripetal force using cricket"

**Expected:**
- ✅ `metaphor: "cricket"`
- ✅ Cricket ball SVG appears (🏏)
- ✅ Ball label becomes "Cricket Ball"
- ✅ Green grass background
- ✅ Narrative mentions cricket

**Console Check:**
```javascript
console.log('🇮🇳 Metaphor applied: cricket');
```

### Test 2: Auto Rickshaw Metaphor

**Question:** "Explain friction using auto-rickshaw"

**Expected:**
- ✅ `metaphor: "auto_rickshaw"`
- ✅ Auto SVG appears (🛺)
- ✅ Road background
- ✅ Indian context in narrative

### Test 3: Diwali Metaphor

**Question:** "Explain light energy using Diwali"

**Expected:**
- ✅ `metaphor: "diwali"`
- ✅ Diya lamp SVG (🪔)
- ✅ Golden festive background
- ✅ Narrative mentions Diwali

### Test 4: Chai Metaphor

**Question:** "Explain heat transfer with chai"

**Expected:**
- ✅ `metaphor: "chai"`
- ✅ Chai cup SVG (☕)
- ✅ Steam animation
- ✅ Temperature context

---

## 4️⃣ NARRATIVE ENGINE TEST

### Test: 5-Beat Teaching Flow

**Question:** "Explain force and motion"

**Expected Beat Sequence:**

**Beat 1 (0-2s): Setup**
- ✅ Text bubble appears: "Let me show you force and motion..."
- ✅ Hand in idle pose
- ✅ No items drawn yet

**Beat 2 (2-4s): Concept**
- ✅ Text: "When force is applied..."
- ✅ First item draws (ball)
- ✅ Hand follows stroke
- ✅ pathLength animates 0→1

**Beat 3 (4-6s): Connection**
- ✅ Text: "...it causes motion!"
- ✅ Second item draws (arrow/force)
- ✅ Hand moves to new position

**Beat 4 (6-8s): Insight**
- ✅ Text: "The key formula is F = ma"
- ✅ Items highlight (yellow glow)
- ✅ Pause for emphasis
- ✅ Hand in pointing pose

**Beat 5 (8-10s): Memory Hook**
- ✅ Text: "Now you'll never forget! 💪"
- ✅ All items visible
- ✅ Hand returns to idle

**Console Logs:**
```javascript
// Should see these in order:
"🎬 Beat 1: Setup"
"🎬 Beat 2: Concept"
"🎬 Beat 3: Connection"
"🎬 Beat 4: Insight"
"🎬 Beat 5: Memory Hook"
"🎬 Narrative teaching complete!"
```

---

## 5️⃣ DRAWING HAND + STROKE SYNCHRONIZATION TEST

### Test: Hand Follows Path

**Setup:**
```jsx
<MagicNotebookEngine
  question="Explain circular motion"
  context={{ subject: 'physics' }}
  showNarrative={true}
  showControls={true}
/>
```

**Expected Behavior:**

1. **Initial State (t=0s)**
   - Hand: Idle pose, positioned at (50, 50)
   - Canvas: Empty, paper background

2. **Beat 2 Start (t=2s)**
   - Hand: Switches to drawing pose
   - Hand: Moves to start of first stroke
   - Item: Circle begins drawing
   - Hand position: Follows circle perimeter

3. **During Circle Draw (t=2-3s)**
   - pathLength: Animates 0 → 1
   - Hand: Rotates to face drawing direction
   - Hand X/Y: Matches current point on circle
   - Smooth motion (60 FPS)

4. **Circle Complete (t=3s)**
   - pathLength: 1.0
   - Hand: Pauses at completion point
   - Hand: Switches back to idle pose briefly

5. **Next Element (t=4s)**
   - Hand: Moves to arrow start
   - Hand: Switches to drawing pose
   - Arrow: Begins drawing
   - Hand: Follows arrow path

**Verification Checklist:**
- ✅ Hand visible throughout
- ✅ Hand never jumps (smooth transitions)
- ✅ Hand rotation matches stroke direction
- ✅ Hand appears "on top" of strokes (z-index)
- ✅ Hand switches poses correctly
- ✅ Timing synchronized (no lag)

---

## 6️⃣ BACKEND API TEST

### Test Endpoint Health

```bash
# Terminal:
curl http://localhost:8001/api/ai/visual-engine/health

# Expected response:
{
  "status": "ok",
  "openai_available": true,
  "version": "v6.0"
}
```

### Test Concept Breaking

```bash
curl -X POST http://localhost:8001/api/ai/visual-engine/concept-break \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain Newton'\''s second law using cricket",
    "context": {
      "subject": "physics",
      "level": "high_school"
    },
    "model": "gpt-4o-mini"
  }'
```

**Expected Response Structure:**
```json
{
  "blueprint": {
    "mode": "SCENE",
    "concept": "Newton's Second Law",
    "subject": "physics",
    "metaphor": "cricket",
    "entities": [...],
    "relations": [...],
    "beats": [...],
    "confidence": 0.9,
    "method": "llm"
  }
}
```

### Test Frontend → Backend Integration

```javascript
// Browser console:
import { useBreakConceptMutation } from './hooks/useConceptBreaker';

// In React component:
const { mutate } = useBreakConceptMutation();

mutate({
  question: "Explain momentum using cricket",
  context: { subject: 'physics', level: 'high_school' }
}, {
  onSuccess: (blueprint) => {
    console.log('✅ Blueprint received:', blueprint);
    console.log('Mode:', blueprint.mode);
    console.log('Metaphor:', blueprint.metaphor);
    console.log('Entities:', blueprint.entities.length);
  },
  onError: (error) => {
    console.error('❌ API Error:', error);
  }
});
```

---

## 7️⃣ DOM INSPECTION CHECKLIST

### Visual DOM Structure Check

Open DevTools → Elements, verify:

```html
<!-- Expected structure: -->
<div class="magic-notebook-engine">
  
  <!-- 1. Main SVG Canvas -->
  <svg width="600" height="500">
    <!-- Sketch filters -->
    <defs>
      <filter id="pencil-texture">...</filter>
      <filter id="hand-drawn">...</filter>
    </defs>
    
    <!-- Background -->
    <rect fill="#FFFEF7" />
    
    <!-- Mode-specific content -->
    <g id="scene-mode">
      <!-- Items -->
      <g class="sketch-circle">
        <path d="..." stroke="#333" />
        <text>Ball</text>
      </g>
      
      <!-- Arrows -->
      <g class="sketch-arrow">
        <path d="..." />
      </g>
    </g>
  </svg>
  
  <!-- 2. Drawing Hand Overlay -->
  <div class="drawing-hand" style="position: absolute; ...">
    <svg>
      <!-- Hand SVG -->
      <g class="hand-drawing-pose">...</g>
    </svg>
  </div>
  
  <!-- 3. Text Bubble -->
  <div class="text-bubble" style="position: absolute; ...">
    <svg>
      <path d="..." fill="#FFF9C4" />
      <text>Let me show you...</text>
    </svg>
  </div>
  
  <!-- 4. Controls (if any) -->
  <div class="narrative-controls">
    <button>⏮️</button>
    <button>▶️</button>
    <button>⏹️</button>
    <button>⏭️</button>
  </div>
  
</div>
```

### CSS Verification

Check computed styles:

```javascript
// In console:
const engine = document.querySelector('.magic-notebook-engine');
console.log('Background:', getComputedStyle(engine).background);
// Expected: #FFFEF7 (paper color)

const svg = engine.querySelector('svg');
console.log('SVG dimensions:', svg.getAttribute('width'), svg.getAttribute('height'));
// Expected: 600 x 500

const hand = document.querySelector('.drawing-hand');
console.log('Hand position:', getComputedStyle(hand).position);
// Expected: absolute

console.log('Hand z-index:', getComputedStyle(hand).zIndex);
// Expected: > 10 (above canvas)
```

### Animation State Check

```javascript
// Check Framer Motion animations:
const paths = document.querySelectorAll('path[style*="pathLength"]');
console.log('Animated paths:', paths.length);
// Expected: > 0

paths.forEach((path, i) => {
  const style = getComputedStyle(path);
  console.log(`Path ${i} pathLength:`, path.style.pathLength);
});
// Expected: Values between 0 and 1
```

---

## 8️⃣ PERFORMANCE CHECKS

### Frame Rate Test

```javascript
let frameCount = 0;
let lastTime = performance.now();

function measureFPS() {
  frameCount++;
  const now = performance.now();
  
  if (now - lastTime >= 1000) {
    console.log('FPS:', frameCount);
    // Expected: ~60 FPS
    frameCount = 0;
    lastTime = now;
  }
  
  requestAnimationFrame(measureFPS);
}

measureFPS();
```

### Load Time Test

```javascript
console.time('Blueprint Generation');
// Ask question...
// When blueprint appears:
console.timeEnd('Blueprint Generation');
// Expected: < 2 seconds (with LLM), < 100ms (cached)
```

---

## ✅ INTEGRATION COMPLETE CHECKLIST

Mark each as complete after testing:

**Validators:**
- [ ] Physics validator triggers on friction slider
- [ ] Math validator catches division by zero
- [ ] Chemistry validator checks valency
- [ ] ValidationFeedback shows shake animation
- [ ] Ghost Mentor appears with error message

**8 Modes:**
- [ ] SCENE mode renders correctly
- [ ] COMPARISON shows split view
- [ ] PROCESS shows numbered steps
- [ ] CYCLE shows circular arrows
- [ ] STRUCTURE shows callouts
- [ ] GRAPH plots functions
- [ ] TIMELINE shows events
- [ ] HIERARCHY shows tree

**Metaphors:**
- [ ] Cricket metaphor applies (ball → 🏏)
- [ ] Auto metaphor applies (🛺)
- [ ] Chai metaphor applies (☕)
- [ ] Diwali metaphor applies (🪔)

**Narrative:**
- [ ] 5 beats play in sequence
- [ ] Text bubbles appear with typewriter
- [ ] Pauses work correctly
- [ ] Beat transitions smooth

**Drawing Hand:**
- [ ] Hand visible during drawing
- [ ] Hand follows stroke paths
- [ ] Hand rotates with direction
- [ ] Hand switches poses
- [ ] Timing synchronized

**Backend:**
- [ ] Health endpoint responds
- [ ] Concept-break endpoint works
- [ ] GPT-4o-mini returns JSON
- [ ] Frontend receives blueprint
- [ ] Error handling works

**Performance:**
- [ ] 60 FPS animation
- [ ] < 2s blueprint generation
- [ ] No memory leaks
- [ ] Smooth interactions

---

## 🎯 FINAL VALIDATION

**When ALL checkboxes above are checked, integration is 100% complete.**

Mark in main integration document:
```
✅ INTEGRATION: 100% COMPLETE
✅ ALL TESTS PASSED
✅ PRODUCTION READY
```




















