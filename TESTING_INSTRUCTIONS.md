# Visual Professor Engine - Testing Instructions

## 🎯 Your Mission

**Confirm that the Visual Professor Engine is working end-to-end:**
- Backend generates proper visual data ✅
- Frontend renders animated entities ✅
- Framer Motion animates smoothly ✅
- Professor narration syncs ✅

---

## 📋 PRE-REQUISITES

Ensure you have:
- Backend running on `http://localhost:8001`
- Frontend running on `http://localhost:3000`
- Browser DevTools console accessible (F12)

---

## 🧪 TEST 1: Backend Integration Test (Python)

### Run this in terminal to verify backend is generating visuals correctly:

```bash
cd backend
python test_integration.py
```

### Expected Output:
```
=================================================
TESTING: Visual Professor Pipeline for 'velocity'
=================================================

[1] Sending question to backend...
[2] Checking teaching_visual in response...
✅ Teaching visual found
   Concept: velocity
   Subject: physics
   Stages: 5

[3] Validating stage structure...
   Stage 1 has 4 blocks
   Block types: ['title_card', 'narration_box', 'animated_scene', 'key_insight']

[4] Finding animated_scene block...
✅ Found animated_scene block

[5] Validating scene structure...
   Entities: 4
     - metro_train (type: vehicle)
       Position: (150, 200)
     - track (type: rail)
       Position: (50, 240)
     - direction_arrow (type: indicator)
       Position: (280, 200)
     - speedometer (type: gauge)
       Position: (410, 200)

   Actions: 8
     - move on metro_train
       To: (400, 250)
     - rotate on direction_arrow
       To: (180, 0)
     ...

[6] Verifying entity count...
✅ Good entity count: 4

[7] Verifying action count...
✅ Good action count: 8

[8] Checking narration...
✅ Narration found: Velocity needs two things: speed AND direction...

=================================================
✅ ALL CHECKS PASSED - Visual Pipeline Working!
=================================================
```

If this passes, your **BACKEND IS CORRECT** ✅

---

## 🎨 TEST 2: Frontend Visual Rendering (Browser)

### Step 1: Open Browser
Go to: `http://localhost:3000`

### Step 2: Ask Question
In the AI Tutor chat, type:
```
What is velocity?
```

### Step 3: Watch for Visual
You should see a box with:
- **Blue sky background** at top
- **Green ground** at bottom
- **Red metro train** in the middle
- **Yellow arrow** above the train
- **Purple speedometer** on the right

### Step 4: Watch the Animation
After ~1 second, the train should:
1. **Move right** (smooth Framer Motion) 
2. **Arrow rotates** 180 degrees
3. **Speedometer pulses** (if visible)
4. Complete in ~2.5 seconds

---

## 🔍 TEST 3: Console Debugging (Browser DevTools)

### Step 1: Open Console
Press `F12` and go to **Console** tab

### Step 2: Check Logs
When visual loads, you should see:
```
[SceneRenderer] Rendering scene: {background: {...}, entities: [...], actions: [...]}
[SceneRenderer] Entity metro_train: {
  type: "vehicle",
  initialPos: {x: 150, y: 200},
  animations: [{action: 'move', to: {x: 400, y: 250}}]
}
[SceneRenderer] Entity direction_arrow: {
  type: "indicator",
  initialPos: {x: 280, y: 200},
  animations: [{action: 'rotate', to: {rotation: 180}}]
}
[TeachingVisualPlayer] Using SceneRenderer
```

### Step 3: Verify No Errors
Should see **0 errors**, only informational logs

---

## 🎬 TEST 4: Visual Progression Test

### Ask 3 Different Questions

#### Question 1:
```
What is velocity?
```
Expected visual: **Metro train moving horizontally**

#### Question 2:
```
Explain projectile motion
```
Expected visual: **Cricket ball in parabolic arc** (if implemented)

#### Question 3:
```
What is valency?
```
Expected visual: **Atoms with electron shells** (if implemented)

---

## 📊 TEST 5: Performance Metrics

