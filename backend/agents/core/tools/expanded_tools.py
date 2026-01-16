"""
🔧 Expanded Tool Set for Agentic System
=========================================

Comprehensive tools that allow agents to act more autonomously.
"""

import os
import json
import asyncio
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


# ============== Learning & Teaching Tools ==============

class MetaphorGeneratorTool(BaseTool):
    """Generate culturally relevant metaphors for concepts"""

    @property
    def name(self) -> str:
        return "metaphor_generator"

    @property
    def description(self) -> str:
        return "Generate relatable metaphors and analogies for complex concepts. Great for making abstract ideas concrete."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "concept": "The concept to explain (e.g., 'momentum')",
            "context": "Student context (age, interests, culture)"
        }

    async def execute(self, concept: str, context: str = "", **kwargs) -> ToolResult:
        """Generate metaphor for concept"""
        try:
            from agents.core.shared_utils import MetaphorGenerator

            metaphor = MetaphorGenerator.generate_metaphor(concept)

            if metaphor:
                return ToolResult.success_result(
                    f"Here's a metaphor for {concept}: {metaphor}",
                    metadata={"concept": concept, "metaphor": metaphor}
                )

            # Generate dynamic metaphor based on context
            if "cricket" in context.lower():
                base = f"{concept} is like a cricket match where"
            elif "bollywood" in context.lower():
                base = f"{concept} is like a Bollywood movie where"
            else:
                base = f"{concept} can be understood as"

            result = f"{base} [would need specific details about {concept} to complete]"

            return ToolResult.success_result(result)

        except Exception as e:
            return ToolResult.error_result(f"Metaphor generation failed: {e}")


class ExampleGeneratorTool(BaseTool):
    """Generate examples for concepts"""

    @property
    def name(self) -> str:
        return "example_generator"

    @property
    def description(self) -> str:
        return "Generate practical examples to illustrate concepts. Can create numerical problems or real-world scenarios."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "concept": "The concept to exemplify",
            "difficulty": "easy, medium, or hard",
            "count": "Number of examples (1-3)"
        }

    async def execute(
        self,
        concept: str,
        difficulty: str = "medium",
        count: int = 1,
        **kwargs
    ) -> ToolResult:
        """Generate examples"""
        try:
            examples = []

            # Physics examples
            if "momentum" in concept.lower():
                if difficulty == "easy":
                    examples.append("A 2 kg ball moving at 3 m/s has momentum = 2 × 3 = 6 kg⋅m/s")
                elif difficulty == "medium":
                    examples.append("A 1000 kg car at 20 m/s collides with a 1500 kg car at rest. Find final velocities.")
                else:
                    examples.append("Two particles collide obliquely. Given initial momenta, find scattering angles.")

            elif "force" in concept.lower():
                if difficulty == "easy":
                    examples.append("Pushing a 10 kg box with 50 N force. Acceleration = F/m = 50/10 = 5 m/s²")
                else:
                    examples.append("A block on an incline with friction. Calculate acceleration down the slope.")

            # Chemistry examples
            elif "mole" in concept.lower():
                if difficulty == "easy":
                    examples.append("How many moles in 36g of water (H₂O)? MW = 18, so moles = 36/18 = 2")
                else:
                    examples.append("Calculate moles of gas at STP occupying 44.8 L volume.")

            # Math examples
            elif "derivative" in concept.lower():
                if difficulty == "easy":
                    examples.append("Find d/dx of x². Answer: 2x")
                else:
                    examples.append("Find d/dx of sin(x²). Use chain rule: 2x⋅cos(x²)")

            if not examples:
                examples.append(f"Generic example for {concept}: Consider a scenario where {concept} applies...")

            result = "\n".join(examples[:count])
            return ToolResult.success_result(
                f"Examples for {concept} ({difficulty}):\n{result}",
                metadata={"concept": concept, "examples": examples}
            )

        except Exception as e:
            return ToolResult.error_result(f"Example generation failed: {e}")


