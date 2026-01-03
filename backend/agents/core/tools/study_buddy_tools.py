"""
🎯 Study Buddy Tools - Interactive Learning Companion Tools
============================================================

Tools specifically designed for StudyBuddyAgent to enable TRUE agentic behavior:
- QuizGeneratorTool: Generate practice questions by topic + difficulty
- PracticeTrackerTool: Track practice outcomes, streaks, mastery deltas
- SpacedRepetitionTool: Schedule next practice based on performance
- FlashcardGeneratorTool: Generate flashcards for quick revision

These tools enable StudyBuddy to:
1. Generate adaptive content (not just prompts)
2. Track real progress in database
3. Provide personalized recommendations
4. Build spaced repetition schedules
"""

import logging
import json
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from agents.core.tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


# =============================================================================
# QUIZ GENERATOR TOOL
# =============================================================================

class QuizGeneratorTool(BaseTool):
    """
    Generates practice questions based on topic, difficulty, and student history.
    
    Uses structured question generation with:
    - Difficulty scaling (easy/medium/hard)
    - Topic-specific question patterns
    - Student performance-aware selection
    """
    
    @property
    def name(self) -> str:
        return "quiz_generator"
    
    @property
    def description(self) -> str:
        return (
            "Generate practice quiz questions for a given topic and difficulty level. "
            "Use this tool when student wants to be quizzed, tested, or practice questions. "
            "Returns structured questions with options and correct answers for verification."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "topic": "Topic to generate questions for (e.g., 'Friction', 'Photosynthesis')",
            "difficulty": "Difficulty level: 'easy', 'medium', 'hard' (default: medium)",
            "question_count": "Number of questions to generate (default: 3, max: 10)",
            "question_type": "Type: 'mcq', 'true_false', 'fill_blank', 'mixed' (default: mcq)"
        }
    
    # Topic-specific question templates for structured generation
    QUESTION_TEMPLATES = {
        "physics": {
            "mcq": [
                {"stem": "What is the SI unit of {concept}?", "concepts": ["force", "energy", "power", "momentum"]},
                {"stem": "Which law describes {phenomenon}?", "concepts": ["inertia", "action-reaction", "gravitation"]},
                {"stem": "In {scenario}, what happens to {variable}?", "concepts": ["projectile motion", "circular motion"]},
            ],
            "true_false": [
                {"stem": "{concept} is a scalar quantity.", "concepts": ["speed", "velocity", "acceleration", "force"]},
                {"stem": "The formula for {concept} is {formula}.", "concepts": ["kinetic energy", "potential energy"]},
            ]
        },
        "chemistry": {
            "mcq": [
                {"stem": "What is the molecular formula of {compound}?", "concepts": ["water", "glucose", "methane"]},
                {"stem": "Which type of bond is present in {compound}?", "concepts": ["NaCl", "H2O", "CO2"]},
            ]
        },
        "biology": {
            "mcq": [
                {"stem": "Which organelle is responsible for {function}?", "concepts": ["respiration", "protein synthesis", "photosynthesis"]},
                {"stem": "The process of {process} occurs in the {location}.", "concepts": ["glycolysis", "Krebs cycle"]},
            ]
        },
        "mathematics": {
            "mcq": [
                {"stem": "What is the derivative of {function}?", "concepts": ["sin x", "cos x", "e^x", "ln x"]},
                {"stem": "Solve: {equation}", "concepts": ["quadratic", "linear", "polynomial"]},
            ]
        }
    }
    
    async def execute(
        self,
        topic: str = "",
        difficulty: str = "medium",
        question_count: int = 3,
        question_type: str = "mcq",
        context: Dict = None,
        **kwargs
    ) -> ToolResult:
        """
        Generate quiz questions for the given topic.
        
        Returns structured quiz data that can be verified and tracked.
        """
        try:
            if not topic:
                return ToolResult.error_result("Topic is required for quiz generation")
            
            # Normalize inputs
            difficulty = difficulty.lower() if difficulty else "medium"
            if difficulty not in ["easy", "medium", "hard"]:
                difficulty = "medium"
            
            question_count = min(max(int(question_count or 3), 1), 10)
            question_type = question_type.lower() if question_type else "mcq"
            
            # Get student context for adaptive generation
            student_profile = (context or {}).get('student_profile', {})
            student_level = student_profile.get('mastery_level', 50)
            weak_topics = student_profile.get('weak_topics', [])
            
            # Adjust difficulty based on student level
            if student_level < 30:
                adjusted_difficulty = "easy" if difficulty == "medium" else difficulty
            elif student_level > 70:
                adjusted_difficulty = "hard" if difficulty == "medium" else difficulty
            else:
                adjusted_difficulty = difficulty
            
            logger.info(f"🎯 [QuizGenerator] Generating {question_count} {adjusted_difficulty} {question_type} questions for '{topic}'")
            
            # Generate questions using LLM
            questions = await self._generate_questions_llm(
                topic=topic,
                difficulty=adjusted_difficulty,
                question_count=question_count,
                question_type=question_type,
                context=context
            )
            
            # Format output
            quiz_data = {
                "topic": topic,
                "difficulty": adjusted_difficulty,
                "question_count": len(questions),
                "question_type": question_type,
                "questions": questions,
                "generated_at": datetime.utcnow().isoformat(),
                "student_level_adjusted": student_level != 50
            }
            
            # Create formatted display for student
            display_text = self._format_quiz_display(questions, topic, adjusted_difficulty)
            
            logger.info(f"✅ [QuizGenerator] Generated {len(questions)} questions for '{topic}'")
            
            return ToolResult.success_result(
                display_text,
                metadata=quiz_data
            )
            
        except Exception as e:
            logger.error(f"❌ [QuizGenerator] Error: {e}", exc_info=True)
            return ToolResult.error_result(f"Failed to generate quiz: {str(e)}")
    
    async def _generate_questions_llm(
        self,
        topic: str,
        difficulty: str,
        question_count: int,
        question_type: str,
        context: Dict
    ) -> List[Dict]:
        """Generate questions using LLM for variety and accuracy"""
        import os
        from services.llm_service import call_llm
        
        api_key = os.environ.get('OPENAI_API_KEY')
        
        difficulty_guide = {
            "easy": "Basic recall, direct from textbook, single-step",
            "medium": "Application-based, requires understanding, 2-3 steps",
            "hard": "Analysis/synthesis, tricky options, multi-concept"
        }
        
        type_guide = {
            "mcq": "Multiple choice with 4 options (A, B, C, D)",
            "true_false": "True or False statements",
            "fill_blank": "Fill in the blank with one word/phrase",
            "mixed": "Mix of MCQ, True/False, and Fill in the blank"
        }
        
        prompt = f"""Generate {question_count} practice questions for Indian students on:

**Topic:** {topic}
**Difficulty:** {difficulty} - {difficulty_guide.get(difficulty, '')}
**Type:** {question_type} - {type_guide.get(question_type, '')}

STRICT FORMAT (JSON array):
[
  {{
    "question": "Question text here",
    "type": "mcq" | "true_false" | "fill_blank",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."] (for MCQ only),
    "correct_answer": "A" | "True" | "word/phrase",
    "explanation": "Brief explanation of why this is correct",
    "difficulty": "{difficulty}",
    "concept": "Specific concept being tested"
  }}
]

RULES:
- Questions must be exam-relevant (JEE/NEET/CBSE level)
- Options should have plausible distractors
- Include brief explanation for learning
- Return ONLY valid JSON array, no markdown

Generate exactly {question_count} questions:"""

        try:
            response = await call_llm(
                prompt=prompt,
                api_key=api_key,
                temperature=0.7,
                max_tokens=2000,
                model="gpt-4o-mini"
            )
            
            # Parse JSON response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            questions = json.loads(response)
            
            # Validate and clean questions
            valid_questions = []
            for q in questions:
                if isinstance(q, dict) and "question" in q:
                    q["id"] = len(valid_questions) + 1
                    valid_questions.append(q)
            
            return valid_questions[:question_count]
            
        except Exception as e:
            logger.warning(f"LLM quiz generation failed: {e}, using fallback")
            # Fallback to simple template
            return [{
                "id": 1,
                "question": f"This is a practice question about {topic}. Please solve or answer.",
                "type": question_type,
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"] if question_type == "mcq" else None,
                "correct_answer": "A",
                "explanation": f"This tests your understanding of {topic}.",
                "difficulty": difficulty,
                "concept": topic
            }]
    
    def _format_quiz_display(self, questions: List[Dict], topic: str, difficulty: str) -> str:
        """Format questions for display to student"""
        emoji_map = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
        
        lines = [
            f"## 📝 Quiz: {topic.title()}",
            f"**Difficulty:** {emoji_map.get(difficulty, '🟡')} {difficulty.title()}",
            f"**Questions:** {len(questions)}",
            "",
            "---",
            ""
        ]
        
        for i, q in enumerate(questions, 1):
            lines.append(f"### Question {i}")
            lines.append(q.get("question", ""))
            
            if q.get("type") == "mcq" and q.get("options"):
                lines.append("")
                for opt in q["options"]:
                    lines.append(f"  {opt}")
            elif q.get("type") == "true_false":
                lines.append("\n**True** or **False**?")
            elif q.get("type") == "fill_blank":
                lines.append("\n*Fill in the blank*")
            
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "Take your time! Let me know your answers and I'll check them. 💪"
        ])
        
        return "\n".join(lines)


