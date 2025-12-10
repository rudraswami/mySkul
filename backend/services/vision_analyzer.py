"""
Vision Analyzer Service
Analyzes images/screenshots uploaded by students using Kimi-VL (primary)
Extracts text, diagrams, equations, and provides intelligent answers

SUPPORTS: Kimi-VL (primary), Qwen-VL (secondary), GPT-4o Vision (fallback)

Kimi-VL Capabilities:
- OCR text extraction
- Diagram understanding
- Math formula extraction
- Textbook page analysis
- Handwritten notes recognition
- Image → text → reasoning flows
"""
import logging
import base64
import os
import re
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """Analyzes student-uploaded images using Kimi-VL, Qwen-VL, or GPT-4 Vision"""
    
    def __init__(self):
        # Load settings - try from config first, then env vars directly
        try:
            from core.config import settings
            kimi_key_from_settings = settings.KIMI_VISION_API_KEY
            kimi_model_from_settings = settings.KIMI_VISION_MODEL
            kimi_base_from_settings = settings.KIMI_VISION_BASE_URL
            use_kimi_from_settings = settings.USE_KIMI_VISION
        except Exception as e:
            logger.warning(f"⚠️ Could not load settings: {e}, using env vars directly")
            kimi_key_from_settings = None
            kimi_model_from_settings = None
            kimi_base_from_settings = None
            use_kimi_from_settings = True
        
        # Kimi-VL for vision (PRIMARY) - use hardcoded fallback if settings fail
        # IMPORTANT: Kimi uses api.moonshot.AI not api.moonshot.CN
        self.kimi_api_key = (
            kimi_key_from_settings or 
            os.environ.get('KIMI_VISION_API_KEY') or 
            "sk-aEzUhSMy0Izz6bUnbJiwtpBxDADeI94vByaUTqOvOV6y2EP9"  # Default key
        )
        self.kimi_model = (
            kimi_model_from_settings or 
            os.environ.get('KIMI_VISION_MODEL') or 
            "moonshot-v1-8k-vision-preview"  # Use 8k model (most stable)
        )
        self.kimi_base_url = (
            kimi_base_from_settings or 
            os.environ.get('KIMI_VISION_BASE_URL') or 
            "https://api.moonshot.ai/v1"  # CORRECT: moonshot.AI not moonshot.CN
        )
        # Enable Kimi if we have a key (always try it first)
        self.use_kimi = bool(self.kimi_api_key) and (use_kimi_from_settings if use_kimi_from_settings is not None else True)
        
        # Qwen-VL for vision (SECONDARY fallback)
        try:
            from core.config import settings
            self.qwen_api_key = settings.QWEN_VL_API_KEY
            self.qwen_model = settings.QWEN_VL_MODEL
            self.qwen_base_url = settings.QWEN_VL_BASE_URL
            self.use_qwen = settings.USE_QWEN_VISION and bool(self.qwen_api_key)
        except:
            self.qwen_api_key = os.environ.get('QWEN_VL_API_KEY', '')
            self.qwen_model = os.environ.get('QWEN_VL_MODEL', 'qwen-vl-max')
            self.qwen_base_url = os.environ.get('QWEN_VL_BASE_URL', '')
            self.use_qwen = bool(self.qwen_api_key)
        
        # GPT-4o Vision (FINAL fallback) - needs valid OpenAI key
        self.openai_key = os.environ.get('OPENAI_API_KEY')  # Only use actual OpenAI key
        
        # Log initialization with full debug info
        logger.info(f"🔍 VisionAnalyzer init: use_kimi={self.use_kimi}, kimi_key={'***' + self.kimi_api_key[-4:] if self.kimi_api_key else 'None'}")
        logger.info(f"🔍 VisionAnalyzer init: use_qwen={self.use_qwen}, openai_key={'set' if self.openai_key else 'NOT SET'}")
        
        if self.use_kimi:
            logger.info(f"✅ VisionAnalyzer using Kimi-VL ({self.kimi_model}) [PRIMARY]")
        elif self.use_qwen:
            logger.info(f"✅ VisionAnalyzer using Qwen-VL ({self.qwen_model}) [SECONDARY]")
        elif self.openai_key:
            logger.info(f"✅ VisionAnalyzer using GPT-4o Vision [FALLBACK]")
        else:
            logger.warning(f"⚠️ VisionAnalyzer: NO valid vision API configured!")
    
    async def analyze_image(
        self,
        image_data: str,
        question: str,
        subject_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze image and extract relevant information using Kimi-VL (primary)
        
        Args:
            image_data: Base64 encoded image or URL
            question: Student's question about the image
            subject_hint: Optional subject hint
        
        Returns:
            {
                'ocr_text': 'Full extracted text from image...',
                'diagram_insight': 'Diagram shows a circuit with...',
                'semantic_tags': ['physics', 'circuit', 'resistor'],
                'raw_vision_response': 'Full model response...',
                'extracted_text': 'Equation: F = ma...',
                'content_type': 'equation|diagram|text|mixed',
                'analysis': 'The image shows Newton's second law...',
                'subject_detected': 'Physics',
                'key_elements': ['force', 'mass', 'acceleration']
            }
        """
        try:
            import litellm
            
            # Prepare image for API
            if image_data.startswith('http'):
                image_url = image_data
            else:
                image_url = f"data:image/jpeg;base64,{image_data}"
            
            # Vision system prompt optimized for Kimi-VL educational content analysis
            vision_system = """You are Kimi-VL, an expert vision-language model analyzing educational images for Indian students (JEE, NEET, CBSE).

Your capabilities:
- OCR: Extract ALL text precisely (including equations, formulas, handwriting)
- Diagram Analysis: Understand circuit diagrams, graphs, molecular structures, anatomical diagrams
- Formula Recognition: Identify and extract mathematical/scientific formulas
- Textbook Understanding: Parse textbook pages, examples, solved problems
- Handwriting Recognition: Read handwritten notes and solutions

CRITICAL: Extract EXACTLY what is shown in the image. NO creative interpretation.

Analyze and extract:
1. **Content Type**: MCQ question | Numerical problem | Diagram | Textbook page | Handwritten notes | Equation | Graph | Circuit
2. **OCR Text**: Extract ALL visible text word-for-word (equations, questions, options, labels)
3. **Subject**: Physics | Chemistry | Mathematics | Biology
4. **Diagram Insight**: Describe what the diagram/figure shows (if present)
5. **Key Concepts**: Main topics/formulas visible
6. **Semantic Tags**: List relevant topic tags

FORMAT YOUR RESPONSE AS:
**Content Type**: [MCQ|Problem|Diagram|etc]
**Subject**: [Subject name]

**OCR Text**:
[Exact text from image - include ALL text, equations, labels]

**Question** (if applicable):
[Full question text]

**Options** (if MCQ):
A) [exact text]
B) [exact text]
C) [exact text]  
D) [exact text]

