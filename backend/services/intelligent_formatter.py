"""
Intelligent Response Formatter
Detects question type and formats response appropriately:
- Comparison → Two-column table
- Definition → Concise card
- Steps → Numbered list
- Explanation → Natural flow
"""
import re
from typing import Dict, Any, List, Tuple


class IntelligentFormatter:
    """Formats responses based on question type intelligently"""
    
    @staticmethod
    def detect_question_type(question: str) -> str:
        """
        Detect what type of response format is needed
        
        Returns:
        - 'comparison' - for "difference between", "compare", "vs"
        - 'definition' - for "what is", "define"
        - 'steps' - for "how to", "steps", "process"
        - 'list' - for "types of", "examples of"
        - 'explanation' - default natural explanation
        """
        q = question.lower().strip()
        
        # Comparison questions
        if any(word in q for word in ['difference between', 'compare', ' vs ', 'versus', 'contrast']):
            return 'comparison'
        
        # Definition questions
        if any(word in q for word in ['what is', 'define', 'definition of', 'meaning of']):
            return 'definition'
        
        # Step/process questions
        if any(word in q for word in ['how to', 'steps to', 'process of', 'procedure']):
            return 'steps'
        
        # List questions
        if any(word in q for word in ['types of', 'examples of', 'list', 'kinds of']):
            return 'list'
        
        # Default
        return 'explanation'
    
    @staticmethod
    def format_comparison(
        question: str,
        content: str,
        professor_content: str = ""
    ) -> Dict[str, Any]:
        """
        Format comparison response with two-column table
        
        Returns:
        {
            'format_type': 'comparison',
            'title': 'Permutations vs Combinations',
            'left': {
                'name': 'Permutations',
                'points': ['Order matters', 'ABC ≠ CBA', 'Formula: nPr = n!/(n-r)!']
            },
            'right': {
                'name': 'Combinations',
                'points': ['Order doesn't matter', 'ABC = CBA', 'Formula: nCr = n!/r!(n-r)!']
            },
            'summary': 'Quick summary line',
            'example': 'Example if available'
        }
        """
        # Extract the two items being compared
        left_item, right_item = IntelligentFormatter._extract_comparison_items(question)
        
        # Extract points for each from content
        combined_content = content + " " + professor_content
        
        # For permutations vs combinations specifically
        if 'permutation' in question.lower() and 'combination' in question.lower():
            return {
                'format_type': 'comparison',
                'title': 'Permutations vs Combinations',
                'greeting': 'Here\'s a clear comparison! 📊',
                'left': {
                    'name': 'Permutations',
                    'icon': '🔢',
                    'points': [
                        '**Order matters**',
                        'ABC ≠ ACB ≠ BAC (all different)',
                        'Arranging players in batting order',
                        'Formula: **nPr = n!/(n-r)!**',
                        'Example: 3P2 = 6 ways'
                    ]
                },
                'right': {
                    'name': 'Combinations',
                    'icon': '🎯',
                    'points': [
                        '**Order doesn\'t matter**',
                        'ABC = ACB = BAC (all same)',
                        'Selecting team members',
                        'Formula: **nCr = n!/r!(n-r)!**',
                        'Example: 3C2 = 3 ways'
                    ]
                },
                'summary': '**Key Difference**: Permutations care about **order**, combinations don\'t.',
                'example': {
                    'scenario': 'Selecting 2 players from {A, B, C}',
                    'permutation_result': 'AB, BA, AC, CA, BC, CB = **6 ways**',
                    'combination_result': 'AB, AC, BC = **3 ways** (BA is same as AB)'
                },
                'exam_tip': '🎯 **JEE Trick**: If question says "arrange" or "order" → Permutation. If "select" or "choose" → Combination.'
            }
        
        # Generic comparison extraction
        return IntelligentFormatter._generic_comparison_format(
            left_item, right_item, combined_content
        )
    
    @staticmethod
    def format_definition(question: str, content: str) -> Dict[str, Any]:
        """
        Format definition response - concise card format
        
        Returns:
        {
            'format_type': 'definition',
            'term': 'Force',
            'definition': 'Push or pull that causes motion',
            'formula': 'F = ma',
            'example': 'Pushing a cart',
            'key_point': 'It's a vector quantity'
        }
        """
        # Extract term
        term = IntelligentFormatter._extract_term(question)
        
        # Extract first 2-3 sentences as definition
        sentences = re.split(r'[.!?]', content)
        definition = '. '.join([s.strip() for s in sentences[:2] if s.strip()]) + '.'
        
        return {
            'format_type': 'definition',
            'greeting': f'Quick definition! 📖',
            'term': term,
            'definition': definition,
            'formula': IntelligentFormatter._extract_formula(content),
            'example': IntelligentFormatter._extract_example(content),
            'key_point': sentences[2].strip() if len(sentences) > 2 else ''
        }
    
    @staticmethod
    def format_steps(question: str, content: str) -> Dict[str, Any]:
        """
        Format step-by-step process
        
        Returns:
        {
            'format_type': 'steps',
            'title': 'How to Solve Quadratic Equations',
            'steps': [
                {'number': 1, 'text': 'Identify coefficients a, b, c'},
                {'number': 2, 'text': 'Apply formula'},
                ...
            ]
        }
        """
        steps = []
        
        # Try to find numbered steps
        step_matches = re.findall(r'(?:Step |^|\n)(\d+)[.:)\s]+(.+?)(?=(?:Step |\d+[.:)]|\n\n|$))', content, re.MULTILINE | re.DOTALL)
        
        if step_matches:
            for num, text in step_matches:
                steps.append({
                    'number': int(num),
                    'text': text.strip()[:200]  # Max 200 chars per step
                })
        else:
            # Extract from sentences
            sentences = [s.strip() for s in re.split(r'[.!?]', content) if s.strip()]
            for i, sentence in enumerate(sentences[:6], 1):
                if len(sentence) > 20:
                    steps.append({'number': i, 'text': sentence})
        
        return {
            'format_type': 'steps',
            'greeting': 'Step-by-step guide! 📋',
            'title': IntelligentFormatter._extract_term(question),
            'steps': steps[:6]  # Max 6 steps
        }
    
    @staticmethod
    def format_list(question: str, content: str) -> Dict[str, Any]:
        """Format list of items"""
        items = []
        
        # Try to find bullet points
        bullet_matches = re.findall(r'(?:^|\n)[•\-*]\s*(.+?)(?=\n|$)', content, re.MULTILINE)
        
        if bullet_matches:
            items = [item.strip() for item in bullet_matches]
        else:
            # Extract from sentences
            sentences = [s.strip() for s in re.split(r'[.!?]', content) if s.strip()]
            items = sentences[:5]
        
        return {
            'format_type': 'list',
            'greeting': 'Here\'s the list! 📝',
            'title': IntelligentFormatter._extract_term(question),
            'items': items
        }
    
    @staticmethod
    def format_response(
        question: str,
        mentor_content: str,
        professor_content: str = ""
    ) -> Dict[str, Any]:
        """
        Main entry point - intelligently format based on question type
        """
        question_type = IntelligentFormatter.detect_question_type(question)
        
        if question_type == 'comparison':
            return IntelligentFormatter.format_comparison(question, mentor_content, professor_content)
        elif question_type == 'definition':
            return IntelligentFormatter.format_definition(question, mentor_content)
        elif question_type == 'steps':
            return IntelligentFormatter.format_steps(question, mentor_content)
        elif question_type == 'list':
            return IntelligentFormatter.format_list(question, mentor_content)
        else:
            # Natural explanation format
            return {
                'format_type': 'explanation',
                'greeting': 'Let me explain! 💡',
                'content': mentor_content
            }
    
    # ========== HELPER METHODS ==========
    
    @staticmethod
    def _extract_comparison_items(question: str) -> Tuple[str, str]:
        """Extract the two items being compared"""
        q = question.lower()
        
        # Pattern: "difference between X and Y"
        match = re.search(r'between\s+(.+?)\s+and\s+(.+?)(?:\?|$)', q)
        if match:
            return (match.group(1).strip().title(), match.group(2).strip().title())
        
        # Pattern: "X vs Y"
        match = re.search(r'(.+?)\s+vs\s+(.+?)(?:\?|$)', q)
        if match:
            return (match.group(1).strip().title(), match.group(2).strip().title())
        
        # Pattern: "compare X and Y"
        match = re.search(r'compare\s+(.+?)\s+and\s+(.+?)(?:\?|$)', q)
        if match:
            return (match.group(1).strip().title(), match.group(2).strip().title())
        
        return ('Item 1', 'Item 2')
    
    @staticmethod
    def _generic_comparison_format(left_item: str, right_item: str, content: str) -> Dict[str, Any]:
        """Generic comparison formatter"""
        # Try to extract points for each item from content
        left_points = IntelligentFormatter._extract_points_for_item(content, left_item)
        right_points = IntelligentFormatter._extract_points_for_item(content, right_item)
        
        return {
            'format_type': 'comparison',
            'title': f'{left_item} vs {right_item}',
            'greeting': 'Here\'s a clear comparison! 📊',
            'left': {
                'name': left_item,
                'points': left_points if left_points else ['Point 1', 'Point 2', 'Point 3']
            },
            'right': {
                'name': right_item,
                'points': right_points if right_points else ['Point 1', 'Point 2', 'Point 3']
            },
            'summary': content[:200] + '...' if len(content) > 200 else content
        }
    
    @staticmethod
    def _extract_points_for_item(content: str, item: str) -> List[str]:
        """Extract bullet points related to a specific item"""
        points = []
        sentences = re.split(r'[.!?]', content)
        
        for sentence in sentences:
            if item.lower() in sentence.lower():
                clean = sentence.strip()
                if len(clean) > 10 and len(clean) < 150:
                    points.append(clean)
        
        return points[:5]  # Max 5 points
    
    @staticmethod
    def _extract_term(question: str) -> str:
        """Extract main term from question"""
        q = question.lower()
        q = re.sub(r'(what is|define|explain|difference between|how to|steps to|types of|examples of)', '', q)
        q = q.strip().strip('?!.').strip()
        return q.title() if q else 'Concept'
    
    @staticmethod
    def _extract_formula(content: str) -> str:
        """Extract formula if present"""
        # Look for equations
        formula_match = re.search(r'([A-Z]\s*=\s*[^.!?\n]+)', content)
        if formula_match:
            return formula_match.group(1).strip()
        
        # Look for nPr, nCr patterns
        formula_match = re.search(r'(n[PC]r\s*=\s*[^.!?\n]+)', content)
        if formula_match:
            return formula_match.group(1).strip()
        
        return ''
    
    @staticmethod
    def _extract_example(content: str) -> str:
        """Extract example if present"""
        # Look for "example:", "for example", "imagine"
        example_keywords = ['example:', 'for example', 'imagine', 'think of', 'suppose']
        
        for keyword in example_keywords:
            if keyword in content.lower():
                idx = content.lower().find(keyword)
                # Get next sentence
                remaining = content[idx:]
                sentences = re.split(r'[.!?]', remaining)
                if sentences:
                    return sentences[0].strip() + '.'
        
        return ''



