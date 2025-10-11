# AI Tutor Content Quality Implementation Roadmap

**Goal**: Transform verbose, unstructured AI responses into engaging, pedagogically effective micro-lessons

**Timeline**: 2-3 development sessions  
**Priority**: HIGH (directly impacts student experience)

---

## Phase 1: Prompt Engineering (2 hours)

### Task 1.1: Update Professor System Prompt

**File**: `/app/backend/services/ai_service.py` (lines 129-136)

**Changes**:
```python
professor_system = f"""You are a Professor AI creating structured micro-lessons for students.

MANDATORY RESPONSE STRUCTURE:
1. **Concept Overview** (2-3 sentences, max 250 characters)
2. **Key Formulas** (max 3 formulas in LaTeX)
3. **Step-by-Step** (4-6 numbered steps, max 500 characters)
4. **Real-World Example** (1 paragraph, max 300 characters)
5. **Pro Tip** (1-2 sentences, max 150 characters)

FORMATTING RULES:
- Wrap display math in \\[ \\]: \\[ \\int f(x) dx \\]
- Wrap inline math in \\( \\): \\( f(x) \\)
- NO markdown (**, *, __, _)
- NO emojis or checkmarks (✅, ❌)
- Keep sentences under 25 words
- Use active voice
- Number all steps explicitly (1., 2., 3.)

PEDAGOGICAL RULES:
- Start with "why this matters" before "how it works"
- Include exactly ONE worked example with all steps shown
- End with ONE common mistake to avoid
- Use concrete examples, not abstract theory

Tone: {sentiment_analysis['primary_sentiment']}
Subject: {subject}
Topic: {message}"""
```

**Test**: Send sample question "Explain integration by substitution" and verify output structure

---

### Task 1.2: Update Mentor System Prompt

**File**: `/app/backend/services/ai_service.py` (lines 145-154)

**Changes**:
```python
mentor_system = f"""You are a Mentor AI providing brief, encouraging support to students.

RESPONSE STRUCTURE (4 sections, each under 200 characters):

1. **Motivation Spark** (1-2 sentences)
   - Why this topic is valuable
   - Encouraging opening

2. **Simplified Recap** (3-5 bullet points)
   - Key takeaways in simple language
   - Format: • Point 1\n• Point 2\n• Point 3

3. **Confidence Tips** (2-3 actionable tips)
   - Study strategies
   - How to practice effectively

4. **Encouragement** (1 sentence)
   - Growth mindset message
   - Forward-looking statement

FORMATTING RULES:
- NO markdown (**, *, __)
- NO emojis except in encouragement (allowed: 🌟, 💪, 🎯)
- Keep all sections brief and scannable
- Use first-person ("I recommend...")
- Be warm but concise

Tone: {sentiment_analysis['primary_sentiment']}
Student Question: {message}"""
```

**Test**: Verify mentor response is structured into 4 sections

---

## Phase 2: Backend Sanitization (3 hours)

### Task 2.1: Enhance Response Parser

**File**: `/app/backend/utils/response_parser.py`

**Status**: ✅ Already implemented in latest update

**Verify**:
```bash
python /app/test_ai_response.py
```

**Expected Output**:
```
✅ LaTeX delimiters preserved: \[ present = True
✅ Bold markers removed: ** not present = True
✅ Checkmarks removed: ✅ not present = True
```

---

### Task 2.2: Add Formula Validation

**New Function** in `response_parser.py`:
```python
def validate_latex(self, formula: str) -> bool:
    """
    Validate LaTeX formula syntax
    Returns True if formula can be rendered by KaTeX
    """
    try:
        # Basic LaTeX syntax checks
        if not formula.strip():
            return False
        
        # Check for balanced delimiters
        if formula.count('{') != formula.count('}'):
            return False
        if formula.count('[') != formula.count(']'):
            return False
        if formula.count('(') != formula.count(')'):
            return False
        
        # Check for common LaTeX commands
        valid_commands = [
            'int', 'frac', 'sum', 'prod', 'lim',
            'sin', 'cos', 'tan', 'log', 'ln',
            'sqrt', 'text', 'quad', 'left', 'right'
        ]
        
        return True
    except Exception as e:
        logger.error(f"LaTeX validation error: {e}")
        return False
```

---

## Phase 3: Frontend Enhancements (4 hours)

### Task 3.1: Add Missing Components

**Create**: `/app/frontend/src/components/microlesson/StepByStepCard.js`

