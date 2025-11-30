# 🤖 DRUV AI - AGENT IMPLEMENTATION BLUEPRINT

## Current Agent Architecture

```
backend/agents/
├── base_agent.py          # Abstract base class for all agents
├── supervisor.py          # Orchestrator - routes to sub-agents
├── mentor.py              # Emotional, intuitive explanations
├── professor.py           # Formal, structured explanations
├── visualise.py           # Visual generation agent
├── response_adapter.py    # Formats responses uniformly
└── enhanced_supervisor.py # Advanced orchestration
```

---

## 🆕 NEW AGENTS TO IMPLEMENT

### Agent 1: Doubt Resolver Agent

**File:** `backend/agents/doubt_resolver.py`

```python
"""
Doubt Resolver Agent - Zero-Judgment Instant Help

Philosophy: "There are no stupid questions, only unexplored curiosities."

Capabilities:
- Instant doubt clearing with visual explanations
- Never condescends or makes student feel bad
- Tracks common doubts to create preemptive content
- Escalates complex doubts to Professor agent
"""

class DoubtResolverAgent(BaseAgent):
    
    async def process(self, query: str, context: Dict) -> Dict:
        # 1. Classify doubt type (conceptual, calculation, definition)
        # 2. Check if similar doubt answered before (memory)
        # 3. Generate simple, visual explanation
        # 4. Add "Did this help?" feedback loop
        # 5. If student still stuck, escalate
        pass
    
    def _classify_doubt(self, query: str) -> str:
        """Classify: conceptual | calculation | definition | comparison"""
        pass
    
    def _generate_visual_explanation(self, doubt: str, concept: str) -> Dict:
        """Always include a visual for doubts"""
        pass
```

---

### Agent 2: Motivation Agent

**File:** `backend/agents/motivation.py`

```python
"""
Motivation Agent - Emotional Support & Confidence Building

Philosophy: "A student who believes they can succeed is already halfway there."

Triggers:
- Long gap in activity (burnout detection)
- Multiple wrong answers (frustration)
- Late night studying (stress)
- Before major exams (anxiety)
- After completing milestones (celebration)
"""

class MotivationAgent(BaseAgent):
    
    MOTIVATION_TRIGGERS = {
        'frustration': ['wrong_answer_streak', 'repeated_same_question'],
        'burnout': ['no_activity_3_days', 'session_time_dropping'],
        'anxiety': ['exam_approaching', 'late_night_sessions'],
        'celebration': ['milestone_reached', 'streak_achieved']
    }
    
    async def process(self, context: Dict) -> Dict:
        # 1. Detect emotional state from usage patterns
        # 2. Select appropriate message type
        # 3. Personalize with student's name and achievements
        # 4. Optionally suggest break or change of activity
        pass
    
    def _detect_emotional_state(self, usage_data: Dict) -> str:
        """Analyze patterns to detect: frustrated | burned_out | anxious | confident"""
        pass
    
    def _get_motivational_message(self, state: str, student: Dict) -> str:
        """Generate personalized, genuine motivation"""
        pass
```

---

### Agent 3: Exam Coach Agent

**File:** `backend/agents/exam_coach.py`

```python
"""
Exam Coach Agent - Strategic Exam Preparation

Philosophy: "Smart preparation beats hard preparation."

Specializations:
- JEE (Main + Advanced)
- NEET
- CBSE/ICSE Boards
- State Boards
- Olympiads
"""

class ExamCoachAgent(BaseAgent):
    
    EXAM_STRATEGIES = {
        'JEE_MAINS': {
            'paper_pattern': {'physics': 25, 'chemistry': 25, 'math': 25},
            'time_per_question': 1.6,  # minutes
            'high_weightage': ['mechanics', 'organic', 'calculus'],
            'typical_easy': ['modern_physics', 'inorganic', 'probability']
        },
        'NEET': {
            'paper_pattern': {'physics': 45, 'chemistry': 45, 'biology': 90},
            'time_per_question': 1.0,
            'high_weightage': ['human_physiology', 'genetics', 'organic']
        }
    }
    
    async def process(self, query: str, context: Dict) -> Dict:
        # 1. Understand what exam help is needed
        # 2. Provide strategic advice based on exam type
        # 3. Suggest time allocation and attempt order
        # 4. Share PYQ patterns and predictions
        pass
    
    def _get_exam_strategy(self, exam: str, days_left: int) -> Dict:
        """Generate customized preparation strategy"""
        pass
    
    def _analyze_pyq_patterns(self, exam: str, topic: str) -> Dict:
        """Find patterns in past year questions"""
        pass
```

