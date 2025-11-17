"""
Visualise Agent - Visual Generation & Animation Specifications
Generates visual descriptors and animation metadata
"""
import logging
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class VisualiseAgent(BaseAgent):
    """
    Visualise Agent generates visual specifications and animations
    
    Key Features:
    - Concept-aware visual selection
    - Integration with Visual Professor Engine
    - Metaphor-based visual mapping
    - Animation specifications
    """
    
    def get_agent_type(self) -> str:
        return "Visualise"
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate visual specification for the concept
        
        Args:
            query: Student's question
            context: Dict with subject, student_profile, request_visual flag
        
        Returns:
            Visual specification or None if no meaningful visual
        """
        try:
            logger.info(f"🎨 Visualise agent processing: {query[:100]}")
            
            # Check if visual is requested
            if not context.get('request_visual', True):
                logger.info("🚫 Visual not requested, skipping")
                return self._format_response(
                    content=None,
                    metadata={'visual_skipped': True, 'reason': 'not_requested'}
                )
            
            # Extract context
            subject = context.get('subject', 'General')
            student_profile = context.get('student_profile', {})
            
            # Determine if visual is meaningful for this query
            if not self._should_generate_visual(query, subject):
                logger.info("🚫 Visual not meaningful for this query type")
                return self._format_response(
                    content=None,
                    metadata={'visual_skipped': True, 'reason': 'not_meaningful'}
                )
            
            # Generate visual specification
            visual_spec = await self._generate_visual_spec(query, subject, student_profile)
            
            return self._format_response(
                content=visual_spec,
                metadata={
                    'visual_type': visual_spec.get('type', 'animated_lesson'),
                    'has_stages': bool(visual_spec.get('stages')),
                    'metaphor': student_profile.get('interests', ['cricket'])[0] if student_profile.get('interests') else 'cricket'
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Visualise agent error: {e}", exc_info=True)
            return self._format_error(f"Visual generation failed: {str(e)}")
    
    def _should_generate_visual(self, query: str, subject: str) -> bool:
        """
        Determine if visual is meaningful for this query
        
        Returns:
            True if visual should be generated
        """
        # Skip visuals for certain query types
        skip_patterns = [
            'compare', 'contrast', 'difference between',
            'vs', 'versus',
            'clarify', 'explain again', 'what do you mean'
        ]
        
        query_lower = query.lower()
        for pattern in skip_patterns:
            if pattern in query_lower:
                return False
        
        # Only generate for conceptual/teaching questions
        if len(query.strip()) < 10:  # Too short
            return False
        
        return True
    
    async def _generate_visual_spec(
        self,
        query: str,
        subject: str,
        student_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate visual specification using Visual Professor Engine
        
        Returns:
            Visual specification dict with stages, animations, metadata
        """
        try:
            # Try Visual Professor Generator (Priority 1)
            from services.visual_professor import VisualProfessorGenerator
            
            vpg = VisualProfessorGenerator(student_profile=student_profile)
            
            visual_result = await vpg.generate_visual(
                question=query,
                subject=subject,
                student_profile=student_profile
            )
            
            if visual_result and visual_result.get('stages'):
                logger.info(f"✅ Visual Professor generated {len(visual_result['stages'])} stages")
                return visual_result
            
            # Fallback to template-based visual
            logger.warning("⚠️ Visual Professor returned empty, using template fallback")
            return self._get_fallback_visual(query, subject, student_profile)
            
        except Exception as e:
            logger.error(f"❌ Visual generation error: {e}")
            return self._get_fallback_visual(query, subject, student_profile)
    
    def _get_fallback_visual(
        self,
        query: str,
        subject: str,
        student_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback visual when dynamic generation fails
        
        Returns:
            Basic visual specification
        """
        metaphor = student_profile.get('interests', ['cricket'])[0] if student_profile.get('interests') else 'cricket'
        
        return {
            'visual_id': f'fallback_{hash(query) % 100000}',
            'type': 'static_concept',
            'stages': [
                {
                    'stage_id': 1,
                    'title': 'Understanding the Concept',
                    'duration_ms': 3000,
                    'narration': f'Let me explain this concept using a {metaphor} analogy.',
                    'animations': [],
                    'elements': []
                }
            ],
            'metadata': {
                'template_id': 'fallback_visual',
                'subject': subject,
                'metaphor': metaphor,
                'is_fallback': True
            }
        }

