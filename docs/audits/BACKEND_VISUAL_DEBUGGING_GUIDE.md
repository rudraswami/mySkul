# Backend Visual Professor Generator - Debugging Guide

## 🔍 Problem Identified

The API response shows **NO `teaching_visual` field**, which means:
1. Visual Professor Generator is either not being called
2. Or it's failing silently
3. Or it's returning empty/invalid results

## ✅ Fixes Applied

### 1. Enhanced Logging (`backend/api/ai.py`)

Added detailed logging at every step:
- ✅ Logs when Visual Professor Generator starts
- ✅ Logs import success
- ✅ Logs return value and structure
- ✅ Logs when `teaching_visual` is added to response
- ✅ Logs errors with full traceback

### 2. Fallback Mechanism

If Visual Professor Generator fails, it now:
- ✅ Attempts to call `_fallback_visual()` directly
- ✅ Ensures a visual is always generated (if possible)

---

## 🧪 How to Debug

### Step 1: Check Backend Logs

Look for these log messages in your backend console:

```
🎨 Starting Visual Professor Generator for: what is velocity...
✅ VisualProfessorGenerator imported successfully
📊 Detected: physics.velocity | Intent: concept_explanation | Type: process
✅ Template resolved: professor_physics_velocity_concept_explanation
✅ Using universal professor template with 3 stages
✅ Generated visual professor explanation: 3 stages
📊 Visual Professor Generator returned: <class 'dict'>, has stages: True
✅ Visual Professor Generator: 3 stages generated
📦 Teaching visual structure: visual_id=prof_123456, type=animated_lesson, stages=3
✅ Added teaching_visual to response: prof_123456 with 3 stages
```

### Step 2: Check for Errors

If you see errors like:

```
❌ Visual Professor Generator failed with exception: ...
❌ Traceback: ...
```

**Common Issues:**

1. **Import Error**:
   ```
   ModuleNotFoundError: No module named 'services.visual_professor'
   ```
   **Fix**: Check that `backend/services/visual_professor/__init__.py` exists and exports `VisualProfessorGenerator`

2. **Concept Detection Error**:
   ```
   AttributeError: 'NoneType' object has no attribute 'subject'
   ```
   **Fix**: Check `UnifiedConceptDetector.detect()` is returning valid `ConceptMetadata`

3. **Template Registry Error**:
   ```
   KeyError: 'stages'
   ```
   **Fix**: Check `UniversalTemplateGenerator.generate_template()` is returning valid template with `stages`

4. **VisualTeachingEngine Error**:
   ```
   TypeError: generate_teaching_visual() missing required argument
   ```
   **Fix**: Check `VisualTeachingEngine.generate_teaching_visual()` signature

### Step 3: Check `allow_visual` Flag

Look for this log:
```
⚠️ No teaching_visual generated. tv=None, allow_visual=True/False
```

If `allow_visual=False`, check:
- `_should()` function is returning `True`
- `_intent` is not `"compare_contrast"` or `"clarification_or_followup"`

### Step 4: Check Repetition Guard

The repetition guard might be blocking visuals. Look for:
- No error logs
- `tv` is set but then becomes `None` after repetition check

---

## 🔧 Quick Test

### Test 1: Direct Import Test

Run this in Python shell:
```python
from services.visual_professor import VisualProfessorGenerator
vpg = VisualProfessorGenerator()
print("✅ Import successful")
```

### Test 2: Generate Visual Test

```python
import asyncio
from services.visual_professor import VisualProfessorGenerator

async def test():
    vpg = VisualProfessorGenerator()
    result = await vpg.generate_visual(
        question="What is velocity?",
        subject="Physics",
        student_profile={"region": "Delhi"}
    )
    print(f"Result: {result}")
    print(f"Has stages: {bool(result.get('stages'))}")
    print(f"Stages count: {len(result.get('stages', []))}")

asyncio.run(test())
```

### Test 3: Check API Endpoint Directly

```bash
curl -X POST http://localhost:8001/api/ai/neuro-symbolic \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "What is velocity?",
    "subject": "Physics",
    "session_id": "test123"
  }' | jq '.response.teaching_visual'
```

---

## 📊 Expected Response Structure

When working correctly, the API response should have:

```json
{
  "response": {
    "teaching_visual": {
      "visual_id": "prof_123456",
      "type": "animated_lesson",
      "stages": [
        {
          "stage_id": "intro",
          "duration_ms": 2500,
          "narration": "Let's understand velocity step by step.",
          "lottie_assets": [...],
          "blocks": [...]
        },
        // ... more stages (minimum 3)
      ],
      "total_duration_ms": 10000,
      "metadata": {...},
      "professor_avatar": {...}
    }
  }
}
```

---

## 🚨 Common Issues & Solutions

### Issue 1: No Logs Appearing

**Symptom**: No logs at all in backend console

**Solution**:
- Check logger level is set to `INFO` or `DEBUG`
- Check logs are going to console (not just file)

### Issue 2: Import Fails

**Symptom**: `ModuleNotFoundError: No module named 'services.visual_professor'`

**Solution**:
- Check `backend/services/visual_professor/__init__.py` exists
- Check Python path includes `backend/` directory
- Try: `cd backend && python -c "from services.visual_professor import VisualProfessorGenerator"`

### Issue 3: Generator Returns Empty Stages

**Symptom**: Logs show `has stages: False` or `stages=[]`

**Solution**:
- Check `UniversalTemplateGenerator._generate_stages()` is working
- Check concept detection is returning valid metadata
- Check template registry is returning valid template

### Issue 4: Repetition Guard Blocks Visual

**Symptom**: Visual generated but then `tv` becomes `None`

**Solution**:
- Check session ID is unique for each test
- Temporarily disable repetition guard for testing:
  ```python
  # Comment out repetition guard check
  # if _LAST_TV_BY_SESSION.get(sid) == sig or sig in combined_recent:
  #     tv = None
  ```

---

## ✅ Success Criteria

Visual Professor Generator is working when:

1. ✅ Backend logs show: `✅ Visual Professor Generator: 3 stages generated`
2. ✅ Backend logs show: `✅ Added teaching_visual to response`
3. ✅ API response includes `response.teaching_visual` field
4. ✅ `teaching_visual.stages` array has minimum 3 stages
5. ✅ Frontend console shows: `✅ ANIMATED TEACHING VISUAL DETECTED`

---

## 🎯 Next Steps

1. **Restart Backend Server** to load new logging code
2. **Ask a question** (e.g., "What is velocity?")
3. **Check backend logs** for the log messages above
4. **Check API response** in Network tab for `teaching_visual` field
5. **Report findings** - share the backend logs if still not working

---

**Last Updated**: After adding enhanced logging and fallback mechanism
**Status**: ⚠️ Waiting for backend logs to diagnose issue