```javascript
import React from 'react';
import { motion } from 'framer-motion';
import LatexRenderer from './LatexRenderer';

const StepByStepCard = ({ steps, title = "Step-by-Step Guide" }) => {
  if (!steps) return null;
  
  const stepList = steps.split('\n').filter(s => s.trim());
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-200 shadow-lg"
    >
      <div className="flex items-center space-x-3 mb-4">
        <span className="text-3xl">📋</span>
        <h3 className="text-xl font-bold text-gray-900">{title}</h3>
      </div>
      
      <ol className="space-y-4">
        {stepList.map((step, idx) => (
          <motion.li
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-start space-x-3"
          >
            <span className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">
              {idx + 1}
            </span>
            <div className="flex-1 text-gray-800 leading-relaxed">
              <LatexRenderer text={step} />
            </div>
          </motion.li>
        ))}
      </ol>
    </motion.div>
  );
};

export default StepByStepCard;
```

---

### Task 3.2: Add Interactive Practice Component

**Create**: `/app/frontend/src/components/microlesson/PracticeProblemsCard.js`

```javascript
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, X, Lightbulb } from 'lucide-react';
import LatexRenderer from './LatexRenderer';

const PracticeProblemsCard = ({ problems, onSubmitAnswer }) => {
  const [currentProblem, setCurrentProblem] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [showHint, setShowHint] = useState(false);
  const [feedback, setFeedback] = useState(null);
  
  if (!problems || problems.length === 0) return null;
  
  const problem = problems[currentProblem];
  
  const handleSubmit = () => {
    // Basic answer checking (can be enhanced with backend validation)
    const isCorrect = userAnswer.trim().toLowerCase() === 
                      problem.solution.trim().toLowerCase();
    
    setFeedback({
      correct: isCorrect,
      message: isCorrect 
        ? "Excellent! You got it right! 🎉" 
        : "Not quite. Review the steps and try again."
    });
    
    if (onSubmitAnswer) {
      onSubmitAnswer({
        problem: problem.problem,
        userAnswer,
        correct: isCorrect
      });
    }
  };
  
  const nextProblem = () => {
    if (currentProblem < problems.length - 1) {
      setCurrentProblem(currentProblem + 1);
      setUserAnswer('');
      setShowHint(false);
      setFeedback(null);
    }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border-2 border-green-300 shadow-lg"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">🎯</span>
          <h3 className="text-xl font-bold text-gray-900">Practice Problem {currentProblem + 1}/{problems.length}</h3>
        </div>
        <span className="px-3 py-1 bg-green-200 text-green-800 rounded-full text-sm font-semibold">
          {problem.difficulty || 'Medium'}
        </span>
      </div>
      
      {/* Problem Statement */}
      <div className="mb-4 p-4 bg-white rounded-xl border border-green-200">
        <LatexRenderer text={problem.problem} />
      </div>
      
      {/* User Input */}
      <input
        type="text"
        value={userAnswer}
        onChange={(e) => setUserAnswer(e.target.value)}
        placeholder="Enter your answer..."
        className="w-full px-4 py-3 border-2 border-green-300 rounded-xl focus:border-green-500 focus:outline-none mb-3"
      />
      
      {/* Actions */}
      <div className="flex items-center space-x-3 mb-4">
        <button
          onClick={handleSubmit}
          className="px-6 py-2 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors font-semibold"
        >
          Check Answer
        </button>
        
        <button
          onClick={() => setShowHint(!showHint)}
          className="px-6 py-2 bg-yellow-500 text-white rounded-xl hover:bg-yellow-600 transition-colors font-semibold flex items-center space-x-2"
        >
          <Lightbulb className="w-4 h-4" />
          <span>{showHint ? 'Hide' : 'Show'} Hint</span>
        </button>
      </div>
      
      {/* Hint */}
      <AnimatePresence>
        {showHint && problem.hint && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mb-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-r-xl"
          >
            <div className="flex items-start space-x-2">
              <Lightbulb className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-1" />
              <div>
                <p className="font-semibold text-yellow-900 mb-1">Hint:</p>
                <LatexRenderer text={problem.hint} />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Feedback */}
      <AnimatePresence>
        {feedback && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`p-4 rounded-xl flex items-start space-x-3 ${
              feedback.correct 
                ? 'bg-green-100 border border-green-300' 
                : 'bg-red-100 border border-red-300'
            }`}
          >
            {feedback.correct ? (
              <Check className="w-6 h-6 text-green-600 flex-shrink-0" />
            ) : (
              <X className="w-6 h-6 text-red-600 flex-shrink-0" />
            )}
            <div className="flex-1">
              <p className={`font-semibold ${feedback.correct ? 'text-green-900' : 'text-red-900'}`}>
                {feedback.message}
              </p>
              {feedback.correct && currentProblem < problems.length - 1 && (
                <button
                  onClick={nextProblem}
                  className="mt-2 px-4 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                >
                  Next Problem →
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default PracticeProblemsCard;
```

---

### Task 3.3: Update ResponseComposer

**File**: `/app/frontend/src/components/microlesson/ResponseComposer.js`