Open **Network tab** in DevTools:

| Metric | Target | Check |
|--------|--------|-------|
| API Response | <100ms | ✅ Should be 50-80ms |
| Visual Load | <50ms | ✅ Should be <20ms |
| FPS During Animation | 60fps | ✅ No jank/stuttering |
| Memory | <50MB | ✅ Check Task Manager |

---

## ✅ SUCCESS CRITERIA

When you complete all 5 tests, you should have:

### ✅ Backend Test
- Python script runs without errors
- Shows 4+ entities
- Shows 8+ actions
- Outputs "ALL CHECKS PASSED"

### ✅ Frontend Visual
- See colored background (sky + ground)
- See metro train (red SVG)
- See arrow (yellow SVG)
- See smooth animation (2.5 seconds)

### ✅ Console Logs
- 0 JavaScript errors
- See SceneRenderer debug logs
- See entity animations logged

### ✅ Multi-Concept
- Different visuals for different concepts
- No repeated/generic visuals

### ✅ Performance
- Response time <100ms
- Smooth 60fps animation
- No lag or stuttering

---

## 🐛 TROUBLESHOOTING

### Issue: "Only colored rectangles appear, no entities"

**Debug:**
1. Check console: Look for `Unknown entity type` warnings
2. Verify: Entity ID should match ENTITY_MAP in SceneRenderer.js
3. Fix: Add missing component or update mapping

**Expected:**
```
// GOOD
[SceneRenderer] Entity metro_train: MetroTrain component loaded
[SceneRenderer] Entity direction_arrow: DirectionArrow component loaded

// BAD
[SceneRenderer] Unknown entity type: metro_train
```

---

### Issue: "Animation not smooth / entities don't move"

**Debug:**
1. Check console: Look for `animations: []` - if empty, actions aren't mapped
2. Verify: Action.entity must match entity.id exactly
3. Fix: Check backend is generating matching entity IDs

**Expected:**
```
// GOOD
animations: [{action: 'move', to: {x: 400, y: 250}, duration_ms: 2500}]

// BAD
animations: []
```

---

### Issue: "No visual appears at all"

**Debug:**
1. Check API response: Open DevTools Network tab, find `/api/ai/neuro-symbolic` request
2. Look for `response.teaching_visual` - if null, backend didn't generate it
3. Check backend logs for errors

**Fix:**
```bash
# Backend logs should show:
🎨 Using metaphor entities: ['metro_train', 'track', 'direction_arrow']
🎬 Scene generated: delhi_metro_road, 4 entities, 8 actions
```

---

### Issue: "Professor text not syncing"

**Debug:**
1. Check narration timing
2. Verify stage index matches action timeline

**Fix:**
- Not critical for MVP
- Can sync later

---

## 🎯 FINAL VALIDATION

Once all tests pass:

### ✅ Checklist
- [ ] Backend test passes (Python script)
- [ ] Frontend shows animated entities
- [ ] Console shows no errors
- [ ] Animation is smooth (60fps)
- [ ] Different concepts show different visuals
- [ ] Response time <100ms

### 🎉 You're Done!

Your Visual Professor Engine is **WORKING**.

---

## 📞 If Tests Fail

### Immediate Actions:
1. Check backend logs: `uvicorn main:app --port 8001`
2. Check frontend logs: Browser Console (F12)
3. Run Python test: `python backend/test_integration.py`
4. Compare with this guide

### Get Logs:
```bash
# Backend logs
tail -f backend.log

# Frontend console (F12) → Console tab
# Check for:
#  - [SceneRenderer] logs
#  - [TeachingVisualPlayer] logs
#  - Error messages
```

---

## 🚀 NEXT STEPS (After Validation)

Once working:
1. Add more entity components (Atom, Mirror, Leaf, etc.)
2. Implement interactive sliders
3. Add Lottie professor avatar
4. Expand to 10+ concepts
5. Deploy to production

---

**Good luck! Your Visual Professor Engine is now ready to teach.** 🎓
