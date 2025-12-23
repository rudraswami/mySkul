"""
Memory Extraction Engine
Extracts learning facts from conversations for long-term storage
"""
import logging
import uuid
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


def _normalize_to_dict(payload: Any) -> Dict[str, Any]:
    """
    DEFENSIVE: Normalize any input to a dict to prevent 'list' object has no attribute 'get' errors.
    
    This is a structural fix, NOT keyword-based.
    
    Normalization rules:
    - dict → return as-is
    - list → wrap as {"items": list}
    - tuple/set → convert to list then wrap
    - None → return {}
    - pydantic BaseModel → convert to dict
    - string → wrap as {"content": string}
    - other → wrap as {"value": str(other)}
    
    NEVER raises. Always returns a dict.
    """
    if payload is None:
        return {}
    
    if isinstance(payload, dict):
        return payload
    
    if isinstance(payload, (list, tuple)):
        # Wrap list/tuple as {"items": [...]}
        items = list(payload) if isinstance(payload, tuple) else payload
        return {"items": items}
    
    if isinstance(payload, set):
        return {"items": list(payload)}
    
    if isinstance(payload, str):
        return {"content": payload}
    
    # Check for pydantic model
    if hasattr(payload, 'model_dump'):
        try:
            return payload.model_dump()
        except Exception:
            pass
    elif hasattr(payload, 'dict'):
        try:
            return payload.dict()
        except Exception:
            pass
    
    # Fallback: wrap as {"value": str(payload)}
    return {"value": str(payload)}


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
        response: Any,
        session_id: str,
        message_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Extract what student learned from this interaction
        
        Args:
            user_id: Student user ID
            question: Student's question
            response: AI response data (any type - will be normalized)
            session_id: Current session
            message_id: Message ID
        
        Returns:
            List of memory facts to store
        """
        try:
            facts = []
            
            # DEFENSIVE: Normalize response to dict to prevent 'list' object has no attribute 'get'
            original_type = type(response).__name__
            response = _normalize_to_dict(response)
            if original_type != 'dict':
                logger.debug(f"💾 Memory normalize: converted {original_type} to dict wrapper | user={user_id[:8] if user_id else 'unknown'}")
            
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
        # DEFENSIVE: response should already be a dict from normalization, but be safe
        response_content = response.get('content', '') if isinstance(response, dict) else str(response)
        text = (question + " " + str(response_content)).lower()
        
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
        # DEFENSIVE: response should already be a dict from normalization, but be safe
        response_text = str(response.get('content', '') if isinstance(response, dict) else response).lower()
        
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