# =============================================================================
# PRACTICE TRACKER TOOL
# =============================================================================

class PracticeTrackerTool(BaseTool):
    """
    Tracks practice outcomes, updates streaks, and calculates mastery deltas.
    
    Enables:
    - Recording quiz/practice results
    - Tracking streaks and consistency
    - Calculating topic mastery changes
    - Identifying topics needing review
    """
    
    @property
    def name(self) -> str:
        return "practice_tracker"
    
    @property
    def description(self) -> str:
        return (
            "Track and record practice session outcomes. Use this tool after student "
            "completes a quiz or practice session to record results, update streaks, "
            "and identify areas needing more practice. Returns progress summary."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "user_id": "User ID to track progress for",
            "topic": "Topic practiced",
            "questions_attempted": "Number of questions attempted",
            "questions_correct": "Number of correct answers",
            "time_spent_minutes": "Time spent on practice (minutes)",
            "difficulty": "Difficulty level: 'easy', 'medium', 'hard'",
            "action": "Action: 'record' (save results), 'get_summary' (get progress), 'get_recommendations'"
        }
    
    async def execute(
        self,
        user_id: str = "",
        topic: str = "",
        questions_attempted: int = 0,
        questions_correct: int = 0,
        time_spent_minutes: int = 0,
        difficulty: str = "medium",
        action: str = "record",
        context: Dict = None,
        **kwargs
    ) -> ToolResult:
        """Execute practice tracking action"""
        try:
            context = context or {}
            db = context.get('db')
            
            if action == "get_summary":
                return await self._get_progress_summary(user_id, db, context)
            elif action == "get_recommendations":
                return await self._get_recommendations(user_id, db, context)
            else:  # record
                return await self._record_practice(
                    user_id, topic, questions_attempted, questions_correct,
                    time_spent_minutes, difficulty, db, context
                )
                
        except Exception as e:
            logger.error(f"❌ [PracticeTracker] Error: {e}", exc_info=True)
            return ToolResult.error_result(f"Tracking failed: {str(e)}")
    
    async def _record_practice(
        self,
        user_id: str,
        topic: str,
        attempted: int,
        correct: int,
        time_minutes: int,
        difficulty: str,
        db,
        context: Dict
    ) -> ToolResult:
        """Record a practice session"""
        
        # Calculate accuracy
        accuracy = (correct / attempted * 100) if attempted > 0 else 0
        
        # Calculate mastery delta (simplified formula)
        difficulty_multiplier = {"easy": 0.5, "medium": 1.0, "hard": 1.5}.get(difficulty, 1.0)
        mastery_delta = (accuracy - 50) * difficulty_multiplier * 0.1  # Scale to reasonable delta
        
        # Create session record
        session_record = {
            "user_id": user_id,
            "topic": topic,
            "questions_attempted": attempted,
            "questions_correct": correct,
            "accuracy": accuracy,
            "time_spent_minutes": time_minutes,
            "difficulty": difficulty,
            "mastery_delta": mastery_delta,
            "recorded_at": datetime.utcnow().isoformat(),
            "session_type": "practice"
        }
        
        # Try to save to database
        if db is not None:
            try:
                await db.practice_sessions.insert_one(session_record)
                logger.info(f"📊 [PracticeTracker] Recorded session for {user_id}: {topic}")
            except Exception as db_error:
                logger.warning(f"DB save failed (non-critical): {db_error}")
        
        # Generate feedback
        if accuracy >= 80:
            feedback = f"🎉 Excellent! {correct}/{attempted} correct ({accuracy:.0f}%). You're mastering {topic}!"
            recommendation = "Ready for harder questions or new topic."
        elif accuracy >= 60:
            feedback = f"👍 Good job! {correct}/{attempted} correct ({accuracy:.0f}%). Keep practicing {topic}."
            recommendation = "Review the questions you got wrong, then try again."
        else:
            feedback = f"📚 {correct}/{attempted} correct ({accuracy:.0f}%). {topic} needs more practice."
            recommendation = "Let's review the basics before more questions."
        
        summary = f"""## 📊 Practice Session Results

**Topic:** {topic}
**Difficulty:** {difficulty.title()}
**Score:** {correct}/{attempted} ({accuracy:.0f}%)
**Time:** {time_minutes} minutes

{feedback}

**Recommendation:** {recommendation}

**Mastery Change:** {'+' if mastery_delta > 0 else ''}{mastery_delta:.1f}%
"""
        
        return ToolResult.success_result(
            summary,
            metadata={
                "accuracy": accuracy,
                "mastery_delta": mastery_delta,
                "topic": topic,
                "needs_review": accuracy < 60
            }
        )
    
    async def _get_progress_summary(self, user_id: str, db, context: Dict) -> ToolResult:
        """Get overall progress summary for user"""
        
        # Try to fetch from database
        sessions = []
        if db is not None:
            try:
                cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
                cursor = db.practice_sessions.find({
                    "user_id": user_id,
                    "recorded_at": {"$gte": cutoff}
                })
                sessions = await cursor.to_list(length=100)
            except:
                pass
        
        if not sessions:
            return ToolResult.success_result(
                "No practice sessions recorded yet. Let's start practicing! 📚",
                metadata={"has_data": False}
            )
        
        # Calculate stats
        total_questions = sum(s.get("questions_attempted", 0) for s in sessions)
        total_correct = sum(s.get("questions_correct", 0) for s in sessions)
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Topic breakdown
        topics = {}
        for s in sessions:
            topic = s.get("topic", "Unknown")
            if topic not in topics:
                topics[topic] = {"attempted": 0, "correct": 0}
            topics[topic]["attempted"] += s.get("questions_attempted", 0)
            topics[topic]["correct"] += s.get("questions_correct", 0)
        
        # Identify weak topics
        weak_topics = [
            t for t, d in topics.items()
            if d["attempted"] > 0 and (d["correct"] / d["attempted"] * 100) < 60
        ]
        
        summary = f"""## 📈 Your Progress Summary (Last 30 Days)

**Total Sessions:** {len(sessions)}
**Questions Practiced:** {total_questions}
**Overall Accuracy:** {overall_accuracy:.0f}%

### Topic Breakdown
"""
        for topic, data in sorted(topics.items(), key=lambda x: x[1]["correct"]/max(x[1]["attempted"],1)):
            acc = (data["correct"] / data["attempted"] * 100) if data["attempted"] > 0 else 0
            emoji = "🟢" if acc >= 70 else "🟡" if acc >= 50 else "🔴"
            summary += f"- {emoji} **{topic}**: {acc:.0f}% ({data['correct']}/{data['attempted']})\n"
        
        if weak_topics:
            summary += f"\n### 🎯 Focus Areas\nTopics needing more practice: {', '.join(weak_topics)}"
        
        return ToolResult.success_result(
            summary,
            metadata={"has_data": True, "weak_topics": weak_topics, "overall_accuracy": overall_accuracy}
        )
    
    async def _get_recommendations(self, user_id: str, db, context: Dict) -> ToolResult:
        """Get personalized practice recommendations"""
        
        # Get progress summary first
        summary_result = await self._get_progress_summary(user_id, db, context)
        weak_topics = summary_result.metadata.get("weak_topics", []) if summary_result.metadata else []
        accuracy = summary_result.metadata.get("overall_accuracy", 50) if summary_result.metadata else 50
        
        recommendations = ["## 🎯 Your Personalized Practice Plan\n"]
        
        if weak_topics:
            recommendations.append("### Priority Topics (Need Practice)")
            for topic in weak_topics[:3]:
                recommendations.append(f"- 📚 **{topic}** - Start with easy questions, then medium")
        
        if accuracy >= 70:
            recommendations.append("\n### Next Steps")
            recommendations.append("- ⬆️ Try harder difficulty questions")
            recommendations.append("- 🎯 Focus on time management")
            recommendations.append("- 📝 Attempt mixed topic quizzes")
        elif accuracy >= 50:
            recommendations.append("\n### Next Steps")
            recommendations.append("- 📖 Review concepts for weak topics")
            recommendations.append("- 🔄 Practice same difficulty until 70%+")
            recommendations.append("- ⏰ Take your time, accuracy > speed")
        else:
            recommendations.append("\n### Next Steps")
            recommendations.append("- 📚 Start with NCERT basics")
            recommendations.append("- 🟢 Begin with easy questions only")
            recommendations.append("- 💬 Ask for explanations when confused")
        
        return ToolResult.success_result(
            "\n".join(recommendations),
            metadata={"weak_topics": weak_topics, "current_level": accuracy}
        )


