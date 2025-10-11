"""
Format Validator for AI Tutor Responses
Ensures all output is readable, structured, and emotionally engaging
"""
import re
from typing import Dict, Any, List


class FormatValidator:
    """Validates and fixes AI-generated educational content formatting"""
    
    # Emoji patterns to remove
    EMOJI_PATTERNS = [
        r'[\U0001F1E0-\U0001F9FF]',  # Most emojis
        r'[\u2600-\u26FF]',           # Misc symbols
        r'[\u2700-\u27BF]',           # Dingbats
        r'[1-9]️⃣',                    # Numbered emojis
        r'[🔟]',                       # Special ten emoji
        r'[✅❌☑💡🔎📔💙👇📚🧮🧠]',    # Specific unwanted emojis
    ]
    
    # Markdown patterns to clean
    MARKDOWN_PATTERNS = [
        (r'\*\*(.+?)\*\*', r'\1'),    # **bold** → text
        (r'\*(.+?)\*', r'\1'),        # *italic* → text
        (r'__(.+?)__', r'\1'),        # __underline__ → text
        (r'_(.+?)_', r'\1'),          # _italic_ → text
        (r'###(.+)', r'\1'),          # ### heading → text
    ]
    
    # Allowed emojis (only in mentor encouragement)
    ALLOWED_EMOJIS = ['🌟', '💪', '🎯', '⚡']
    
    def __init__(self):
        self.emoji_regex = re.compile('|'.join(self.EMOJI_PATTERNS))
    
    def validate_and_fix_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fix entire dual response structure
        """
        fixed_response = response.copy()
        
        # Fix Professor response
        if 'primary' in fixed_response and fixed_response['primary']:
            fixed_response['primary'] = self._fix_professor_response(
                fixed_response['primary']
            )
        
        # Fix Mentor response
        if 'secondary' in fixed_response and fixed_response['secondary']:
            fixed_response['secondary'] = self._fix_mentor_response(
                fixed_response['secondary']
            )
        
        return fixed_response
    
    def _fix_professor_response(self, professor: Dict[str, Any]) -> Dict[str, Any]:
        """Fix Professor response formatting"""
        fixed = professor.copy()
        
        # Fix micro_lesson_sections
        if 'micro_lesson_sections' in fixed:
            sections = fixed['micro_lesson_sections']
            
            # Clean each section
            for key in ['concept_overview', 'step_by_step', 'real_life_analogy', 'mentor_tip']:
                if key in sections and sections[key]:
                    sections[key] = self._clean_text_strict(sections[key])
            
            # Clean formulas (preserve LaTeX)
            if 'key_formula' in sections:
                if isinstance(sections['key_formula'], list):
                    sections['key_formula'] = [
                        self._clean_formula(f) for f in sections['key_formula']
                    ]
                else:
                    sections['key_formula'] = self._clean_formula(sections['key_formula'])
            
            # Fix visual prompt
            if 'visual_prompt' in sections and sections['visual_prompt']:
                sections['visual_prompt'] = self._clean_text_strict(sections['visual_prompt'])
        
        # Fix response text
        if 'response' in fixed and fixed['response']:
            fixed['response'] = self._clean_text_strict(fixed['response'])
        
        return fixed
    
    def _fix_mentor_response(self, mentor: Dict[str, Any]) -> Dict[str, Any]:
        """Fix Mentor response formatting"""
        fixed = mentor.copy()
        
        # Fix mentor_sections
        if 'mentor_sections' in fixed:
            sections = fixed['mentor_sections']
            
            # Clean sections strictly (no emojis except encouragement)
            for key in ['motivation_spark', 'simplified_recap', 'confidence_tips']:
                if key in sections and sections[key]:
                    sections[key] = self._clean_text_strict(sections[key])
            
            # Encouragement can have allowed emojis
            if 'encouragement' in sections and sections['encouragement']:
                sections['encouragement'] = self._clean_text_allow_emojis(
                    sections['encouragement']
                )
        
        # Fix response text
        if 'response' in fixed and fixed['response']:
            fixed['response'] = self._clean_text_strict(fixed['response'])
        
        return fixed
    
    def _clean_text_strict(self, text: str) -> str:
        """
        Strict cleaning: remove ALL emojis and markdown
        """
        if not text:
            return ''
        
        cleaned = text
        
        # Remove ALL emojis
        cleaned = self.emoji_regex.sub('', cleaned)
        
        # Remove markdown formatting
        for pattern, replacement in self.MARKDOWN_PATTERNS:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # Remove specific problematic characters
        cleaned = cleaned.replace('✅', '✓')  # Replace checkmark emoji with symbol
        cleaned = cleaned.replace('❌', '✗')
        
        # Clean up multiple spaces
        cleaned = re.sub(r'  +', ' ', cleaned)
        
        # Clean up multiple newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def _clean_text_allow_emojis(self, text: str) -> str:
        """
        Soft cleaning: allow specific emojis, remove markdown
        """
        if not text:
            return ''
        
        cleaned = text
        
        # Remove markdown first
        for pattern, replacement in self.MARKDOWN_PATTERNS:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # Remove emojis except allowed ones
        # Build pattern that excludes allowed emojis
        allowed_pattern = '|'.join(re.escape(e) for e in self.ALLOWED_EMOJIS)
        
        # Remove unwanted emojis but keep allowed ones
        # This is tricky - let's keep it simple and just remove known bad ones
        bad_emojis = ['👇', '📚', '🧮', '🧠', '✅', '❌', '☑', '💡', '🔎', '📔', '💙']
        for emoji in bad_emojis:
            cleaned = cleaned.replace(emoji, '')
        
        # Remove numbered emojis
        cleaned = re.sub(r'[0-9]️⃣', '', cleaned)
        cleaned = cleaned.replace('🔟', '')
        
        # Clean up spaces
        cleaned = re.sub(r'  +', ' ', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def _clean_formula(self, formula: str) -> str:
        """
        Clean formula but PRESERVE LaTeX delimiters
        """
        if not formula:
            return ''
        
        # Remove emojis from formula
        cleaned = self.emoji_regex.sub('', formula)
        
        # Remove markdown but NOT LaTeX backslashes
        cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', cleaned)
        cleaned = re.sub(r'\*(?!\\)(.+?)\*', r'\1', cleaned)  # Don't remove \*
        
        # Clean up spaces
        cleaned = re.sub(r'  +', ' ', cleaned)
        
        return cleaned.strip()
    
    def validate_structure(self, response: Dict[str, Any]) -> List[str]:
        """
        Validate response structure and return list of issues
        """
        issues = []
        
        # Check Professor structure
        if 'primary' in response and response['primary']:
            primary = response['primary']
            if 'micro_lesson_sections' not in primary:
                issues.append("Missing micro_lesson_sections in Professor response")
            else:
                sections = primary['micro_lesson_sections']
                required = ['concept_overview', 'step_by_step']
                for req in required:
                    if req not in sections or not sections[req]:
                        issues.append(f"Missing or empty {req} in Professor response")
        
        # Check Mentor structure
        if 'secondary' in response and response['secondary']:
            secondary = response['secondary']
            if 'mentor_sections' not in secondary:
                issues.append("Missing mentor_sections in Mentor response")
            else:
                sections = secondary['mentor_sections']
                required = ['motivation_spark', 'encouragement']
                for req in required:
                    if req not in sections or not sections[req]:
                        issues.append(f"Missing or empty {req} in Mentor response")
        
        return issues
    
    def format_for_display(self, text: str) -> str:
        """
        Final formatting pass before sending to frontend
        """
        if not text:
            return ''
        
        # Ensure paragraphs are properly separated
        text = re.sub(r'\.(?=[A-Z])', '.\n\n', text)
        
        # Ensure bullets are on new lines
        text = re.sub(r'•', '\n•', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Fix numbered lists
        text = re.sub(r'(\d+\.)(?=\S)', r'\1 ', text)
        
        return text.strip()


# Global instance
format_validator = FormatValidator()
