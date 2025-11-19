"""
Agentic Question Generator
Uses Supervisor → Professor architecture to generate verified exam questions
"""
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from agents.supervisor import SupervisorAgent
from agents.professor import ProfessorAgent

logger = logging.getLogger(__name__)


class AgenticQuestionGenerator:
    """
    Generates exam questions using the agentic architecture
    
    Flow:
    1. Supervisor validates requirements and plans question generation
    2. Professor generates verified questions following blueprint
    3. Supervisor validates quality and correctness
    4. Returns structured question objects
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with agentic system"""
        self.config = config or {}
        self.supervisor = SupervisorAgent(config)
        self.professor = ProfessorAgent(config)
        logger.info("🤖 Agentic Question Generator initialized")
    
    async def generate_question(
        self,
        blueprint: Dict[str, Any],
        question_number: int,
        subject: str,
        difficulty: str,
        question_type: str,
        topic: Optional[str] = None,
        chapter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a single verified question using agentic system
        
        Args:
            blueprint: Test blueprint with distribution rules
            question_number: Question number in test
            subject: Subject (Mathematics, Physics, etc.)
            difficulty: easy, medium, or hard
            question_type: mcq, numerical, integer, reasoning
            topic: Optional specific topic
            chapter: Optional chapter name
        
        Returns:
            Structured question dict
        """
        try:
            logger.info(f"📝 Generating Q{question_number}: {subject} - {difficulty} - {question_type}")
            
            # Step 1: Run Supervisor → Mentor → Professor planning loop
            mentor_notes, professor_plan = await self._get_agentic_plan(
                subject=subject,
                blueprint=blueprint,
                difficulty=difficulty,
                question_type=question_type,
                topic=topic,
                chapter=chapter
            )
            
            # Step 2: Generate question using Professor agent with agentic plan
            question_prompt = self._build_question_prompt(
                subject=subject,
                difficulty=difficulty,
                question_type=question_type,
                topic=topic,
                chapter=chapter,
                exam_type=blueprint.get("exam_type", "JEE"),
                professor_plan=professor_plan,
                mentor_notes=mentor_notes
            )
            
            professor_context = {
                "subject": subject,
                "exam_mode": blueprint.get("exam_type", "JEE"),
                "student_profile": {"mastery_level": self._difficulty_to_mastery(difficulty)}
            }
            
            # Generate question content
            professor_response = await self.professor.process(question_prompt, professor_context)
            question_content = professor_response.get("content", "")
            
            # Step 3: Parse and structure question
            structured_question = self._parse_question_response(
                question_content=question_content,
                question_number=question_number,
                subject=subject,
                difficulty=difficulty,
                question_type=question_type,
                topic=topic
            )
            structured_question["bloom_level"] = self._difficulty_to_bloom(difficulty)
            structured_question["metadata"] = {
                "mentor_notes": mentor_notes,
                "professor_plan": professor_plan,
                "blueprint_ref": {
                    "subject": subject,
                    "topic": topic,
                    "chapter": chapter,
                    "question_type": question_type,
                    "difficulty": difficulty
                }
            }
            
            # Step 4: Validate question quality
            validation_result = self._validate_question(structured_question, blueprint)
            structured_question["validation"] = validation_result
            
            if not validation_result["valid"]:
                logger.warning(f"⚠️ Question validation failed: {validation_result['reason']}")
                # Generate fallback question
                structured_question = self._generate_fallback_question(
                    question_number, subject, difficulty, question_type
                )
                structured_question["metadata"]["validation"] = validation_result
            
            logger.info(f"✅ Generated Q{question_number}: {structured_question.get('question_text', '')[:50]}...")
            return structured_question
            
        except Exception as e:
            logger.error(f"❌ Question generation failed: {e}", exc_info=True)
            # Return fallback question
            return self._generate_fallback_question(
                question_number, subject, difficulty, question_type
            )
    
    def _build_question_prompt(
        self,
        subject: str,
        difficulty: str,
        question_type: str,
        topic: Optional[str],
        chapter: Optional[str],
        exam_type: str,
        professor_plan: Optional[str] = None,
        mentor_notes: Optional[str] = None
    ) -> str:
        """Build prompt for question generation"""
        
        topic_str = f" on {topic}" if topic else ""
        chapter_str = f" from chapter '{chapter}'" if chapter else ""
        
        difficulty_guidance = {
            "easy": "Use fundamental concepts. Single-step or two-step problems. Straightforward application.",
            "medium": "Require multiple steps. Combine 2-3 concepts. Moderate complexity.",
            "hard": "Complex multi-step problems. Require deep understanding. May involve tricks or edge cases."
        }
        
        question_type_guidance = {
            "mcq": "Generate a Multiple Choice Question with exactly 4 options (A, B, C, D). One correct answer.",
            "numerical": "Generate a Numerical Answer Type question. Student enters a number.",
            "integer": "Generate an Integer Answer Type question (0-9 digits).",
            "reasoning": "Generate a Reasoning-based question with logical steps."
        }
        
        prompt = f"""Generate a {difficulty} difficulty {question_type.upper()} question for {exam_type} exam in {subject}{topic_str}{chapter_str}.

Requirements:
- {difficulty_guidance.get(difficulty, "")}
- {question_type_guidance.get(question_type, "")}
- Must be exam-appropriate and solvable
- Include clear, unambiguous problem statement
- For MCQ: Provide 4 distinct options, mark correct one
- For Numerical/Integer: Provide the correct numerical answer
- Include step-by-step solution explanation

Guidance from planning phase:
- Mentor reminders: {mentor_notes or "Keep it friendly but precise"}
- Professor plan outline: {professor_plan or "Ensure logical flow"}

Format your response as JSON:
{{
  "question_text": "Clear problem statement",
  "options": ["Option A", "Option B", "Option C", "Option D"],  // Only for MCQ
  "correct_answer": 0,  // Index for MCQ, number for numerical
  "explanation": "Step-by-step solution",
  "concepts_used": ["concept1", "concept2"],
  "marks": 1
}}

Generate the question now:"""
        
        return prompt
    
    def _parse_question_response(
        self,
        question_content: str,
        question_number: int,
        subject: str,
        difficulty: str,
        question_type: str,
        topic: Optional[str]
    ) -> Dict[str, Any]:
        """Parse LLM response into structured question"""
        
        # Try to extract JSON from response
        try:
            # Look for JSON block in response
            json_start = question_content.find("{")
            json_end = question_content.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = question_content[json_start:json_end]
                json_str = self._strip_code_fence(json_str)
                parsed = json.loads(json_str)
                
                # Build structured question
                question = {
                    "question_id": str(uuid.uuid4()),
                    "question_number": question_number,
                    "subject": subject,
                    "topic": topic or "General",
                    "question_text": parsed.get("question_text", ""),
                    "question_type": question_type,
                    "difficulty": difficulty,
                    "marks": parsed.get("marks", 1),
                    "correct_answer": self._normalize_correct_answer(parsed.get("correct_answer"), question_type),
                    "explanation": parsed.get("explanation", ""),
                    "concepts_used": parsed.get("concepts_used", []),
                    "options": self._normalize_options(parsed.get("options"), question_type)
                }
                
                return question
        except Exception as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
        
        # Fallback: Generate from text
        return self._generate_fallback_question(question_number, subject, difficulty, question_type)
    
    def _validate_question(self, question: Dict[str, Any], blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Validate question quality and correctness"""
        
        issues = []
        
        # Check required fields
        if not question.get("question_text"):
            issues.append("Missing question text")
        
        if question.get("question_type") == "mcq" and len(question.get("options", [])) != 4:
            issues.append("MCQ must have exactly 4 options")
        
        if question.get("correct_answer") is None:
            issues.append("Missing correct answer")
        
        # Check difficulty alignment
        expected_difficulty = question.get("difficulty")
        if expected_difficulty not in ["easy", "medium", "hard"]:
            issues.append(f"Invalid difficulty: {expected_difficulty}")
        
        # Check exam alignment
        exam_type = blueprint.get("exam_type", "JEE")
        subject = question.get("subject", "")
        
        # Basic validation: subject should match blueprint
        if subject not in blueprint.get("subjects", []):
            issues.append(f"Subject {subject} not in blueprint")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "reason": "; ".join(issues) if issues else "Valid"
        }
    
    def _generate_fallback_question(
        self,
        question_number: int,
        subject: str,
        difficulty: str,
        question_type: str
    ) -> Dict[str, Any]:
        """Generate a fallback question if agentic generation fails"""
        logger.warning(f"Using fallback question for Q{question_number}")
        
        question = {
            "question_id": str(uuid.uuid4()),
            "question_number": question_number,
            "subject": subject,
            "topic": "General",
            "question_text": f"Sample {difficulty} {question_type} question {question_number} in {subject}. This is a placeholder question.",
            "question_type": question_type,
            "difficulty": difficulty,
            "marks": 1,
            "correct_answer": 0 if question_type == "mcq" else 42,
            "explanation": "This is a fallback question. Please regenerate the test for AI-generated questions.",
            "concepts_used": [],
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ] if question_type == "mcq" else []
        }
        question["metadata"] = {
            "fallback": True,
            "reason": "Agentic generation failed - placeholder inserted"
        }
        return question
    
    def _difficulty_to_mastery(self, difficulty: str) -> int:
        """Map difficulty to mastery level for adaptive generation"""
        mapping = {
            "easy": 30,
            "medium": 60,
            "hard": 85
        }
        return mapping.get(difficulty, 50)

    def _difficulty_to_bloom(self, difficulty: str) -> str:
        """Map difficulty to Bloom's taxonomy stage"""
        bloom_map = {
            "easy": "remember",
            "medium": "apply",
            "hard": "analyze"
        }
        return bloom_map.get(difficulty, "understand")

    async def _get_agentic_plan(
        self,
        subject: str,
        blueprint: Dict[str, Any],
        difficulty: str,
        question_type: str,
        topic: Optional[str],
        chapter: Optional[str]
    ) -> Tuple[str, str]:
        """Use Supervisor → Mentor → Professor to plan the question"""
        try:
            supervisor_prompt = self._build_supervisor_prompt(
                subject=subject,
                blueprint=blueprint,
                difficulty=difficulty,
                question_type=question_type,
                topic=topic,
                chapter=chapter
            )
            context = {
                "subject": subject,
                "exam_mode": blueprint.get("exam_type", "JEE"),
                "student_profile": {
                    "mastery_level": self._difficulty_to_mastery(difficulty)
                },
                "request_visual": False
            }
            supervisor_result = await self.supervisor.run(supervisor_prompt, context)
            mentor_notes = supervisor_result.get("mentor", {}).get("content", "").strip()
            professor_plan = supervisor_result.get("professor", {}).get("content", "").strip()
            return mentor_notes, professor_plan
        except Exception as exc:
            logger.warning("Supervisor planning failed (non-critical): %s", exc)
            return "", ""

    def _build_supervisor_prompt(
        self,
        subject: str,
        blueprint: Dict[str, Any],
        difficulty: str,
        question_type: str,
        topic: Optional[str],
        chapter: Optional[str]
    ) -> str:
        """Create planning prompt for Supervisor agent"""
        focus_topic = topic or chapter or "core syllabus"
        return (
            f"You are coordinating agents to craft a {difficulty} {question_type.upper()} question "
            f"for {blueprint.get('exam_type', 'JEE')} - subject {subject}. "
            f"The question must target {focus_topic} and follow the blueprint summary: "
            f"\"{blueprint.get('summary', '')}\". Provide mentor guidance and a professor plan "
            f"with bullet points covering concept, trap, and verification."
        )

    def _normalize_options(self, options: Any, question_type: str) -> List[str]:
        """Ensure options always return as list of clean strings"""
        if question_type != "mcq":
            return []
        if not options:
            return ["A) Placeholder", "B) Placeholder", "C) Placeholder", "D) Placeholder"]
        normalized = []
        for idx, option in enumerate(options):
            if isinstance(option, str):
                normalized.append(option.strip())
            elif isinstance(option, dict):
                text = option.get("text") or option.get("value") or ""
                label = option.get("label") or option.get("id") or chr(65 + idx)
                normalized.append(f"{label}) {text}".strip())
            else:
                normalized.append(str(option))
        return normalized[:4]

    def _normalize_correct_answer(self, value: Any, question_type: str) -> Any:
        """Normalize correct answer to index for MCQ and raw value for others"""
        if question_type != "mcq":
            return value
        if isinstance(value, str):
            value = value.strip()
            if value and value[0].isalpha():
                return value[0].upper()
        if isinstance(value, int):
            return max(0, min(value, 3))
        return 0

    def _strip_code_fence(self, json_str: str) -> str:
        """Remove ```json ... ``` wrappers if present"""
        if json_str.startswith("```"):
            json_str = json_str.strip().strip("`")
            if json_str.startswith("json"):
                json_str = json_str[4:]
        return json_str.strip()

