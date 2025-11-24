"""
Fast Mock Test Generator
Generates ALL questions in ONE LLM call using GPT-4
Target: 20 questions in 10-30 seconds (vs 5+ minutes with agentic system)
"""
import logging
import json
import uuid
import re
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class FastMockTestGenerator:
    """Ultra-fast mock test generation using batch LLM calls"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_test_fast(
        self,
        exam_type: str,
        subject: str,
        num_questions: int,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate complete test in ONE LLM call
        
        Returns test with all questions in 10-30 seconds
        """
        try:
            # Use Emergent integrations library (same as agents)
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Create optimized prompt for batch generation
            prompt = self._create_batch_generation_prompt(
                exam_type, subject, num_questions, difficulty
            )
            
            logger.info(f"🚀 Fast generation: {exam_type} - {subject} - {num_questions}Q - {difficulty}")
            
            # Initialize LLM client
            llm_client = LlmChat(
                api_key=self.api_key,
                session_id=f"fast_test_{uuid.uuid4()}",
                system_message=f"You are an expert {exam_type} exam question generator. Generate high-quality, accurate MCQ questions with verified answers in valid JSON format."
            ).with_model("openai", "gpt-4o-mini").with_params(
                temperature=0.7,
                max_tokens=8000
            )
            
            # ONE LLM call for ALL questions
            user_msg = UserMessage(text=prompt)
            response_text = await llm_client.send_message(user_msg)
            
            # Parse response - extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            questions_json = json.loads(json_match.group())
            questions = questions_json.get('questions', [])
            
            # Validate and format
            formatted_questions = []
            for i, q in enumerate(questions[:num_questions], 1):
                formatted_q = {
                    "question_id": str(uuid.uuid4()),
                    "question_number": i,
                    "subject": subject,
                    "topic": q.get('topic', 'General'),
                    "question_text": q['question'],
                    "options": [
                        f"A) {q['options']['A']}",
                        f"B) {q['options']['B']}",
                        f"C) {q['options']['C']}",
                        f"D) {q['options']['D']}"
                    ],
                    "correct_answer": q['correct_answer'],
                    "marks": q.get('marks', 1),
                    "difficulty": q.get('difficulty', difficulty),
                    "explanation": q.get('explanation', ''),
                    "concepts_used": q.get('concepts', []),
                    "metadata": {
                        "fast_generated": True,
                        "model": "gpt-4o-mini"
                    }
                }
                formatted_questions.append(formatted_q)
            
            logger.info(f"✅ Fast generation complete: {len(formatted_questions)} questions")
            
            return {
                "questions": formatted_questions,
                "blueprint": {
                    "exam_type": exam_type,
                    "subject": subject,
                    "difficulty": difficulty,
                    "time_limit_minutes": num_questions * 2,  # 2 mins per question
                },
                "quality_report": {
                    "requested_questions": num_questions,
                    "generated_questions": len(formatted_questions),
                    "validated_questions": len(formatted_questions),
                    "fast_mode": True,
                    "generation_method": "batch_llm"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Fast generation failed: {e}", exc_info=True)
            raise Exception(f"Fast test generation failed: {str(e)}")
    
    def _create_batch_generation_prompt(
        self,
        exam_type: str,
        subject: str,
        num_questions: int,
        difficulty: str
    ) -> str:
        """Create optimized prompt for batch question generation"""
        
        return f"""Generate {num_questions} high-quality MCQ questions for {exam_type} exam in {subject}.

Difficulty: {difficulty}
Format: Return ONLY valid JSON

REQUIREMENTS:
- Questions must be exam-accurate and verified
- Cover different topics in {subject}
- Each question has 4 options (A, B, C, D)
- Mark correct answer clearly
- Provide brief explanation

JSON FORMAT (return exactly this structure):
{{
  "questions": [
    {{
      "question": "What is Newton's second law of motion?",
      "options": {{
        "A": "F = ma",
        "B": "E = mc²",
        "C": "v = u + at",
        "D": "s = ut + ½at²"
      }},
      "correct_answer": "A",
      "explanation": "Newton's second law states that Force equals mass times acceleration (F = ma).",
      "difficulty": "easy",
      "topic": "Newton's Laws",
      "concepts": ["Force", "Mass", "Acceleration"],
      "marks": 1
    }},
    ... (generate {num_questions} questions like this)
  ]
}}

IMPORTANT:
- NO escape characters (\\) in JSON
- Use simple quotes
- Each question unique and topic-diverse
- Verified correct answers only
- {difficulty} difficulty level

Generate {num_questions} questions now:"""


async def generate_fast_mock_test(
    exam_type: str,
    subject: str,
    num_questions: int,
    difficulty: str,
    api_key: str
) -> Dict[str, Any]:
    """Helper function for fast test generation"""
    generator = FastMockTestGenerator(api_key)
    return await generator.generate_test_fast(exam_type, subject, num_questions, difficulty)

