# 🎨 DRUV AI VISUAL ENGINE V2 - PHASED ROADMAP

## 📊 Current State Analysis

### ✅ Already Implemented (DO NOT DUPLICATE)
1. **Core Architecture**
   - `InteractiveVisualCard.jsx` - Universal visual loader
   - `TOONParser.js` - TOON → Scene config converter
   - `InteractionEngine.js` - Tap, swipe, long-press handlers
   - `AnimationTimeline.js` - Animation sequencing
   - `SceneObjectRegistry.js` - Object state management

2. **Scene Components**
   - `CompactPhysicsScene.jsx` - Force demo with sliders
   - `MotionVisualScene.jsx` - Velocity/acceleration
   - `GravityVisualScene.jsx` - Falling objects
   - `BiologyCellScene.jsx` - Interactive cell organelles
   - `ChemistryAtomScene.jsx` - Atomic structure
   - `MathPythagorasScene.jsx` - Geometry

3. **Indian Context System**
   - `indianContext.js` - Regional props (auto, mango, chai)
   - Hinglish labels support
   - Cricket-themed physics demos

4. **Concept Registry**
   - 50+ concepts mapped (Physics, Chemistry, Biology, Math)
   - Auto-detection from questions
   - Subject-specific scene routing

---

## 🚀 PHASE 1: Context Layers & Visual Depth (Week 1-2)

### 1.1 Context Layer Component
**File**: `frontend/src/visual-engine/components/ContextLayer.jsx`

```
┌─────────────────────────────────────────────────────────┐
│ 🌍 Why This Matters                                     │
│ "Every time you throw a ball, you're applying force!"  │
├─────────────────────────────────────────────────────────┤
│ 📚 Exam POV                                             │
│ "JEE/NEET: 2-3 questions every year on F=ma"           │
├─────────────────────────────────────────────────────────┤
│                   [VISUAL SCENE]                        │
└─────────────────────────────────────────────────────────┘
```

**Tasks**:
- [ ] Create `ContextLayer.jsx` with real-life relevance
- [ ] Add exam importance indicators
- [ ] Create context data for each concept in registry
- [ ] Integrate above visual scene

### 1.2 Multi-Layer Reveal System
**File**: `frontend/src/visual-engine/components/LayeredVisual.jsx`

```
Layer 1: Basic Scene (Auto-show)
Layer 2: Formula + Calculations (Tap to reveal)
Layer 3: Deep Mechanics (Vectors, Graphs)
Layer 4: Exam Mode (Questions inside scene)
```

**Tasks**:
- [ ] Create `LayeredVisual.jsx` wrapper component
- [ ] Add layer toggle UI (tabs or swipe)
- [ ] Implement smooth layer transitions
- [ ] Add "Unlock Next Layer" gamification

### 1.3 Enhanced Animation System
**File**: Update `frontend/src/visual-engine/core/AnimationLibrary.js`

**Tasks**:
- [ ] Add speed blur effect for moving objects
- [ ] Add pulse animation for force arrows
- [ ] Add friction visual (sparks/lines)
- [ ] Add vector magnitude scaling
- [ ] Add smooth micro-transitions on slider change

---

## 🚀 PHASE 2: Professor Avatar Enhancement (Week 2-3)

### 2.1 Interactive Professor Component
**File**: `frontend/src/visual-engine/components/ProfessorAvatar.jsx`

**Current State**: Static professor in CompactPhysicsScene
**Target State**: Dynamic, reactive professor

**Tasks**:
- [ ] Extract professor into standalone component
- [ ] Add gesture states: point, explain, celebrate, think
- [ ] Add reactions to value changes ("Wow! Strong force!")
- [ ] Add speech bubbles with Hinglish tips
- [ ] Add eye tracking (follows ball/object)

### 2.2 Professor Dialogue System
**File**: `frontend/src/visual-engine/config/professorDialogues.js`

```javascript
{
  force: {
    high: "Wah! Bahut strong force! 💪",
    low: "Thoda aur force lagao beta",
    explain: "Dekho, jitna force, utna acceleration",
    mistake: "Arre! Mass badha, speed kam hogi"
  }
}
```

**Tasks**:
- [ ] Create dialogue database per concept
- [ ] Add trigger conditions (value thresholds)
- [ ] Add Hinglish/English toggle
- [ ] Add voice-over support (future)

---

## 🚀 PHASE 3: Real-World Object Library (Week 3-4)

### 3.1 Enhanced Props Library
**File**: Update `frontend/src/visual-engine/components/PropsLayer.jsx`

**Current Props**: ball, bat, auto, mango, box
**New Props Needed**:

