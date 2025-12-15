"""
🔮 NETRA v4.0 - Image Generation Client
=======================================

Client for generating educational images using Google's AI models.
Primary: Gemini 2.0 Flash with native image generation
Fallback: Gemini 1.5 for text-based visual descriptions

Uses the Gemini API for image generation capabilities.
"""

import logging
import base64
import asyncio
import io
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from .contracts import ImagenPrompt, VisualData

logger = logging.getLogger(__name__)


class ImagenClient:
    """
    Client for AI image generation.
    
    Uses Gemini 2.0 Flash's native image generation capability
    to create unique educational visuals.
    """
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or "gemini-2.0-flash-exp"
        self._client = None
        self._genai = None
    
    async def _get_client(self):
        """Lazy initialization of the Gemini client"""
        if self._genai is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._genai = genai
            self._client = genai.GenerativeModel(
                self.model,
                generation_config={
                    "temperature": 0.9,
                    "top_p": 0.95,
                }
            )
        return self._genai, self._client
    
    async def generate_image(
        self, 
        prompt: ImagenPrompt,
        request_id: Optional[str] = None
    ) -> tuple[VisualData, Dict[str, Any]]:
        """
        Generate an educational image using Gemini 2.0 Flash.
        
        Args:
            prompt: The composed ImagenPrompt with main and negative prompts
            request_id: Optional request ID for tracking
            
        Returns:
            Tuple of (VisualData, generation_metadata)
        """
        request_id = request_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            genai, client = await self._get_client()
            
            # Compose the full prompt for image generation
            full_prompt = f"""Generate a high-quality educational illustration:

{prompt.main_prompt}

Style requirements:
- Modern, clean educational visual
- {', '.join(prompt.style_modifiers) if prompt.style_modifiers else 'Professional design'}
- Clear, easy to understand
- Suitable for students

Avoid:
{prompt.negative_prompt}

Create this as a detailed educational diagram or illustration."""

            logger.info(f"🎨 [Imagen] Generating image for request {request_id}")
            logger.info(f"🎨 [Imagen] Prompt: {prompt.main_prompt[:150]}...")
            
            # Generate using Gemini 2.0 Flash with image output
            # Note: Gemini 2.0 Flash experimental supports image generation
            response = await asyncio.to_thread(
                client.generate_content,
                full_prompt,
            )
            
            elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Check if response contains an image
            image_base64 = None
            
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            # Check for inline image data
                            if hasattr(part, 'inline_data') and part.inline_data:
                                image_data = part.inline_data.data
                                if isinstance(image_data, bytes):
                                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                                    break
                            # Check for blob data
                            elif hasattr(part, 'blob') and part.blob:
                                image_data = part.blob
                                if isinstance(image_data, bytes):
                                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                                    break
            
            # If no image was generated, create a placeholder or raise error
            if not image_base64:
                logger.warning("🎨 [Imagen] No image in response, generating placeholder...")
                # Generate a text description instead as fallback
                image_base64, width, height = await self._generate_fallback_visual(
                    prompt, genai
                )
            else:
                width, height = 1024, 576  # Default dimensions
            
            visual_data = VisualData(
                type="generated_image",
                image_base64=image_base64,
                image_format="png",
                width=width,
                height=height
            )
            
            generation_meta = {
                "request_id": request_id,
                "time_ms": elapsed_ms,
                "prompt_used": prompt.main_prompt,
                "negative_prompt": prompt.negative_prompt,
                "model": self.model,
                "timestamp": start_time.isoformat()
            }
            
            logger.info(f"✅ [Imagen] Image generated in {elapsed_ms}ms")
            
            return visual_data, generation_meta
                
        except Exception as e:
            logger.error(f"❌ [Imagen] Generation failed: {e}")
            raise
    
    async def _generate_fallback_visual(
        self, 
        prompt: ImagenPrompt,
        genai
    ) -> tuple[str, int, int]:
        """
        Generate a fallback visual when image generation fails.
        Creates an SVG-based educational visual.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple educational visual
            width, height = 1024, 576
            img = Image.new('RGB', (width, height), color='#F8FAFC')
            draw = ImageDraw.Draw(img)
            
            # Add gradient-like background
            for y in range(height):
                r = int(248 - (y / height) * 10)
                g = int(250 - (y / height) * 10)
                b = int(252 - (y / height) * 10)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Add title
            try:
                font_large = ImageFont.truetype("arial.ttf", 32)
                font_medium = ImageFont.truetype("arial.ttf", 18)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Extract concept from prompt
            concept = prompt.main_prompt[:100] + "..." if len(prompt.main_prompt) > 100 else prompt.main_prompt
            
            # Draw title area
            draw.rectangle([(50, 50), (width - 50, 120)], fill='#3B82F6', outline='#2563EB')
            draw.text((70, 70), "Educational Visual", fill='white', font=font_large)
            
            # Draw content area
            draw.rectangle([(50, 140), (width - 50, height - 50)], fill='white', outline='#E2E8F0')
            
            # Add concept text
            y_pos = 170
            words = concept.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                if len(test_line) < 60:
                    line = test_line
                else:
                    draw.text((70, y_pos), line, fill='#1E293B', font=font_medium)
                    y_pos += 30
                    line = word
            if line:
                draw.text((70, y_pos), line, fill='#1E293B', font=font_medium)
            
            # Add visual elements
            draw.ellipse([(width//2 - 80, height//2 - 40), (width//2 + 80, height//2 + 40)], 
                        fill='#EFF6FF', outline='#3B82F6', width=2)
            draw.text((width//2 - 40, height//2 - 10), "Concept", fill='#3B82F6', font=font_medium)
            
            # Draw arrows
            for angle in [0, 90, 180, 270]:
                import math
                cx, cy = width//2, height//2
                r = 100
                x1 = cx + int(r * math.cos(math.radians(angle)))
                y1 = cy + int(r * math.sin(math.radians(angle)))
                x2 = cx + int((r + 50) * math.cos(math.radians(angle)))
                y2 = cy + int((r + 50) * math.sin(math.radians(angle)))
                draw.line([(x1, y1), (x2, y2)], fill='#94A3B8', width=2)
            
            # Add note
            draw.text((70, height - 80), "🔮 Visual generated by NETRA v4.0", fill='#64748B', font=font_medium)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64, width, height
            
        except Exception as e:
            logger.error(f"Fallback visual generation failed: {e}")
            # Return a minimal placeholder
            return self._create_minimal_placeholder()
    
    def _create_minimal_placeholder(self) -> tuple[str, int, int]:
        """Create a minimal placeholder image"""
        # Minimal 1x1 transparent PNG
        minimal_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        return minimal_png, 1, 1
    
    async def generate_with_retry(
        self,
        prompt: ImagenPrompt,
        request_id: Optional[str] = None,
        max_retries: int = 2
    ) -> tuple[VisualData, Dict[str, Any]]:
        """
        Generate image with retry logic for resilience.
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await self.generate_image(prompt, request_id)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"⚠️ [Imagen] Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
        
        raise last_error


def create_imagen_client(api_key: str, model: str = None, use_fallback: bool = False) -> ImagenClient:
    """
    Factory function to create an Imagen client.
    
    Args:
        api_key: Google API key
        model: Model to use (default: gemini-2.0-flash-exp)
        use_fallback: Ignored for now (kept for API compatibility)
    """
    return ImagenClient(api_key, model)

