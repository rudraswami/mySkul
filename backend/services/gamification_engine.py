"""
🎮 DRUV AI Gamification Engine
================================
Makes learning addictive through:
- Micro-dopamine loops
- Streak system
- Adaptive difficulty
- XP & Leveling
- Personalized learning paths

Inspired by: Duolingo, Khan Academy, Snapchat
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)


# ============ ENUMS & CONSTANTS ============

class StudentLevel(Enum):
    """Student progression levels"""
    EXPLORER = 1      # 0-500 XP
    ANALYST = 2       # 500-1500 XP
    TACTICIAN = 3     # 1500-3500 XP
    SCIENTIST = 4     # 3500-7000 XP
    MASTER = 5        # 7000+ XP

class DifficultyLevel(Enum):
    """Adaptive difficulty levels"""
    BEGINNER = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5

class StreakType(Enum):
    """Types of streaks"""
    DAILY = "daily"
    WEEKLY = "weekly"
    SUBJECT = "subject"
    CONCEPT = "concept"

class BadgeType(Enum):
    """Achievement badge types"""
    # Streak badges
    FLAME_STARTER = "flame_starter"       # 3-day streak
    BLUE_STREAK = "blue_streak"           # 7-day streak
    GOLDEN_STREAK = "golden_streak"       # 30-day streak
    LEGENDARY_STREAK = "legendary_streak" # 100-day streak
    
    # Learning badges
    FIRST_QUESTION = "first_question"
    CONCEPT_CRUSHER = "concept_crusher"   # 10 concepts mastered
    SUBJECT_STAR = "subject_star"         # Subject completed
    SPEED_DEMON = "speed_demon"           # Fast correct answers
    DEEP_DIVER = "deep_diver"             # Asked follow-up questions
    
    # Special badges
    NIGHT_OWL = "night_owl"               # Studied after 10 PM
    EARLY_BIRD = "early_bird"             # Studied before 6 AM
    WEEKEND_WARRIOR = "weekend_warrior"   # Studied on weekend
    COMEBACK_KID = "comeback_kid"         # Returned after break


# ============ DATA CLASSES ============

@dataclass
class MicroReward:
    """Small dopamine hit for immediate feedback"""
    message: str
    emoji: str
    xp_earned: int
    celebration_type: str  # 'confetti', 'glow', 'shake', 'bounce', 'none'
    sound_effect: Optional[str] = None

@dataclass
class StreakData:
    """Student's streak information"""
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[str] = None
    streak_type: StreakType = StreakType.DAILY
    streak_frozen: bool = False
    freeze_count: int = 0

@dataclass
class StudentProgress:
    """Complete student progress tracking"""
    user_id: str
    total_xp: int = 0
    level: StudentLevel = StudentLevel.EXPLORER
    current_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    
    # Streaks
    daily_streak: int = 0
    longest_streak: int = 0
    last_activity: Optional[datetime] = None
    
    # Session stats
    questions_today: int = 0
    correct_today: int = 0
    time_spent_today: int = 0  # minutes
    
    # Performance tracking
    recent_accuracy: List[bool] = field(default_factory=list)  # Last 10 answers
    topic_mastery: Dict[str, float] = field(default_factory=dict)  # topic -> mastery %
    
    # Badges
    badges_earned: List[str] = field(default_factory=list)
    
    # Personalization
    preferred_analogies: List[str] = field(default_factory=list)  # cricket, cooking, etc.
    learning_style: str = "visual"  # visual, reading, kinesthetic
    study_time_preference: str = "evening"  # morning, afternoon, evening, night


# ============ MICRO-DOPAMINE SYSTEM ============