# =============================================================================
# SPACED REPETITION TOOL
# =============================================================================

class SpacedRepetitionTool(BaseTool):
    """
    Implements spaced repetition scheduling for optimal retention.
    
    Uses SM-2 inspired algorithm to:
    - Calculate optimal review intervals
    - Schedule next practice sessions
    - Track retention estimates
    """
    
    @property
    def name(self) -> str:
        return "spaced_repetition"
    
    @property
    def description(self) -> str:
        return (
            "Schedule spaced repetition reviews for topics. Use this tool to determine "
            "when a topic should be reviewed next based on past performance. "
            "Helps with long-term retention through scientifically-backed scheduling."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "topic": "Topic to schedule review for",
            "last_accuracy": "Accuracy in last practice (0-100)",
            "days_since_last_practice": "Days since last practiced",
            "action": "Action: 'schedule' (get next review date), 'get_due' (topics due for review)"
        }
    
    # SM-2 inspired intervals (simplified)
    BASE_INTERVALS = [1, 3, 7, 14, 30, 60]  # Days
    
    async def execute(
        self,
        topic: str = "",
        last_accuracy: float = 50,
        days_since_last_practice: int = 0,
        action: str = "schedule",
        context: Dict = None,
        **kwargs
    ) -> ToolResult:
        """Execute spaced repetition scheduling"""
        try:
            if action == "get_due":
                return await self._get_due_topics(context)
            else:  # schedule
                return self._calculate_next_review(topic, last_accuracy, days_since_last_practice)
                
        except Exception as e:
            logger.error(f"❌ [SpacedRepetition] Error: {e}", exc_info=True)
            return ToolResult.error_result(f"Scheduling failed: {str(e)}")
    
    def _calculate_next_review(self, topic: str, accuracy: float, days_since: int) -> ToolResult:
        """Calculate when topic should be reviewed next"""
        
        # Ease factor based on accuracy (SM-2 inspired)
        if accuracy >= 90:
            ease = 2.5
            quality = "excellent"
        elif accuracy >= 70:
            ease = 2.0
            quality = "good"
        elif accuracy >= 50:
            ease = 1.5
            quality = "fair"
        else:
            ease = 1.0
            quality = "needs work"
        
        # Determine current interval index based on days since
        current_idx = 0
        for i, interval in enumerate(self.BASE_INTERVALS):
            if days_since >= interval:
                current_idx = i + 1
        current_idx = min(current_idx, len(self.BASE_INTERVALS) - 1)
        
        # Calculate next interval
        if accuracy < 50:
            # Reset to beginning if struggling
            next_interval = self.BASE_INTERVALS[0]
            current_idx = 0
        else:
            # Progress to next interval, modified by ease
            next_idx = min(current_idx + 1, len(self.BASE_INTERVALS) - 1)
            next_interval = int(self.BASE_INTERVALS[next_idx] * ease)
        
        next_date = datetime.now() + timedelta(days=next_interval)
        
        summary = f"""## 📅 Spaced Repetition Schedule: {topic}

**Last Performance:** {accuracy:.0f}% ({quality})
**Days Since Last Practice:** {days_since}

### Next Review
- **Recommended Date:** {next_date.strftime('%A, %B %d')}
- **Days from Now:** {next_interval}
- **Retention Estimate:** {min(95, accuracy + 10):.0f}% (if reviewed on time)

### Why This Schedule?
{"Great performance! Interval extended for efficient learning." if accuracy >= 70 else "More frequent reviews will help solidify this topic." if accuracy >= 50 else "Let's review soon to strengthen your understanding."}
"""
        
        return ToolResult.success_result(
            summary,
            metadata={
                "next_review_days": next_interval,
                "next_review_date": next_date.isoformat(),
                "quality": quality,
                "topic": topic
            }
        )
    
    async def _get_due_topics(self, context: Dict) -> ToolResult:
        """Get list of topics due for review"""
        context = context or {}
        db = context.get('db')
        user_id = context.get('user_id', '')
        
        due_topics = []
        
        # Try to get from database
        if db is not None:
            try:
                # Get recent practice sessions
                sessions = await db.practice_sessions.find({
                    "user_id": user_id
                }).sort("recorded_at", -1).to_list(length=50)
                
                # Group by topic and find due reviews
                topic_last_practice = {}
                for s in sessions:
                    topic = s.get("topic")
                    if topic and topic not in topic_last_practice:
                        topic_last_practice[topic] = {
                            "last_date": s.get("recorded_at"),
                            "last_accuracy": s.get("accuracy", 50)
                        }
                
                now = datetime.utcnow()
                for topic, data in topic_last_practice.items():
                    try:
                        last_date = datetime.fromisoformat(data["last_date"].replace('Z', '+00:00'))
                        days_since = (now - last_date).days
                        
                        # Simple due check: accuracy determines interval
                        accuracy = data["last_accuracy"]
                        if accuracy >= 80 and days_since > 14:
                            due_topics.append({"topic": topic, "days_overdue": days_since - 14, "priority": "low"})
                        elif accuracy >= 50 and days_since > 7:
                            due_topics.append({"topic": topic, "days_overdue": days_since - 7, "priority": "medium"})
                        elif accuracy < 50 and days_since > 3:
                            due_topics.append({"topic": topic, "days_overdue": days_since - 3, "priority": "high"})
                    except:
                        pass
                        
            except Exception as e:
                logger.warning(f"Failed to get due topics from DB: {e}")
        
        if not due_topics:
            return ToolResult.success_result(
                "✅ No topics are due for review right now! Keep up the good work.",
                metadata={"due_count": 0}
            )
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        due_topics.sort(key=lambda x: priority_order.get(x["priority"], 1))
        
        summary = "## 📚 Topics Due for Review\n\n"
        for item in due_topics:
            emoji = "🔴" if item["priority"] == "high" else "🟡" if item["priority"] == "medium" else "🟢"
            summary += f"- {emoji} **{item['topic']}** ({item['days_overdue']} days overdue)\n"
        
        summary += "\nWant me to quiz you on any of these topics?"
        
        return ToolResult.success_result(
            summary,
            metadata={"due_count": len(due_topics), "due_topics": due_topics}
        )