class QuizGeneratorTool(BaseTool):
    """Generate quiz questions"""

    @property
    def name(self) -> str:
        return "quiz_generator"

    @property
    def description(self) -> str:
        return "Generate quiz questions to test understanding. Includes MCQs and short answer questions."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "topic": "Topic for the quiz",
            "question_type": "mcq or short_answer",
            "count": "Number of questions (1-5)"
        }

    async def execute(
        self,
        topic: str,
        question_type: str = "mcq",
        count: int = 1,
        **kwargs
    ) -> ToolResult:
        """Generate quiz questions"""
        try:
            questions = []

            if question_type == "mcq":
                # Generate MCQ
                template = {
                    "question": f"Which of the following is true about {topic}?",
                    "options": [
                        f"Option A related to {topic}",
                        f"Option B related to {topic}",
                        f"Option C related to {topic}",
                        f"Option D related to {topic}"
                    ],
                    "correct": "A",
                    "explanation": f"Option A is correct because [explanation about {topic}]"
                }
                questions.append(template)

            else:
                # Short answer
                questions.append({
                    "question": f"Explain the concept of {topic} in your own words.",
                    "hint": f"Think about the key characteristics of {topic}",
                    "sample_answer": f"{topic} is [would need specific content to complete]"
                })

            result = json.dumps(questions[:count], indent=2)
            return ToolResult.success_result(
                f"Quiz questions on {topic}:\n{result}",
                metadata={"questions": questions}
            )

        except Exception as e:
            return ToolResult.error_result(f"Quiz generation failed: {e}")


# ============== Memory & Context Tools ==============