class MicroDopamineEngine:
    """
    Generates tiny wins and celebrations for every interaction.
    Makes students feel good about learning.
    """
    
    # Celebration messages by context
    CORRECT_ANSWER_MESSAGES = [
        ("🎉", "Boom! You nailed it!", "confetti"),
        ("⚡", "Lightning fast! That was perfect!", "glow"),
        ("🔥", "You're on fire! Keep going!", "shake"),
        ("✨", "Brilliant! You've got this!", "sparkle"),
        ("🚀", "Rocketing through! Amazing!", "bounce"),
        ("💪", "Strong answer! You're crushing it!", "pulse"),
        ("🧠", "Big brain energy! Correct!", "glow"),
        ("👏", "That's the way! Perfect!", "confetti"),
    ]
    
    UNDERSTANDING_MESSAGES = [
        ("💡", "Great! You understood that perfectly!", "glow"),
        ("🎯", "Spot on! You've got the concept!", "pulse"),
        ("✅", "Exactly right! Moving on!", "bounce"),
        ("🌟", "Star student moment! You got it!", "sparkle"),
    ]
    
    FAST_ANSWER_MESSAGES = [
        ("⚡", "Speed demon! That was quick!", "shake"),
        ("🏃", "Racing through! Impressive speed!", "bounce"),
        ("💨", "Whoosh! Fast and correct!", "glow"),
    ]
    
    STREAK_MESSAGES = {
        3: ("🔥", "3-day streak! You're building momentum!", "flame"),
        5: ("🔥🔥", "5 days strong! Unstoppable!", "flame"),
        7: ("💙", "BLUE STREAK UNLOCKED! 7 days!", "confetti"),
        14: ("💎", "2 weeks! You're a diamond!", "confetti"),
        30: ("🏆", "GOLDEN STREAK! 30 days! LEGENDARY!", "confetti"),
    }
    
    ENCOURAGEMENT_MESSAGES = [
        ("💪", "Don't worry, let's try another approach!", "pulse"),
        ("🤔", "Good thinking! Let me explain differently...", "none"),
        ("📚", "This one's tricky - here's a hint!", "glow"),
        ("🌱", "Learning happens through trying! Let's go!", "bounce"),
    ]
    
    LEVEL_UP_MESSAGES = {
        StudentLevel.ANALYST: ("🔬", "LEVEL UP! You're now an ANALYST!", "confetti"),
        StudentLevel.TACTICIAN: ("🎯", "LEVEL UP! You're now a TACTICIAN!", "confetti"),
        StudentLevel.SCIENTIST: ("🧪", "LEVEL UP! You're now a SCIENTIST!", "confetti"),
        StudentLevel.MASTER: ("👑", "LEVEL UP! You're now a MASTER!", "confetti"),
    }
    
    @classmethod
    def get_correct_answer_reward(cls, is_fast: bool = False, streak: int = 0) -> MicroReward:
        """Generate reward for correct answer"""
        if is_fast:
            emoji, message, celebration = random.choice(cls.FAST_ANSWER_MESSAGES)
            xp = 15  # Bonus for speed
        else:
            emoji, message, celebration = random.choice(cls.CORRECT_ANSWER_MESSAGES)
            xp = 10
        
        # Streak bonus
        if streak > 0:
            xp += min(streak * 2, 20)  # Up to 20 bonus XP for streaks
        
        return MicroReward(
            message=message,
            emoji=emoji,
            xp_earned=xp,
            celebration_type=celebration
        )
    
    @classmethod
    def get_understanding_reward(cls) -> MicroReward:
        """Generate reward for understanding a concept"""
        emoji, message, celebration = random.choice(cls.UNDERSTANDING_MESSAGES)
        return MicroReward(
            message=message,
            emoji=emoji,
            xp_earned=5,
            celebration_type=celebration
        )
    
    @classmethod
    def get_streak_reward(cls, streak_days: int) -> Optional[MicroReward]:
        """Generate reward for streak milestones"""
        if streak_days in cls.STREAK_MESSAGES:
            emoji, message, celebration = cls.STREAK_MESSAGES[streak_days]
            return MicroReward(
                message=message,
                emoji=emoji,
                xp_earned=streak_days * 5,
                celebration_type=celebration
            )
        return None
    
    @classmethod
    def get_encouragement(cls) -> MicroReward:
        """Generate encouragement for wrong answers"""
        emoji, message, celebration = random.choice(cls.ENCOURAGEMENT_MESSAGES)
        return MicroReward(
            message=message,
            emoji=emoji,
            xp_earned=2,  # Small XP for trying
            celebration_type=celebration
        )
    
    @classmethod
    def get_level_up_reward(cls, new_level: StudentLevel) -> MicroReward:
        """Generate reward for leveling up"""
        if new_level in cls.LEVEL_UP_MESSAGES:
            emoji, message, celebration = cls.LEVEL_UP_MESSAGES[new_level]
            return MicroReward(
                message=message,
                emoji=emoji,
                xp_earned=100,
                celebration_type=celebration
            )
        return MicroReward(
            message="Level up!",
            emoji="🆙",
            xp_earned=50,
            celebration_type="confetti"
        )


