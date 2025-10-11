"""
Hybrid Response Parser for AI Tutor 2.1
Combines AI-powered parsing with rule-based fallback for reliable micro-lesson generation
"""
import re
from typing import Dict, Any, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage


class ResponseParser:
    """Parse AI responses into structured micro-lesson sections"""
    
    def __init__(self, emergent_llm_key: str):
        self.emergent_llm_key = emergent_llm_key
        self.parser_chat = None
    
    async def parse_response(self, ai_response: str, subject: str, topic: str) -> Dict[str, Any]:
        """
        Hybrid parsing: Try AI-powered parsing first, fallback to rule-based
        Returns structured sections for micro-lesson rendering
        """
        try:
            # Try AI-powered parsing
            parsed = await self._ai_parse(ai_response, subject, topic)
            if self._validate_parsed_structure(parsed):
                return parsed
        except Exception as e:
            print(f"AI parsing failed: {e}, falling back to rule-based")
        
        # Fallback to rule-based parsing
        return self._rule_based_parse(ai_response, subject, topic)
    
    async def _ai_parse(self, response: str, subject: str, topic: str) -> Dict[str, Any]:
        """AI-powered parsing using GPT-5"""
        if not self.parser_chat:
            self.parser_chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id="response_parser",
                system_message="""You are a response parser. Structure educational content into these sections:
1. concept_overview: 2-3 sentence summary
2. key_formula: Any mathematical formulas (LaTeX format)
3. step_by_step: Numbered steps or explanation
4. real_life_analogy: Practical example or analogy
5. mentor_tip: Motivational or strategic advice
6. visual_prompt: Brief description for visual generation

Return valid JSON only, no extra text."""
            ).with_model("openai", "gpt-5")
        
        parse_prompt = f"""Parse this {subject} explanation about {topic} into structured sections:

{response[:1000]}

Return JSON with keys: concept_overview, key_formula, step_by_step, real_life_analogy, mentor_tip, visual_prompt"""
        
        parser_response = await self.parser_chat.send_message(UserMessage(text=parse_prompt))
        
        # Extract JSON from response
        import json
        response_text = parser_response if isinstance(parser_response, str) else str(parser_response)
        
        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        raise ValueError("No valid JSON found in parser response")
    
    def _rule_based_parse(self, response: str, subject: str, topic: str) -> Dict[str, Any]:
        """Rule-based parsing as fallback"""
        sections = {
            'concept_overview': '',
            'key_formula': '',
            'step_by_step': '',
            'real_life_analogy': '',
            'mentor_tip': '',
            'visual_prompt': f"Generate a visual illustration for {topic} in {subject}"
        }
        
        # Split response into paragraphs
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        if len(paragraphs) == 0:
            sections['concept_overview'] = response[:200]
            return sections
        
        # First paragraph is usually concept overview
        sections['concept_overview'] = paragraphs[0] if paragraphs else ''
        
        # Look for formulas (LaTeX or equation patterns)
        formula_patterns = [
            r'\$\$.*?\$\$',
            r'\$.*?\$',
            r'[A-Za-z]\s*=\s*[^,\n]+',
            r'\b[A-Z][a-z]?\s*=\s*[\d\w\+\-\*/\^]+',
        ]
        for pattern in formula_patterns:
            formulas = re.findall(pattern, response)
            if formulas:
                sections['key_formula'] = ' '.join(formulas[:3])
                break
        
        # Look for numbered steps
        step_patterns = [
            r'(?:Step\s+\d+|^\d+\.|^●|^•|\*\*Step)',
        ]
        for pattern in step_patterns:
            if re.search(pattern, response, re.MULTILINE | re.IGNORECASE):
                # Extract steps section
                steps_text = '\n'.join([p for p in paragraphs if re.search(pattern, p, re.IGNORECASE)])
                if steps_text:
                    sections['step_by_step'] = steps_text
                    break
        
        # Look for analogies or examples
        analogy_keywords = ['for example', 'imagine', 'think of', 'like', 'similar to', 'real-world', 'real life']
        for para in paragraphs:
            if any(keyword in para.lower() for keyword in analogy_keywords):
                sections['real_life_analogy'] = para
                break
        
        # Look for tips or advice
        tip_keywords = ['tip:', 'remember', 'important', 'note:', 'pro tip', 'keep in mind']
        for para in paragraphs:
            if any(keyword in para.lower() for keyword in tip_keywords):
                sections['mentor_tip'] = para
                break
        
        # If no specific sections found, distribute content
        if not sections['step_by_step'] and len(paragraphs) > 1:
            sections['step_by_step'] = '\n\n'.join(paragraphs[1:min(3, len(paragraphs))])
        
        if not sections['real_life_analogy'] and len(paragraphs) > 3:
            sections['real_life_analogy'] = paragraphs[-1]
        
        return sections
    
    def _validate_parsed_structure(self, parsed: Dict[str, Any]) -> bool:
        """Validate that parsed structure has required fields"""
        required_fields = ['concept_overview']
        return all(field in parsed for field in required_fields)
    
    def extract_formulas(self, text: str) -> List[str]:
        """Extract all LaTeX formulas from text"""
        formulas = []
        
        # Match LaTeX delimiters
        latex_patterns = [
            r'\$\$(.*?)\$\$',  # Display math
            r'\$(.*?)\$',      # Inline math
            r'\\begin\{equation\}(.*?)\\end\{equation\}',
            r'\\begin\{align\}(.*?)\\end\{align\}',
        ]
        
        for pattern in latex_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            formulas.extend(matches)
        
        return formulas