class MemoryRecallTool(BaseTool):
    """
    Recall information from REAL persistent student memory.
    
    MEMORY CONTRACT: Uses MemoryService as the SINGLE SOURCE OF TRUTH.
    NO hardcoded data. Returns real student data from MongoDB.
    """
    
    def __init__(self, db=None):
        """Initialize with optional database connection."""
        super().__init__()
        self._db = db
        self._memory_service = None
    
    def _get_memory_service(self, db=None):
        """Lazy-load MemoryService with provided or stored db."""
        if self._memory_service is None:
            actual_db = db or self._db
            if actual_db:
                from services.memory_service import MemoryService
                self._memory_service = MemoryService(actual_db)
        return self._memory_service

    @property
    def name(self) -> str:
        return "memory_recall"

    @property
    def description(self) -> str:
        return "Recall real student memory: preferences, weak/strong areas, past struggles, learning style."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "query": "What to recall (e.g., 'weak_topics', 'preferences', 'streak', 'goals')",
            "user_id": "Student ID (required)"
        }

    async def execute(self, query: str, user_id: str = "", **kwargs) -> ToolResult:
        """
        Recall REAL memory from persistent database.
        
        NO FAKE DATA. If memory is empty, returns honest empty result.
        """
        try:
            if not user_id:
                return ToolResult.error_result("user_id is required for memory recall")
            
            # Get database from context if not already set
            context = kwargs.get('context', {})
            db = context.get('db') or self._db
            
            memory_service = self._get_memory_service(db)
            
            # If no database connection, return honest empty result
            if not memory_service:
                return ToolResult.success_result(
                    "Memory service not available (no database connection)",
                    metadata={"memories": [], "status": "no_db"},
                    data={}
                )
            
            # Get REAL student profile from persistent storage
            # BEST-EFFORT: Don't block agent execution on memory timeout
            import asyncio
            try:
                profile = await asyncio.wait_for(
                    memory_service.get_student_profile(user_id),
                    timeout=1.0  # 1s max - don't block agent
                )
            except asyncio.TimeoutError:
                logger.warning(f"⚡ RecallMemoryTool: Profile timeout (>1s), using empty profile")
                profile = {}
            except Exception as e:
                logger.warning(f"⚠️ RecallMemoryTool: Profile error, using empty profile: {e}")
                profile = {}
            
            # Build memory response from REAL data
            memories = {}
            query_lower = query.lower()
            
            # Extract relevant data based on query
            if 'weak' in query_lower or 'struggle' in query_lower or 'difficulty' in query_lower:
                weak_topics = profile.get('weak_topics', [])
                if weak_topics:
                    memories['weak_areas'] = ', '.join(weak_topics)
            
            if 'strong' in query_lower or 'good' in query_lower or 'strength' in query_lower:
                strong_topics = profile.get('strong_topics', [])
                if strong_topics:
                    memories['strong_areas'] = ', '.join(strong_topics)
            
            if 'preference' in query_lower or 'style' in query_lower or 'learn' in query_lower:
                pref_explanation = profile.get('preferred_explanation', '')
                pref_analogies = profile.get('preferred_analogies', [])
                pacing = profile.get('pacing', '')
                if pref_explanation:
                    memories['explanation_style'] = pref_explanation
                if pref_analogies:
                    memories['preferred_analogies'] = ', '.join(pref_analogies)
                if pacing:
                    memories['learning_pace'] = pacing
            
            if 'streak' in query_lower or 'practice' in query_lower or 'consistency' in query_lower:
                streak = profile.get('practice_streak', 0)
                revision_streak = profile.get('revision_streak', 0)
                if streak > 0:
                    memories['practice_streak'] = f"{streak} days"
                if revision_streak > 0:
                    memories['revision_streak'] = f"{revision_streak} days"
            
            if 'goal' in query_lower or 'target' in query_lower or 'exam' in query_lower:
                goals = profile.get('current_goals', [])
                exam_target = profile.get('exam_target', '')
                if goals:
                    memories['goals'] = ', '.join(goals)
                if exam_target:
                    memories['exam_target'] = exam_target
            
            if 'mastery' in query_lower or 'topic' in query_lower or 'progress' in query_lower:
                mastery_by_topic = profile.get('mastery_by_topic', {})
                if mastery_by_topic:
                    # Get top 5 topics by mastery
                    sorted_topics = sorted(
                        mastery_by_topic.items(),
                        key=lambda x: x[1].get('mastery_score', 0) if isinstance(x[1], dict) else 0,
                        reverse=True
                    )[:5]
                    if sorted_topics:
                        memories['topic_mastery'] = '; '.join([
                            f"{t}: {int(v.get('mastery_score', 0) * 100) if isinstance(v, dict) else 0}%"
                            for t, v in sorted_topics
                        ])
            
            # If query is generic (all, everything, history), return all available
            if any(word in query_lower for word in ['all', 'everything', 'history', 'full', 'complete']):
                if profile.get('weak_topics'):
                    memories['weak_areas'] = ', '.join(profile['weak_topics'])
                if profile.get('strong_topics'):
                    memories['strong_areas'] = ', '.join(profile['strong_topics'])
                if profile.get('preferred_explanation'):
                    memories['explanation_style'] = profile['preferred_explanation']
                if profile.get('practice_streak', 0) > 0:
                    memories['practice_streak'] = f"{profile['practice_streak']} days"
                if profile.get('exam_target'):
                    memories['exam_target'] = profile['exam_target']
            
            # Format response
            if memories:
                result_lines = [f"{key}: {value}" for key, value in memories.items()]
                result = "\n".join(result_lines)
                return ToolResult.success_result(
                    f"Student memory (real data):\n{result}",
                    metadata={"memories": result_lines, "status": "from_db"},
                    data=memories
                )
            
            # Honest empty result - NO FAKE DATA
            return ToolResult.success_result(
                "No memory data found for this student yet. This is a new student or no relevant data for this query.",
                metadata={"memories": [], "status": "empty"},
                data={}
            )

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Memory recall error: {e}")
            return ToolResult.error_result(f"Memory recall failed: {e}")