# ============ STREAK SYSTEM ============

class StreakEngine:
    """
    Manages daily streaks - the #1 addiction mechanism.
    Like Duolingo/Snapchat streaks.
    """
    
    STREAK_BADGES = {
        3: BadgeType.FLAME_STARTER,
        7: BadgeType.BLUE_STREAK,
        30: BadgeType.GOLDEN_STREAK,
        100: BadgeType.LEGENDARY_STREAK,
    }
    
    @classmethod
    def calculate_streak(cls, last_activity: Optional[datetime], current_streak: int) -> Dict:
        """Calculate if streak continues, breaks, or stays"""
        now = datetime.now()
        today = now.date()
        
        if last_activity is None:
            return {
                "new_streak": 1,
                "streak_status": "started",
                "message": "🔥 Day 1! Your learning journey begins!",
                "badge_earned": None
            }
        
        last_date = last_activity.date()
        days_diff = (today - last_date).days
        
        if days_diff == 0:
            # Same day - streak continues
            return {
                "new_streak": current_streak,
                "streak_status": "maintained",
                "message": f"🔥 Day {current_streak} streak continues!",
                "badge_earned": None
            }
        elif days_diff == 1:
            # Next day - streak increases
            new_streak = current_streak + 1
            badge = cls.STREAK_BADGES.get(new_streak)
            
            messages = {
                3: "🔥 3-day streak! You're building a habit!",
                5: "🔥🔥 5 days! You're unstoppable!",
                7: "💙 BLUE STREAK! 7 days of dedication!",
                14: "💎 2 WEEKS! Diamond-level commitment!",
                21: "🏅 3 WEEKS! You're a champion!",
                30: "🏆 GOLDEN STREAK! 30 days! LEGENDARY!",
            }
            
            message = messages.get(new_streak, f"🔥 Day {new_streak}! Keep the fire burning!")
            
            return {
                "new_streak": new_streak,
                "streak_status": "increased",
                "message": message,
                "badge_earned": badge.value if badge else None
            }
        else:
            # Streak broken
            return {
                "new_streak": 1,
                "streak_status": "broken",
                "message": "🌱 New streak started! Let's build it back!",
                "badge_earned": None,
                "days_missed": days_diff - 1
            }
    
    @classmethod
    def get_streak_motivation(cls, streak: int, time_of_day: str) -> str:
        """Get motivational message based on streak and time"""
        if streak == 0:
            return "Start your streak today! 🔥"
        
        if streak < 3:
            return f"Day {streak} - Just {3 - streak} more days for your first badge! 🎯"
        elif streak < 7:
            return f"Day {streak} - Blue Streak badge in {7 - streak} days! 💙"
        elif streak < 30:
            return f"Day {streak} 🔥 - Golden Streak in {30 - streak} days! 🏆"
        else:
            return f"Day {streak} 🔥🔥🔥 - You're LEGENDARY! Keep going!"


# ============ ADAPTIVE DIFFICULTY ENGINE ============

