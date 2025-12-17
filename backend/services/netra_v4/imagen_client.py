"""
🔮 NETRA v4.0 - DALL-E 3 Image Generation Client
================================================

Production image generation using OpenAI's DALL-E 3.
This is the ONLY image generation engine - no fallbacks, no placeholders.

DALL-E 3 produces:
- Rich, contextual educational illustrations
- Unique visuals for every concept
- Modern, engaging edtech-grade content

If generation fails, we return an error - never fake or placeholder images.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from openai import AsyncOpenAI
from openai import APIError, RateLimitError, APIConnectionError

from .contracts import ImagenPrompt, VisualData

logger = logging.getLogger(__name__)


class ImagenClient:
    """
    DALL-E 3 Image Generation Client.
    
    Uses OpenAI's DALL-E 3 API to generate unique, rich educational visuals.
    NO PIL fallbacks, NO placeholders, NO generic diagrams.
    """
    
    def __init__(self, openai_api_key: str, model: str = "dall-e-3"):
        """
        Initialize DALL-E 3 client.
        
        Args:
            openai_api_key: OpenAI API key (same key used for GPT-4.1-mini)
            model: DALL-E model version (dall-e-3 recommended)
        """
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for DALL-E 3 image generation")
        
        self.api_key = openai_api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=openai_api_key)
        
        # DALL-E 3 configuration
        self.default_size = "1792x1024"  # Landscape format for educational content
        self.default_quality = "standard"  # "standard" or "hd"
        self.default_style = "vivid"  # "vivid" or "natural"
        
        logger.info(f"🎨 [DALL-E 3] Client initialized (model: {self.model})")
    
    async def generate_image(
        self, 
        prompt: ImagenPrompt,
        request_id: Optional[str] = None
    ) -> tuple[VisualData, Dict[str, Any]]:
        """
        Generate an educational image using DALL-E 3.
        
        Args:
            prompt: The composed ImagenPrompt with main and negative prompts
            request_id: Optional request ID for tracking
            
        Returns:
            Tuple of (VisualData, generation_metadata)
            
        Raises:
            Exception: If image generation fails (NO fallback to placeholders)
        """
        request_id = request_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Compose the DALL-E 3 optimized prompt
        dalle_prompt = self._compose_dalle_prompt(prompt)
        
        logger.info(f"🎨 [DALL-E 3] Generating image for request {request_id}")
        logger.info(f"🎨 [DALL-E 3] Prompt length: {len(dalle_prompt)} chars")
        
        try:
            # Call OpenAI DALL-E 3 API
            response = await self.client.images.generate(
                model=self.model,
                prompt=dalle_prompt,
                n=1,
                size=self.default_size,
                quality=self.default_quality,
                style=self.default_style,
                response_format="b64_json"  # Get base64 directly
            )
            
            # Extract image data
            if not response.data or len(response.data) == 0:
                raise Exception("DALL-E 3 returned no image data")
            
            image_data = response.data[0]
            image_base64 = image_data.b64_json
            revised_prompt = image_data.revised_prompt or dalle_prompt
            
            if not image_base64:
                raise Exception("DALL-E 3 returned empty image")
            
            # Parse dimensions from size setting
            width, height = map(int, self.default_size.split("x"))
            
            elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
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
                "prompt_used": dalle_prompt,
                "revised_prompt": revised_prompt,  # DALL-E 3 may revise the prompt
                "negative_prompt": prompt.negative_prompt,
                "model": self.model,
                "size": self.default_size,
                "quality": self.default_quality,
                "style": self.default_style,
                "timestamp": start_time.isoformat()
            }
            
            logger.info(f"✅ [DALL-E 3] Image generated in {elapsed_ms}ms")
            logger.info(f"✅ [DALL-E 3] Image size: {width}x{height}")
            
            return visual_data, generation_meta
        
        except RateLimitError as e:
            logger.error(f"❌ [DALL-E 3] Rate limit exceeded: {e}")
            raise Exception(f"DALL-E 3 rate limit exceeded. Please try again in a moment.")
        
        except APIConnectionError as e:
            logger.error(f"❌ [DALL-E 3] Connection error: {e}")
            raise Exception(f"Failed to connect to DALL-E 3. Please check your network.")
        
        except APIError as e:
            logger.error(f"❌ [DALL-E 3] API error: {e}")
            if "content_policy" in str(e).lower() or "safety" in str(e).lower():
                raise Exception(f"DALL-E 3 content policy rejection. Please rephrase your question.")
            raise Exception(f"DALL-E 3 API error: {str(e)}")
        
        except Exception as e:
            logger.error(f"❌ [DALL-E 3] Generation failed: {e}")
            raise  # Re-raise - NO fallback to placeholders
    
    def _compose_dalle_prompt(self, prompt: ImagenPrompt) -> str:
        """
        Compose an optimized prompt for DALL-E 3.
        
        DALL-E 3 works best with:
        - Clear, detailed descriptions
        - Specific style instructions
        - Educational context emphasis
        - Avoiding certain patterns that lead to generic outputs
        """
        # Start with the main prompt from strategy resolver
        base_prompt = prompt.main_prompt
        
        # Add educational context and quality directives
        educational_prefix = """Create a premium educational illustration that:
