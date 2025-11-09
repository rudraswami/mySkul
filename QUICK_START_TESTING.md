# Quick Start Testing Guide - Visual Teaching Engine

## 🚀 Get Started in 5 Minutes

### Prerequisites
- ✅ Python 3.8+ installed
- ✅ Node.js 14+ installed
- ✅ MongoDB running
- ✅ Backend and frontend set up

---

## Step 1: Verify Files Exist

```bash
# Check backend files
ls backend/services/visual_teaching_engine.py
ls backend/services/cultural_metaphor_library.py
ls backend/services/grammar_visual_templates.py
ls backend/api/visual_teaching.py

# Check frontend files
ls frontend/src/components/TeachingVisualPlayer.js
ls frontend/src/components/InteractionLayer.js
ls frontend/src/engines/AnimationEngine.js
```

All files should exist! ✓

---

## Step 2: Start Backend

```bash
cd backend

# Install dependencies (if not already installed)
pip install fastapi uvicorn motor pymongo pydantic

# Start server
python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Backend should be running on `http://localhost:8000` ✓

---

## Step 3: Test API Endpoint

### Test 1: Generate Visual for Active/Passive Voice

```bash
# Using curl (Windows PowerShell)
curl -X POST http://localhost:8000/api/visual-teaching/generate `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -d '{
    "question": "Explain active and passive voice",
    "subject": "English",
    "complexity": "medium"
  }'

# Or using curl (Linux/Mac)
curl -X POST http://localhost:8000/api/visual-teaching/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "question": "Explain active and passive voice",
    "subject": "English",
    "complexity": "medium"
  }'
```

Expected response (abbreviated):
```json
{
  "success": true,
  "visual_id": "abc-123-...",
  "type": "animated_lesson",
  "stages": [
    {
      "stage_id": "stage-1",
      "duration_ms": 3000,
      "narration": "Let's understand active and passive voice using cooking!",
      "animations": [...]
    },
    ...
  ],
  "total_duration_ms": 28000,
  "interaction_points": [1, 3, 4, 5],
  "metadata": {
    "subject": "English",
    "topic": "Active and Passive Voice",
    "cultural_metaphor": "cooking"
  }
}
```

If you see this → Template system working! ✅

---

### Test 2: Check Available Patterns

```bash
curl http://localhost:8000/api/visual-teaching/patterns
```

Expected response:
```json
{
  "visual_patterns": [
    {
      "name": "flow_diagram",
      "description": "Step-by-step process visualization"
    },
    {
      "name": "split_screen",
      "description": "Side-by-side comparison"
    },
    ...
  ],
  "concept_types": [...]
}
```

---

### Test 3: Quick Generate (No Auth)

```bash
curl "http://localhost:8000/api/visual-teaching/quick-generate?question=Explain%20active%20voice&subject=English"
```

Expected response:
```json
{
  "success": true,
  "visual": {...}
}
```

---

## Step 4: Start Frontend

```bash
cd frontend

# Install dependencies (if not already installed)
npm install framer-motion lucide-react d3

# Start development server
npm start
```

Expected output:
```
Compiled successfully!

You can now view druv-ai in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000
```

Frontend should be running on `http://localhost:3000` ✓

---

## Step 5: Test in Browser

### Option A: Direct API Test (Recommended First)

1. Open browser dev tools (F12)
2. Go to Console tab
3. Paste this code:

```javascript
// Test API directly from browser
fetch('http://localhost:8000/api/visual-teaching/quick-generate?question=Explain%20active%20voice&subject=English')
  .then(res => res.json())
  .then(data => {
    console.log('✅ API Response:', data);
    if (data.success) {
      console.log('✅ Visual ID:', data.visual.visual_id);
      console.log('✅ Number of stages:', data.visual.stages.length);
      console.log('✅ Total duration:', data.visual.total_duration_ms / 1000, 'seconds');
    }
  })
  .catch(err => console.error('❌ Error:', err));
```

Expected console output:
```
✅ API Response: {success: true, visual: {...}}
✅ Visual ID: abc-123-...
✅ Number of stages: 7
✅ Total duration: 28 seconds
```

---

### Option B: Test with Frontend Component

1. Navigate to your chat interface
2. Ask a question: **"Explain active and passive voice"**
3. Backend should detect the keywords
4. Should return teaching_visual in response
5. MentorResponseV2 should render TeachingVisualPlayer
6. You should see animated visual instead of static image!

Expected behavior:
- ✅ Animated stages unfold automatically
- ✅ Narration bar shows text
- ✅ Progress bar advances
- ✅ Interaction prompts appear
- ✅ Play/pause/restart controls work
- ✅ Speed controls work (0.5x, 1x, 1.5x, 2x)

---

## Step 6: Test Interactions

When you see an interaction prompt:

### Quiz Interaction (Stage 4)
1. Question appears: "Which voice puts the DOER in spotlight?"
2. Options: [Active Voice, Passive Voice, Both equally]
3. Click "Active Voice"
4. Expected: ✅ Green feedback "Perfect! Active voice makes the doer the hero!"
5. Auto-continues after 2 seconds

### Drag Interaction (Stage 5)
1. Prompt: "Drag words to form passive voice"
2. Drag items to correct positions
3. Expected: Validation and feedback

### Prediction (Stage 6)
1. Prompt: "Which voice would you use for: 'The suspect was arrested last night'?"
2. Select "Passive Voice"
3. Expected: Explanation appears

---

## Step 7: Verify Analytics

### Check MongoDB

