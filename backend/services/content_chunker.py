"""
Content Chunker - Breaks long paragraphs into structured, scannable sections
Converts text-heavy responses into student-friendly chunks with visual hierarchy
"""
import re
from typing import Dict, List, Any


class ContentChunker:
    """
    Transforms AI responses into structured, visual sections:
    - Summary (2-3 lines)
    - Formula (if applicable)
    - Example (with Indian context)
    - Common Mistakes
    - Exam Tips
    - Quick Revision (bullet points)
    """
    
    @staticmethod
    def chunk_response(
        mentor_content: str,
        professor_content: str,
        subject: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Break content into structured sections
        
        Returns:
        {
            'greeting': 'Alright! Let me break this down...',
            'summary': '2-3 line summary',
            'formula': 'Key formulas',
            'example': 'Indian context example',
            'mistakes': 'Common mistakes list',
            'exam_tip': 'Exam-specific tip',
            'quick_revision': 'Bullet points'
        }
        """
        sections = {}
        
        # 1. Greeting - exciting opener
        sections['greeting'] = ContentChunker._create_greeting(question, subject)
        
        # 2. Summary - extract first 2-3 sentences
        sections['summary'] = ContentChunker._extract_summary(mentor_content)
        
        # 3. Formula - extract any formulas
        sections['formula'] = ContentChunker._extract_formulas(professor_content, mentor_content)
        
        # 4. Example - extract or create example
        sections['example'] = ContentChunker._extract_example(mentor_content, professor_content)
        
        # 5. Common Mistakes
        sections['mistakes'] = ContentChunker._extract_mistakes(professor_content)
        
        # 6. Exam Tip
        sections['exam_tip'] = ContentChunker._create_exam_tip(subject, question)
        
        # 7. Quick Revision - bullet points
        sections['quick_revision'] = ContentChunker._create_quick_revision(mentor_content, professor_content)
        
        return sections
    
    @staticmethod
    def _create_greeting(question: str, subject: str) -> str:
        """Create exciting greeting based on question"""
        greetings = [
            f"Alright! Let me break down {subject} for you... 🔥",
            f"Okay, here's the deal with this concept... 💡",
            f"Let's tackle this {subject} question together! 🎯",
            f"Cool question! Here's how to think about it... ✨",
            f"Alright, exam mode - let's master this! ⚡"
        ]
        import random
        return random.choice(greetings)
    
    @staticmethod
    def _extract_summary(content: str) -> str:
        """Extract 2-3 sentence summary"""
        # Get first 2-3 sentences
        sentences = re.split(r'[.!?]', content)
        summary_sentences = [s.strip() for s in sentences[:3] if s.strip()]
        summary = '. '.join(summary_sentences)
        
        # Ensure it's not too long
        if len(summary) > 200:
            summary = summary[:200] + '...'
        
        return summary + '.' if summary and not summary.endswith('.') else summary
    
    @staticmethod
    def _extract_formulas(professor_content: str, mentor_content: str) -> str:
        """Extract formulas with formatting"""
        combined = professor_content + ' ' + mentor_content
        
        # Look for equations with = sign
        formulas = []
        
        # Pattern 1: F = ma style
        formula_matches = re.findall(r'([A-Z][a-z]?\s*=\s*[^.!?\n]+)', combined)
        formulas.extend(formula_matches)
        
        # Pattern 2: LaTeX style \[ \]
        latex_matches = re.findall(r'\\\[(.*?)\\\]', combined)
        formulas.extend(latex_matches)
        
        if formulas:
            formatted = '**Key Formula:**\n\n'
            for formula in formulas[:2]:  # Max 2 formulas
                formatted += f"**{formula.strip()}**\n\n"
            
            # Add variable explanations
            formatted += "Where:\n"
            # Extract variables (capital letters)
            variables = re.findall(r'\b([A-Z])\b', formulas[0]) if formulas else []
            for var in set(variables[:3]):  # Max 3 variables
                formatted += f"• {var} = [Variable name]\n"
            
            return formatted
        
        return "**Formula:** Check detailed explanation above"
    
    @staticmethod
    def _extract_example(mentor_content: str, professor_content: str) -> str:
        """Extract Indian context example"""
        combined = mentor_content + ' ' + professor_content
        
        # Look for example keywords
        example_keywords = ['example', 'imagine', 'think of', 'like when', 'suppose', 'raju', 'market', 'cricket']
        
        for keyword in example_keywords:
            if keyword.lower() in combined.lower():
                # Find the paragraph with the keyword
                paragraphs = combined.split('\n\n')
                for para in paragraphs:
                    if keyword.lower() in para.lower():
                        return f"**Indian Context Example:**\n\n{para.strip()}"
        
        # Default example
        return "**Example:**\n\nThink of pushing a vegetable cart in an Indian market - the heavier the cart, the more force you need!"
    
    @staticmethod
    def _extract_mistakes(professor_content: str) -> str:
        """Extract or create common mistakes list"""
        mistakes_keywords = ['mistake', 'common error', 'avoid', 'wrong', 'don\'t', 'misconception']
        
        mistakes = []
        for keyword in mistakes_keywords:
            if keyword.lower() in professor_content.lower():
                # Found mistakes section
                sentences = re.split(r'[.!?]', professor_content)
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        mistakes.append(f"❌ {sentence.strip()}")
        
        if mistakes:
            return '\n\n'.join(mistakes[:3])  # Max 3 mistakes
        
        # Default mistakes
        return "❌ **Don't forget units!** Always include proper units\n\n❌ **Watch the signs** Positive vs negative matters\n\n❌ **Convert units** Make sure all units are consistent"
    
    @staticmethod
    def _create_exam_tip(subject: str, question: str) -> str:
        """Create exam-specific tip"""
        exam_tips = {
            'physics': '🎯 **JEE/NEET Pattern:** They often test concepts with numerical values - practice unit conversions!',
            'chemistry': '🎯 **Exam Tip:** Memorize key reactions and conditions - they love asking about catalysts and temperature!',
            'mathematics': '🎯 **Quick Trick:** If stuck, try substituting simple values to understand the pattern!',
            'biology': '🎯 **NEET Focus:** Diagrams score marks! Always label clearly and use proper terminology!'
        }
        
        for subject_key in exam_tips:
            if subject_key.lower() in subject.lower():
                return exam_tips[subject_key]
        
        return '🎯 **Exam Strategy:** Understand the concept first, then practice variations - that\'s how you ace it!'
    
    @staticmethod
    def _create_quick_revision(mentor_content: str, professor_content: str) -> str:
        """Create bullet point quick revision"""
        combined = mentor_content + ' ' + professor_content
        
        # Extract key sentences
        sentences = re.split(r'[.!?]', combined)
        key_points = []
        
        # Look for sentences with keywords
        keywords = ['is', 'means', 'defined as', 'formula', 'important', 'key', 'remember']
        
        for sentence in sentences[:10]:  # Check first 10 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 100:  # Not too short, not too long
                for keyword in keywords:
                    if keyword in sentence.lower():
                        # Clean and add as bullet
                        clean = sentence.replace('\n', ' ').strip()
                        if clean and clean not in key_points:
                            key_points.append(f"• {clean}")
                            break
            
            if len(key_points) >= 5:  # Max 5 points
                break
        
        if key_points:
            return '\n'.join(key_points)
        
        # Default revision points
        return "• Understand the core concept first\n• Memorize key formulas\n• Practice with examples\n• Note common mistakes\n• Review before exam"


def format_for_streaming(sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Format chunked sections for streaming
    
    Returns list of sections in streaming order:
    [
        {'type': 'greeting', 'content': '...'},
        {'type': 'summary', 'content': '...'},
        ...
    ]
    """
    streaming_order = [
        'greeting',
        'summary',
        'formula',
        'example',
        'mistakes',
        'exam_tip',
        'quick_revision'
    ]
    
    stream_sections = []
    for section_type in streaming_order:
        if section_type in sections and sections[section_type]:
            stream_sections.append({
                'type': section_type,
                'content': sections[section_type]
            })
    
    return stream_sections