---

### Agent 4: Study Buddy Agent

**File:** `backend/agents/study_buddy.py`

```python
"""
Study Buddy Agent - Peer Learning Simulation

Philosophy: "Learning together is learning better."

Personality:
- Relatable, same-age feel
- Makes mistakes sometimes (realistic)
- Celebrates together
- Uses student slang naturally
"""

class StudyBuddyAgent(BaseAgent):
    
    BUDDY_PERSONALITIES = {
        'enthusiastic': {
            'phrases': ['Bro, let me try this!', 'Wait wait, I think I got it!'],
            'mistakes': 'often',
            'celebration': 'high_five_emoji'
        },
        'thoughtful': {
            'phrases': ['Hmm, let me think about this...', 'Oh interesting!'],
            'mistakes': 'sometimes',
            'celebration': 'genuine_praise'
        }
    }
    
    async def process(self, query: str, context: Dict) -> Dict:
        # 1. Simulate thinking process out loud
        # 2. Sometimes make relatable mistakes
        # 3. Work through problem step-by-step together
        # 4. Celebrate when solution found
        pass
    
    def _simulate_thinking(self, problem: str) -> List[str]:
        """Generate realistic thinking steps"""
        pass
```

---

### Agent 5: Weak Area Detective Agent

**File:** `backend/agents/weak_area_detective.py`

```python
"""
Weak Area Detective Agent - Knowledge Gap Analysis

Philosophy: "You can't fix what you can't see."

Analysis Types:
- Topic-level weaknesses
- Concept-level gaps
- Skill-level issues (calculation, conceptual, application)
- Time-based patterns
"""

class WeakAreaDetectiveAgent(BaseAgent):
    
    async def process(self, user_id: str, context: Dict) -> Dict:
        # 1. Analyze all past answers
        # 2. Find patterns in wrong answers
        # 3. Identify knowledge gaps
        # 4. Generate improvement plan
        # 5. Predict potential exam problems
        pass
    
    def _analyze_answer_patterns(self, answers: List[Dict]) -> Dict:
        """Find patterns: time_of_day, topic, question_type"""
        pass
    
    def _identify_knowledge_gaps(self, wrong_answers: List[Dict]) -> List[str]:
        """Map wrong answers to missing concepts"""
        pass
    
    def _generate_improvement_plan(self, gaps: List[str], days: int) -> Dict:
        """Create targeted study plan"""
        pass
```

---

### Agent 6: Voice Learning Agent

**File:** `backend/agents/voice_learning.py`

```python
"""
Voice Learning Agent - Audio-Based Learning

Philosophy: "Learning should fit into life, not the other way around."

Use Cases:
- Commute learning (buses, trains)
- Revision while doing chores
- Auditory learners
- Tired eyes after long study sessions
"""

class VoiceLearningAgent(BaseAgent):
    
    VOICE_MODES = {
        'podcast': 'conversational, engaging explanation',
        'revision': 'quick facts, key points only',
        'story': 'concept as narrative',
        'quiz': 'interactive Q&A'
    }
    
    async def process(self, query: str, context: Dict) -> Dict:
        # 1. Convert content to speech-friendly format
        # 2. Generate audio or SSML for TTS
        # 3. Include pause points for thinking
        # 4. Support voice commands for interaction
        pass
    
    def _convert_to_audio_script(self, content: str, mode: str) -> str:
        """Convert visual content to audio-friendly format"""
        pass
```