# =============================================================================
# FLASHCARD GENERATOR TOOL
# =============================================================================

class FlashcardGeneratorTool(BaseTool):
    """
    Generates flashcards for quick revision.
    
    Creates:
    - Term/Definition cards
    - Formula cards
    - Concept/Example cards
    """
    
    @property
    def name(self) -> str:
        return "flashcard_generator"
    
    @property
    def description(self) -> str:
        return (
            "Generate flashcards for quick revision of a topic. Use this tool when "
            "student wants flashcards, quick revision, or memory aids. "
            "Creates front/back card pairs for efficient studying."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "topic": "Topic to generate flashcards for",
            "card_count": "Number of flashcards (default: 5, max: 15)",
            "card_type": "Type: 'definition', 'formula', 'concept', 'mixed' (default: mixed)"
        }
    
    async def execute(
        self,
        topic: str = "",
        card_count: int = 5,
        card_type: str = "mixed",
        context: Dict = None,
        **kwargs
    ) -> ToolResult:
        """Generate flashcards for the topic"""
        try:
            if not topic:
                return ToolResult.error_result("Topic is required for flashcard generation")
            
            card_count = min(max(int(card_count or 5), 1), 15)
            
            logger.info(f"🎴 [FlashcardGenerator] Creating {card_count} flashcards for '{topic}'")
            
            # Generate flashcards using LLM
            cards = await self._generate_flashcards_llm(topic, card_count, card_type, context)
            
            # Format for display
            display = self._format_flashcards(cards, topic)
            
            return ToolResult.success_result(
                display,
                metadata={"cards": cards, "count": len(cards), "topic": topic}
            )
            
        except Exception as e:
            logger.error(f"❌ [FlashcardGenerator] Error: {e}", exc_info=True)
            return ToolResult.error_result(f"Failed to generate flashcards: {str(e)}")
    
    async def _generate_flashcards_llm(
        self,
        topic: str,
        count: int,
        card_type: str,
        context: Dict
    ) -> List[Dict]:
        """Generate flashcards using LLM"""
        import os
        from services.llm_service import call_llm
        
        api_key = os.environ.get('OPENAI_API_KEY')
        
        prompt = f"""Generate {count} flashcards for Indian students on: {topic}

Card type: {card_type}

STRICT FORMAT (JSON array):
[
  {{
    "front": "Question or term (what to recall)",
    "back": "Answer or definition (what to remember)",
    "type": "definition" | "formula" | "concept" | "example",
    "hint": "Optional memory hint"
  }}
]

RULES:
- Front should be a clear question or term
- Back should be concise but complete
- Include exam-relevant content (JEE/NEET/CBSE)
- Add memory hints where helpful
- Return ONLY valid JSON array

Generate exactly {count} flashcards:"""

        try:
            response = await call_llm(
                prompt=prompt,
                api_key=api_key,
                temperature=0.7,
                max_tokens=1500,
                model="gpt-4o-mini"
            )
            
            # Parse JSON
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            cards = json.loads(response)
            return cards[:count]
            
        except Exception as e:
            logger.warning(f"LLM flashcard generation failed: {e}")
            return [{"front": f"What is {topic}?", "back": f"Review your notes on {topic}", "type": "concept"}]
    
    def _format_flashcards(self, cards: List[Dict], topic: str) -> str:
        """Format flashcards for display"""
        lines = [
            f"## 🎴 Flashcards: {topic.title()}",
            f"**Cards Generated:** {len(cards)}",
            "",
            "*Reveal each answer when you're ready!*",
            "",
            "---",
            ""
        ]
        
        for i, card in enumerate(cards, 1):
            card_type = card.get("type", "concept")
            emoji = {"definition": "📖", "formula": "🔢", "concept": "💡", "example": "📝"}.get(card_type, "🎴")
            
            lines.append(f"### Card {i} {emoji}")
            lines.append(f"**Front:** {card.get('front', '')}")
            lines.append("")
            lines.append(f"<details><summary>🔍 Reveal Answer</summary>")
            lines.append("")
            lines.append(f"**Back:** {card.get('back', '')}")
            if card.get("hint"):
                lines.append(f"")
                lines.append(f"💡 *Hint: {card.get('hint')}*")
            lines.append("")
            lines.append("</details>")
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "Practice these cards regularly for best retention! 📚"
        ])
        
        return "\n".join(lines)


# =============================================================================
# TOOL EXPORTS
# =============================================================================

__all__ = [
    'QuizGeneratorTool',
    'PracticeTrackerTool',
    'SpacedRepetitionTool',
    'FlashcardGeneratorTool'
]
