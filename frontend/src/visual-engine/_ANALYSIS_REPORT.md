# 🔍 VISUAL ENGINE AUDIT & DECISION MATRIX

**Date:** $(date)
**Purpose:** Pre-Phase 1 analysis for Magic Notebook Engine V6
**Auditor:** Cursor AI

---

## 📊 EXECUTIVE SUMMARY

**Total Files Scanned:** 42 files
**Decision Breakdown:**
- ✅ **Keep & Enhance:** 8 files (19%)
- 🔄 **Replace Completely:** 18 files (43%)
- 📦 **Archive (Legacy):** 16 files (38%)

---

## ✅ KEEP & ENHANCE (Good Foundation)

### 1. **`visual-engine/sketch/SketchPrimitives.jsx`** ✅ KEEP
**Status:** Well-structured, RoughJS-powered, excellent foundation

**What's Good:**
- Already uses RoughJS for hand-drawn aesthetics
- Framer Motion pathLength animations working
- Clean component architecture
- `SketchCircle`, `SketchRect`, `SketchArrow`, `SketchLabel`, `SketchHighlight`, `SketchStickFigure`, `SketchDoodle`, `SketchLine`
- Animation variants: `drawVariants`, `fadeInVariants`, `popVariants`
- `NOTEBOOK_THEME` constants defined

**What Needs Enhancement:**
- Add `SketchPath` for custom curves
- Add pulse/glow animations
- Add typewriter text effect for labels
- Optimize RoughJS path generation (memoization)
- Add more doodle types

**Action:** ✅ **ENHANCE IN PLACE**

---

### 2. **`visual-engine/sketch/RevealSequenceEngine.js`** ✅ KEEP
**Status:** Solid timing foundation, needs narrative integration

**What's Good:**
- Clean `RevealSequenceEngine` class
- Timing constants (SHAPES, CONNECTIONS, LABELS, DOODLES)
- Stagger system
- Sequence builder pattern
- Preset sequences

**What Needs Enhancement:**
- Add 5-beat narrative structure
- Hand movement coordination
- Text bubble timing
- Pause/emphasis system
- Beat transitions

**Action:** ✅ **ENHANCE IN PLACE**

---

### 3. **`visual-engine/validators/ValidatorEngine.js`** ✅ KEEP
**Status:** Good plugin architecture, expand rules

**What's Good:**
- Clean validator plugin system
- Subject detection
- Feedback structure

**What Needs Enhancement:**
- Expand PhysicsValidator rules
- Add ChemistryValidator
- Add BiologyValidator
- Add MathValidator
- Visual feedback triggers (shake, glow, scribble)

**Action:** ✅ **ENHANCE IN PLACE**

---

### 4. **`visual-engine/feedback/FeedbackController.js`** ✅ KEEP
**Status:** Good feedback system, needs Ghost Mentor integration

**What Needs Enhancement:**
- Integrate with narrative beats
- Add visual feedback animations
- Sticky note positioning

**Action:** ✅ **ENHANCE IN PLACE**

---

### 5. **`visual-engine/primitives/` folder** ✅ KEEP (Selective)
**Status:** Some primitives are useful building blocks

**Keep These:**
- `Arrow.jsx` - Useful for force vectors
- `Label.jsx` - Text labeling
- `AnimatedPath.jsx` - Path animations
- `HandText.jsx` - Handwriting effect

**Archive These (Legacy):**
- `Vehicle.jsx`, `Ball.jsx`, `Track.jsx` - Too specific, use sketch primitives
- `Atom.jsx`, `Cell.jsx`, `Wave.jsx` - Should be composed from sketch primitives
- `Formula.jsx`, `Counter.jsx` - Replace with sketch versions

**Action:** ✅ **KEEP CORE, ARCHIVE REST**

---

### 6. **`visual-engine/logic/PhysicsValidator.js`** ✅ KEEP
**Status:** Good physics rules, expand constraints

**Action:** ✅ **ENHANCE IN PLACE**

---

### 7. **`components/visuals/SmartBoard.jsx`** ✅ KEEP
**Status:** Main integration point, already calls V6

**What's Good:**
- Already imports `UniversalSketchCanvasV6`
- Sketch theme constants
- Notebook paper background
- Good empty state

**What Needs:**
- Wire to new MagicNotebookEngine when ready
- Feature flag for gradual rollout

**Action:** ✅ **KEEP, WIRE NEW ENGINE**

---