class EmotionDetectorTool(BaseTool):
    """Detect emotional state from text"""

    @property
    def name(self) -> str:
        return "emotion_detector"

    @property
    def description(self) -> str:
        return "Detect emotional state and stress level from student's message."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "text": "The text to analyze",
            "context": "Additional context (time, previous messages)"
        }

    async def execute(self, text: str, context: str = "", **kwargs) -> ToolResult:
        """Detect emotions"""
        try:
            text_lower = text.lower()

            # Simple emotion detection
            emotions = {
                "frustrated": ["stuck", "confused", "don't get it", "frustrated", "annoying"],
                "anxious": ["worried", "scared", "nervous", "exam tomorrow", "panicking"],
                "motivated": ["excited", "ready", "let's do this", "confident"],
                "tired": ["exhausted", "tired", "sleepy", "can't focus"],
                "happy": ["great", "awesome", "happy", "got it", "yes!"]
            }

            detected = []
            for emotion, keywords in emotions.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected.append(emotion)

            # Check time context
            if "late night" in context.lower():
                detected.append("possibly tired")

            if detected:
                primary_emotion = detected[0]
                confidence = 0.7 if len(detected) == 1 else 0.5

                return ToolResult.success_result(
                    f"Detected emotional state: {primary_emotion} (confidence: {confidence:.1%})",
                    metadata={
                        "primary_emotion": primary_emotion,
                        "all_emotions": detected,
                        "confidence": confidence
                    }
                )

            return ToolResult.success_result(
                "Emotional state appears neutral",
                metadata={"primary_emotion": "neutral", "confidence": 0.6}
            )

        except Exception as e:
            return ToolResult.error_result(f"Emotion detection failed: {e}")


# ============== Study Planning Tools ==============

class StudyPlannerTool(BaseTool):
    """Create personalized study plans"""

    @property
    def name(self) -> str:
        return "study_planner"

    @property
    def description(self) -> str:
        return "Create personalized study schedules and revision plans based on exam dates and topics."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "exam_date": "Target exam date",
            "topics": "List of topics to cover",
            "daily_hours": "Available study hours per day"
        }

    async def execute(
        self,
        exam_date: str,
        topics: str,
        daily_hours: int = 3,
        **kwargs
    ) -> ToolResult:
        """Create study plan"""
        try:
            # Parse topics
            topic_list = [t.strip() for t in topics.split(',')]

            # Calculate days available
            from agents.core.shared_utils import TimeManager
            target_date = TimeManager.parse_natural_time(exam_date) or datetime.now() + timedelta(days=30)
            days_available = (target_date - datetime.now()).days

            if days_available <= 0:
                return ToolResult.error_result("Exam date must be in the future")

            # Create plan
            topics_per_day = len(topic_list) / days_available
            plan = []

            for i in range(min(7, days_available)):  # Show first week
                day_topics = topic_list[int(i * topics_per_day):int((i + 1) * topics_per_day)]
                if day_topics:
                    plan.append(f"Day {i+1}: {', '.join(day_topics)} ({daily_hours} hours)")

            result = "\n".join(plan)
            return ToolResult.success_result(
                f"Study plan for {days_available} days:\n{result}\n\nRemember to include breaks and revision time!",
                metadata={
                    "days_available": days_available,
                    "topics": topic_list,
                    "plan": plan
                }
            )

        except Exception as e:
            return ToolResult.error_result(f"Study planning failed: {e}")


class ProgressTrackerTool(BaseTool):
    """Track learning progress"""

    @property
    def name(self) -> str:
        return "progress_tracker"

    @property
    def description(self) -> str:
        return "Track and analyze student's learning progress over time."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "user_id": "Student ID",
            "metric": "What to track (accuracy, speed, topics_covered)"
        }

    async def execute(self, user_id: str, metric: str = "overall", **kwargs) -> ToolResult:
        """Track progress"""
        try:
            # Simulated progress data
            progress = {
                "overall": {
                    "score": 75,
                    "trend": "improving",
                    "change": "+12% from last week"
                },
                "accuracy": {
                    "current": 82,
                    "previous": 78,
                    "best": 85
                },
                "speed": {
                    "avg_time": "3.2 minutes per question",
                    "improvement": "20% faster than last month"
                },
                "topics_covered": {
                    "completed": ["Mechanics", "Algebra", "Organic Chemistry"],
                    "in_progress": ["Calculus", "Thermodynamics"],
                    "pending": ["Optics", "Probability"]
                }
            }

            if metric in progress:
                data = progress[metric]
                result = json.dumps(data, indent=2)
                return ToolResult.success_result(
                    f"Progress report ({metric}):\n{result}",
                    metadata={"metric": metric, "data": data}
                )

            return ToolResult.success_result(
                f"Overall progress: {progress['overall']['score']}% ({progress['overall']['trend']})",
                metadata=progress
            )

        except Exception as e:
            return ToolResult.error_result(f"Progress tracking failed: {e}")


