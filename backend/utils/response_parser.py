"""
Hybrid Response Parser for AI Tutor 2.1
Combines AI-powered parsing with rule-based fallback for reliable micro-lesson generation
"""
import re
from typing import Dict, Any, List, Optional
from services.llm_compat import LlmChat, UserMessage


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
                system_message="""You are a response parser optimizing educational content for readability.

Extract and structure content into these sections:
1. concept_overview: 2-3 sentence summary (clean, no emojis)
2. key_formula: Array of LaTeX formulas (preserve \\[ \\] delimiters)
3. step_by_step: Numbered explanation (preserve 1., 2., 3. format)
4. real_life_analogy: Practical example (clean text)
5. mentor_tip: Strategic advice (clean text)
6. visual_prompt: Description for visual generation

CRITICAL PARSING RULES:
- Remove ALL emoji characters from text
- Preserve LaTeX delimiters: \\[, \\], \\(, \\)
- Remove markdown symbols: **, *, __, _
- Keep numbered lists as: 1., 2., 3. (not 1️⃣, 2️⃣)
- Remove special characters: ✅, ❌, 💡, 🔎
- Clean output = readable on any screen

Return valid JSON only, no extra text or markdown."""
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
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
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
    
    def sanitize_text(self, text: str) -> str:
        """
        Enhanced sanitization for database storage
        Removes escaped characters, special symbols, and ensures markdown compatibility
        """
        if not text:
            return ''
        
        # Phase 1: Remove ALL escaped characters first (before DB save)
        cleaned = text
        
        # Remove escaped quotes, slashes, and problematic escapes
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace("\\'", "'")
        cleaned = cleaned.replace('\\/', '/')
        cleaned = cleaned.replace('\\n', '\n')
        cleaned = cleaned.replace('\\r', '\r')
        cleaned = cleaned.replace('\\t', '\t')
        
        # Remove double and triple backslashes (preserve single for LaTeX)
        cleaned = re.sub(r'\\{3,}', r'\\', cleaned)  # \\\\ → \
        cleaned = cleaned.replace('\\\\', '\\')      # \\ → \
        
        # Remove JSON escape artifacts
        cleaned = cleaned.replace('\\u00a0', ' ')    # Non-breaking space
        cleaned = cleaned.replace('\\u2009', ' ')    # Thin space
        cleaned = cleaned.replace('\\u202f', ' ')    # Narrow no-break space
        cleaned = cleaned.replace('\\u200b', '')     # Zero-width space
        
        # Remove problematic Unicode sequences that appear as literals
        cleaned = re.sub(r'\\u[0-9a-fA-F]{4}', '', cleaned)
        
        # Aggressive emoji removal with extended patterns
        emoji_pattern = re.compile(
            "["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\u2190-\u21FF"          # Arrows
            "\u2600-\u26FF"          # Miscellaneous Symbols
            "\u2700-\u27BF"          # Dingbats
            "\u3000-\u303F"          # CJK Symbols and Punctuation
            "\u24C2-\u24FF"          # Enclosed Alphanumerics
            "\u200d"                 # Zero width joiner
            "\ufe0f"                 # Variation selector
            "]+", 
            flags=re.UNICODE
        )
        cleaned = emoji_pattern.sub('', cleaned)
        
        # Remove specific problematic symbols that bypass regex
        bad_symbols = ['✅', '❌', '☑', '💡', '🔎', '📔', '💙', '👇', '📚', '🧮', '🧠', 
                      '🎯', '⚡', '💪', '🌟', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', 
                      '7️⃣', '8️⃣', '9️⃣', '🔟', '✳️', '❗', '❓', '⭐', '🎪']
        for symbol in bad_symbols:
            cleaned = cleaned.replace(symbol, '')
        
        # Clean markdown symbols for DB storage (markdown-friendly)
        cleaned = re.sub(r'\*{2,}(.+?)\*{2,}', r'\1', cleaned)  # **bold** → text
        cleaned = re.sub(r'_{2,}(.+?)_{2,}', r'\1', cleaned)    # __text__ → text
        cleaned = re.sub(r'`{1,3}(.+?)`{1,3}', r'\1', cleaned)  # `code` → code
        cleaned = re.sub(r'#{1,6}\s*(.+)', r'\1', cleaned)      # # heading → text
        
        # Remove non-breaking spaces and special unicode
        cleaned = cleaned.replace('\u00a0', ' ')
        cleaned = cleaned.replace('\xa0', ' ')
        cleaned = cleaned.replace('\u200b', '')
        cleaned = cleaned.replace('\u2009', ' ')
        cleaned = cleaned.replace('\u202f', ' ')
        
        # Clean up excessive whitespace
        cleaned = re.sub(r' {3,}', ' ', cleaned)
        cleaned = re.sub(r'  +', ' ', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in cleaned.split('\n')]
        cleaned = '\n'.join(line for line in lines if line)
        
        return cleaned.strip()
    
    def clean_text(self, text: str) -> str:
        """
        Legacy method - now calls sanitize_text for consistency
        """
        return self.sanitize_text(text)    
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