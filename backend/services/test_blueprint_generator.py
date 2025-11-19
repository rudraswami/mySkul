"""
Test Blueprint Generator
Creates deterministic test blueprints based on user parameters
"""
import logging
import uuid
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class TestBlueprintGenerator:
    """Generates deterministic test blueprints"""
    
    # Difficulty distribution templates
    DIFFICULTY_DISTRIBUTIONS = {
        "easy": {"easy": 0.7, "medium": 0.3, "hard": 0.0},
        "medium": {"easy": 0.2, "medium": 0.6, "hard": 0.2},
        "hard": {"easy": 0.1, "medium": 0.4, "hard": 0.5},
        "mixed": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
    }
    
    # Question type distributions by exam
    QUESTION_TYPES_BY_EXAM = {
        "JEE": {
            "mcq": 0.6,
            "numerical": 0.3,
            "integer": 0.1
        },
        "NEET": {
            "mcq": 0.9,
            "numerical": 0.1
        },
        "UPSC": {
            "mcq": 0.7,
            "reasoning": 0.2,
            "essay": 0.1
        }
    }
    
    def generate_blueprint(
        self,
        exam_type: str,
        subjects: List[str],
        num_questions: int,
        difficulty_level: int,
        test_type: str = "full_length",
        chapters: List[str] = None,
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a deterministic test blueprint
        
        Args:
            exam_type: JEE, NEET, UPSC
            subjects: List of subjects
            num_questions: Total number of questions
            difficulty_level: 1=easy, 2=medium, 3=hard
            test_type: full_length, chapter_wise, subject_wise, adaptive
            chapters: Optional list of chapters (for chapter_wise)
            focus_areas: Optional focus areas for adaptive mode
        
        Returns:
            Blueprint dict with question distribution
        """
        logger.info(
            "📋 Generating blueprint: exam=%s subjects=%s questions=%s difficulty=%s",
            exam_type,
            subjects,
            num_questions,
            difficulty_level,
        )
        
        # Map difficulty level to distribution (supports int or string values)
        difficulty_key = self._normalize_difficulty_key(difficulty_level)
        distribution = self.DIFFICULTY_DISTRIBUTIONS[difficulty_key]
        
        # Calculate question distribution per difficulty
        easy_count = max(1, int(num_questions * distribution["easy"]))
        medium_count = max(1, int(num_questions * distribution["medium"]))
        hard_count = num_questions - easy_count - medium_count
        
        # Ensure we have at least one question per difficulty if possible
        if hard_count < 0:
            hard_count = 0
            medium_count = num_questions - easy_count
        
        # Distribute questions across subjects
        questions_per_subject = self._distribute_questions(num_questions, len(subjects))
        
        # Get question types for this exam
        question_types_dist = self.QUESTION_TYPES_BY_EXAM.get(exam_type, {"mcq": 1.0})
        
        # Build blueprint
        subject_plan = self._build_subject_plan(
            subjects=subjects,
            questions_per_subject=questions_per_subject,
            distribution=distribution,
            chapters=chapters or [],
            focus_areas=focus_areas or []
        )

        blueprint = {
            "blueprint_id": str(uuid.uuid4()),
            "exam_type": exam_type,
            "test_type": test_type,
            "subjects": subjects,
            "chapters": chapters or [],
            "difficulty_distribution": {
                "easy": easy_count,
                "medium": medium_count,
                "hard": hard_count
            },
            "questions_per_subject": {
                subject: count
                for subject, count in zip(subjects, questions_per_subject)
            },
            "subject_plan": subject_plan,
            "question_types": question_types_dist,
            "total_questions": num_questions,
            "total_marks": num_questions,  # 1 mark per question default
            "time_limit_minutes": self._calculate_time_limit(exam_type, num_questions),
            "generation_mode": "agentic",
            "focus_areas": focus_areas or [],
            "bloom_distribution": self._derive_bloom_distribution(distribution),
            "validation_rules": {
                "no_duplicates": True,
                "topic_coverage": True,
                "difficulty_match": True,
                "exam_alignment": True
            },
            "review_checklist": [
                "Ensure each subject has coverage per blueprint",
                "Verify Bloom's level progression (Remember → Apply → Evaluate)",
                "Check that numerical questions include precise answers",
                "Confirm time limit aligns with exam pacing"
            ],
        }
        
        blueprint["summary"] = self._summarize_blueprint(blueprint)
        
        logger.info("✅ Blueprint generated: %s", blueprint["difficulty_distribution"])
        return blueprint
    
    def _distribute_questions(self, total: int, num_subjects: int) -> List[int]:
        """Distribute questions evenly across subjects"""
        base = total // num_subjects
        remainder = total % num_subjects
        distribution = [base] * num_subjects
        # Distribute remainder to first subjects
        for i in range(remainder):
            distribution[i] += 1
        return distribution
    
    def _calculate_time_limit(self, exam_type: str, num_questions: int) -> int:
        """Calculate time limit in minutes based on exam type"""
        time_per_question = {
            "JEE": 2.5,  # 2.5 minutes per question
            "NEET": 1.5,
            "UPSC": 2.0
        }
        base_time = time_per_question.get(exam_type, 2.0)
        return int(base_time * num_questions)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _normalize_difficulty_key(self, difficulty_level: Any) -> str:
        """Support both slider ints and text labels"""
        if isinstance(difficulty_level, str):
            difficulty_level = difficulty_level.lower().strip()
            if difficulty_level in {"easy", "medium", "hard"}:
                return difficulty_level
            if difficulty_level in {"very easy"}:
                return "easy"
            if difficulty_level in {"very hard", "difficult"}:
                return "hard"
            return "mixed"
        if isinstance(difficulty_level, int):
            if difficulty_level <= 2:
                return "easy"
            if difficulty_level == 3:
                return "medium"
            if difficulty_level >= 4:
                return "hard"
        return "mixed"

    def _build_subject_plan(
        self,
        subjects: List[str],
        questions_per_subject: List[int],
        distribution: Dict[str, float],
        chapters: List[str],
        focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Create per-subject blueprint entries with topics and difficulty splits"""
        topic_sources = chapters or focus_areas or []
        subject_plan = []
        topic_index = 0

        for idx, subject in enumerate(subjects):
            total = questions_per_subject[idx]
            difficulty_split = self._split_difficulty_for_subject(total, distribution)
            focus_topics = self._derive_topics_for_subject(subject, topic_sources, topic_index, total)
            topic_index += len(focus_topics)

            subject_plan.append({
                "subject": subject,
                "question_count": total,
                "difficulty_split": difficulty_split,
                "focus_topics": focus_topics or ["Fundamental concepts"]
            })

        return subject_plan

    def _split_difficulty_for_subject(
        self,
        total: int,
        distribution: Dict[str, float]
    ) -> Dict[str, int]:
        """Allocate difficulty counts for a subject while ensuring totals add up"""
        easy = max(0, round(total * distribution["easy"]))
        medium = max(0, round(total * distribution["medium"]))
        hard = total - easy - medium
        if hard < 0:
            hard = 0
            medium = total - easy
        return {"easy": easy, "medium": medium, "hard": hard}

    def _derive_topics_for_subject(
        self,
        subject: str,
        topic_sources: List[str],
        start_index: int,
        total_questions: int
    ) -> List[str]:
        """Assign focus topics to a subject in a deterministic way"""
        if not topic_sources:
            return []

        topics = []
        for i in range(min(total_questions, len(topic_sources))):
            topic = topic_sources[(start_index + i) % len(topic_sources)]
            topics.append(f"{subject}: {topic}")
        return topics

    def _derive_bloom_distribution(self, distribution: Dict[str, int]) -> Dict[str, int]:
        """Map difficulty split to Bloom's taxonomy levels"""
        return {
            "remember": max(1, int(distribution["easy"] * 0.5)),
            "understand": max(1, int(distribution["easy"] * 0.5 + distribution["medium"] * 0.3)),
            "apply": max(1, int(distribution["medium"] * 0.5)),
            "analyze": max(0, int(distribution["medium"] * 0.2 + distribution["hard"] * 0.3)),
            "evaluate": max(0, int(distribution["hard"] * 0.4)),
            "create": max(0, int(distribution["hard"] * 0.3)),
        }

    def _summarize_blueprint(self, blueprint: Dict[str, Any]) -> str:
        """Generate a short human-readable summary for UI"""
        subject_overview = ", ".join(
            f"{plan['subject']} ({plan['question_count']}Q)"
            for plan in blueprint.get("subject_plan", [])
        )
        difficulty = blueprint.get("difficulty_distribution", {})
        return (
            f"{blueprint['total_questions']} questions • "
            f"{difficulty.get('easy', 0)}/{difficulty.get('medium', 0)}/{difficulty.get('hard', 0)} "
            f"easy/medium/hard • Subjects: {subject_overview}"
        )

