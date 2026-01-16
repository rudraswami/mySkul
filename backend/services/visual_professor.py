"""
🎨 Visual Professor Generator - Scene-Based Visual Generation
==============================================================

Generates step-by-step animated visuals for educational content.
Works with the frontend's NETRA v5 scene renderer.

This module provides:
1. Intent-based visual planning (math, physics, conceptual)
2. Scene object generation (actors, forces, labels)
3. Animation sequencing (teaching beats)
"""

import logging
import hashlib
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class VisualProfessorGenerator:
    """
    Generates professor-style animated visuals for educational content.
    
    Works with NETRA v5 scene renderer on the frontend.
    """
    
    def __init__(self, student_profile: Optional[Dict[str, Any]] = None):
        """
        Initialize the visual generator.
        
        Args:
            student_profile: Student context for personalization
        """
        self.student_profile = student_profile or {}
        self.region = self.student_profile.get('region', 'India')
        logger.info(f"🎨 VisualProfessorGenerator initialized for region: {self.region}")
    
    async def generate_visual(
        self,
        question: str,
        subject: str,
        student_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate scene-based visual for a question.
        
        Args:
            question: The user's question
            subject: Subject area (Physics, Math, etc.)
            student_profile: Additional student context
            
        Returns:
            Visual specification with stages for animation
        """
        try:
            logger.info(f"🎨 Generating visual for: {question[:50]}...")
            
            # Merge profiles
            profile = {**self.student_profile, **(student_profile or {})}
            
            # Detect intent
            intent = self._classify_intent(question, subject)
            logger.info(f"🎯 Visual intent: {intent}")
            
            # Generate visual based on intent
            if intent == 'calculation':
                return self._generate_math_visual(question, subject)
            elif intent == 'physics':
                return self._generate_physics_visual(question, subject)
            elif intent == 'conceptual':
                return self._generate_conceptual_visual(question, subject)
            else:
                return self._fallback_visual(question, subject)
                
        except Exception as e:
            logger.error(f"❌ Visual generation failed: {e}")
            return self._fallback_visual(question, subject)
    
    def _classify_intent(self, question: str, subject: str) -> str:
        """Classify the visual intent based on question and subject."""
        q_lower = question.lower()
        
        # Math/Calculation patterns
        if any(p in q_lower for p in ['solve', 'calculate', 'find x', 'equation', '=']):
            return 'calculation'
        
        # Physics patterns
        if any(p in q_lower for p in ['force', 'motion', 'newton', 'gravity', 'velocity', 'acceleration']):
            return 'physics'
        
        # Subject-based fallback
        if subject and subject.lower() in ['physics']:
            return 'physics'
        if subject and subject.lower() in ['math', 'mathematics', 'algebra']:
            return 'calculation'
        
        return 'conceptual'
    
    def _generate_math_visual(self, question: str, subject: str) -> Dict[str, Any]:
        """Generate visual for math/calculation questions."""
        visual_id = f"math_{self._hash_question(question)}"
        
        return {
            "visual_id": visual_id,
            "type": "animated_lesson",
            "visual_type": "step_by_step",
            "total_duration_ms": 5000,
            "metadata": {
                "domain": "mathematics",
                "topic": self._extract_topic(question),
                "intent": "calculation"
            },
            "stages": [
                {
                    "id": "stage_1",
                    "title": "Understanding the Problem",
                    "duration_ms": 2000,
                    "scene_objects": [
                        {
                            "id": "equation_display",
                            "type": "label",
                            "visualForm": "equation",
                            "label": question,
                            "position": {"x": 290, "y": 100}
                        }
                    ],
                    "animation": "fade_in"
                },
                {
                    "id": "stage_2", 
                    "title": "Solution Steps",
                    "duration_ms": 3000,
                    "scene_objects": [
                        {
                            "id": "step_indicator",
                            "type": "label",
                            "visualForm": "text",
                            "label": "Solving step by step...",
                            "position": {"x": 290, "y": 250}
                        }
                    ],
                    "animation": "sequential_build"
                }
            ],
            "professor_avatar": {
                "expression": "explaining",
                "gesture": "pointing"
            },
            "lottie_base_url": "https://cdn.ai-tutor.in/visuals"
        }
    
    def _generate_physics_visual(self, question: str, subject: str) -> Dict[str, Any]:
        """Generate visual for physics questions."""
        visual_id = f"physics_{self._hash_question(question)}"
        topic = self._extract_topic(question)
        
        return {
            "visual_id": visual_id,
            "type": "animated_lesson",
            "visual_type": "physics_scene",
            "total_duration_ms": 6000,
            "metadata": {
                "domain": "physics",
                "topic": topic,
                "intent": "conceptual"
            },
            "stages": [
                {
                    "id": "stage_1",
                    "title": "Setting Up the Scene",
                    "duration_ms": 2000,
                    "scene_objects": [
                        {
                            "id": "env_background",
                            "type": "environment",
                            "visualForm": "outdoor_scene"
                        },
                        {
                            "id": "surface_ground",
                            "type": "surface",
                            "visualForm": "flat_ground",
                            "position": {"x": 0, "y": 315}
                        }
                    ],
                    "animation": "fade_in"
                },
                {
                    "id": "stage_2",
                    "title": "The Key Concept",
                    "duration_ms": 2000,
                    "scene_objects": [
                        {
                            "id": "main_object",
                            "type": "actor",
                            "visualForm": "sliding_block",
                            "label": topic,
                            "position": {"x": 240, "y": 245}
                        }
                    ],
                    "animation": "slide_in"
                },
                {
                    "id": "stage_3",
                    "title": "Understanding Forces",
                    "duration_ms": 2000,
                    "scene_objects": [
                        {
                            "id": "force_arrow",
                            "type": "force",
                            "visualForm": "arrow",
                            "variant": "applied",
                            "position": {"x": 295, "y": 280}
                        }
                    ],
                    "animation": "draw_arrow"
                }
            ],
            "professor_avatar": {
                "expression": "explaining",
                "gesture": "demonstrating"
            },
            "lottie_base_url": "https://cdn.ai-tutor.in/visuals"
        }
    
    def _generate_conceptual_visual(self, question: str, subject: str) -> Dict[str, Any]:
        """Generate visual for conceptual questions."""
        visual_id = f"concept_{self._hash_question(question)}"
        topic = self._extract_topic(question)
        
        return {
            "visual_id": visual_id,
            "type": "animated_lesson",
            "visual_type": "concept_map",
            "total_duration_ms": 4000,
            "metadata": {
                "domain": subject or "general",
                "topic": topic,
                "intent": "conceptual"
            },
            "stages": [
                {
                    "id": "stage_1",
                    "title": "Introduction",
                    "duration_ms": 2000,
                    "scene_objects": [
                        {
                            "id": "title_label",
                            "type": "label",
                            "visualForm": "title",
                            "label": topic,
                            "position": {"x": 290, "y": 50}
                        }
                    ],
                    "animation": "fade_in"
                },
                {
                    "id": "stage_2",
                    "title": "Key Ideas",
                    "duration_ms": 2000,
                    "scene_objects": [
                        {
                            "id": "main_concept",
                            "type": "actor",
                            "visualForm": "concept_node",
                            "label": topic,
                            "position": {"x": 290, "y": 200}
                        }
                    ],
                    "animation": "expand"
                }
            ],
            "professor_avatar": {
                "expression": "thinking",
                "gesture": "explaining"
            },
            "lottie_base_url": "https://cdn.ai-tutor.in/visuals"
        }
    
    def _fallback_visual(self, question: str, subject: str) -> Dict[str, Any]:
        """Generate fallback visual when other methods fail."""
        visual_id = f"fallback_{self._hash_question(question)}"
        topic = self._extract_topic(question)
        
        logger.info(f"🎨 Using fallback visual for: {topic}")
        
        return {
            "visual_id": visual_id,
            "type": "animated_lesson",
            "visual_type": "simple_explanation",
            "total_duration_ms": 3000,
            "metadata": {
                "domain": subject or "general",
                "topic": topic,
                "intent": "explanation",
                "is_fallback": True
            },
            "stages": [
                {
                    "id": "stage_1",
                    "title": topic[:50] if topic else "Understanding the Concept",
                    "duration_ms": 3000,
                    "scene_objects": [
                        {
                            "id": "env_background",
                            "type": "environment",
                            "visualForm": "classroom"
                        },
                        {
                            "id": "main_label",
                            "type": "label",
                            "visualForm": "title",
                            "label": topic[:30] if topic else "Topic",
                            "position": {"x": 290, "y": 100}
                        },
                        {
                            "id": "explanation_area",
                            "type": "label",
                            "visualForm": "text_box",
                            "label": "Let me explain this concept...",
                            "position": {"x": 290, "y": 250}
                        }
                    ],
                    "animation": "teacher_drawing"
                }
            ],
            "professor_avatar": {
                "expression": "friendly",
                "gesture": "welcoming"
            },
            "lottie_base_url": "https://cdn.ai-tutor.in/visuals"
        }
    
    def _hash_question(self, question: str) -> str:
        """Generate a short hash for visual ID."""
        return hashlib.md5(question.encode()).hexdigest()[:8]
    
    def _extract_topic(self, question: str) -> str:
        """Extract the main topic from a question."""
        # Remove common prefixes
        prefixes = ['explain', 'what is', 'how does', 'describe', 'solve', 'calculate']
        q_lower = question.lower()
        
        for prefix in prefixes:
            if q_lower.startswith(prefix):
                return question[len(prefix):].strip().strip(':').strip()
        
        # Return first 50 chars if no prefix match
        return question[:50] if len(question) > 50 else question