- Is visually engaging and immediately understandable
- Uses rich colors, depth, and spatial relationships
- Shows concepts through visual metaphors and real-world context
- Has clear visual hierarchy and storytelling
- Feels alive and dynamic, not static or flat
- Is suitable for modern edtech platforms

"""
        
        # Add style modifiers
        style_suffix = ""
        if prompt.style_modifiers:
            style_suffix = f"\n\nStyle: {', '.join(prompt.style_modifiers)}"
        
        # Add anti-generic directives
        anti_generic = """

IMPORTANT: 
- Do NOT create simple diagrams with circles and arrows
- Do NOT create generic flowcharts or org charts
- Do NOT create abstract or symbolic representations
- Instead, create rich, illustrative scenes that SHOW the concept in action
- Use real-world visual metaphors and scenarios
- Make it feel like a premium educational animation frame"""
        
        # Compose final prompt (DALL-E 3 has 4000 char limit)
        full_prompt = f"{educational_prefix}{base_prompt}{style_suffix}{anti_generic}"
        
        # Ensure we stay within DALL-E 3's limit
        if len(full_prompt) > 4000:
            # Truncate intelligently, keeping the important parts
            full_prompt = f"{educational_prefix}{base_prompt[:2500]}{anti_generic}"
        
        return full_prompt
    
    async def generate_with_retry(
        self,
        prompt: ImagenPrompt,
        request_id: Optional[str] = None,
        max_retries: int = 2
    ) -> tuple[VisualData, Dict[str, Any]]:
        """
        Generate image with retry logic for resilience.
        
        Retries on transient failures only. 
        NEVER falls back to placeholders.
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await self.generate_image(prompt, request_id)
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Don't retry on certain errors
                if "content_policy" in error_str or "safety" in error_str:
                    logger.warning(f"⚠️ [DALL-E 3] Content policy rejection, not retrying")
                    raise
                
                if "billing" in error_str or "quota" in error_str:
                    logger.warning(f"⚠️ [DALL-E 3] Billing/quota issue, not retrying")
                    raise
                
                if "rate limit" in error_str:
                    # Wait longer for rate limits
                    wait_time = 5 * (attempt + 1)
                    logger.warning(f"⚠️ [DALL-E 3] Rate limited, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                elif attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"⚠️ [DALL-E 3] Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
        
        # All retries exhausted
        logger.error(f"❌ [DALL-E 3] All {max_retries + 1} attempts failed")
        raise last_error


def create_imagen_client(
    openai_api_key: str, 
    model: str = "dall-e-3",
    use_fallback: bool = False  # Ignored - kept for API compatibility
) -> ImagenClient:
    """
    Factory function to create a DALL-E 3 image generation client.
    
    Args:
        openai_api_key: OpenAI API key (same as used for GPT models)
        model: DALL-E model version (dall-e-3 recommended)
        use_fallback: Ignored - no fallbacks allowed
    """
    if use_fallback:
        logger.warning("⚠️ use_fallback=True is ignored - DALL-E 3 is the ONLY engine")
    
    return ImagenClient(openai_api_key, model)