**Diagram Insight**:
[What the diagram shows, key elements, relationships]

**Key Concepts**: [List main concepts]
**Semantic Tags**: [physics, mechanics, newton, force, etc.]

Be FACTUAL and PRECISE. Extract exactly what you see."""

            raw_response = None
            model_used = None
            
            # PRIMARY: Try Kimi-VL first
            if self.use_kimi:
                logger.info(f"📷 Calling Kimi-VL ({self.kimi_model}) for image analysis [PRIMARY]...")
                try:
                    response = await self._call_kimi_vision(image_url, question, vision_system)
                    raw_response = response.choices[0].message.content
                    model_used = "kimi-vl"
                    logger.info("✅ Kimi-VL analysis successful")
                except Exception as kimi_error:
                    logger.warning(f"⚠️ Kimi-VL failed: {kimi_error}")
                    raw_response = None
            
            # SECONDARY: Try Qwen-VL if Kimi failed
            if raw_response is None and self.use_qwen:
                logger.info(f"📷 Calling Qwen-VL ({self.qwen_model}) for image analysis [SECONDARY]...")
                try:
                    response = await self._call_qwen_vision(image_url, question, vision_system)
                    raw_response = response.choices[0].message.content
                    model_used = "qwen-vl"
                    logger.info("✅ Qwen-VL analysis successful")
                except Exception as qwen_error:
                    logger.warning(f"⚠️ Qwen-VL failed: {qwen_error}")
                    raw_response = None
            
            # FALLBACK: Use GPT-4o Vision
            if raw_response is None:
                logger.info(f"📷 Calling GPT-4o Vision [FALLBACK] (image size: {len(image_data)} chars)")
                response = await self._call_gpt4_vision(image_url, question, vision_system)
                raw_response = response.choices[0].message.content
                model_used = "gpt-4o"
            
            # Parse structured output
            result = self._parse_vision_response(raw_response, subject_hint, model_used)
            
            logger.info(f"✅ Image analyzed via {model_used}: {result['content_type']}, Subject: {result['subject_detected']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Image analysis failed: {e}", exc_info=True)
            return {
                'ocr_text': '',
                'diagram_insight': '',
                'semantic_tags': [],
                'raw_vision_response': '',
                'extracted_text': '',
                'content_type': 'unknown',
                'analysis': 'Failed to analyze image',
                'subject_detected': subject_hint or 'General',
                'key_elements': [],
                'has_equations': False,
                'has_diagram': False,
                'error': str(e),
                'model_used': 'none'
            }
    
    async def _call_kimi_vision(self, image_url: str, question: str, system_prompt: str):
        """Call Kimi-VL (Moonshot) for image analysis (PRIMARY vision model)
        
        Uses httpx for direct API call to Moonshot API
        Based on official Kimi documentation:
        - Base URL: https://api.moonshot.ai/v1
        - Only base64 images supported (not URL)
        - System message is simple string
        - User content is list with image_url and text types
        """
        import httpx
        
        logger.info(f"🔮 Kimi-VL API call: model={self.kimi_model}, base_url={self.kimi_base_url}")
        logger.info(f"🔮 Kimi-VL API key: ***{self.kimi_api_key[-8:] if self.kimi_api_key else 'None'}")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.kimi_api_key}",
                "Content-Type": "application/json"
            }
            
            # Kimi Vision API format (per official docs):
            # - system message is string content
            # - user message content is LIST with image_url FIRST, then text
            payload = {
                "model": self.kimi_model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are Kimi, an AI assistant that excels at analyzing educational images. Extract text, equations, diagrams, and key concepts precisely."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",  # Image FIRST per Kimi docs
                                "image_url": {
                                    "url": image_url  # Must be base64 data URI
                                }
                            },
                            {
                                "type": "text",
                                "text": f"{system_prompt}\n\nStudent's question: {question}\n\nAnalyze this image thoroughly and extract all text, equations, and concepts."
                            }
                        ]
                    }
                ],
                "temperature": 0.3
            }
            
            logger.info(f"🔮 Sending request to {self.kimi_base_url}/chat/completions")
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.kimi_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"❌ Kimi-VL API error: {response.status_code} - {error_text}")
                    raise Exception(f"Kimi API error: {response.status_code} - {error_text}")
                
                result = response.json()
                logger.info(f"✅ Kimi-VL response received successfully")
                
                # Return in LiteLLM-compatible format
                class MockChoice:
                    def __init__(self, content):
                        self.message = type('obj', (object,), {'content': content})()
                
                class MockResponse:
                    def __init__(self, content):
                        self.choices = [MockChoice(content)]
                
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                return MockResponse(content)
                
        except httpx.TimeoutException:
            logger.error(f"❌ Kimi-VL API timeout after 90s")
            raise Exception("Kimi-VL API timeout after 90s")
        except Exception as e:
            logger.error(f"❌ Kimi-VL API error: {e}")
            raise
    
    async def _call_qwen_vision(self, image_url: str, question: str, system_prompt: str):
        """Call Qwen-VL for image analysis (SECONDARY fallback)"""
        import litellm
        
        return await litellm.acompletion(
            model=f"openai/{self.qwen_model}",
            api_key=self.qwen_api_key,
            api_base=self.qwen_base_url,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Student's question: {question}\n\nAnalyze this image:"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.2
        )
    
    def _parse_vision_response(self, raw_response: str, subject_hint: Optional[str], model_used: str) -> Dict[str, Any]:
        """Parse vision model response into structured output"""
        
        # Extract OCR text
        ocr_text = self._extract_section(raw_response, "OCR Text", "Extracted Text", "Full Text")
        if not ocr_text:
            ocr_text = raw_response  # Use full response if no section found
        
        # Extract diagram insight
        diagram_insight = self._extract_section(raw_response, "Diagram Insight", "Diagrams/Figures", "Diagram")
        
        # Extract semantic tags
        tags_text = self._extract_section(raw_response, "Semantic Tags", "Key Concepts", "Tags")
        semantic_tags = self._parse_tags(tags_text) if tags_text else self._extract_key_elements(raw_response)
        
        # Build structured result
        return {
            # New structured fields
            'ocr_text': ocr_text.strip() if ocr_text else '',
            'diagram_insight': diagram_insight.strip() if diagram_insight else '',
            'semantic_tags': semantic_tags,
            'raw_vision_response': raw_response,
            'model_used': model_used,
            
            # Legacy fields (for backward compatibility)
            'extracted_text': ocr_text.strip() if ocr_text else raw_response,
            'content_type': self._detect_content_type(raw_response),
            'analysis': raw_response,
            'subject_detected': self._detect_subject_from_analysis(raw_response, subject_hint),
            'key_elements': self._extract_key_elements(raw_response),
            'has_equations': 'equation' in raw_response.lower() or '=' in raw_response,
            'has_diagram': 'diagram' in raw_response.lower() or 'figure' in raw_response.lower() or 'graph' in raw_response.lower()
        }
    
    def _extract_section(self, text: str, *section_names: str) -> Optional[str]:
        """Extract a section from the response by section name"""
        for name in section_names:
            # Try to find section with ** markers
            pattern = rf'\*\*{name}\*\*[:\s]*\n?(.*?)(?=\n\*\*|\Z)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
            
            # Try without ** markers
            pattern = rf'{name}[:\s]*\n?(.*?)(?=\n[A-Z]|\Z)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _parse_tags(self, tags_text: str) -> List[str]:
        """Parse semantic tags from text"""
        if not tags_text:
            return []
        
        # Remove brackets and split by comma or space
        tags_text = re.sub(r'[\[\]]', '', tags_text)
        tags = re.split(r'[,\s]+', tags_text)
        
        # Clean and filter
        return [tag.strip().lower() for tag in tags if tag.strip() and len(tag.strip()) > 1]
    
    async def _call_gpt4_vision(self, image_url: str, question: str, system_prompt: str):
        """Fallback to GPT-4o Vision when other models are unavailable"""
        import litellm
        
        # Check if we have a valid OpenAI key
        if not self.openai_key:
            logger.error("❌ No valid OpenAI API key for GPT-4o Vision fallback")
            raise Exception("No valid OpenAI API key configured for vision fallback")
        
        logger.info(f"📷 Calling GPT-4o Vision [FALLBACK]...")
        
        return await litellm.acompletion(
            model="gpt-4o",
            api_key=self.openai_key,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Student's question: {question}\n\nAnalyze this image:"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.2
        )
    
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


    # =========================================================================
    # CONVENIENCE METHODS FOR SPECIFIC USE CASES
    # =========================================================================
    
    async def extract_image_text(self, image_data: str) -> Dict[str, Any]:
        """
        Extract text/OCR from image using Kimi-VL
        Optimized for text extraction (formulas, handwriting, printed text)
        
        Returns:
            {
                'ocr_text': 'Extracted text...',
                'has_equations': True/False,
                'confidence': 'high/medium/low'
            }
        """
        result = await self.analyze_image(image_data, "Extract all text from this image")
        return {
            'ocr_text': result.get('ocr_text', ''),
            'extracted_text': result.get('extracted_text', ''),
            'has_equations': result.get('has_equations', False),
            'model_used': result.get('model_used', 'unknown'),
            'confidence': 'high' if len(result.get('ocr_text', '')) > 50 else 'medium'
        }
    
    async def analyze_diagram(self, image_data: str, diagram_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze diagram using Kimi-VL
        Optimized for diagram understanding (circuits, graphs, molecular structures)
        
        Args:
            image_data: Base64 encoded image
            diagram_type: Optional hint ('circuit', 'graph', 'molecular', 'anatomical')
        
        Returns:
            {
                'diagram_insight': 'Description of diagram...',
                'components': ['resistor', 'capacitor'],
                'relationships': 'Series connection...',
                'semantic_tags': ['physics', 'circuit']
            }
        """
        hint = f"This is a {diagram_type} diagram. " if diagram_type else ""
        question = f"{hint}Analyze this diagram in detail. Identify all components, labels, and relationships."
        
        result = await self.analyze_image(image_data, question)
        return {
            'diagram_insight': result.get('diagram_insight', ''),
            'components': result.get('key_elements', []),
            'semantic_tags': result.get('semantic_tags', []),
            'content_type': result.get('content_type', 'diagram'),
            'subject_detected': result.get('subject_detected', 'General'),
            'model_used': result.get('model_used', 'unknown'),
            'raw_analysis': result.get('raw_vision_response', '')
        }
    
    async def get_visual_context(self, image_data: str, question: str) -> Dict[str, Any]:
        """
        Get visual context for reasoning pipeline
        Returns structured data ready for DeepSeek reasoning
        
        Args:
            image_data: Base64 encoded image
            question: Student's question
        
        Returns:
            {
                'visual_context': 'Formatted context for reasoning...',
                'ocr_text': 'Raw extracted text',
                'diagram_insight': 'Diagram description',
                'semantic_tags': ['tag1', 'tag2'],
                'subject': 'Physics',
                'ready_for_reasoning': True
            }
        """
        result = await self.analyze_image(image_data, question)
        
        # Build context string for reasoning model
        context_parts = []
        
        if result.get('ocr_text'):
            context_parts.append(f"[IMAGE CONTAINS TEXT]:\n{result['ocr_text']}")
        
        if result.get('diagram_insight'):
            context_parts.append(f"[DIAGRAM SHOWS]:\n{result['diagram_insight']}")
        
        if result.get('semantic_tags'):
            context_parts.append(f"[TOPICS]: {', '.join(result['semantic_tags'])}")
        
        visual_context = "\n\n".join(context_parts) if context_parts else result.get('raw_vision_response', '')
        
        return {
            'visual_context': visual_context,
            'ocr_text': result.get('ocr_text', ''),
            'diagram_insight': result.get('diagram_insight', ''),
            'semantic_tags': result.get('semantic_tags', []),
            'subject': result.get('subject_detected', 'General'),
            'content_type': result.get('content_type', 'unknown'),
            'model_used': result.get('model_used', 'unknown'),
            'ready_for_reasoning': bool(visual_context),
            'raw_vision_response': result.get('raw_vision_response', '')
        }


# =========================================================================
# MODULE-LEVEL HELPER FUNCTIONS
# =========================================================================

async def analyze_student_image(
    image_data: str,
    question: str,
    subject_hint: Optional[str] = None
) -> Dict[str, Any]:
    """Helper function to analyze student-uploaded images using Kimi-VL"""
    analyzer = VisionAnalyzer()
    return await analyzer.analyze_image(image_data, question, subject_hint)


async def extract_image_text(image_data: str) -> Dict[str, Any]:
    """Extract text/OCR from image using Kimi-VL"""
    analyzer = VisionAnalyzer()
    return await analyzer.extract_image_text(image_data)


async def analyze_diagram(image_data: str, diagram_type: Optional[str] = None) -> Dict[str, Any]:
    """Analyze diagram using Kimi-VL"""
    analyzer = VisionAnalyzer()
    return await analyzer.analyze_diagram(image_data, diagram_type)


async def get_visual_context(image_data: str, question: str) -> Dict[str, Any]:
    """Get visual context for reasoning pipeline using Kimi-VL"""
    analyzer = VisionAnalyzer()
    return await analyzer.get_visual_context(image_data, question)

