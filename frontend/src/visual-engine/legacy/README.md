# 📦 Legacy Code Archive

**Purpose:** Safely store old code during migration to V6

## ⚠️ DEPRECATION NOTICE

All files in this folder are **deprecated** and will be removed in a future release.

They are kept here temporarily for:
1. **Reference** - Understanding old logic
2. **Fallback** - Emergency rollback if V6 has issues
3. **Migration** - Gradual transition without breaking existing features

**DO NOT** use these components in new code.
**DO NOT** enhance or fix bugs in these files.
**DO** migrate to the new V6 system.

---

## What's Here

### `components/`
- `ConfigDrivenSketch.jsx` - Old V5.1 universal renderer (1723 lines, monolithic)
- `RevolutionarySketch.jsx` - V4 renderer

**Replaced by:** `core/UniversalSketchRenderer.jsx`

---

### `templates/`
- `RaceTemplate.jsx` - Box-based race comparison
- `ProcessTemplate.jsx` - Box-based process flow
- `CycleTemplate.jsx` - Box-based cycle
- `GraphTemplate.jsx` - Box-based graph
- `StructureTemplate.jsx` - Box-based structure
- `CauseEffectTemplate.jsx` - Box-based cause-effect
- `ScaleTemplate.jsx` - Box-based scale
- `TimelineTemplate.jsx` - Box-based timeline

**Replaced by:** `modes/` system (hand-drawn, not boxes)

---

### `UniversalSketchCanvas_OLD.jsx`
Old V5 mode router (just a wrapper).

**Replaced by:** `core/MagicNotebookEngine.jsx`

---

### `UniversalSketchCanvasV6_OLD.jsx`
Old V6 attempt with HTML sliders.

**Replaced by:** `core/UniversalSketchRenderer.jsx` + `controls/SketchSlider.jsx`

---

### `InteractiveControls_OLD.js`
HTML `<input type="range">` sliders.

**Replaced by:** `controls/SketchSlider.jsx` (RoughJS, no HTML)

---

## Migration Timeline

- **Phase 1-4:** Build new system in parallel (old code untouched)
- **Phase 5-8:** Gradual feature flag rollout
- **Phase 9:** Update all imports to new system
- **Phase 10:** Remove legacy exports from `visual-engine/index.js`
- **Future:** Delete this entire folder

---

## If You Need to Rollback

1. Check git history for original file locations
2. Move files back from `legacy/` to original locations
3. Update imports
4. Disable V6 feature flag

---

**Last Updated:** Phase 1A
**Status:** Empty (files will be moved here gradually)

