"""
📚 Smart Study Planner Agent
============================

AI-powered daily study plan generator that combines:
- Spaced repetition due reviews
- Weak area focus sessions
- New topic introduction
- Break optimization based on Pomodoro principles
- Exam countdown urgency adjustment

This agent creates personalized, actionable daily study plans.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class StudyBlockType(str, Enum):
    """Types of study blocks"""
    REVISION = "revision"          # Spaced repetition reviews
    DEEP_FOCUS = "deep_focus"      # Weak area intensive practice
    NEW_LEARNING = "new_learning"  # New concept introduction
    PRACTICE = "practice"          # Problem solving
    BREAK = "break"                # Rest period
    QUICK_REVIEW = "quick_review"  # Flash review before sleep


class EnergyLevel(str, Enum):
    """Student energy levels throughout the day"""
    PEAK = "peak"           # Best for hard topics
    MODERATE = "moderate"   # Good for revision
    LOW = "low"             # Light review only


@dataclass
class StudyBlock:
    """A single study block in the plan"""
    block_type: StudyBlockType
    duration_minutes: int
    topic: str
    subject: str
    description: str
    tips: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    xp_reward: int = 0
    priority: int = 1  # 1 = highest
    
    def to_dict(self) -> Dict:
        return {
            "block_type": self.block_type.value,
            "duration_minutes": self.duration_minutes,
            "topic": self.topic,
            "subject": self.subject,
            "description": self.description,
            "tips": self.tips,
            "resources": self.resources,
            "xp_reward": self.xp_reward,
            "priority": self.priority
        }


@dataclass
class DailyStudyPlan:
    """Complete daily study plan"""
    date: str
    total_study_minutes: int
    total_break_minutes: int
    blocks: List[StudyBlock]
    daily_goals: List[str]
    motivational_quote: str
    streak_target: bool
    xp_target: int
    exam_countdown: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date,
            "total_study_minutes": self.total_study_minutes,
            "total_break_minutes": self.total_break_minutes,
            "blocks": [b.to_dict() for b in self.blocks],
            "daily_goals": self.daily_goals,
            "motivational_quote": self.motivational_quote,
            "streak_target": self.streak_target,
            "xp_target": self.xp_target,
            "exam_countdown": self.exam_countdown
        }


class StudyPlannerAgent:
    """
    🧠 Intelligent Study Planner Agent
    
    Generates personalized daily study plans based on:
    - Student's current mastery levels
    - Spaced repetition schedule
    - Weak areas that need focus
    - Available study time
    - Exam countdown urgency
    - Time of day optimization
    """
    
    def __init__(self, db=None):
        self.db = db
        self.default_study_hours = 4
        self.pomodoro_duration = 45  # minutes
        self.break_duration = 10     # minutes
        
        # Motivational quotes for Indian students
        self.quotes = [
            "सफलता वहीं मिलती है जहाँ मेहनत होती है। - APJ Abdul Kalam",
            "Small daily improvements lead to stunning results. Keep going!",
            "Today's preparation determines tomorrow's achievement.",
            "हर दिन एक नई शुरुआत है। Make it count! 🚀",
            "The expert in anything was once a beginner. You've got this!",
            "Focus on progress, not perfection. Every step counts.",
            "Your only competition is who you were yesterday.",
            "Dream big, start small, act now. - Robin Sharma",
            "Consistency beats intensity. Show up every day! 💪",
            "The pain of discipline is nothing compared to the pain of regret."
        ]
    
    async def generate_daily_plan(
        self,
        user_id: str,
        available_hours: Optional[float] = None,
        exam_date: Optional[datetime] = None,
        preferred_subjects: Optional[List[str]] = None,
        energy_pattern: str = "morning"  # morning, evening, or flexible
    ) -> DailyStudyPlan:
        """
        Generate a personalized daily study plan
        
        Args:
            user_id: Student's user ID
            available_hours: Hours available for study today
            exam_date: Target exam date for urgency calculation
            preferred_subjects: Subjects to focus on (optional)
            energy_pattern: When student is most alert
            
        Returns:
            DailyStudyPlan with optimized study blocks
        """
        
        study_hours = available_hours or self.default_study_hours
        study_minutes = int(study_hours * 60)
        
        # Get student data
        due_reviews = await self._get_due_reviews(user_id)
        weak_areas = await self._get_weak_areas(user_id)
        recent_topics = await self._get_recent_topics(user_id)
        user_prefs = await self._get_user_preferences(user_id)
        
        # Calculate exam urgency
        exam_countdown = None
        urgency_multiplier = 1.0
        if exam_date:
            days_to_exam = (exam_date - datetime.now(timezone.utc)).days
            exam_countdown = days_to_exam
            if days_to_exam <= 7:
                urgency_multiplier = 1.5  # Intense revision mode
            elif days_to_exam <= 30:
                urgency_multiplier = 1.2  # Focused preparation
        
        # Build study blocks
        blocks = []
        remaining_minutes = study_minutes
        
        # 1. Morning Revision Block (Spaced Repetition)
        if due_reviews and remaining_minutes >= 30:
            revision_duration = min(45, remaining_minutes // 4, len(due_reviews) * 5)
            revision_topics = due_reviews[:min(5, len(due_reviews))]
            
            blocks.append(StudyBlock(
                block_type=StudyBlockType.REVISION,
                duration_minutes=revision_duration,
                topic=", ".join([r.get("concept", "Review") for r in revision_topics[:3]]),
                subject=revision_topics[0].get("subject", "Mixed") if revision_topics else "Mixed",
                description="🔄 Spaced Repetition Review - Strengthen your memory!",
                tips=[
                    "Try to recall before looking at answers",
                    "Mark difficult concepts for extra review",
                    "Use active recall, not passive reading"
                ],
                xp_reward=revision_duration * 2,
                priority=1
            ))
            remaining_minutes -= revision_duration
            
            # Add break after revision
            if remaining_minutes >= 10:
                blocks.append(self._create_break_block(10, "revision"))
                remaining_minutes -= 10
        
        # 2. Deep Focus Block (Weak Areas)
        if weak_areas and remaining_minutes >= 45:
            weak_topic = weak_areas[0]
            focus_duration = min(60, remaining_minutes // 2)
            
            blocks.append(StudyBlock(
                block_type=StudyBlockType.DEEP_FOCUS,
                duration_minutes=focus_duration,
                topic=weak_topic.get("topic", "Focus Area"),
                subject=weak_topic.get("subject", "General"),
                description=f"🎯 Deep Focus Session - Master your weak area!",
                tips=[
                    f"Current mastery: {weak_topic.get('mastery', 0):.0%} - Let's improve!",
                    "Work through problems step by step",
                    "Don't skip the basics - they matter",
                    "Ask Sathi if you're stuck!"
                ],
                resources=[
                    f"Practice problems on {weak_topic.get('topic', 'this topic')}",
                    "Video explanations available"
                ],
                xp_reward=focus_duration * 3,
                priority=1
            ))
            remaining_minutes -= focus_duration
            
            # Add break
            if remaining_minutes >= 10:
                blocks.append(self._create_break_block(15, "deep_focus"))
                remaining_minutes -= 15
        
        # 3. New Learning Block
        if remaining_minutes >= 45:
            next_topic = await self._get_next_topic(user_id, preferred_subjects)
            learning_duration = min(45, remaining_minutes // 2)
            
            blocks.append(StudyBlock(
                block_type=StudyBlockType.NEW_LEARNING,
                duration_minutes=learning_duration,
                topic=next_topic.get("topic", "New Concept"),
                subject=next_topic.get("subject", "General"),
                description="📖 Learn Something New - Expand your knowledge!",
                tips=[
                    "Take notes in your own words",
                    "Create mind maps for complex topics",
                    "Connect new concepts to what you already know",
                    "Teach the concept to an imaginary student"
                ],
                xp_reward=learning_duration * 2,
                priority=2
            ))
            remaining_minutes -= learning_duration
            
            # Add break
            if remaining_minutes >= 10:
                blocks.append(self._create_break_block(10, "learning"))
                remaining_minutes -= 10
        
        # 4. Practice Block
        if remaining_minutes >= 30:
            practice_duration = min(45, remaining_minutes)
            practice_subject = preferred_subjects[0] if preferred_subjects else "Mixed"
            
            blocks.append(StudyBlock(
                block_type=StudyBlockType.PRACTICE,
                duration_minutes=practice_duration,
                topic="Problem Solving Practice",
                subject=practice_subject,
                description="✏️ Practice Session - Apply what you've learned!",
                tips=[
                    "Time yourself on each problem",
                    "Don't look at solutions too quickly",
                    "Review mistakes carefully",
                    "Try variations of problems you got wrong"
                ],
                xp_reward=practice_duration * 2,
                priority=2
            ))
            remaining_minutes -= practice_duration
        
        # 5. Quick Review (End of day)
        if remaining_minutes >= 15:
            blocks.append(StudyBlock(
                block_type=StudyBlockType.QUICK_REVIEW,
                duration_minutes=15,
                topic="Today's Summary",
                subject="All",
                description="🌙 Quick Review - Consolidate today's learning!",
                tips=[
                    "Recall 3 key things you learned today",
                    "Note down any pending doubts",
                    "Plan tomorrow's focus area"
                ],
                xp_reward=30,
                priority=3
            ))
        
        # Calculate totals
        total_study = sum(b.duration_minutes for b in blocks if b.block_type != StudyBlockType.BREAK)
        total_breaks = sum(b.duration_minutes for b in blocks if b.block_type == StudyBlockType.BREAK)
        total_xp = sum(b.xp_reward for b in blocks)
        
        # Generate daily goals
        daily_goals = self._generate_daily_goals(blocks, weak_areas, exam_countdown)
        
        # Select motivational quote
        import random
        quote = random.choice(self.quotes)
        
        plan = DailyStudyPlan(
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            total_study_minutes=total_study,
            total_break_minutes=total_breaks,
            blocks=blocks,
            daily_goals=daily_goals,
            motivational_quote=quote,
            streak_target=True,
            xp_target=total_xp,
            exam_countdown=exam_countdown
        )
        
        # Save plan to database
        await self._save_plan(user_id, plan)
        
        logger.info(f"📚 Generated study plan for {user_id}: {len(blocks)} blocks, {total_study} min study")
        
        return plan
    
    def _create_break_block(self, duration: int, after_block: str) -> StudyBlock:
        """Create an optimized break block"""
        
        break_tips = {
            "revision": [
                "Stretch your body",
                "Look at something far away (20-20-20 rule)",
                "Hydrate! Drink water 💧"
            ],
            "deep_focus": [
                "Take a short walk",
                "Do some light exercises",
                "Listen to your favorite song",
                "Have a healthy snack 🍎"
            ],
            "learning": [
                "Rest your eyes",
                "Quick meditation (2 min)",
                "Chat with family briefly"
            ]
        }
        
        return StudyBlock(
            block_type=StudyBlockType.BREAK,
            duration_minutes=duration,
            topic="Recharge Break",
            subject="Rest",
            description="☕ Take a mindful break - You've earned it!",
            tips=break_tips.get(after_block, ["Rest and recharge"]),
            xp_reward=5,
            priority=3
        )
    
    def _generate_daily_goals(
        self, 
        blocks: List[StudyBlock], 
        weak_areas: List[Dict],
        exam_countdown: Optional[int]
    ) -> List[str]:
        """Generate specific, achievable daily goals"""
        
        goals = []
        
        # Goal based on blocks
        revision_blocks = [b for b in blocks if b.block_type == StudyBlockType.REVISION]
        if revision_blocks:
            goals.append(f"✅ Complete {len(revision_blocks)} revision session(s)")
        
        focus_blocks = [b for b in blocks if b.block_type == StudyBlockType.DEEP_FOCUS]
        if focus_blocks:
            topic = focus_blocks[0].topic
            goals.append(f"🎯 Improve mastery in {topic}")
        
        learning_blocks = [b for b in blocks if b.block_type == StudyBlockType.NEW_LEARNING]
        if learning_blocks:
            goals.append(f"📖 Learn at least 1 new concept")
        
        practice_blocks = [b for b in blocks if b.block_type == StudyBlockType.PRACTICE]
        if practice_blocks:
            goals.append(f"✏️ Solve 10+ practice problems")
        
        # Urgency-based goal
        if exam_countdown and exam_countdown <= 30:
            goals.append(f"⏰ Exam in {exam_countdown} days - Stay focused!")
        
        # Streak goal
        goals.append("🔥 Maintain your study streak")
        
        return goals[:5]  # Max 5 goals
    
    async def _get_due_reviews(self, user_id: str) -> List[Dict]:
        """Get concepts due for spaced repetition review"""
        if not self.db:
            return []
        
        try:
            # Query spaced_repetition_items collection
            now = datetime.now(timezone.utc)
            cursor = self.db.spaced_repetition_items.find({
                "user_id": user_id,
                "next_review_at": {"$lte": now}
            }).sort("next_review_at", 1).limit(10)
            
            reviews = await cursor.to_list(length=10)
            return reviews
        except Exception as e:
            logger.error(f"Error getting due reviews: {e}")
            return []
    
    async def _get_weak_areas(self, user_id: str) -> List[Dict]:
        """Get student's weak areas from knowledge tracker"""
        if not self.db:
            return [{"topic": "Physics - Mechanics", "subject": "Physics", "mastery": 0.35}]
        
        try:
            # Query concept_knowledge collection for low mastery items
            cursor = self.db.concept_knowledge.find({
                "user_id": user_id,
                "mastery_level": {"$lt": 0.6}
            }).sort("mastery_level", 1).limit(5)
            
            weak = await cursor.to_list(length=5)
            
            if not weak:
                # Return default if no data
                return [{"topic": "Core Concepts", "subject": "General", "mastery": 0.5}]
            
            return [
                {
                    "topic": w.get("concept_name", "Unknown"),
                    "subject": w.get("subject", "General"),
                    "mastery": w.get("mastery_level", 0.5)
                }
                for w in weak
            ]
        except Exception as e:
            logger.error(f"Error getting weak areas: {e}")
            return [{"topic": "Practice Areas", "subject": "General", "mastery": 0.5}]
    
    async def _get_recent_topics(self, user_id: str) -> List[str]:
        """Get recently studied topics to avoid repetition"""
        if not self.db:
            return []
        
        try:
            # Query recent study sessions
            cursor = self.db.study_sessions.find({
                "user_id": user_id
            }).sort("created_at", -1).limit(5)
            
            sessions = await cursor.to_list(length=5)
            return [s.get("topic", "") for s in sessions if s.get("topic")]
        except Exception as e:
            logger.error(f"Error getting recent topics: {e}")
            return []
    
    async def _get_user_preferences(self, user_id: str) -> Dict:
        """Get user's study preferences"""
        if not self.db:
            return {"daily_study_hours": 4, "preferred_time": "morning"}
        
        try:
            user = await self.db.users.find_one({"user_id": user_id})
            return user.get("study_preferences", {}) if user else {}
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    async def _get_next_topic(self, user_id: str, preferred_subjects: Optional[List[str]] = None) -> Dict:
        """Determine the next topic to learn based on syllabus progression"""
        
        # Default topic suggestions based on common JEE/NEET curriculum
        default_topics = [
            {"topic": "Kinematics - Projectile Motion", "subject": "Physics"},
            {"topic": "Chemical Bonding", "subject": "Chemistry"},
            {"topic": "Calculus - Integration", "subject": "Mathematics"},
            {"topic": "Cell Biology", "subject": "Biology"},
            {"topic": "Thermodynamics", "subject": "Physics"},
            {"topic": "Organic Chemistry - Reactions", "subject": "Chemistry"}
        ]
        
        if preferred_subjects:
            # Filter by preferred subjects
            filtered = [t for t in default_topics if t["subject"] in preferred_subjects]
            if filtered:
                import random
                return random.choice(filtered)
        
        import random
        return random.choice(default_topics)
    
    async def _save_plan(self, user_id: str, plan: DailyStudyPlan) -> None:
        """Save the generated plan to database"""
        if not self.db:
            return
        
        try:
            plan_doc = {
                "user_id": user_id,
                "plan": plan.to_dict(),
                "created_at": datetime.now(timezone.utc),
                "status": "active"
            }
            
            # Upsert - replace today's plan if exists
            await self.db.daily_study_plans.update_one(
                {"user_id": user_id, "plan.date": plan.date},
                {"$set": plan_doc},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving study plan: {e}")
    
    async def get_today_plan(self, user_id: str) -> Optional[DailyStudyPlan]:
        """Get today's existing plan if available"""
        if not self.db:
            return None
        
        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            doc = await self.db.daily_study_plans.find_one({
                "user_id": user_id,
                "plan.date": today,
                "status": "active"
            })
            
            if doc and doc.get("plan"):
                return doc["plan"]
            return None
        except Exception as e:
            logger.error(f"Error getting today's plan: {e}")
            return None
    
    async def mark_block_complete(self, user_id: str, block_index: int) -> Dict:
        """Mark a study block as completed and award XP"""
        if not self.db:
            return {"success": False, "error": "Database not available"}
        
        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            # Get current plan
            doc = await self.db.daily_study_plans.find_one({
                "user_id": user_id,
                "plan.date": today
            })
            
            if not doc:
                return {"success": False, "error": "No plan found for today"}
            
            plan = doc.get("plan", {})
            blocks = plan.get("blocks", [])
            
            if block_index >= len(blocks):
                return {"success": False, "error": "Invalid block index"}
            
            # Mark as complete
            await self.db.daily_study_plans.update_one(
                {"_id": doc["_id"]},
                {"$set": {f"plan.blocks.{block_index}.completed": True}}
            )
            
            # Award XP
            xp_reward = blocks[block_index].get("xp_reward", 0)
            await self.db.user_progress.update_one(
                {"user_id": user_id},
                {"$inc": {"xp": xp_reward}},
                upsert=True
            )
            
            return {
                "success": True,
                "xp_awarded": xp_reward,
                "message": f"Great job! +{xp_reward} XP earned! 🎉"
            }
        except Exception as e:
            logger.error(f"Error marking block complete: {e}")
            return {"success": False, "error": str(e)}