class AdaptiveDifficultyEngine:
    """
    Keeps students in the "flow state" - not too easy, not too hard.
    Adjusts difficulty dynamically based on performance.
    """
    
    # Flow state parameters
    TARGET_ACCURACY = 0.7  # 70% correct = optimal challenge
    ACCURACY_WINDOW = 10   # Last 10 questions
    
    @classmethod
    def calculate_difficulty(cls, recent_accuracy: List[bool], current_difficulty: DifficultyLevel) -> Dict:
        """
        Adjust difficulty based on recent performance.
        Returns new difficulty and explanation.
        """
        if len(recent_accuracy) < 3:
            return {
                "difficulty": current_difficulty,
                "change": "none",
                "message": None
            }
        
        # Calculate accuracy from recent answers
        accuracy = sum(recent_accuracy[-cls.ACCURACY_WINDOW:]) / len(recent_accuracy[-cls.ACCURACY_WINDOW:])
        
        if accuracy > 0.85:
            # Too easy - increase difficulty
            if current_difficulty.value < DifficultyLevel.EXPERT.value:
                new_difficulty = DifficultyLevel(current_difficulty.value + 1)
                return {
                    "difficulty": new_difficulty,
                    "change": "increased",
                    "message": "🚀 You're crushing it! Let's try something more challenging!",
                    "accuracy": accuracy
                }
        elif accuracy < 0.5:
            # Too hard - decrease difficulty
            if current_difficulty.value > DifficultyLevel.BEGINNER.value:
                new_difficulty = DifficultyLevel(current_difficulty.value - 1)
                return {
                    "difficulty": new_difficulty,
                    "change": "decreased",
                    "message": "💪 Let's build your foundation with some practice questions!",
                    "accuracy": accuracy
                }
        
        # In flow state
        return {
            "difficulty": current_difficulty,
            "change": "none",
            "message": None,
            "accuracy": accuracy
        }
    
    @classmethod
    def get_adaptive_response_style(cls, difficulty: DifficultyLevel, is_confused: bool) -> Dict:
        """
        Get response style based on difficulty and student state.
        """
        if is_confused:
            return {
                "use_visual": True,
                "use_analogy": True,
                "use_simpler_language": True,
                "break_into_steps": True,
                "add_hint": True,
                "explanation_depth": "detailed"
            }
        
        styles = {
            DifficultyLevel.BEGINNER: {
                "use_visual": True,
                "use_analogy": True,
                "use_simpler_language": True,
                "break_into_steps": True,
                "add_hint": False,
                "explanation_depth": "detailed"
            },
            DifficultyLevel.EASY: {
                "use_visual": True,
                "use_analogy": True,
                "use_simpler_language": False,
                "break_into_steps": True,
                "add_hint": False,
                "explanation_depth": "standard"
            },
            DifficultyLevel.MEDIUM: {
                "use_visual": True,
                "use_analogy": False,
                "use_simpler_language": False,
                "break_into_steps": False,
                "add_hint": False,
                "explanation_depth": "standard"
            },
            DifficultyLevel.HARD: {
                "use_visual": False,
                "use_analogy": False,
                "use_simpler_language": False,
                "break_into_steps": False,
                "add_hint": False,
                "explanation_depth": "concise"
            },
            DifficultyLevel.EXPERT: {
                "use_visual": False,
                "use_analogy": False,
                "use_simpler_language": False,
                "break_into_steps": False,
                "add_hint": False,
                "explanation_depth": "exam_focused"
            }
        }
        
        return styles.get(difficulty, styles[DifficultyLevel.MEDIUM])


# ============ XP & LEVELING SYSTEM ============