### 8. **`visual-engine/sketch/index.js`** ✅ KEEP
**Status:** Export file

**Action:** ✅ **UPDATE EXPORTS**

---

## 🔄 REPLACE COMPLETELY (Create New Clean Version)

### 1. **`visual-engine/sketch/UniversalSketchCanvasV6.jsx`** 🔄 REPLACE
**Why Replace:**
- Uses HTML `<input type="range">` sliders (lines 170-184) ❌
- Not a true renderer (mixes rendering + controls + state)
- No hand drawing system
- No narrative engine integration
- No 5-beat structure
- Hardcoded blueprint generation (not from ConceptBreaker)
- No mode routing

**Current HTML Slider:**
```jsx
<input
  type="range"
  min={min}
  max={max}
  value={value}
  onChange={(e) => onChange(Number(e.target.value))}
  style={{ ... }}
/>
```

**Action:** 🔄 **CREATE NEW `core/UniversalSketchRenderer.jsx`**
**Archive:** Move to `legacy/UniversalSketchCanvasV6_OLD.jsx`

---

### 2. **`visual-engine/UniversalSketchCanvas.jsx`** 🔄 REPLACE
**Why Replace:**
- Just a wrapper/router, no real rendering
- Imports old V6 component
- Mode detection is basic
- No generative pipeline

**Action:** 🔄 **CREATE NEW `core/MagicNotebookEngine.jsx`**
**Archive:** Move to `legacy/UniversalSketchCanvas_OLD.jsx`

---

### 3. **`components/visuals/InteractiveControls.js`** 🔄 REPLACE
**Why Replace:**
- Uses HTML `<input type="range">` (lines 144-156) ❌
- Corporate styled sliders
- Not sketchy aesthetic

**Action:** 🔄 **CREATE NEW `controls/SketchSlider.jsx`**
**Archive:** Move to `legacy/InteractiveControls_OLD.js`

---

### 4. **`components/visuals/templates/SplitComparisonTemplate.jsx`** 🔄 REPLACE
**Why Replace:**
- HTML slider (line 156) ❌
- Should use mode system, not separate template

**Action:** 🔄 **INTEGRATE INTO `modes/ComparisonMode.js`**
**Archive:** Move to `legacy/templates/`

---

### 5. **`components/visuals/templates/ForceComparisonTemplate.jsx`** 🔄 REPLACE
**Why Replace:**
- HTML controls
- Should use mode system

**Action:** 🔄 **INTEGRATE INTO `modes/SceneMode.js`**
**Archive:** Move to `legacy/templates/`

---

## 📦 ARCHIVE (Legacy, No Longer Needed)

### Templates Folder (Complete Archive)
All files in `visual-engine/templates/` should be archived:

1. ❌ `RaceTemplate.jsx` - Box-based, not sketchy
2. ❌ `ProcessTemplate.jsx` - Replace with `ProcessMode.js`
3. ❌ `CycleTemplate.jsx` - Replace with `CycleMode.js`
4. ❌ `GraphTemplate.jsx` - Replace with `GraphMode.js`
5. ❌ `StructureTemplate.jsx` - Replace with `StructureMode.js`
6. ❌ `CauseEffectTemplate.jsx` - Integrate into modes
7. ❌ `ScaleTemplate.jsx` - Replace with `ComparisonMode.js`
8. ❌ `TimelineTemplate.jsx` - Replace with `TimelineMode.js`

**Reason:** These are old box-based templates, not hand-drawn. Replace with mode system.

**Action:** Move all to `visual-engine/legacy/templates/`

---

### Components Folder (Archive)

1. ❌ `visual-engine/components/ConfigDrivenSketch.jsx`
   - **Lines:** 1723 lines
   - **Issues:** Monolithic, uses old templates, complex, hard to maintain
   - **Action:** Archive to `legacy/components/`

2. ❌ `visual-engine/components/RevolutionarySketch.jsx`
   - **Issues:** Old system, superseded by V6
   - **Action:** Archive to `legacy/components/`

---

### Visual Components (Archive)

1. ❌ `components/visuals/AnimatedScene.js`
2. ❌ `components/visuals/SceneRenderer.js`
3. ❌ `components/visuals/SVGSceneRenderer.js`
4. ❌ `components/visuals/SimpleAnimationEngine.js`
5. ❌ `components/visuals/RobustAnimationEngine.js`

**Reason:** Old animation systems, superseded by Framer Motion + RevealSequenceEngine

**Action:** Move to `components/visuals/legacy/`

