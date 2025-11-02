"""
Parser for Neuro-Symbolic AI Tutor responses
Extracts structured data from LLM response text
"""
import re
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class NeuroSymbolicParser:
    """Parser for neuro-symbolic tutor responses"""
    
    @staticmethod
    def extract_section(text: str, section_type: str) -> Optional[str]:
        """
        Extract content from a specific section
        
        Args:
            text: Full response text
            section_type: Section type (e.g., PRACTICAL_EXPLANATION, INDIAN_EXAMPLE)
        
        Returns:
            Section content or None if not found
        """
        pattern = rf'\[SECTION:{section_type}\](.*?)\[/SECTION:{section_type}\]'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            content = match.group(1).strip()
            # Remove section header if present (e.g., "**👋 Practical Explanation**")
            content = re.sub(r'\*\*[🎯🇮🇳🎭🧠✅👋✨➕].*?\*\*\n*', '', content, count=1)
            return content.strip()
        
        return None
    
    @staticmethod
    def parse_visual_schema(text: str) -> Optional[Dict[str, Any]]:
        """
        Parse visual schema JSON from response
        
        Args:
            text: Full response text or visual schema section
        
        Returns:
            Parsed JSON dict or None if invalid
        """
        # Extract visual schema section first
        schema_text = NeuroSymbolicParser.extract_section(text, 'VISUAL_SCHEMA')
        
        if not schema_text:
            logger.warning("Visual schema section not found")
            return None
        
        # Try to find JSON object in the text
        # Look for { ... } pattern
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, schema_text, re.DOTALL)
        
        for match in matches:
            try:
                # Try to parse as JSON
                schema_dict = json.loads(match)
                
                # Validate required fields
                required_fields = ['diagram_type', 'title', 'nodes', 'edges', 'caption']
                if all(field in schema_dict for field in required_fields):
                    return schema_dict
            except json.JSONDecodeError:
                continue
        
        logger.warning("Could not parse valid visual schema JSON")
        return None
    
    @staticmethod
    def parse_professor_verification(text: str) -> Optional[Dict[str, Any]]:
        """
        Parse professor verification section
        
        Returns:
            Dict with steps, source, confidence, note
        """
        section_text = NeuroSymbolicParser.extract_section(text, 'PROFESSOR_VERIFICATION')
        
        if not section_text:
            return None
        
        # Extract steps (numbered list)
        steps_pattern = r'(?:Steps to prove logic:?\n)((?:\d+\.\s+.*?\n?)+)'
        steps_match = re.search(steps_pattern, section_text, re.IGNORECASE | re.DOTALL)
        
        steps = []
        if steps_match:
            steps_text = steps_match.group(1)
            # Split by numbered items
            step_items = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', steps_text, re.DOTALL)
            steps = [step.strip() for step in step_items if step.strip()]
        
        # Extract source
        source_pattern = r'(?:Source:?\s*)(.*?)(?=\n\*\*|$)'
        source_match = re.search(source_pattern, section_text, re.IGNORECASE | re.DOTALL)
        source = source_match.group(1).strip() if source_match else "Standard reference"
        
        # Extract confidence score
        confidence_pattern = r'Confidence Score:?\s*\[?([\d.]+)\]?'
        confidence_match = re.search(confidence_pattern, section_text, re.IGNORECASE)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.7
        
        # Ensure confidence is between 0.0 and 1.0
        confidence = max(0.0, min(1.0, confidence))
        
        # Extract note if present
        note_pattern = r'\*\*If uncertain:\*\*\s*(.*?)(?=\[/SECTION|$)'
        note_match = re.search(note_pattern, section_text, re.IGNORECASE | re.DOTALL)
        note = note_match.group(1).strip() if note_match else None
        
        return {
            'steps': steps if steps else ["Verification steps not clearly formatted"],
            'source': source,
            'confidence': confidence,
            'note': note
        }
    
    @staticmethod
    def parse_mini_practice(text: str) -> Optional[Dict[str, Any]]:
        """
        Parse mini practice section
        
        Returns:
            Dict with question, options, hint, question_type
        """
        section_text = NeuroSymbolicParser.extract_section(text, 'MINI_PRACTICE')
        
        if not section_text:
            return None
        
        # Extract question
        question_pattern = r'\*\*Question:\*\*\s*(.*?)(?=\n\*\*|$)'
        question_match = re.search(question_pattern, section_text, re.IGNORECASE | re.DOTALL)
        question = question_match.group(1).strip() if question_match else ""
        
        # Extract options (for MCQ)
        options_pattern = r'(?:\*\*Options:\*\*\s*\n)((?:[A-D]\)\s+.*?\n?)+)'
        options_match = re.search(options_pattern, section_text, re.IGNORECASE | re.DOTALL)
        
        options = []
        question_type = "short_answer"
        
        if options_match:
            options_text = options_match.group(1)
            # Extract each option
            option_items = re.findall(r'([A-D])\)\s+(.*?)(?=\n[A-D]\)|\n\*\*|$)', options_text, re.DOTALL)
            options = [opt[1].strip() for opt in option_items if opt[1].strip()]
            if options:  # Only set to MCQ if we actually parsed options
                question_type = "mcq"
        
        # Extract hint
        hint_pattern = r'\*\*Hint:\*\*\s*(.*?)(?=\n\*\*|\[/SECTION|$)'
        hint_match = re.search(hint_pattern, section_text, re.IGNORECASE | re.DOTALL)
        hint = hint_match.group(1).strip() if hint_match else "Think step by step"
        
        return {
            'question': question,
            'options': options,
            'hint': hint,
            'question_type': question_type
        }
    
    @staticmethod
    def parse_full_response(text: str, subject: str, exam_mode: str, emotion: str = "neutral") -> Dict[str, Any]:
        """
        Parse complete neuro-symbolic response
        
        Args:
            text: Full LLM response text
            subject: Subject name
            exam_mode: Exam type
            emotion: Detected student emotion
        
        Returns:
            Dict matching NeuroSymbolicResponse model
        """
        try:
            # Extract all sections
            practical_explanation = NeuroSymbolicParser.extract_section(text, 'PRACTICAL_EXPLANATION')
            indian_example = NeuroSymbolicParser.extract_section(text, 'INDIAN_EXAMPLE')
            metaphor = NeuroSymbolicParser.extract_section(text, 'METAPHOR')
            encouragement = NeuroSymbolicParser.extract_section(text, 'ENCOURAGEMENT')
            ask = NeuroSymbolicParser.extract_section(text, 'ASK')
            
            # Parse complex sections
            visual_schema = NeuroSymbolicParser.parse_visual_schema(text)
            professor_verification = NeuroSymbolicParser.parse_professor_verification(text)
            mini_practice = NeuroSymbolicParser.parse_mini_practice(text)
            
            # Build response dict
            response = {
                'practical_explanation': practical_explanation or "Explanation not found in response.",
                'indian_example': indian_example or "Example not provided.",
                'metaphor': metaphor or "Metaphor not provided.",
                'visual_schema': visual_schema or {
                    'diagram_type': 'flow',
                    'title': 'Concept Flow',
                    'nodes': [{'id': 'n1', 'label': 'Concept', 'type': 'main'}],
                    'edges': [],
                    'caption': 'Visual representation'
                },
                'professor_verification': professor_verification or {
                    'steps': ['Verification steps not available'],
                    'source': 'Standard reference',
                    'confidence': 0.7,
                    'note': None
                },
                'mini_practice': mini_practice or {
                    'question': 'Practice question not available',
                    'options': None,
                    'hint': 'Review the concept',
                    'question_type': 'short_answer'
                },
                'encouragement': encouragement or "Keep learning!",
                'ask': ask or "Want to explore more?",
                'student_emotion': emotion,
                'response_tone': 'balanced',
                'subject': subject,
                'exam_mode': exam_mode
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error parsing neuro-symbolic response: {str(e)}")
            # Return minimal valid response
            return {
                'practical_explanation': "Error parsing response. Please try again.",
                'indian_example': "Example unavailable.",
                'metaphor': "Metaphor unavailable.",
                'visual_schema': {
                    'diagram_type': 'flow',
                    'title': 'Error',
                    'nodes': [{'id': 'n1', 'label': 'Parsing Error', 'type': 'main'}],
                    'edges': [],
                    'caption': 'Error occurred'
                },
                'professor_verification': {
                    'steps': ['Error parsing verification'],
                    'source': 'Unknown',
                    'confidence': 0.0,
                    'note': None
                },
                'mini_practice': {
                    'question': 'Practice unavailable',
                    'options': None,
                    'hint': 'Try again',
                    'question_type': 'short_answer'
                },
                'encouragement': "Let's try again.",
                'ask': "Want to rephrase?",
                'student_emotion': emotion,
                'response_tone': 'error',
                'subject': subject,
                'exam_mode': exam_mode
            }