class XPEngine:
    """
    Experience points and leveling system.
    Makes progress tangible and rewarding.
    """
    
    # XP thresholds for each level
    LEVEL_THRESHOLDS = {
        StudentLevel.EXPLORER: 0,
        StudentLevel.ANALYST: 500,
        StudentLevel.TACTICIAN: 1500,
        StudentLevel.SCIENTIST: 3500,
        StudentLevel.MASTER: 7000,
    }
    
    # XP rewards for different actions
    XP_REWARDS = {
        "correct_answer": 10,
        "fast_correct": 15,
        "streak_bonus": 5,  # Per streak day
        "concept_mastered": 50,
        "subject_completed": 200,
        "daily_goal_reached": 25,
        "first_question_today": 10,
        "asked_followup": 5,
        "used_visual": 3,
        "completed_quiz": 30,
    }
    
    @classmethod
    def calculate_level(cls, total_xp: int) -> StudentLevel:
        """Calculate level from XP"""
        for level in reversed(StudentLevel):
            if total_xp >= cls.LEVEL_THRESHOLDS[level]:
                return level
        return StudentLevel.EXPLORER
    
    @classmethod
    def get_level_progress(cls, total_xp: int) -> Dict:
        """Get progress within current level"""
        current_level = cls.calculate_level(total_xp)
        
        # Find XP needed for next level
        levels = list(StudentLevel)
        current_index = levels.index(current_level)
        
        if current_index >= len(levels) - 1:
            # Max level
            return {
                "level": current_level,
                "level_name": current_level.name.title(),
                "current_xp": total_xp,
                "level_xp": total_xp - cls.LEVEL_THRESHOLDS[current_level],
                "next_level_xp": None,
                "progress_percent": 100,
                "is_max_level": True
            }
        
        next_level = levels[current_index + 1]
        current_threshold = cls.LEVEL_THRESHOLDS[current_level]
        next_threshold = cls.LEVEL_THRESHOLDS[next_level]
        
        xp_in_level = total_xp - current_threshold
        xp_needed = next_threshold - current_threshold
        progress = (xp_in_level / xp_needed) * 100
        
        return {
            "level": current_level,
            "level_name": current_level.name.title(),
            "current_xp": total_xp,
            "level_xp": xp_in_level,
            "next_level_xp": xp_needed,
            "xp_to_next": xp_needed - xp_in_level,
            "progress_percent": round(progress, 1),
            "next_level_name": next_level.name.title(),
            "is_max_level": False
        }
    
    @classmethod
    def award_xp(cls, action: str, multiplier: float = 1.0, streak_days: int = 0) -> Dict:
        """Award XP for an action"""
        base_xp = cls.XP_REWARDS.get(action, 5)
        
        # Apply multiplier
        xp = int(base_xp * multiplier)
        
        # Streak bonus
        if streak_days > 0:
            streak_bonus = min(streak_days * cls.XP_REWARDS["streak_bonus"], 50)
            xp += streak_bonus
        
        return {
            "xp_earned": xp,
            "action": action,
            "base_xp": base_xp,
            "multiplier": multiplier,
            "streak_bonus": streak_bonus if streak_days > 0 else 0
        }


# ============ PERSONALIZED LEARNING PATH ============

