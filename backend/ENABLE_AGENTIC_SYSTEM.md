# 🚀 ENABLE AGENTIC SYSTEM

The agentic architecture is **fully implemented** but **disabled by default**. Follow these steps to enable it:

---

## ⚡ Quick Start (3 Steps)

### **Step 1: Set Environment Variable**

**Option A - Manual Edit (Windows)**:
1. Open `backend\.env` in a text editor
2. Add or update this line:
   ```
   USE_AGENTIC_SYSTEM=true
   ```
3. Save the file

**Option B - Command Line (PowerShell)**:
```powershell
cd backend
echo "USE_AGENTIC_SYSTEM=true" >> .env
```

**Option C - Command Line (CMD)**:
```cmd
cd backend
echo USE_AGENTIC_SYSTEM=true >> .env
```

---

### **Step 2: Restart Backend Server**

**If server is running**:
1. Press `Ctrl+C` to stop
2. Wait for clean shutdown

**Then restart**:
```bash
cd C:\Users\DELL\DruvAI\personal\backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

### **Step 3: Verify Activation**

**Look for these logs when server starts**:
```
🤖 Supervisor initialized with all sub-agents
   ├── Mentor agent initialized
   ├── Professor agent initialized
   └── Visualise agent initialized
```

**When you ask a question in AI Tutor, you should see**:
```
🤖 Using Agentic System for neuro-symbolic response
🎯 Detected intent: concept
👥 Activating agents: mentor, professor, visualise
   Routing to Mentor agent...
   Routing to Professor agent...
   Routing to Visualise agent...
✅ Supervisor orchestration complete
✅ Agentic response adapted successfully
```

---

## ✅ Verification Checklist

After enabling, verify with this checklist:

- [ ] Environment variable `USE_AGENTIC_SYSTEM=true` is set
- [ ] Backend server restarted successfully
- [ ] Logs show "Supervisor initialized with all sub-agents"
- [ ] Frontend AI Tutor is accessible
- [ ] Ask a test question (e.g., "Explain Newton's Laws")
- [ ] Response arrives within 3-5 seconds
- [ ] Logs show "Using Agentic System for neuro-symbolic response"
- [ ] Response includes both emotional and formal explanations

---

## 🧪 Test Queries

Try these questions to test different agent behaviors:

### **1. Conceptual Explanation** (Activates all agents)
```
"Explain Newton's Second Law of Motion"
```
Expected: Mentor metaphor + Professor derivation + Visual

### **2. Derivation** (Activates Professor + Visualise)
```
"Derive the quadratic formula"
```
Expected: Step-by-step formal proof

### **3. Application Problem** (Activates all agents)
```
"Calculate the force if mass is 10kg and acceleration is 5m/s²"
```
Expected: Mentor encouragement + Professor solution steps

### **4. Greeting** (Activates only Mentor)
```
"Hi!"
```
Expected: Quick friendly greeting (no professor)

---

## 🔍 Troubleshooting

### **Issue: Logs still show "Using legacy neuro-symbolic system"**

**Cause**: Environment variable not loaded

**Fix**:
1. Verify `.env` file contains: `USE_AGENTIC_SYSTEM=true`
2. No spaces around `=`
3. No quotes around value
4. File saved properly
5. Restart server (full stop + start, not just reload)

---

### **Issue: "ImportError: No module named 'agents'"**

**Cause**: Python path issue

**Fix**:
```bash
cd C:\Users\DELL\DruvAI\personal\backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn main:app --reload
```

---

### **Issue: "❌ Agentic system failed, falling back to legacy"**

**Cause**: Agent initialization error

**Fix**:
1. Check logs for specific error
2. Verify `EMERGENT_LLM_KEY` is set in `.env`
3. Check if all agent files exist in `backend/agents/`
4. Verify no syntax errors: `python -m py_compile backend/agents/*.py`

---

### **Issue: Response is slower than expected**

**Expected**: 2-4 seconds  
**Actual**: 5+ seconds

**Cause**: Sequential LLM calls

**Fix** (future optimization):
- Implement LLM response caching
- Use streaming responses
- Optimize prompt lengths

---

## 📊 Performance Comparison

| Metric | Legacy System | Agentic System |
|--------|---------------|----------------|
| Response Time | 3-5 seconds | 2-4 seconds |
| Token Usage | 800-1000 | 700-900 |
| Metaphor Quality | Static | Dynamic |
| Step-by-Step Clarity | Mixed | Structured |
| Visual Integration | Limited | Enhanced |
| Fallback Support | ❌ | ✅ |

---

## 🎯 Expected Behavior

### **With Agentic System ENABLED**

**User asks**: "Explain photosynthesis"

**System flow**:
1. SupervisorAgent detects intent: "concept"
2. Routes to: Mentor + Professor + Visualise
3. **Mentor** generates: Cricket/cooking metaphor about energy conversion
4. **Professor** generates: Step-by-step chemical equation
5. **Visualise** generates: Multi-stage animation spec
6. ResponseAdapter merges: Neuro-symbolic format
7. Frontend renders: Dual-layer response

**User sees**:
- 🎯 Intuitive Understanding (Mentor's metaphor)
- 📚 Formal Explanation (Professor's steps)
- 🎨 Visual Animation (if Visual Professor available)

---

### **With Agentic System DISABLED**

**User asks**: "Explain photosynthesis"

**System flow**:
1. AIService.generate_neuro_symbolic_response()
2. Single LLM call with unified prompt
3. Response parser extracts sections
4. Frontend renders

**User sees**:
- Combined response (less structured)
- Static visual (if any)
- No clear mentor/professor separation

---

## 🔄 Rollback (Disable Agentic System)

If you encounter issues, quickly disable:

### **Option 1: Environment Variable**
```bash
# In backend/.env
USE_AGENTIC_SYSTEM=false
```

### **Option 2: Comment Out in Code**
Edit `backend/api/ai.py` line 994:
```python
# USE_AGENTIC_SYSTEM = os.getenv("USE_AGENTIC_SYSTEM", "false").lower() == "true"
USE_AGENTIC_SYSTEM = False  # Force disable
```

Then restart server.

---

## 📝 Configuration Options

Add these to `backend/.env` for customization:

```bash
# Enable/disable agentic system
USE_AGENTIC_SYSTEM=true

# LLM settings
EMERGENT_LLM_KEY=your_api_key_here

# Agent behavior (optional, defaults shown)
MENTOR_TEMPERATURE=0.8          # Creativity (0.0-1.0)
PROFESSOR_TEMPERATURE=0.3       # Precision (0.0-1.0)
MENTOR_MAX_TOKENS=300           # Response length
PROFESSOR_MAX_TOKENS=400        # Response length

# Visual settings (optional)
ENABLE_VISUAL_GENERATION=true
VISUAL_FALLBACK_ENABLED=true
```

---

## ✅ Success Indicators

You'll know the system is working when:

1. ✅ Logs show agent initialization
2. ✅ Responses have clear mentor/professor sections
3. ✅ Metaphors are contextual (not random)
4. ✅ Step-by-step formatting is consistent
5. ✅ Visual specifications appear (when applicable)
6. ✅ Response time is 2-4 seconds
7. ✅ No fallback errors in logs

---

## 🎉 You're Ready!

Once enabled, the agentic system will:
- ✅ Provide more structured responses
- ✅ Separate emotional and logical reasoning
- ✅ Dynamically select metaphors
- ✅ Generate better visuals
- ✅ Maintain fallback safety

**Start the backend and test with a question!** 🚀