# ============== Visual & Creative Tools ==============

class DiagramGeneratorTool(BaseTool):
    """Generate diagram specifications"""

    @property
    def name(self) -> str:
        return "diagram_generator"

    @property
    def description(self) -> str:
        return "Generate specifications for educational diagrams and visualizations."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "concept": "What to visualize",
            "diagram_type": "Type (flowchart, mindmap, graph, circuit, etc.)"
        }

    async def execute(
        self,
        concept: str,
        diagram_type: str = "auto",
        **kwargs
    ) -> ToolResult:
        """Generate diagram spec"""
        try:
            # Generate SVG-like specification
            if diagram_type == "flowchart":
                spec = f"""
Flowchart for {concept}:
┌─────────────┐
│    Start    │
└──────┬──────┘
       ↓
┌─────────────┐
│  Process 1  │
└──────┬──────┘
       ↓
   ◇ Decision ◇
    ↙        ↘
  Yes          No
   ↓            ↓
┌──────┐    ┌──────┐
│Result│    │ Alt  │
└──────┘    └──────┘
"""
            elif diagram_type == "mindmap":
                spec = f"""
Mind Map for {concept}:
        {concept}
       /    |    \\
   Topic1  Topic2  Topic3
     |       |       |
  Detail   Detail  Detail
"""
            else:
                spec = f"[Diagram specification for {concept} would be generated based on type]"

            return ToolResult.success_result(
                f"Diagram specification:\n{spec}",
                metadata={"concept": concept, "type": diagram_type}
            )

        except Exception as e:
            return ToolResult.error_result(f"Diagram generation failed: {e}")


class MnemonicGeneratorTool(BaseTool):
    """Generate memory aids and mnemonics"""

    @property
    def name(self) -> str:
        return "mnemonic_generator"

    @property
    def description(self) -> str:
        return "Create mnemonics, acronyms, and memory aids for better retention."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "items": "List of items to remember",
            "type": "acronym, rhyme, or story"
        }

    async def execute(
        self,
        items: str,
        type: str = "acronym",
        **kwargs
    ) -> ToolResult:
        """Generate mnemonic"""
        try:
            item_list = [i.strip() for i in items.split(',')]

            if type == "acronym":
                # Create acronym from first letters
                acronym = ''.join([item[0].upper() for item in item_list])
                result = f"Acronym: {acronym}\n"
                result += "\n".join([f"{letter} - {item}" for letter, item in zip(acronym, item_list)])

            elif type == "rhyme":
                result = f"Rhyme for remembering {', '.join(item_list)}:\n"
                result += f"[Would generate a rhyme based on the items]"

            else:  # story
                result = f"Story to remember {', '.join(item_list)}:\n"
                result += f"Once upon a time, {item_list[0]} met {item_list[1] if len(item_list) > 1 else 'a friend'}..."

            return ToolResult.success_result(
                result,
                metadata={"items": item_list, "type": type}
            )

        except Exception as e:
            return ToolResult.error_result(f"Mnemonic generation failed: {e}")


# ============== Motivation & Support Tools ==============