class PersonalizedLearningEngine:
    """
    Creates personalized learning experiences based on student profile.
    Adapts analogies, visuals, and difficulty to individual needs.
    """
    
    # Analogy categories
    ANALOGY_PROFILES = {
        "cricket": {
            "force": "bowler throwing ball",
            "velocity": "ball speed",
            "acceleration": "fast bowler run-up",
            "momentum": "batsman hitting six",
            "energy": "power shot",
        },
        "cooking": {
            "force": "stirring curry",
            "velocity": "chopping speed",
            "acceleration": "heating up pan",
            "momentum": "rolling dough",
            "energy": "gas flame",
        },
        "gaming": {
            "force": "character pushing objects",
            "velocity": "player movement speed",
            "acceleration": "speed boost",
            "momentum": "combo attacks",
            "energy": "health/mana bar",
        },
        "bollywood": {
            "force": "hero punch in fight scene",
            "velocity": "car chase speed",
            "acceleration": "dance moves getting faster",
            "momentum": "story building up",
            "energy": "item song energy",
        },
        "daily_life": {
            "force": "pushing door",
            "velocity": "walking speed",
            "acceleration": "auto rickshaw starting",
            "momentum": "running and stopping",
            "energy": "eating food for strength",
        }
    }
    
    @classmethod
    def get_personalized_analogy(cls, concept: str, preferences: List[str]) -> Optional[str]:
        """Get analogy based on student preferences"""
        for pref in preferences:
            if pref in cls.ANALOGY_PROFILES:
                analogy = cls.ANALOGY_PROFILES[pref].get(concept.lower())
                if analogy:
                    return analogy
        
        # Default to daily life
        return cls.ANALOGY_PROFILES["daily_life"].get(concept.lower())
    
    @classmethod
    def get_learning_recommendations(cls, progress: StudentProgress) -> List[Dict]:
        """Get personalized learning recommendations"""
        recommendations = []
        
        # Based on mastery
        weak_topics = [
            topic for topic, mastery in progress.topic_mastery.items()
            if mastery < 0.6
        ]
        
        if weak_topics:
            recommendations.append({
                "type": "practice",
                "message": f"Let's strengthen: {', '.join(weak_topics[:3])}",
                "topics": weak_topics[:3],
                "priority": "high"
            })
        
        # Based on streak
        if progress.daily_streak > 0 and progress.daily_streak < 7:
            recommendations.append({
                "type": "streak",
                "message": f"Keep your {progress.daily_streak}-day streak alive!",
                "days_to_badge": 7 - progress.daily_streak,
                "priority": "medium"
            })
        
        # Based on time
        if progress.questions_today < 5:
            recommendations.append({
                "type": "daily_goal",
                "message": f"Answer {5 - progress.questions_today} more questions for daily bonus!",
                "remaining": 5 - progress.questions_today,
                "priority": "low"
            })
        
        return recommendations


# ============ MAIN GAMIFICATION SERVICE ============