---

### Sketch Utilities (Archive)

1. ❌ `components/visual/VisualSketchViewer.js` - Old SVG viewer
2. ❌ `components/SketchAnimator.js` - Old animator
3. ❌ `hooks/useSketchSense.js` - Old hook, not needed

**Action:** Move to `legacy/hooks/`

---

## 🏗️ NEW FOLDER STRUCTURE

```
frontend/src/visual-engine/
│
├── core/                              # ✨ NEW - Core rendering
│   ├── UniversalSketchRenderer.jsx   # NEW (replaces UniversalSketchCanvasV6)
│   ├── MagicNotebookEngine.jsx       # NEW (main entry point)
│   ├── EngineContext.jsx             # NEW (React Context)
│   ├── BlueprintSchema.js            # NEW (validation)
│   └── types.js                      # NEW (JSDoc types)
│
├── intelligence/                      # ✨ NEW - The "brain"
│   ├── ConceptBreaker.js             # NEW (LLM-powered)
│   ├── SceneComposer.js              # NEW (layout algorithms)
│   ├── MetaphorMapper.js             # NEW (cultural context)
│   ├── ModeDetector.js               # NEW
│   └── prompts/                      # NEW
│       └── general-prompt.txt
│
├── primitives/                        # ✅ ENHANCED
│   ├── SketchCircle.jsx              # Keep from SketchPrimitives
│   ├── SketchRect.jsx                # Keep
│   ├── SketchArrow.jsx               # Keep
│   ├── SketchLabel.jsx               # Keep (add typewriter)
│   ├── SketchHighlight.jsx           # Keep (add pulse)
│   ├── SketchStickFigure.jsx         # Keep
│   ├── SketchDoodle.jsx              # Keep (add types)
│   ├── SketchLine.jsx                # Keep
│   ├── SketchPath.jsx                # ✨ NEW
│   ├── SketchFilters.jsx             # Keep
│   └── index.js                      # Update
│
├── controls/                          # ✨ NEW - Sketchy controls
│   ├── SketchSlider.jsx              # NEW (RoughJS, no HTML)
│   ├── SketchToggle.jsx              # NEW
│   ├── SketchButton.jsx              # NEW
│   ├── SketchKnob.jsx                # NEW
│   └── index.js                      # NEW
│
├── narrative/                         # ✨ NEW - 5-beat system
│   ├── NarrativeEngine.js            # NEW
│   ├── DrawingHand.jsx               # NEW
│   ├── TextBubble.jsx                # NEW
│   ├── RevealSequencer.js            # Enhanced from existing
│   ├── HandMotionPath.js             # NEW
│   └── assets/                       # NEW
│       └── hand-drawing.svg
│
├── validators/                        # ✅ ENHANCED
│   ├── ValidatorEngine.js            # Keep & enhance
│   ├── PhysicsValidator.js           # Keep & expand
│   ├── ChemistryValidator.js         # ✨ NEW
│   ├── BiologyValidator.js           # ✨ NEW
│   ├── MathValidator.js              # ✨ NEW
│   └── index.js                      # Update
│
├── metaphors/                         # ✨ NEW - Indian context
│   ├── MetaphorDatabase.js           # NEW
│   ├── AssetLibrary.js               # NEW
│   ├── SubstitutionRules.js          # NEW
│   └── assets/                       # NEW
│       ├── cricket-ball.svg
│       └── auto-rickshaw.svg
│
├── modes/                             # ✨ NEW - 8 master modes
│   ├── ModeRegistry.js               # NEW
│   ├── SceneMode.js                  # NEW
│   ├── ComparisonMode.js             # NEW
│   ├── ProcessMode.js                # NEW
│   ├── CycleMode.js                  # NEW
│   ├── StructureMode.js              # NEW
│   ├── GraphMode.js                  # NEW
│   ├── TimelineMode.js               # NEW
│   ├── HierarchyMode.js              # NEW
│   └── index.js                      # NEW
│
├── layouts/                           # ✨ NEW - Positioning
│   ├── ForceDirectedLayout.js        # NEW
│   ├── GridLayout.js                 # NEW
│   ├── CircularLayout.js             # NEW
│   ├── TreeLayout.js                 # NEW
│   ├── FlowLayout.js                 # NEW
│   └── index.js                      # NEW
│
├── legacy/                            # 📦 ARCHIVE
│   ├── _DEPRECATION_NOTICE.md        # NEW
│   ├── components/                   # Archived old components
│   │   ├── ConfigDrivenSketch.jsx
│   │   └── RevolutionarySketch.jsx
│   ├── templates/                    # Archived old templates
│   │   ├── RaceTemplate.jsx
│   │   ├── ProcessTemplate.jsx
│   │   └── ...
│   ├── UniversalSketchCanvas_OLD.jsx
│   └── UniversalSketchCanvasV6_OLD.jsx
│
├── feedback/                          # ✅ KEEP
│   ├── FeedbackController.js         # Keep & enhance
│   └── index.js                      # Keep
│
├── sketch/                            # ⚠️ RESTRUCTURE
│   ├── SketchPrimitives.jsx          # MOVE to primitives/
│   ├── RevealSequenceEngine.js       # MOVE to narrative/
│   └── index.js                      # Update
│
└── index.js                           # ✅ UPDATE (main export)
```