---

### Agent 7: Parent Report Agent

**File:** `backend/agents/parent_report.py`

```python
"""
Parent Report Agent - Guardian Communication

Philosophy: "Informed parents = supported students."

Report Types:
- Weekly summary
- Achievement alerts
- Concern alerts (only when necessary)
- Exam preparation status
"""

class ParentReportAgent(BaseAgent):
    
    REPORT_TEMPLATES = {
        'weekly': {
            'sections': ['time_spent', 'topics_covered', 'achievements', 'areas_to_focus'],
            'tone': 'positive_first',
            'frequency': 'sunday_evening'
        },
        'achievement': {
            'trigger': ['streak_milestone', 'concept_mastered', 'level_up'],
            'tone': 'celebratory'
        },
        'concern': {
            'trigger': ['no_activity_5_days', 'performance_drop'],
            'tone': 'supportive_suggestion'
        }
    }
    
    async def generate_report(self, user_id: str, report_type: str) -> Dict:
        # 1. Gather student activity data
        # 2. Analyze progress
        # 3. Generate parent-friendly summary
        # 4. Include actionable suggestions
        pass
```

---

## 🔧 IMPLEMENTATION PRIORITY

| Agent | Priority | Effort | Impact | Timeline |
|-------|----------|--------|--------|----------|
| Doubt Resolver | 🔴 HIGH | 2 weeks | ⭐⭐⭐⭐⭐ | Sprint 1 |
| Motivation | 🔴 HIGH | 1 week | ⭐⭐⭐⭐ | Sprint 1 |
| Weak Area Detective | 🟠 MEDIUM | 2 weeks | ⭐⭐⭐⭐⭐ | Sprint 2 |
| Exam Coach | 🟠 MEDIUM | 2 weeks | ⭐⭐⭐⭐ | Sprint 2 |
| Parent Report | 🟡 LOW | 1 week | ⭐⭐⭐ | Sprint 3 |
| Study Buddy | 🟡 LOW | 3 weeks | ⭐⭐⭐⭐ | Sprint 3 |
| Voice Learning | 🟡 LOW | 4 weeks | ⭐⭐⭐ | Sprint 4 |

---

## 📝 INTEGRATION WITH EXISTING SYSTEM

### Update Supervisor Agent

```python
# In supervisor.py

class SupervisorAgent(BaseAgent):
    def __init__(self, config):
        # Existing agents
        self.mentor = MentorAgent(config)
        self.professor = ProfessorAgent(config)
        self.visualise = VisualiseAgent(config)
        
        # NEW agents
        self.doubt_resolver = DoubtResolverAgent(config)
        self.motivation = MotivationAgent(config)
        self.exam_coach = ExamCoachAgent(config)
        self.weak_detector = WeakAreaDetectiveAgent(config)
    
    async def route_to_agent(self, query: str, context: Dict) -> str:
        """Intelligent routing to appropriate agent"""
        intent = self._detect_intent(query)
        
        if intent == 'doubt':
            return 'doubt_resolver'
        elif intent == 'exam_strategy':
            return 'exam_coach'
        elif self._detect_frustration(context):
            return 'motivation'  # Intercept with support
        else:
            return 'mentor'  # Default
```

---

## 🎯 SUCCESS CRITERIA

Each agent should:
1. ✅ Respond in < 2 seconds
2. ✅ Have personality consistent with Druv AI brand
3. ✅ Use memory system for personalization
4. ✅ Log interactions for analytics
5. ✅ Support both Hindi and English
6. ✅ Have clear handoff protocol to other agents

---

*Blueprint Version: 1.0*
*Author: Druv AI Team*