class GamificationService:
    """
    Main service that orchestrates all gamification features.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.dopamine = MicroDopamineEngine()
        self.streak = StreakEngine()
        self.difficulty = AdaptiveDifficultyEngine()
        self.xp = XPEngine()
        self.personalization = PersonalizedLearningEngine()
    
    async def process_interaction(
        self,
        user_id: str,
        interaction_type: str,
        is_correct: bool = True,
        response_time_ms: int = 0,
        concept: str = "",
        subject: str = ""
    ) -> Dict:
        """
        Process a student interaction and return gamification response.
        """
        # Get or create student progress
        progress = await self._get_student_progress(user_id)
        
        result = {
            "micro_reward": None,
            "streak_update": None,
            "xp_earned": 0,
            "level_up": None,
            "difficulty_change": None,
            "badges_earned": [],
            "recommendations": [],
            "celebration": None
        }
        
        # 1. Process streak
        streak_result = self.streak.calculate_streak(
            progress.last_activity,
            progress.daily_streak
        )
        result["streak_update"] = streak_result
        
        if streak_result["badge_earned"]:
            result["badges_earned"].append(streak_result["badge_earned"])
        
        # 2. Award XP
        is_fast = response_time_ms < 5000  # Under 5 seconds
        action = "fast_correct" if is_fast and is_correct else ("correct_answer" if is_correct else "asked_question")
        
        xp_result = self.xp.award_xp(
            action=action,
            streak_days=streak_result["new_streak"]
        )
        result["xp_earned"] = xp_result["xp_earned"]
        
        # 3. Check for level up
        old_level = progress.level
        new_total_xp = progress.total_xp + xp_result["xp_earned"]
        new_level = self.xp.calculate_level(new_total_xp)
        
        if new_level != old_level:
            result["level_up"] = {
                "old_level": old_level.name,
                "new_level": new_level.name,
                "celebration": self.dopamine.get_level_up_reward(new_level)
            }
        
        # 4. Get micro reward
        if is_correct:
            result["micro_reward"] = self.dopamine.get_correct_answer_reward(
                is_fast=is_fast,
                streak=streak_result["new_streak"]
            )
        else:
            result["micro_reward"] = self.dopamine.get_encouragement()
        
        # 5. Update difficulty
        progress.recent_accuracy.append(is_correct)
        difficulty_result = self.difficulty.calculate_difficulty(
            progress.recent_accuracy,
            progress.current_difficulty
        )
        
        if difficulty_result["change"] != "none":
            result["difficulty_change"] = difficulty_result
        
        # 6. Get recommendations
        result["recommendations"] = self.personalization.get_learning_recommendations(progress)
        
        # 7. Update progress in DB
        await self._update_student_progress(user_id, {
            "total_xp": new_total_xp,
            "level": new_level,
            "daily_streak": streak_result["new_streak"],
            "longest_streak": max(progress.longest_streak, streak_result["new_streak"]),
            "last_activity": datetime.now(),
            "questions_today": progress.questions_today + 1,
            "correct_today": progress.correct_today + (1 if is_correct else 0),
            "recent_accuracy": progress.recent_accuracy[-20:],  # Keep last 20
            "current_difficulty": difficulty_result["difficulty"]
        })
        
        # 8. Get level progress for display
        result["level_progress"] = self.xp.get_level_progress(new_total_xp)
        
        return result
    
    async def get_student_stats(self, user_id: str) -> Dict:
        """Get complete student stats for dashboard"""
        progress = await self._get_student_progress(user_id)
        level_progress = self.xp.get_level_progress(progress.total_xp)
        
        return {
            "user_id": user_id,
            "level": level_progress,
            "streak": {
                "current": progress.daily_streak,
                "longest": progress.longest_streak,
                "motivation": self.streak.get_streak_motivation(
                    progress.daily_streak,
                    datetime.now().strftime("%p").lower()
                )
            },
            "today": {
                "questions": progress.questions_today,
                "correct": progress.correct_today,
                "accuracy": (progress.correct_today / max(progress.questions_today, 1)) * 100,
                "time_spent": progress.time_spent_today
            },
            "badges": progress.badges_earned,
            "difficulty": progress.current_difficulty.name,
            "recommendations": self.personalization.get_learning_recommendations(progress)
        }
    
    async def _get_student_progress(self, user_id: str) -> StudentProgress:
        """Get student progress from DB or create new"""
        if self.db:
            data = await self.db.gamification.find_one({"user_id": user_id})
            if data:
                return StudentProgress(
                    user_id=user_id,
                    total_xp=data.get("total_xp", 0),
                    level=StudentLevel(data.get("level", 1)),
                    current_difficulty=DifficultyLevel(data.get("difficulty", 3)),
                    daily_streak=data.get("daily_streak", 0),
                    longest_streak=data.get("longest_streak", 0),
                    last_activity=data.get("last_activity"),
                    questions_today=data.get("questions_today", 0),
                    correct_today=data.get("correct_today", 0),
                    recent_accuracy=data.get("recent_accuracy", []),
                    topic_mastery=data.get("topic_mastery", {}),
                    badges_earned=data.get("badges_earned", []),
                    preferred_analogies=data.get("preferred_analogies", ["cricket", "daily_life"]),
                )
        
        return StudentProgress(user_id=user_id)
    
    async def _update_student_progress(self, user_id: str, updates: Dict):
        """Update student progress in DB"""
        if self.db:
            # Convert enums to values
            db_updates = {}
            for key, value in updates.items():
                if isinstance(value, (StudentLevel, DifficultyLevel)):
                    db_updates[key] = value.value
                else:
                    db_updates[key] = value
            
            await self.db.gamification.update_one(
                {"user_id": user_id},
                {"$set": db_updates},
                upsert=True
            )


# ============ SINGLETON INSTANCE ============

_gamification_service: Optional[GamificationService] = None

def get_gamification_service(db=None) -> GamificationService:
    """Get or create gamification service instance"""
    global _gamification_service
    if _gamification_service is None:
        _gamification_service = GamificationService(db)
    return _gamification_service