**Physics**:
- [ ] Cricket ball with seam detail
- [ ] Bat with handle grip
- [ ] Stumps with bails
- [ ] Turf variations (pitch, grass)
- [ ] Wind direction indicator
- [ ] Arm angle visual
- [ ] Skateboard for Newton's laws
- [ ] Spring for oscillation
- [ ] Lens/prism for light
- [ ] Magnet for magnetism

**Chemistry**:
- [ ] Test tube with liquid
- [ ] Beaker with bubbles
- [ ] Bunsen burner
- [ ] Periodic table element card
- [ ] Molecule 3D structure

**Biology**:
- [ ] Leaf with stomata
- [ ] Oxygen bubble
- [ ] Blood cell (RBC/WBC)
- [ ] Neuron
- [ ] Heart with chambers

**Math**:
- [ ] Graph paper background
- [ ] Coordinate axes
- [ ] Geometric shapes (dynamic)
- [ ] Function curve (draggable)

### 3.2 Regional Props System
**File**: Update `frontend/src/visual-engine/utils/indianContext.js`

```javascript
regionalProps = {
  rajasthan: { vehicle: 'camel', landmark: 'desert_fort' },
  karnataka: { vehicle: 'bus', food: 'dosa' },
  mumbai: { vehicle: 'local_train', landmark: 'gateway' },
  tamilnadu: { vehicle: 'auto', food: 'idli' },
  punjab: { vehicle: 'tractor', food: 'lassi' }
}
```

**Tasks**:
- [ ] Add 10+ regional prop variants
- [ ] Auto-detect region from student profile
- [ ] Create cultural mapping for each concept

---

## 🚀 PHASE 4: Live Math Binding (Week 4-5)

### 4.1 Formula-Object Binding System
**File**: `frontend/src/visual-engine/core/FormulaBinding.js`

**Tasks**:
- [ ] Create bidirectional binding (slider ↔ object ↔ formula)
- [ ] Tap ball → show acceleration arrow
- [ ] Tap mass → change ball size
- [ ] Tap force → arrow thickness changes
- [ ] Add graph overlay mode

### 4.2 Real-Time Graph Component
**File**: `frontend/src/visual-engine/components/LiveGraph.jsx`

```
┌─────────────────────────────────────────┐
│  Acceleration vs Time                   │
│  ▲                                      │
│  │    ╭──────────                       │
│  │   ╱                                  │
│  │  ╱                                   │
│  │ ╱                                    │
│  └────────────────────────────▶         │
│     0    1    2    3    4    5          │
└─────────────────────────────────────────┘
```

**Tasks**:
- [ ] Create SVG-based live graph component
- [ ] Add multiple graph types (line, bar, area)
- [ ] Sync with slider values in real-time
- [ ] Add axis labels and units
- [ ] Add "Show Graph" toggle

### 4.3 Toggle Modes
**Tasks**:
- [ ] Add "Gravity Mode" toggle → add gravity vector
- [ ] Add "Friction Mode" toggle → add friction force
- [ ] Add "Air Resistance" toggle
- [ ] Add "Slow Motion" mode

---

## 🚀 PHASE 5: Cross-Concept Linking (Week 5-6)

### 5.1 Concept Navigator
**File**: `frontend/src/visual-engine/components/ConceptNavigator.jsx`

```
┌─────────────────────────────────────────┐
│ Related Concepts:                       │
│ [Force] → [Acceleration] → [Inertia]   │
│            ↓                            │
│       [Momentum]                        │
└─────────────────────────────────────────┘
```

**Tasks**:
- [ ] Create concept relationship map
- [ ] Add clickable concept chips
- [ ] Implement smooth scene transitions
- [ ] Add "Learn More" deep links

### 5.2 Concept Dependency Graph
**File**: `frontend/src/visual-engine/config/conceptGraph.js`

```javascript
{
  force: {
    prerequisites: ['mass', 'acceleration'],
    leads_to: ['momentum', 'work', 'energy'],
    related: ['friction', 'gravity']
  }
}
```

**Tasks**:
- [ ] Define prerequisite chains for all concepts
- [ ] Add "You should know" suggestions
- [ ] Add "Next: Learn about..." prompts

---

## 🚀 PHASE 6: AI-Driven TOON Generation (Week 6-8)

### 6.1 Concept Type Detector
**File**: `backend/services/visual_concept_detector.py`

**Tasks**:
- [ ] Detect concept type from question:
  - Motion/Mechanics
  - Biology Process
  - Math Topic
  - Chemistry Reaction
  - Economics Chart
  - History Timeline
  - Geometry
  - Electricity
  - Algebra
  - Trigonometry

### 6.2 Visual Template Selector
**File**: `backend/services/visual_template_selector.py`