---

## 🚨 HTML SLIDER LOCATIONS (Must Replace)

### File 1: `visual-engine/sketch/UniversalSketchCanvasV6.jsx`
- **Line 170-184:** HTML `<input type="range">`
- **Used in:** Force/Mass sliders
- **Replacement:** New `controls/SketchSlider.jsx` with RoughJS

### File 2: `components/visuals/InteractiveControls.js`
- **Line 144-183:** HTML `<input type="range">` with custom CSS
- **Used in:** All visual controls
- **Replacement:** New `controls/SketchSlider.jsx`

### File 3: `components/visuals/templates/SplitComparisonTemplate.jsx`
- **Line 156-163:** HTML `<input type="range">`
- **Used in:** Comparison sliders
- **Replacement:** Archive template, use `modes/ComparisonMode.js`

### File 4: `components/visuals/templates/ForceComparisonTemplate.jsx`
- **Multiple locations:** HTML sliders
- **Replacement:** Archive, use modes system

---

## 📋 MIGRATION CHECKLIST

### Phase 1: Cleanup & Archive
- [ ] Create `visual-engine/legacy/` folder
- [ ] Create `_DEPRECATION_NOTICE.md`
- [ ] Move `templates/` → `legacy/templates/`
- [ ] Move `components/ConfigDrivenSketch.jsx` → `legacy/components/`
- [ ] Move `components/RevolutionarySketch.jsx` → `legacy/components/`
- [ ] Move `UniversalSketchCanvas.jsx` → `legacy/`
- [ ] Move `UniversalSketchCanvasV6.jsx` → `legacy/`
- [ ] Archive old animation engines
- [ ] Update imports to point to legacy (temporarily)

### Phase 2: Create New Structure
- [ ] Create `core/` folder
- [ ] Create `intelligence/` folder
- [ ] Create `controls/` folder
- [ ] Create `narrative/` folder
- [ ] Create `metaphors/` folder
- [ ] Create `modes/` folder
- [ ] Create `layouts/` folder

### Phase 3: Enhance Existing
- [ ] Enhance `SketchPrimitives.jsx`
- [ ] Enhance `RevealSequenceEngine.js`
- [ ] Enhance `ValidatorEngine.js`
- [ ] Enhance `PhysicsValidator.js`

### Phase 4: Build New (Per Phase Plan)
- [ ] Build `UniversalSketchRenderer.jsx`
- [ ] Build `SketchSlider.jsx` (RoughJS, no HTML)
- [ ] Build `DrawingHand.jsx`
- [ ] Build `NarrativeEngine.js`
- [ ] ... (continue per 10-phase plan)

---

## 🎯 DECISION CRITERIA SUMMARY

### ✅ KEEP & ENHANCE IF:
- Clean, modular code
- Uses RoughJS/Framer Motion
- Follows Magic Notebook aesthetic
- Good architecture
- Reusable

### 🔄 REPLACE IF:
- Uses HTML controls (sliders, buttons)
- Monolithic/hard to maintain
- Box-based/corporate UI
- Not sketchy aesthetic
- Doesn't fit new architecture

### 📦 ARCHIVE IF:
- Old template system
- Superseded by new system
- Not aligned with PRD
- No current usage (dead code)

---

## ✅ NEXT STEPS

1. **Create legacy folder structure**
2. **Move files to archive**
3. **Create new folder structure**
4. **Update all imports**
5. **Start Phase 1: Build UniversalSketchRenderer**

---

**Status:** ✅ Analysis Complete
**Ready for Phase 1:** YES
**Zero Conflicts:** Ensured via legacy folder

