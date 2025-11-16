"""
Unified Concept Detector for Visual Professor Engine
Integrates existing intent, topic, and concept detection systems
Returns structured metadata for visual template selection
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..intent_planner import IntentPlanner
from ..topic_classifier import TopicClassifier
from ..concept_deconstruction import deconstruct as deconstruct_concept
from ..visual_teaching_engine import SemanticParser, ConceptType


@dataclass
class ConceptMetadata:
    """Structured metadata for visual template selection"""
    subject: str
    topic: str
    concept: str
    intent: List[str]  # Can have multiple intents
    concept_type: str  # comparison, transformation, process, etc.
    key_elements: List[str]
    complexity: str  # simple, medium, complex
    confidence: float


class UnifiedConceptDetector:
    """
    Unified concept detector that integrates all existing detection systems
    Returns structured metadata for visual template selection
    """
    
    def __init__(self):
        self.intent_planner = IntentPlanner()
        self.topic_classifier = TopicClassifier()
        self.semantic_parser = SemanticParser()
        self.concept_map = self._load_concept_map()
    
    def detect(self, question: str, subject_hint: Optional[str] = None) -> ConceptMetadata:
        """
        Detect concept metadata from student question
        
        Args:
            question: Student's question
            subject_hint: Optional subject hint (e.g., from request)
            
        Returns:
            ConceptMetadata with all detected information
        """
        # 1. Detect intent using IntentPlanner
        intent_plan = self.intent_planner.detect(question)
        primary_intent = intent_plan.intent
        
        # Map to visual teaching engine intent types
        intent_list = [primary_intent]
        if intent_plan.visual_mode != "none":
            intent_list.append("concept_explanation")  # Always allow concept explanation
        
        # 2. Classify topic using TopicClassifier
        topic = self.topic_classifier.classify_topic(question)
        
        # 3. Deconstruct concept using concept_deconstruction
        deconstruction = deconstruct_concept(question)
        domain = deconstruction.domain or subject_hint or "general"
        detected_topic = deconstruction.topic or topic
        
        # 4. Extract concept name
        from ..intent_planner import IntentPlanner as IP
        concept_name = IP.extract_concept_name(question)
        if not concept_name or concept_name == "Concept":
            # Try to extract from deconstruction
            if deconstruction.entities:
                concept_name = deconstruction.entities[0] if isinstance(deconstruction.entities, list) else str(deconstruction.entities)
            else:
                concept_name = detected_topic.replace('_', ' ').title()
        
        # 5. Detect concept type using SemanticParser
        parsed_intent = self.semantic_parser.parse(question, domain)
        concept_type = parsed_intent.concept_type.value if parsed_intent else "process"
        
        # 6. Extract key elements
        key_elements = parsed_intent.key_elements if parsed_intent else []
        if not key_elements and deconstruction.entities:
            key_elements = deconstruction.entities if isinstance(deconstruction.entities, list) else [str(deconstruction.entities)]
        
        # 7. Assess complexity
        complexity = parsed_intent.complexity_level if parsed_intent else "medium"
        
        # 8. Calculate confidence
        confidence = deconstruction.confidence if hasattr(deconstruction, 'confidence') else 0.7
        if parsed_intent:
            # Boost confidence if semantic parser found clear patterns
            confidence = min(confidence + 0.1, 0.95)
        
        # Normalize subject name
        subject = self._normalize_subject(domain)
        
        return ConceptMetadata(
            subject=subject,
            topic=detected_topic,
            concept=concept_name,
            intent=intent_list,
            concept_type=concept_type,
            key_elements=key_elements,
            complexity=complexity,
            confidence=confidence
        )
    
    def _normalize_subject(self, subject: str) -> str:
        """Normalize subject names to standard format"""
        subject_lower = (subject or "").lower()
        
        mapping = {
            "mathematics": "mathematics",
            "math": "mathematics",
            "physics": "physics",
            "chemistry": "chemistry",
            "biology": "biology",
            "grammar": "grammar",
            "english": "grammar",
            "history": "history",
            "geography": "geography",
            "cs": "computer_science",
            "computer_science": "computer_science",
        }
        
        return mapping.get(subject_lower, "general")
    
    def _load_concept_map(self) -> Dict[str, str]:
        """Load concept mapping for better concept name extraction"""
        # This can be enhanced with a proper concept map later
        return {}
    
    def get_visual_key(self, metadata: ConceptMetadata) -> str:
        """
        Generate a visual key for template lookup
        Format: subject.concept or subject.topic
        """
        concept_key = metadata.concept.lower().replace(' ', '_')
        topic_key = metadata.topic.lower().replace(' ', '_')
        
        # Prefer concept if it's specific, otherwise use topic
        if concept_key and concept_key != "concept" and len(concept_key) > 3:
            return f"{metadata.subject}.{concept_key}"
        else:
            return f"{metadata.subject}.{topic_key}"

