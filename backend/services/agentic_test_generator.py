"""
Agentic Test Generator - Main Orchestrator
Coordinates blueprint generation and question generation using agentic architecture
"""
import logging
import asyncio
from typing import Dict, Any, List
from services.test_blueprint_generator import TestBlueprintGenerator
from services.agentic_question_generator import AgenticQuestionGenerator

logger = logging.getLogger(__name__)


class AgenticTestGenerator:
    """
    Main orchestrator for agentic test generation
    
    Flow:
    1. Generate blueprint from user parameters
    2. Generate questions following blueprint using Professor agent
    3. Validate all questions
    4. Return complete test
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.blueprint_generator = TestBlueprintGenerator()
        self.question_generator = AgenticQuestionGenerator(config)
        logger.info("🎯 Agentic Test Generator initialized")
    
    async def generate_test(
        self,
        exam_type: str,
        subjects: List[str],
        num_questions: int,
        difficulty_level: int,
        test_type: str = "full_length",
        chapters: List[str] = None,
        focus_areas: List[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate complete test using agentic architecture
        
        Args:
            exam_type: JEE, NEET, UPSC
            subjects: List of subjects
            num_questions: Total questions
            difficulty_level: 1=easy, 2=medium, 3=hard
            test_type: full_length, chapter_wise, etc.
            chapters: Optional chapters
            focus_areas: Optional focus areas
            user_id: User ID for personalization
        
        Returns:
            Complete test dict with questions
        """
        logger.info(f"🚀 Starting agentic test generation: {exam_type}, {subjects}, {num_questions}Q")
        
        try:
            # Step 1: Generate blueprint
            blueprint = self.blueprint_generator.generate_blueprint(
                exam_type=exam_type,
                subjects=subjects,
                num_questions=num_questions,
                difficulty_level=difficulty_level,
                test_type=test_type,
                chapters=chapters,
                focus_areas=focus_areas
            )
            
            logger.info(f"📋 Blueprint generated: {blueprint['difficulty_distribution']}")
            
            # Step 2: Generate questions following blueprint
            questions = await self._generate_questions_from_blueprint(blueprint)
            
            if len(questions) < num_questions:
                logger.warning(f"⚠️ Generated {len(questions)} questions, expected {num_questions}")
            
            # Step 3: Final validation
            validated_questions = self._validate_all_questions(questions, blueprint)
            quality_report = self._build_quality_report(
                requested=num_questions,
                generated=len(questions),
                validated=len(validated_questions)
            )
            
            logger.info(f"✅ Test generation complete: {len(validated_questions)} questions")
            
            return {
                "blueprint": blueprint,
                "questions": validated_questions,
                "total_questions": len(validated_questions),
                "generation_mode": "agentic",
                "validation_passed": True,
                "quality_report": quality_report
            }
            
        except Exception as e:
            logger.error(f"❌ Test generation failed: {e}", exc_info=True)
            raise
    
    async def _generate_questions_from_blueprint(self, blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate all questions following blueprint"""
        
        question_specs = self._build_question_specs(blueprint)
        questions: List[Dict[str, Any]] = []

        batch_size = 5
        for i in range(0, len(question_specs), batch_size):
            batch = question_specs[i:i + batch_size]
            tasks = [
                self.question_generator.generate_question(
                    blueprint=blueprint,
                    question_number=spec["number"],
                    subject=spec["subject"],
                    difficulty=spec["difficulty"],
                    question_type=spec["question_type"],
                    topic=spec["topic"],
                    chapter=spec["chapter"]
                )
                for spec in batch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error("❌ Question generation task failed: %s", result)
                    continue
                questions.append(result)
        return questions
    
    def _validate_all_questions(
        self,
        questions: List[Dict[str, Any]],
        blueprint: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validate all questions and filter invalid ones"""
        
        validated = []
        seen_texts = set()
        
        for q in questions:
            # Check for duplicates
            q_text = q.get("question_text", "").lower().strip()
            if q_text in seen_texts:
                logger.warning(f"⚠️ Duplicate question detected: Q{q.get('question_number')}")
                continue
            
            seen_texts.add(q_text)
            
            # Validate using question generator's validation
            validation = self.question_generator._validate_question(q, blueprint)
            
            if validation["valid"]:
                validated.append(q)
            else:
                logger.warning(f"⚠️ Invalid question Q{q.get('question_number')}: {validation['reason']}")
        
        return validated

    def _build_question_specs(self, blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Turn blueprint metadata into per-question specifications"""
        specs: List[Dict[str, Any]] = []
        question_number = 1

        # Difficulty sequencing
        diff_dist = blueprint["difficulty_distribution"]
        difficulty_queue = (
            ["easy"] * diff_dist["easy"]
            + ["medium"] * diff_dist["medium"]
            + ["hard"] * diff_dist["hard"]
        )

        # Question type sequencing
        question_types = blueprint.get("question_types", {"mcq": 1.0})
        total_q = len(difficulty_queue)
        mcq_count = int(total_q * question_types.get("mcq", 0.6))
        numerical_count = int(total_q * question_types.get("numerical", 0.3))
        remaining = total_q - mcq_count - numerical_count
        integer_count = max(0, remaining)

        question_type_queue = (
            ["mcq"] * mcq_count
            + ["numerical"] * numerical_count
            + ["integer"] * integer_count
        )
        while len(question_type_queue) < total_q:
            question_type_queue.append("mcq")

        subjects = blueprint["subjects"]
        subject_plan = blueprint.get("subject_plan", [])
        per_subject_remaining = {
            plan["subject"]: plan.get("question_count", 0) for plan in subject_plan
        }
        subject_topics = {
            plan["subject"]: list(plan.get("focus_topics") or [])
            for plan in subject_plan
        }

        subject_index = 0
        for idx, difficulty in enumerate(difficulty_queue):
            subject = subjects[subject_index]
            rotations = 0
            while per_subject_remaining.get(subject, 0) <= 0 and rotations < len(subjects):
                subject_index = (subject_index + 1) % len(subjects)
                subject = subjects[subject_index]
                rotations += 1

            per_subject_remaining[subject] = max(
                0, per_subject_remaining.get(subject, 0) - 1
            )

            # Rotate focus topics for the subject
            focus_topic = None
            topics_pool = subject_topics.get(subject, [])
            if topics_pool:
                focus_topic = topics_pool.pop(0)
                topics_pool.append(focus_topic)

            specs.append({
                "number": question_number,
                "subject": subject,
                "difficulty": difficulty,
                "question_type": question_type_queue[idx] if idx < len(question_type_queue) else "mcq",
                "topic": focus_topic,
                "chapter": blueprint.get("chapters", [None])[0] if blueprint.get("chapters") else None
            })
            question_number += 1
            subject_index = (subject_index + 1) % len(subjects)

        return specs

    def _build_quality_report(self, requested: int, generated: int, validated: int) -> Dict[str, Any]:
        """Summarize generation quality for analytics and UI"""
        return {
            "requested_questions": requested,
            "generated_questions": generated,
            "validated_questions": validated,
            "dropped_questions": max(0, generated - validated)
        }