```python
TEMPLATE_MAPPING = {
    'motion': ['lab_demo', 'real_world', 'vectors', 'sliders'],
    'biology_process': ['step_timeline', 'highlight_organs', 'flow_arrows'],
    'math': ['formula_sliders', 'graph_updates', 'derivation_layers'],
    'chemistry': ['particle_simulation', 'reaction_timeline'],
    'economics': ['supply_demand_graph', 'interactive_chart'],
    'history': ['timeline', 'event_highlight', 'map_overlay']
}
```

**Tasks**:
- [ ] Create template family definitions
- [ ] Add AI-based template selection
- [ ] Create fallback logic

### 6.3 TOON Auto-Generator
**File**: `backend/services/toon_generator.py`

**Tasks**:
- [ ] Generate TOON blocks from AI analysis
- [ ] Select appropriate objects from library
- [ ] Define animations based on concept type
- [ ] Add interaction definitions
- [ ] Include formula overlays

### 6.4 Visual Object Library API
**File**: `backend/services/visual_object_library.py`

**Tasks**:
- [ ] Create object catalog with metadata
- [ ] Add search by category/concept
- [ ] Add SVG generation for new objects
- [ ] Add animation presets per object

---

## 🚀 PHASE 7: "Try Yourself" Mode (Week 8-9)

### 7.1 Interactive Challenge System
**File**: `frontend/src/visual-engine/components/TryYourselfMode.jsx`

```
┌─────────────────────────────────────────┐
│ 🎯 Try This!                            │
│                                         │
│ "Set force = 0. What happens to the    │
│  ball? Observe and answer!"            │
│                                         │
│ [A] Ball stops immediately             │
│ [B] Ball continues moving              │
│ [C] Ball accelerates                   │
│ [D] Ball reverses                      │
│                                         │
│ [Check Answer]                          │
└─────────────────────────────────────────┘
```

**Tasks**:
- [ ] Create challenge prompt component
- [ ] Add preset challenges per concept
- [ ] Add answer validation
- [ ] Connect to gamification (XP rewards)
- [ ] Add "Explain Why" after answer

### 7.2 Observation Prompts
**Tasks**:
- [ ] "Increase mass: what happens?"
- [ ] "Set force = 0 → what do you observe?"
- [ ] "Compare high vs low acceleration"
- [ ] Add hint system

---

## 🚀 PHASE 8: Subject-Specific Scene Templates (Week 9-12)

### 8.1 New Physics Scenes
**Tasks**:
- [ ] `RefractionScene.jsx` - Lens bending + drag light beam
- [ ] `NewtonLawsScene.jsx` - Skateboard, sliding objects
- [ ] `CircuitScene.jsx` - Interactive circuit builder
- [ ] `WaveScene.jsx` - Oscillation visualization
- [ ] `MagnetismScene.jsx` - Field lines visualization

### 8.2 New Biology Scenes
**Tasks**:
- [ ] `PhotosynthesisScene.jsx` - Light → leaf → O₂ bubbles
- [ ] `RespirationScene.jsx` - Glucose → ATP animation
- [ ] `DNAReplicationScene.jsx` - Helix unwinding
- [ ] `HeartScene.jsx` - Blood flow animation
- [ ] `NeuronScene.jsx` - Signal transmission

### 8.3 New Chemistry Scenes
**Tasks**:
- [ ] `ReactionScene.jsx` - Reactants → Products animation
- [ ] `BalancingScene.jsx` - Equation balancing game
- [ ] `AcidBaseScene.jsx` - pH scale interaction
- [ ] `ElectrolysisScene.jsx` - Ion movement

### 8.4 New Math Scenes
**Tasks**:
- [ ] `IntegralScene.jsx` - Area under curve (draggable)
- [ ] `DerivativeScene.jsx` - Slope visualization
- [ ] `QuadraticScene.jsx` - Parabola with roots
- [ ] `TrigScene.jsx` - Unit circle animation
- [ ] `ProbabilityScene.jsx` - Dice/coin simulation

### 8.5 New Economics Scenes
**Tasks**:
- [ ] `SupplyDemandScene.jsx` - Interactive curves
- [ ] `BalanceSheetScene.jsx` - Assets vs Liabilities blocks
- [ ] `GDPScene.jsx` - Growth visualization

### 8.6 New History Scenes
**Tasks**:
- [ ] `TimelineScene.jsx` - Event navigation
- [ ] `MapScene.jsx` - Historical map overlay
- [ ] `ComparativeScene.jsx` - Before/After

---

## 📋 IMPLEMENTATION PRIORITY

### 🔴 HIGH PRIORITY (Phase 1-3)
1. Context Layers - Adds meaning to visuals
2. Multi-Layer Reveal - Engagement boost
3. Professor Enhancement - Emotional connection
4. Real-World Props - Visual quality

