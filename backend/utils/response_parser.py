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
        """Enhanced rule-based parsing with better extraction"""
        sections = {
            'concept_overview': '',
            'key_formula': [],
            'step_by_step': '',
            'real_life_analogy': '',
            'mentor_tip': '',
            'visual_prompt': f"Generate a visual illustration for {topic} in {subject}"
        }
        
        # Split response into paragraphs and lines
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        
        if len(paragraphs) == 0:
            sections['concept_overview'] = response[:300]
            return sections
        
        # Extract concept overview (first substantial paragraph, up to 300 chars)
        for para in paragraphs[:3]:
            if len(para) > 50 and len(para) < 500:
                sections['concept_overview'] = self.clean_text(para)
                break
        
        if not sections['concept_overview']:
            sections['concept_overview'] = self.clean_text(paragraphs[0][:300] if paragraphs else response[:300])
        
        # Enhanced formula extraction
        formulas = self.extract_formulas(response)
        
        # Also look for equations in text (e.g., F = ma, E = mc^2)
        simple_equation_pattern = r'(?:^|[^a-zA-Z])([A-Z][a-z]?\s*=\s*[^\.,\n]{2,40})(?:[,\.]|$)'
        simple_equations = re.findall(simple_equation_pattern, response, re.MULTILINE)
        
        all_formulas = list(set(formulas + simple_equations))
        sections['key_formula'] = [f.strip() for f in all_formulas if len(f.strip()) > 2][:3]
        
        # Extract step-by-step content
        step_blocks = []
        current_block = []
        in_step_section = False
        
        for line in lines:
            # Check if line starts a step
            if re.match(r'^(\d+[\.\):]|Step\s+\d+|[•\-\*]\s)', line, re.IGNORECASE):
                if current_block:
                    step_blocks.append('\n'.join(current_block))
                current_block = [line]
                in_step_section = True
            elif in_step_section and line and not line.startswith('#'):
                current_block.append(line)
            elif in_step_section and not line:
                if current_block:
                    step_blocks.append('\n'.join(current_block))
                    current_block = []
                in_step_section = False
        
        if current_block:
            step_blocks.append('\n'.join(current_block))
        
        if step_blocks:
            sections['step_by_step'] = self.clean_text('\n\n'.join(step_blocks[:5]))
        
        # Extract real-life examples and applications
        example_keywords = ['example', 'application', 'real-world', 'real life', 'practical', 'consider', 'imagine']
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in example_keywords):
                # Get this paragraph and maybe the next one
                example_text = para
                if i + 1 < len(paragraphs) and len(paragraphs[i + 1]) < 300:
                    example_text += '\n\n' + paragraphs[i + 1]
                sections['real_life_analogy'] = self.clean_text(example_text[:500])
                break
        
        # Extract tips and important notes
        tip_indicators = ['tip', 'remember', 'important', 'note', 'key point', 'pro tip', 'keep in mind', '💡', '⚠️']
        for para in paragraphs:
            para_lower = para.lower()
            if any(tip in para_lower for tip in tip_indicators):
                sections['mentor_tip'] = self.clean_text(para[:400])
                break
        
        # If no specific sections, intelligently distribute
        if not sections['step_by_step'] and len(paragraphs) > 2:
            # Take middle paragraphs as step-by-step
            start_idx = 1 if sections['concept_overview'] else 0
            end_idx = -1 if sections['real_life_analogy'] else len(paragraphs)
            sections['step_by_step'] = self.clean_text('\n\n'.join(paragraphs[start_idx:min(end_idx, start_idx + 3)]))
        
        if not sections['real_life_analogy'] and len(paragraphs) > 3:
            # Last paragraph as analogy
            sections['real_life_analogy'] = self.clean_text(paragraphs[-1])
        
        if not sections['mentor_tip'] and len(paragraphs) > 4:
            # Second to last as tip
            sections['mentor_tip'] = self.clean_text(paragraphs[-2])
        
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
    
    def clean_text(self, text: str) -> str:
        """
        Comprehensive text cleaning - preserves LaTeX, removes artifacts
        AI Tutor 2.4 enhancement - Student-friendly cleaning
        """
        if not text:
            return ''
        
        # Remove markdown formatting (bold, italic)
        cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Remove **bold**
        cleaned = re.sub(r'\*(.+?)\*', r'\1', cleaned)   # Remove *italic*
        cleaned = re.sub(r'__(.+?)__', r'\1', cleaned)   # Remove __bold__
        cleaned = re.sub(r'_(.+?)_', r'\1', cleaned)     # Remove _italic_
        
        # Remove emoji-like checkmarks and boxes (but keep regular emojis)
        cleaned = cleaned.replace('✅', '')
        cleaned = cleaned.replace('❌', '')
        cleaned = cleaned.replace('☑', '')
        cleaned = cleaned.replace('📘', '📘')  # Keep this one
        cleaned = cleaned.replace('📙', '')
        cleaned = cleaned.replace('📗', '')
        
        # First pass: Remove escape sequences (but preserve LaTeX delimiters)
        # We need to keep \[, \], \(, \) for LaTeX rendering
        # Replace escaped quotes and newlines
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace("\\'", "'")
        cleaned = cleaned.replace('\\/', '/')
        
        # Remove double backslashes completely (LaTeX uses single backslash)
        cleaned = cleaned.replace('\\\\', '')
        
        # Remove non-breaking spaces and special unicode
        cleaned = cleaned.replace('\u00a0', ' ')
        cleaned = cleaned.replace('\xa0', ' ')
        cleaned = cleaned.replace('\u200b', '')  # Zero-width space
        cleaned = cleaned.replace('\u2009', ' ')  # Thin space
        cleaned = cleaned.replace('\u202f', ' ')  # Narrow no-break space
        
        # Clean up multiple spaces (but preserve intentional spacing)
        cleaned = re.sub(r' {3,}', '  ', cleaned)
        cleaned = re.sub(r'  +', ' ', cleaned)
        
        # Clean up multiple newlines (max 2 consecutive)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in cleaned.split('\n')]
        cleaned = '\n'.join(lines)
        
        return cleaned.strip()
    
    def split_mentor_response(self, mentor_text: str) -> Dict[str, str]:
        """
        Split mentor response into structured emotional sections
        AI Tutor 2.4 feature
        """
        cleaned = self.clean_text(mentor_text)
        
        # Initialize sections
        sections = {
            'motivation_spark': '',
            'simplified_recap': '',
            'confidence_tips': '',
            'encouragement': ''
        }
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', cleaned)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            sections['motivation_spark'] = cleaned[:150]
            return sections
        
        # First 1-2 sentences as motivation spark
        sections['motivation_spark'] = '. '.join(sentences[:min(2, len(sentences))]) + '.'
        
        # Identify key points (numbered, bulleted, or "Remember", "Important")
        key_points = []
        remaining = []
        
        for sentence in sentences[2:]:
            sentence_lower = sentence.lower()
            if (re.match(r'^\d+[\.\)]', sentence) or 
                sentence.startswith('•') or 
                sentence.startswith('-') or
                any(keyword in sentence_lower for keyword in ['remember', 'important', 'key', 'tip'])):
                key_points.append(sentence)
            else:
                remaining.append(sentence)
        
        # Build simplified recap (bullet points)
        if key_points:
            sections['simplified_recap'] = '\n'.join([f"• {point.strip()}" for point in key_points[:3]])
        elif len(remaining) > 0:
            sections['simplified_recap'] = '\n'.join([f"• {sent.strip()}" for sent in remaining[:3]])
        
        # Confidence tips (action-oriented sentences)
        confidence_words = ['practice', 'try', 'start', 'begin', 'approach', 'focus', 'study', 'learn']
        tips = [s for s in remaining if any(word in s.lower() for word in confidence_words)]
        if tips:
            sections['confidence_tips'] = ' '.join(tips[:2])
        
        # Last sentence as encouragement
        if len(sentences) > 3:
            sections['encouragement'] = sentences[-1].strip() + '.'
        elif not sections['encouragement']:
            sections['encouragement'] = "You've got this! Keep up the great work! 🌟"
        
        # Trim each section to reasonable length
        for key in sections:
            if sections[key] and len(sections[key]) > 200:
                sections[key] = sections[key][:197] + '...'
        
        return sections