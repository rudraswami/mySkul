# Frontend Visual Testing Guide

## 🔍 Problem Identified

The backend **IS generating** `teaching_visual` but the frontend **wasn't extracting or rendering it**.

## ✅ Fixes Applied

### 1. Backend Response Structure
Backend endpoint `/api/ai/neuro-symbolic` returns:
```json
{
  "response": {
    "practical_explanation": "...",
    "metaphor": "...",
    "teaching_visual": {
      "visual_id": "...",
      "type": "animated_lesson",
      "stages": [...],
      "total_duration_ms": 10000,
      ...
    }
  }
}
```

### 2. Frontend Extraction (FIXED)
**File**: `frontend/src/components/AITutorNeuroSymbolic.js`

**Before**:
```javascript
const aiMsg = {
  type: 'ai',
  content: data.response,
  // teaching_visual was NOT extracted!
};
```

**After**:
```javascript
const aiMsg = {
  type: 'ai',
  content: data.response,
  teaching_visual: data.response?.teaching_visual || null,  // ✅ EXTRACTED
  visual_data: data.response?.visual_data || null
};
```

### 3. Frontend Rendering (FIXED)
**File**: `frontend/src/components/neuro-symbolic/NeuroSymbolicResponse.js`

**Before**: Component never checked for `teaching_visual`

**After**: 
- Added `TeachingVisualPlayer` import
- Added PRIORITY 0 check for `teaching_visual`
- Renders `TeachingVisualPlayer` when `teaching_visual.stages` exists

---

## 🧪 How to Test

### Step 1: Open Browser Console
Press `F12` or `Ctrl+Shift+I` to open Developer Tools

### Step 2: Ask a Question
Try these questions:
- "What is valency?"
- "Explain permutations and combinations"
- "What is velocity?"
- "How does photosynthesis work?"

### Step 3: Check Console Logs

You should see these logs:

```
🎨 FULL API RESPONSE: {...}
🎨 Teaching Visual: {visual_id: "...", stages: [...], ...}
🎨 Visual Data: {...}
🎬 NeuroSymbolicResponse - teaching_visual: {...}
```

### Step 4: Verify Visual Rendering

**If `teaching_visual` exists**:
- ✅ You should see a purple-bordered box with "🎓 Professor-Led Visual Explanation"
- ✅ Inside: Multi-step visual player with stages
- ✅ Controls: Prev/Next, Replay, Reset buttons
- ✅ Progress bar showing stage progress
- ✅ Narration text at bottom

**If `teaching_visual` is NULL**:
- ❌ Check backend logs for errors
- ❌ Check if Visual Professor Generator is being called
- ❌ Check if concept detection is working

---

## 🐛 Debugging Checklist

### Backend Issues

1. **Check Backend Logs**:
   ```bash
   # Look for these logs:
   📊 Detected: chemistry.valency | Intent: concept_explanation
   ✅ Template resolved: professor_chemistry_valency_concept_explanation
   ✅ Generated universal template: ... with 3 stages
   ✅ Visual Professor Generator: 3 stages generated
   ```

2. **Check API Response**:
   ```bash
   # In backend, add logging:
   logger.info(f"📤 Sending response with teaching_visual: {result.get('response', {}).get('teaching_visual')}")
   ```

### Frontend Issues

1. **Check Console Logs**:
   - `🎨 FULL API RESPONSE` - Should show full response
   - `🎨 Teaching Visual` - Should show teaching_visual object
   - `🎬 NeuroSymbolicResponse - teaching_visual` - Should show same object

2. **Check Network Tab**:
   - Open Network tab in DevTools
   - Find `/api/ai/neuro-symbolic` request
   - Check Response payload
   - Verify `response.teaching_visual` exists

3. **Check Component Props**:
   - In React DevTools, find `NeuroSymbolicResponse` component
   - Check `response` prop
   - Verify `teaching_visual` is present

---

## 🔧 Common Issues & Solutions

### Issue 1: No Visual Appears

**Symptoms**: Text response but no visual player

**Check**:
1. Console shows `teaching_visual: null`
2. Backend logs show Visual Professor Generator failed
3. Network response doesn't include `teaching_visual`

**Solution**:
- Check backend logs for Visual Professor Generator errors
- Verify concept detection is working
- Check if universal template generator is working

### Issue 2: Visual Appears But Empty

**Symptoms**: Visual player box appears but no content

**Check**:
1. `teaching_visual.stages` is empty array `[]`
2. `teaching_visual.stages.length === 0`

**Solution**:
- Check backend: Visual Professor Generator should generate minimum 3 stages
- Check universal template generator is creating stages

### Issue 3: Visual Appears But Not Interactive

**Symptoms**: Visual shows but buttons don't work

**Check**:
1. `TeachingVisualPlayer` component is rendering
2. Buttons are disabled or not responding

**Solution**:
- Check `TeachingVisualPlayer` component state
- Verify stages have valid `duration_ms` values
- Check for JavaScript errors in console

---

## 📊 Expected Visual Structure

When working correctly, `teaching_visual` should have:

```javascript
{
  visual_id: "prof_123456",
  type: "animated_lesson",
  visual_type: "professor_led",
  stages: [
    {
      stage_id: "intro",
      duration_ms: 2500,
      narration: "Let's understand Valency step by step.",
      narration_style: "professor",
      lottie_assets: [
        {
          url: "https://cdn.ai-tutor.in/visuals/chemistry/valency_intro.json",
          loop: true,
          autoplay: true,
          speed: 1.0
        }
      ],
      blocks: [
        { type: "title_card", title: "Valency" }
      ],
      interactions: [],
      highlights: [],
      transitions: {},
      emphasis: null
    },
    // ... more stages (minimum 3)
  ],
  total_duration_ms: 10000,
  interaction_points: [1, 2],
  professor_avatar: {
    expression: "explaining",
    position: "bottom_right",
    animation: "explain",
    visible_stages: [0, 1, 2]
  },
  metadata: {
    concept: "Valency",
    subject: "chemistry",
    intent: ["concept_explanation"],
    concept_type: "process",
    generation_method: "universal_professor_template"
  }
}
```

---

## ✅ Success Criteria

Visual is working correctly when:

1. ✅ Console shows `teaching_visual` object with `stages` array
2. ✅ Visual player box appears with purple border
3. ✅ Stage navigation works (Prev/Next buttons)
4. ✅ Progress bar updates as stages advance
5. ✅ Narration text displays for each stage
6. ✅ Professor avatar appears (if configured)
7. ✅ Lottie animations load (if URLs are valid)

---

## 🚀 Next Steps

1. **Test with multiple questions** across different subjects
2. **Verify Lottie animations load** (check Network tab for Lottie JSON files)
3. **Test interactions** (scrub timeline, hover elements)
4. **Check mobile responsiveness**

---

**Last Updated**: After Visual Professor Engine System Rebuild
**Status**: ✅ Frontend now extracts and renders `teaching_visual`

