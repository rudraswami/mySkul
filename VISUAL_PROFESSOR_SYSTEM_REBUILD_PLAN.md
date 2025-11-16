# Visual Professor Engine - System Rebuild Plan

## 🔍 BLOCKERS IDENTIFIED

### Blocker 1: Frontend Not Using `teaching_visual`
**File**: `frontend/src/components/mentor-v2/MentorResponseV2.js`
- Line 224: Checks for `animatedTeachingVisual` but only renders if exists
- Line 238: Falls back to static SVG if `animatedTeachingVisual` is null
- **Problem**: Even when backend sends `teaching_visual`, frontend may not render it

### Blocker 2: Legacy Visual Paths Still Active
**Files**: 
- `backend/api/ai.py` lines 1044-1081: Uses `_dyn`, `_tpl`, `_plan` as fallbacks
- `backend/services/ai_service.py` lines 1704-1760: Uses `unified_visual_system` as fallback
- **Problem**: These return static SVGs or old formats, bypassing Visual Professor Engine

### Blocker 3: Template Registry Requires Manual Entries
**File**: `backend/services/visual_professor/template_registry.py`
- Only reads from `templates.json` (4 concepts)
- No auto-generation for unmapped concepts
- **Problem**: 90% of concepts fall back to static visuals

### Blocker 4: VisualProfessorGenerator Doesn't Always Generate Multi-Step
**File**: `backend/services/visual_professor/generator.py`
- Falls back to `_fallback_visual` which is single-stage
- Doesn't enforce multi-step requirement
- **Problem**: Can return single-stage or static visuals

### Blocker 5: Frontend TeachingVisualPlayer Missing Features
**File**: `frontend/src/components/TeachingVisualPlayer.js`
- No Lottie animation support
- No professor avatar overlay
- No scrubbing timeline
- Limited interaction support
- **Problem**: Can't render true professor-led Lottie lessons

---

## 🔧 FIXES TO APPLY

### Fix 1: Universal Template Schema
Create schema that auto-generates templates for ANY concept

### Fix 2: Rebuild Template Registry
Auto-generate templates based on concept metadata, not manual entries

### Fix 3: Update VisualProfessorGenerator
ALWAYS generate multi-step professor-led visuals with Lottie

### Fix 4: Remove Legacy Paths
Disable unified_visual_system, _dyn, _tpl, _plan as visual sources

### Fix 5: Update Frontend
ALWAYS use TeachingVisualPlayer when teaching_visual exists

### Fix 6: Add Lottie & Avatar Support
Enhance TeachingVisualPlayer with full professor-led features