### 🟡 MEDIUM PRIORITY (Phase 4-5)
5. Live Math Binding - Interactive learning
6. Cross-Concept Linking - Knowledge graph

### 🟢 FUTURE (Phase 6-8)
7. AI TOON Generation - Automation
8. Try Yourself Mode - Active learning
9. New Subject Scenes - Content expansion

---

## 📁 FILE STRUCTURE (After All Phases)

```
frontend/src/visual-engine/
├── components/
│   ├── core/
│   │   ├── InteractiveVisualCard.jsx  ✅ EXISTS
│   │   ├── LayeredVisual.jsx          🆕 Phase 1
│   │   ├── ContextLayer.jsx           🆕 Phase 1
│   │   ├── ProfessorAvatar.jsx        🆕 Phase 2
│   │   ├── LiveGraph.jsx              🆕 Phase 4
│   │   ├── ConceptNavigator.jsx       🆕 Phase 5
│   │   └── TryYourselfMode.jsx        🆕 Phase 7
│   ├── physics/
│   │   ├── CompactPhysicsScene.jsx    ✅ EXISTS
│   │   ├── MotionVisualScene.jsx      ✅ EXISTS
│   │   ├── GravityVisualScene.jsx     ✅ EXISTS
│   │   ├── RefractionScene.jsx        🆕 Phase 8
│   │   ├── NewtonLawsScene.jsx        🆕 Phase 8
│   │   ├── CircuitScene.jsx           🆕 Phase 8
│   │   └── WaveScene.jsx              🆕 Phase 8
│   ├── biology/
│   │   ├── BiologyCellScene.jsx       ✅ EXISTS
│   │   ├── PhotosynthesisScene.jsx    🆕 Phase 8
│   │   ├── DNAReplicationScene.jsx    🆕 Phase 8
│   │   └── HeartScene.jsx             🆕 Phase 8
│   ├── chemistry/
│   │   ├── ChemistryAtomScene.jsx     ✅ EXISTS
│   │   ├── ReactionScene.jsx          🆕 Phase 8
│   │   └── AcidBaseScene.jsx          🆕 Phase 8
│   ├── math/
│   │   ├── MathPythagorasScene.jsx    ✅ EXISTS
│   │   ├── IntegralScene.jsx          🆕 Phase 8
│   │   ├── QuadraticScene.jsx         🆕 Phase 8
│   │   └── TrigScene.jsx              🆕 Phase 8
│   └── economics/
│       ├── SupplyDemandScene.jsx      🆕 Phase 8
│       └── BalanceSheetScene.jsx      🆕 Phase 8
├── core/
│   ├── TOONParser.js                  ✅ EXISTS
│   ├── AnimationTimeline.js           ✅ EXISTS
│   ├── InteractionEngine.js           ✅ EXISTS
│   ├── AnimationLibrary.js            🔄 ENHANCE Phase 1
│   └── FormulaBinding.js              🆕 Phase 4
├── config/
│   ├── conceptRegistry.js             ✅ EXISTS (expand)
│   ├── conceptGraph.js                🆕 Phase 5
│   └── professorDialogues.js          🆕 Phase 2
└── utils/
    ├── indianContext.js               ✅ EXISTS (expand)
    └── conceptToTOON.js               ✅ EXISTS

backend/services/
├── visual_concept_detector.py         🆕 Phase 6
├── visual_template_selector.py        🆕 Phase 6
├── toon_generator.py                  🆕 Phase 6
└── visual_object_library.py           🆕 Phase 6
```

---

## ⏱️ ESTIMATED TIMELINE

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|--------------|
| 1 | Context Layers & Visual Depth | 2 weeks | None |
| 2 | Professor Avatar Enhancement | 1 week | Phase 1 |
| 3 | Real-World Object Library | 1 week | None |
| 4 | Live Math Binding | 1.5 weeks | Phase 1, 3 |
| 5 | Cross-Concept Linking | 1 week | Phase 4 |
| 6 | AI-Driven TOON Generation | 2 weeks | Phase 1-5 |
| 7 | "Try Yourself" Mode | 1 week | Phase 4 |
| 8 | Subject-Specific Scenes | 3 weeks | Phase 1-7 |

**Total: ~12-14 weeks for full implementation**

---

## 🎯 SUCCESS METRICS

1. **Engagement**: Time spent on visual > 30 seconds
2. **Interaction Rate**: > 3 taps/swipes per visual
3. **Completion Rate**: > 70% students view all layers
4. **Retention**: Concept recall improved by 40%
5. **Satisfaction**: "Wow factor" rating > 4.5/5

---

## 🚦 READY TO START?

**Recommended First Task**: Phase 1.1 - Context Layer Component

This adds immediate value without touching existing code.



