"""
Memory Extraction Engine
Extracts learning facts from conversations for long-term storage
"""
import logging
import uuid
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """
    Extracts structured memory facts from conversations
    
    Features:
    - Concept extraction
    - Mastery level updates
    - Misconception detection
    - Preference learning
    - Error pattern recognition
    """
    
    def __init__(self, db):
        self.db = db
    
    async def extract_learning_facts(
        self,
        user_id: str,
        question: str,
        response: Dict[str, Any],
        session_id: str,
        message_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Extract what student learned from this interaction
        
        Args:
            user_id: Student user ID
            question: Student's question
            response: AI response data
            session_id: Current session
            message_id: Message ID
        
        Returns:
            List of memory facts to store
        """
        try:
            facts = []
            
            # Extract concepts from question and response
            concepts = self._extract_concepts(question, response)
            
            # Fact 1: Concepts learned
            for concept in concepts:
                facts.append({
                    "user_id": user_id,
                    "fact_id": str(uuid.uuid4()),
                    "fact_type": "concept_learned",
                    "content": f"Student learned about {concept}",
                    "topic": concept,
                    "subject": response.get('subject', self._infer_subject(question)),
                    "confidence": 0.7,  # Initial confidence
                    "source_session_id": session_id,
                    "source_message_id": message_id,
                    "created_at": datetime.now(timezone.utc),
                    "next_review_at": datetime.now(timezone.utc) + timedelta(days=1)
                })
            
            # Fact 2: Mastery updates (from feedback or quiz results)
            feedback = response.get('feedback')
            if feedback == 'helpful':
                # Positive feedback = mastery increased
                for concept in concepts:
                    facts.append({
                        "fact_type": "mastery_update",
                        "topic": concept,
                        "mastery_delta": +10,
                        "reason": "positive_feedback"
                    })
            elif feedback == 'not_helpful':
                # Negative feedback = needs more work
                for concept in concepts:
                    facts.append({
                        "fact_type": "mastery_update",
                        "topic": concept,
                        "mastery_delta": -5,
                        "reason": "negative_feedback"
                    })
            
            # Fact 3: Detect preferences (metaphor style)
            metaphor_pref = self._detect_metaphor_preference(response)
            if metaphor_pref:
                facts.append({
                    "user_id": user_id,
                    "fact_id": str(uuid.uuid4()),
                    "fact_type": "preference",
                    "content": f"Student prefers {metaphor_pref} metaphors",
                    "topic": "metaphor_preference",
                    "subject": "general",
                    "confidence": 0.6,
                    "metadata": {"preferred_metaphor": metaphor_pref},
                    "created_at": datetime.now(timezone.utc)
                })
            
            # Fact 4: Detect strengths (based on question complexity)
            if self._is_advanced_question(question):
                facts.append({
                    "user_id": user_id,
                    "fact_id": str(uuid.uuid4()),
                    "fact_type": "strength",
                    "content": f"Student asks advanced questions about {concepts[0] if concepts else 'topics'}",
                    "topic": concepts[0] if concepts else "unknown",
                    "subject": response.get('subject', 'general'),
                    "confidence": 0.5,
                    "created_at": datetime.now(timezone.utc)
                })
            
            logger.info(f"🧠 Extracted {len(facts)} memory facts")
            return facts
            
        except Exception as e:
            logger.error(f"❌ Memory extraction failed: {e}")
            return []
    
    def _extract_concepts(
        self,
        question: str,
        response: Dict[str, Any]
    ) -> List[str]:
        """
        Extract main concepts from question and response
        
        Returns:
            List of concept identifiers
        """
        concepts = []
        text = (question + " " + str(response.get('content', ''))).lower()
        
        # Physics concepts
        if ("newton" in text or "नेवटन" in text) and "law" in text:
            concepts.append("newton_laws_motion")
        if "force" in text or "बल" in text:
            concepts.append("force_mechanics")
        if "acceleration" in text or "त्वरण" in text:
            concepts.append("acceleration")
        if "velocity" in text or "वेग" in text:
            concepts.append("velocity_kinematics")
        
        # Math - Calculus
        if "derivative" in text or "differentiation" in text or "अवकलन" in text:
            concepts.append("calculus_derivatives")
        if "integral" in text or "integration" in text or "समाकलन" in text:
            concepts.append("calculus_integrals")
        if "fundamental theorem" in text and "calculus" in text:
            concepts.append("fundamental_theorem_calculus")
        if "limit" in text and ("calculus" in text or "math" in text):
            concepts.append("limits_calculus")
        
        # Math - Algebra
        if "quadratic" in text or "वर्ग समीकरण" in text:
            concepts.append("quadratic_equations")
        if "polynomial" in text or "बहुपद" in text:
            concepts.append("polynomials")
        
        # Chemistry
        if "acid" in text or "base" in text or "अम्ल" in text:
            concepts.append("acids_bases")
        if "organic" in text and "chemistry" in text:
            concepts.append("organic_chemistry")
        
        # If no specific concepts found, use general topic
        if not concepts:
            concepts.append("general_concept")
        
        return concepts
    
    def _infer_subject(self, question: str) -> str:
        """Infer subject from question"""
        q_lower = question.lower()
        
        if any(word in q_lower for word in ["force", "velocity", "newton", "motion", "energy"]):
            return "physics"
        elif any(word in q_lower for word in ["derivative", "integral", "equation", "algebra"]):
            return "mathematics"
        elif any(word in q_lower for word in ["acid", "base", "reaction", "organic"]):
            return "chemistry"
        elif any(word in q_lower for word in ["cell", "dna", "genetics", "evolution"]):
            return "biology"
        else:
            return "general"
    
    def _detect_metaphor_preference(self, response: Dict[str, Any]) -> Optional[str]:
        """Detect which metaphor style was used"""
        response_text = str(response.get('content', '')).lower()
        
        if "cricket" in response_text or "bowler" in response_text or "bat" in response_text:
            return "cricket"
        elif "cooking" in response_text or "recipe" in response_text or "kitchen" in response_text:
            return "cooking"
        elif "gaming" in response_text or "game" in response_text or "player" in response_text:
            return "gaming"
        elif "bollywood" in response_text or "movie" in response_text or "film" in response_text:
            return "bollywood"
        
        return None
    
    def _is_advanced_question(self, question: str) -> bool:
        """Check if question indicates advanced understanding"""
        advanced_keywords = [
            "prove", "derive", "proof", "derivation",
            "edge case", "exception", "why does",
            "relationship between", "compare and contrast",
            "implications", "applications"
        ]
        
        q_lower = question.lower()
        return any(keyword in q_lower for keyword in advanced_keywords)