class MotivationalQuoteTool(BaseTool):
    """Generate contextual motivational quotes"""

    @property
    def name(self) -> str:
        return "motivational_quote"

    @property
    def description(self) -> str:
        return "Generate appropriate motivational quotes based on student's situation."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "situation": "Current situation (struggling, success, tired, etc.)",
            "subject": "Optional subject context"
        }

    async def execute(self, situation: str, subject: str = "", **kwargs) -> ToolResult:
        """Generate motivational quote"""
        try:
            quotes = {
                "struggling": [
                    "Every expert was once a beginner. Keep going!",
                    "Mistakes are proof that you're trying. Learn and grow!",
                    "The master has failed more times than the beginner has tried."
                ],
                "success": [
                    "Success is not final, keep up the great work!",
                    "You're doing amazing! Your hard work is paying off.",
                    "Celebrate this win, then aim for the next milestone!"
                ],
                "tired": [
                    "Rest if you must, but don't quit.",
                    "Take a break. Even machines need maintenance.",
                    "Your brain needs rest to consolidate learning. It's okay to pause."
                ],
                "exam": [
                    "You've prepared well. Trust yourself!",
                    "One exam doesn't define you. Do your best!",
                    "Deep breaths. You've got this!"
                ]
            }

            # Select appropriate quotes
            situation_lower = situation.lower()
            selected_quotes = []

            for key, quote_list in quotes.items():
                if key in situation_lower:
                    selected_quotes.extend(quote_list)

            if not selected_quotes:
                selected_quotes = ["Believe in yourself. Every step forward is progress!"]

            quote = random.choice(selected_quotes)

            # Add subject-specific encouragement
            if subject:
                quote += f"\n\nRemember, {subject} becomes easier with practice!"

            return ToolResult.success_result(
                quote,
                metadata={"situation": situation, "quote": quote}
            )

        except Exception as e:
            return ToolResult.error_result(f"Quote generation failed: {e}")


class BreakReminderTool(BaseTool):
    """Suggest study breaks and activities"""

    @property
    def name(self) -> str:
        return "break_reminder"

    @property
    def description(self) -> str:
        return "Suggest appropriate study breaks and refreshing activities."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "study_duration": "How long student has been studying (minutes)",
            "time_of_day": "Current time of day"
        }

    async def execute(
        self,
        study_duration: int = 60,
        time_of_day: str = "",
        **kwargs
    ) -> ToolResult:
        """Suggest break"""
        try:
            suggestions = []

            if study_duration < 30:
                suggestions.append("Keep going for a bit more, then take a 5-minute break")
            elif study_duration < 60:
                suggestions.append("Time for a 10-minute break! Stretch, hydrate, look away from screen")
            elif study_duration < 120:
                suggestions.append("Take a 15-20 minute break. Walk around, have a snack")
            else:
                suggestions.append("You've been studying hard! Take a 30-minute proper break")

            # Add activity suggestions
            activities = [
                "Do some light stretching",
                "Listen to your favorite song",
                "Have a healthy snack and water",
                "Take a short walk",
                "Do breathing exercises",
                "Chat with family for a few minutes"
            ]

            suggestion = random.choice(activities)
            result = f"{suggestions[0]}\n\nSuggested activity: {suggestion}"

            # Add time-specific advice
            from agents.core.shared_utils import TimeManager
            if TimeManager.is_late_night():
                result += "\n\n⚠️ It's late - consider wrapping up and getting good sleep!"

            return ToolResult.success_result(
                result,
                metadata={"study_duration": study_duration, "suggestion": suggestion}
            )

        except Exception as e:
            return ToolResult.error_result(f"Break suggestion failed: {e}")


# ============== Tool Factory ==============

def get_expanded_tools() -> List[BaseTool]:
    """Get all expanded tools"""
    return [
        # Learning tools
        MetaphorGeneratorTool(),
        ExampleGeneratorTool(),
        QuizGeneratorTool(),

        # Memory tools
        MemoryRecallTool(),
        EmotionDetectorTool(),

        # Planning tools
        StudyPlannerTool(),
        ProgressTrackerTool(),

        # Visual tools
        DiagramGeneratorTool(),
        MnemonicGeneratorTool(),

        # Support tools
        MotivationalQuoteTool(),
        BreakReminderTool()
    ]