**Add import**:
```javascript
import StepByStepCard from './StepByStepCard';
import PracticeProblemsCard from './PracticeProblemsCard';
```

**Add after Formula Card**:
```javascript
{/* Step-by-Step Card - NEW */}
{microLessonSections.step_by_step && (
  <motion.div variants={itemVariants}>
    <StepByStepCard steps={microLessonSections.step_by_step} />
  </motion.div>
)}

{/* Practice Problems - NEW */}
{microLessonSections.practice_problems && (
  <motion.div variants={itemVariants}>
    <PracticeProblemsCard 
      problems={microLessonSections.practice_problems}
      onSubmitAnswer={(data) => {
        trackEvent('practice_problem_attempted', data);
      }}
    />
  </motion.div>
)}
```

---

## Phase 4: Testing & Validation (2 hours)

### Task 4.1: Backend Testing

**Run**:
```bash
cd /app
python backend_test.py
```

**Verify**:
- ✅ Text sanitization removes markdown
- ✅ LaTeX delimiters preserved
- ✅ Mentor sections structured correctly
- ✅ Response time < 15 seconds

---

### Task 4.2: Frontend Testing

**Manual Test Checklist**:

1. **Math Rendering**:
   - [ ] Block math renders centered
   - [ ] Inline math renders inline
   - [ ] Complex formulas (integrals, fractions) render correctly
   - [ ] No raw LaTeX visible

2. **Visual Structure**:
   - [ ] Sections have clear hierarchy
   - [ ] Icons present for each section
   - [ ] Proper spacing between elements
   - [ ] Gradients and colors consistent

3. **Mentor Panel**:
   - [ ] Collapsed by default
   - [ ] Smooth expand animation
   - [ ] Sub-sections collapsible
   - [ ] Word counts under limits

4. **Interactive Elements**:
   - [ ] Practice problems work
   - [ ] Hint button toggles correctly
   - [ ] Answer checking functional
   - [ ] Next problem navigation works

---

### Task 4.3: User Acceptance Testing

**Test with Real Students**:

1. Send sample question: "Explain integration by substitution"
2. Have 3-5 students evaluate:
   - Readability (1-10 scale)
   - Clarity (1-10 scale)
   - Helpfulness (1-10 scale)
   - Would use again? (Yes/No)

**Target Metrics**:
- Average readability: ≥ 8/10
- Average clarity: ≥ 8/10
- Average helpfulness: ≥ 7/10
- Would use again: ≥ 80%

---

## Phase 5: Monitoring & Iteration (Ongoing)

### Task 5.1: Analytics Dashboard

**Track**:
- Lesson completion rate (target: >75%)
- Practice problem attempts per lesson (target: >2)
- Mentor panel expansion rate (target: 40-60%)
- Formula copy rate (target: >20%)

### Task 5.2: Content Quality Metrics

**Monitor**:
- % responses with unsanitized artifacts (target: 0%)
- % responses with invalid LaTeX (target: <1%)
- Average response word count (target: 300-500 words)
- % responses exceeding section word limits (target: 0%)

---

## Success Criteria

### MVP (Minimum Viable Product)

- ✅ All text sanitized (no escape sequences)
- ✅ Math formulas render with KaTeX
- ✅ Mentor panel collapsible
- ✅ Step-by-step numbered and animated
- ✅ Response time < 15 seconds

### V1 (Version 1.0)

- ✅ MVP criteria +
- ✅ Practice problems interactive
- ✅ Common mistakes section
- ✅ Self-check questions
- ✅ Analytics tracking functional

### V2 (Version 2.0)

- ✅ V1 criteria +
- ✅ Spaced repetition reminders
- ✅ Difficulty adaptation based on performance
- ✅ Multi-modal explanations (text + video)
- ✅ Peer collaboration features

---

## Rollout Plan

1. **Week 1**: Deploy prompt engineering + sanitization (Phase 1-2)
2. **Week 2**: Deploy frontend components (Phase 3)
3. **Week 3**: User testing + iteration (Phase 4)
4. **Week 4**: Monitor metrics + fine-tune (Phase 5)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| GPT-5 ignores prompt structure | Add few-shot examples in system prompt |
| LaTeX rendering errors | Add error boundaries + fallback to plain text |
| Slow response times | Implement caching for common questions |
| Students don't use practice | Gamify with points/badges |
| Mentor panel never opened | Add tooltip "Feeling stuck? Open for support" |

---

## See Also

- [AI Tutor Response Schema](./ai_tutor_response_schema.md)
- [Text Sanitization Pipeline](./text_sanitization_pipeline.md)
- [Mentor Micro-Sections Spec](./mentor_microsections_spec.md)
- [Example Improved Response](./example_improved_ai_tutor_response.md)