```bash
# Connect to MongoDB
mongo

# Switch to your database
use druv_ai

# Check visual analytics
db.visual_analytics.find().pretty()

# Should show document like:
{
  "user_id": "user-123",
  "visual_id": "abc-123",
  "question": "Explain active and passive voice",
  "subject": "English",
  "visual_type": "animated_lesson",
  "pattern": "split_screen",
  "complexity": "medium",
  "total_duration_ms": 28000,
  "num_stages": 7,
  "num_interactions": 4,
  "is_template": true,
  "timestamp": ISODate("2025-01-09T...")
}

# Check interactions
db.visual_interactions.find().pretty()
```

---

## 🧪 Test Checklist

Run through this checklist to verify everything works:

### Backend Tests

- [ ] ✅ Backend starts without errors
- [ ] ✅ `/api/visual-teaching/generate` endpoint works
- [ ] ✅ Active/passive voice returns 7 stages
- [ ] ✅ Response includes cooking metaphor metadata
- [ ] ✅ Total duration is ~28 seconds
- [ ] ✅ 4 interaction points detected
- [ ] ✅ Analytics logged to MongoDB

### Frontend Tests

- [ ] ✅ Frontend starts without errors
- [ ] ✅ TeachingVisualPlayer component renders
- [ ] ✅ Canvas displays animations
- [ ] ✅ Stage 1 shows kitchen scene
- [ ] ✅ Stage 2 shows split screen (left)
- [ ] ✅ Stage 3 shows split screen (right)
- [ ] ✅ Stage 4 shows comparison + quiz
- [ ] ✅ Narration bar updates per stage
- [ ] ✅ Progress bar advances smoothly

### Interaction Tests

- [ ] ✅ Tap to continue works
- [ ] ✅ Quiz appears at correct stage
- [ ] ✅ Quiz validates correct answer
- [ ] ✅ Quiz shows feedback (green/red)
- [ ] ✅ Drag interaction works
- [ ] ✅ Prediction interaction works
- [ ] ✅ Feedback posts to backend

### Control Tests

- [ ] ✅ Play button starts animation
- [ ] ✅ Pause button pauses animation
- [ ] ✅ Restart button resets to stage 1
- [ ] ✅ Skip button advances to next stage
- [ ] ✅ Speed controls change playback (0.5x, 1x, 1.5x, 2x)
- [ ] ✅ Stage indicators show current position
- [ ] ✅ Volume mute/unmute works

### Integration Tests

- [ ] ✅ MentorResponseV2 detects teaching_visual
- [ ] ✅ Animated visual prioritized over static images
- [ ] ✅ onComplete callback fires when done
- [ ] ✅ onInteraction callback fires for each interaction
- [ ] ✅ Analytics tracked in MongoDB

---

## 🐛 Troubleshooting

### Error: "Module not found: visual_teaching"

**Solution**: Make sure you registered the router in `main.py`:
```python
from api import visual_teaching
app.include_router(visual_teaching.router, tags=["Visual Teaching"])
```

### Error: "get_grammar_visual_template is not defined"

**Solution**: Check import in `visual_teaching.py`:
```python
from services.grammar_visual_templates import get_grammar_visual_template
```

### Error: "cultural_metaphor_library not found"

**Solution**: Verify file exists:
```bash
ls backend/services/cultural_metaphor_library.py
```

### Visual Not Showing in Frontend

**Solution**: Check MentorResponseV2 integration:
1. Open browser console
2. Look for log: `🎬 ANIMATED TEACHING VISUAL DETECTED`
3. If not present, backend not sending teaching_visual
4. If present, check TeachingVisualPlayer is rendering

### Animations Not Smooth

**Solution**:
- Reduce fps in AnimationEngine: `fps: 30` instead of `fps: 60`
- Use Canvas renderer: `renderer: 'canvas'`
- Check browser performance

### Interactions Not Working

**Solution**:
- Check console for errors
- Verify interaction data structure matches InteractionLayer expectations
- Test on different devices (touch vs mouse)

---

## 📊 Success Criteria

After running all tests, you should see:

✅ **Backend**
- 5 new/modified Python files
- 4 API endpoints working
- MongoDB analytics tracking

✅ **Frontend**
- TeachingVisualPlayer rendering
- 7 animated stages displaying
- 4 interactions functional
- Controls working

✅ **Integration**
- Question → Animated visual (end-to-end)
- Cultural metaphors applied
- Analytics logged
- User engagement tracked

✅ **User Experience**
- Smooth animations
- Clear narration
- Engaging interactions
- Cultural relevance
- No repetitive diagrams!

---

## 🎉 You're Done!

If all tests pass, your Visual Teaching Engine is **production-ready**!

Students asking "Explain active and passive voice" will now see:
- ❌ NOT: Static cricket flow diagram
- ✅ YES: Animated cooking + cricket metaphor with 7 engaging stages

---

## 📝 Next Steps

1. **Test Other Templates**
   - "Explain subject verb agreement"
   - "Explain tenses"

2. **Test Dynamic Generation**
   - "Explain photosynthesis" (no template, will use engine)
   - "Compare mitosis and meiosis"

3. **Add More Templates**
   - Create math visual templates
   - Create physics visual templates
   - Create chemistry visual templates

4. **Monitor Analytics**
   ```bash
   mongo
   use druv_ai
   db.visual_analytics.find().count()  # Number of visuals viewed
   db.visual_interactions.find().count()  # Number of interactions
   ```

5. **A/B Test**
   - Compare completion rates: static vs animated
   - Compare quiz scores: static vs animated
   - Track student preference

---

## 🆘 Need Help?

- Check logs: `backend/logs/visual_engine.log`
- Check console: Browser Dev Tools (F12)
- Check MongoDB: `db.visual_analytics.find()`
- Read docs: `VISUAL_TEACHING_ENGINE.md`
- Check flow: `VISUAL_SYSTEM_FLOW.md`

---

**Happy Testing! 🚀**

Transform those lifeless diagrams into living lessons!
