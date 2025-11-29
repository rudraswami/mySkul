"""
Vision Analyzer Service
Analyzes images/screenshots uploaded by students using GPT-4 Vision
Extracts text, diagrams, equations, and provides intelligent answers

USES LITELLM: Same API key configuration as the rest of the app
"""
import logging
import base64
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """Analyzes student-uploaded images using GPT-4 Vision via LiteLLM"""
    
    def __init__(self):
        # Use same key as LiteLLM for consistency
        self.api_key = os.environ.get('EMERGENT_LLM_KEY') or os.environ.get('OPENAI_API_KEY')
        logger.info(f"VisionAnalyzer initialized with API key: {'*' * 10}...{self.api_key[-4:] if self.api_key else 'None'}")
    
    async def analyze_image(
        self,
        image_data: str,
        question: str,
        subject_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze image and extract relevant information using LiteLLM (same config as text responses)
        
        Args:
            image_data: Base64 encoded image or URL
            question: Student's question about the image
            subject_hint: Optional subject hint
        
        Returns:
            {
                'extracted_text': 'Equation: F = ma...',
                'content_type': 'equation|diagram|text|mixed',
                'analysis': 'The image shows Newton's second law...',
                'subject_detected': 'Physics',
                'key_elements': ['force', 'mass', 'acceleration']
            }
        """
        try:
            # Use LiteLLM instead of direct OpenAI - uses same API key config as rest of app
            import litellm
            
            # Prepare image for API
            if image_data.startswith('http'):
                # URL
                image_url = image_data
            else:
                # Base64 - add proper data URI prefix
                image_url = f"data:image/jpeg;base64,{image_data}"
            
            logger.info(f"📷 Calling GPT-4o Vision via LiteLLM (image size: {len(image_data)} chars)")
            
            # CRITICAL: Explicitly pass API key to LiteLLM (it ignores self.api_key otherwise)
            # LiteLLM defaults to OPENAI_API_KEY env var which may be invalid
            response = await litellm.acompletion(
                model="gpt-4o",  # GPT-4 with vision
                api_key=self.api_key,  # Explicitly pass the correct key
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at analyzing educational images for Indian students (JEE, NEET, CBSE).

CRITICAL: Extract EXACTLY what is shown in the image. NO creative interpretation.

Analyze and extract:
1. **Content Type**: MCQ question | Numerical problem | Diagram | Textbook page | Handwritten notes | Equation
2. **Full Text**: Extract ALL visible text word-for-word (equations, questions, options)
3. **Subject**: Physics | Chemistry | Mathematics | Biology
4. **Question Details** (if MCQ): 
   - Question text
   - Options A, B, C, D (exact text)
   - Any diagrams or figures shown
5. **Key Concepts**: Main topics/formulas visible

FORMAT YOUR RESPONSE AS:
**Content Type**: [MCQ|Problem|Diagram|etc]
**Subject**: [Subject name]
**Extracted Text**:
[Exact text from image]

**Question** (if applicable):
[Full question text]

**Options** (if MCQ):
A) [exact text]
B) [exact text]
C) [exact text]  
D) [exact text]

**Diagrams/Figures**: [Description if any]
**Key Concepts**: [List]

Be FACTUAL and PRECISE. Extract exactly what you see."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Student's question: {question}\n\nAnalyze this image and extract all relevant information:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.2  # Lower temperature for accuracy
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the analysis
            result = {
                'extracted_text': analysis_text,
                'content_type': self._detect_content_type(analysis_text),
                'analysis': analysis_text,
                'subject_detected': self._detect_subject_from_analysis(analysis_text, subject_hint),
                'key_elements': self._extract_key_elements(analysis_text),
                'has_equations': 'equation' in analysis_text.lower() or '=' in analysis_text,
                'has_diagram': 'diagram' in analysis_text.lower() or 'figure' in analysis_text.lower()
            }
            
            logger.info(f"✅ Image analyzed successfully: {result['content_type']}, Subject: {result['subject_detected']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Image analysis failed: {e}", exc_info=True)
            return {
                'extracted_text': '',
                'content_type': 'unknown',
                'analysis': 'Failed to analyze image',
                'subject_detected': subject_hint or 'General',
                'key_elements': [],
                'error': str(e)
            }
    
    def _detect_content_type(self, analysis: str) -> str:
        """Detect type of content from analysis"""
        analysis_lower = analysis.lower()
        
        if 'equation' in analysis_lower or 'formula' in analysis_lower:
            return 'equation'
        elif 'diagram' in analysis_lower or 'figure' in analysis_lower or 'graph' in analysis_lower:
            return 'diagram'
        elif 'handwritten' in analysis_lower or 'notes' in analysis_lower:
            return 'handwritten_notes'
        elif 'textbook' in analysis_lower or 'page' in analysis_lower:
            return 'textbook_page'
        elif 'problem' in analysis_lower or 'question' in analysis_lower:
            return 'homework_problem'
        else:
            return 'mixed'
    
    def _detect_subject_from_analysis(self, analysis: str, hint: Optional[str]) -> str:
        """Detect subject from analysis text"""
        analysis_lower = analysis.lower()
        
        subjects = {
            'physics': ['force', 'velocity', 'acceleration', 'energy', 'motion', 'newton', 'mass'],
            'chemistry': ['atom', 'molecule', 'reaction', 'bond', 'element', 'compound', 'acid'],
            'mathematics': ['equation', 'integral', 'derivative', 'function', 'variable', 'theorem'],
            'biology': ['cell', 'dna', 'protein', 'organ', 'tissue', 'enzyme', 'photosynthesis']
        }
        
        max_score = 0
        detected_subject = hint or 'General'
        
        for subject, keywords in subjects.items():
            score = sum(1 for keyword in keywords if keyword in analysis_lower)
            if score > max_score:
                max_score = score
                detected_subject = subject.capitalize()
        
        return detected_subject
    
    def _extract_key_elements(self, analysis: str) -> list:
        """Extract key concepts from analysis"""
        # Simple extraction - look for important terms
        import re
        
        # Find capitalized words or words after ":" or "-"
        elements = re.findall(r'(?:[\:\-]\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', analysis)
        
        return list(set(elements[:5]))  # Return up to 5 unique elements


async def analyze_student_image(
    image_data: str,
    question: str,
    subject_hint: Optional[str] = None
) -> Dict[str, Any]:
    """Helper function to analyze student-uploaded images"""
    analyzer = VisionAnalyzer()
    return await analyzer.analyze_image(image_data, question, subject_hint)

