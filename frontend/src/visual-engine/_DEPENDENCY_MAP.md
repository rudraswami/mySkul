# 📊 DEPENDENCY MAP - PHASE 1 VALIDATION

## 🔍 FILES CURRENTLY IN USE

### **CRITICAL: UniversalSketchCanvasV6.jsx**
**Used by 4 files:**
1. `components/visuals/SmartBoard.jsx` - Main integration point
2. `components/visual/VisualSketchViewer.js` - Legacy viewer
3. `components/SmartResponse.jsx` - Response renderer
4. `visual-engine/index.js` - Main export (default UniversalSketchCanvas)

**Status:** ❌ **CANNOT MOVE YET** - Must build replacement first

**Strategy:**
- Create new `core/UniversalSketchRenderer.jsx`
- Keep old file working
- Update imports after new system is ready
- Use feature flag for gradual migration

---

### **ConfigDrivenSketch.jsx**
**Used by 2 files:**
1. `components/visuals/SmartBoard.jsx` - Fallback renderer
2. `visual-engine/index.js` - Exported as default

**Status:** ⚠️ **KEEP AS FALLBACK** - Used as safety net

**Strategy:**
- Keep in place as emergency fallback
- Mark as legacy in comments
- Eventually remove after V6 is stable

---

### **InteractiveControls.js**
**Used by 2 files:**
1. `components/visuals/InteractiveControls.js` - Self
2. `components/TeachingVisualPlayer.js` - Uses it

**Status:** ⚠️ **IN USE** - Cannot move immediately

**Strategy:**
- Build new `controls/SketchSlider.jsx`
- Update TeachingVisualPlayer to use new controls
- Then archive old InteractiveControls

---

### **Templates (RaceTemplate, ProcessTemplate, etc.)**
**Used by 2 locations:**
1. `visual-engine/components/ConfigDrivenSketch.jsx` - Imports all templates
2. `visual-engine/index.js` - Exports them
3. `visual-engine/templates/index.js` - Exports them

**Status:** ⚠️ **EXPORTED** - Part of public API

**Strategy:**
- Keep templates folder temporarily
- Build mode system in parallel
- Deprecate templates when modes are ready
- Remove from exports gradually

---

## ✅ SAFE TO CREATE NEW FOLDERS

These folders don't exist yet, so we can create them safely:

1. ✅ `visual-engine/core/` - NEW
2. ✅ `visual-engine/intelligence/` - NEW
3. ✅ `visual-engine/controls/` - NEW
4. ✅ `visual-engine/narrative/` - NEW
5. ✅ `visual-engine/metaphors/` - NEW
6. ✅ `visual-engine/modes/` - NEW
7. ✅ `visual-engine/layouts/` - NEW
8. ✅ `visual-engine/legacy/` - NEW (for future moves)

---

## ✅ SAFE TO ENHANCE IN PLACE

These files can be modified directly:

1. ✅ `visual-engine/sketch/SketchPrimitives.jsx` - Add features
2. ✅ `visual-engine/sketch/RevealSequenceEngine.js` - Add narrative support
3. ✅ `visual-engine/validators/ValidatorEngine.js` - Expand validators
4. ✅ `visual-engine/logic/PhysicsValidator.js` - Add rules
5. ✅ `visual-engine/feedback/FeedbackController.js` - Enhance feedback

---

## 🚦 MIGRATION STRATEGY

### **Phase 1A: Setup (Safe)**
1. ✅ Create all new folders
2. ✅ Add README.md to each new folder
3. ✅ Create placeholder files
4. ✅ No moves, no breaks

### **Phase 1B: Build in Parallel (Safe)**
1. ✅ Build new `core/UniversalSketchRenderer.jsx`
2. ✅ Build new `controls/SketchSlider.jsx`
3. ✅ Enhance existing primitives
4. ✅ Old system keeps working

### **Phase 1C: Gradual Migration (Careful)**
1. ⚠️ Add feature flag to SmartBoard
2. ⚠️ Test new renderer alongside old
3. ⚠️ Update imports one by one
4. ⚠️ Move old files to legacy/ after confirming new works

---

## 🎯 IMMEDIATE ACTIONS (Phase 1A)

### ✅ Create Folder Structure
```
visual-engine/
├── core/              # NEW - Create empty
├── intelligence/      # NEW - Create empty
├── controls/          # NEW - Create empty
├── narrative/         # NEW - Create empty
├── validators/        # EXISTS - Keep & enhance
├── metaphors/         # NEW - Create empty
├── modes/             # NEW - Create empty
├── layouts/           # NEW - Create empty
├── legacy/            # NEW - Create for future
├── feedback/          # EXISTS - Keep
├── primitives/        # EXISTS - Keep & enhance
├── sketch/            # EXISTS - Keep & enhance
├── templates/         # EXISTS - Keep for now (deprecate later)
├── components/        # EXISTS - Keep for now (move to legacy later)
└── logic/             # EXISTS - Keep
```

### ✅ What NOT to Do Yet
- ❌ Don't move UniversalSketchCanvasV6.jsx
- ❌ Don't move ConfigDrivenSketch.jsx
- ❌ Don't move InteractiveControls.js
- ❌ Don't move templates/
- ❌ Don't update visual-engine/index.js exports yet

### ✅ What TO Do Now
- ✅ Create new empty folders
- ✅ Add README files to new folders
- ✅ Create DEPRECATION_NOTICE.md in legacy/
- ✅ Start building new components in parallel

---

## 📋 NEXT STEPS CONFIRMED

1. **Create folder structure** (no risk)
2. **Add documentation** (no risk)
3. **Build new UniversalSketchRenderer** (parallel, no risk)
4. **Enhance SketchPrimitives** (safe modifications)
5. **Build SketchSlider** (new file, no risk)
6. **Test new system** (feature flag, safe)
7. **Migrate gradually** (one file at a time, reversible)

---

**Status:** ✅ Ready to create folder structure
**Risk Level:** 🟢 LOW (no moves yet, just setup)

