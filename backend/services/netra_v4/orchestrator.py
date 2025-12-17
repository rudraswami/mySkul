"""
🔮 NETRA v4.0 - Main Orchestrator
=================================

The central orchestrator for the Visual Intelligence module.
Coordinates all components to produce unique, modern educational visuals.

Pipeline:
    User Question
        → Visual Need Detector (should we generate a visual?)
        → Visual Strategy Resolver (what type of visual?) [Gemini]
        → DALL-E 3 Client (generate the image) [OpenAI]
        → Teaching Metadata Generator (add teaching layer) [Gemini]
        → Visual Normalizer (validate and package)
        → Response

This is the SINGLE entry point for visual generation.
"""

import logging
import time
import uuid
from typing import Optional, Dict, Any

from .contracts import (
    VisualRequest,
    VisualResponse,
    UserContext,
)
from .visual_strategy import VisualStrategyResolver, create_strategy_resolver
from .imagen_client import ImagenClient, create_imagen_client
from .teaching_metadata import TeachingMetadataGenerator, create_teaching_generator
from .normalizer import VisualNormalizer, QualityController, create_normalizer, create_quality_controller

logger = logging.getLogger(__name__)


class NetraOrchestrator:
    """
    Main orchestrator for NETRA v4.0 Visual Intelligence.
    
    This class coordinates:
    1. Visual need detection (should we generate?)
    2. Strategy resolution (what type of visual?) - Uses Gemini
    3. Image generation (create the visual) - Uses DALL-E 3
    4. Teaching metadata (make it educational) - Uses Gemini
    5. Quality control (ensure uniqueness)
    
    API Keys:
    - gemini_api_key: For visual strategy and teaching metadata
    - openai_api_key: For DALL-E 3 image generation
    
    Usage:
        orchestrator = create_orchestrator(gemini_key, openai_key)
        response = await orchestrator.generate(request)
    """
    
    def __init__(
        self,
        gemini_api_key: str,
        openai_api_key: str,
        gemini_model: str = "gemini-2.5-flash",
        dalle_model: str = "dall-e-3"
    ):
        """
        Initialize the orchestrator with all required components.
        
        Args:
            gemini_api_key: Google API key for Gemini (strategy + teaching)
            openai_api_key: OpenAI API key for DALL-E 3 (image generation)
            gemini_model: Model for reasoning (default: gemini-2.5-flash)
            dalle_model: DALL-E model version (default: dall-e-3)
        """
        self.gemini_api_key = gemini_api_key
        self.openai_api_key = openai_api_key
        
        # Validate API keys
        if not gemini_api_key:
            raise ValueError("Gemini API key is required for visual strategy")
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for DALL-E 3 image generation")
        
        # Initialize components
        # Strategy resolver uses Gemini for intelligent concept analysis
        self.strategy_resolver = create_strategy_resolver(gemini_api_key, gemini_model)
        
        # Image client uses DALL-E 3 for actual image generation
        self.imagen_client = create_imagen_client(openai_api_key, dalle_model)
        
        # Teaching generator uses Gemini for educational content
        self.teaching_generator = create_teaching_generator(gemini_api_key, gemini_model)
        
        # Normalizer and quality controller
        self.normalizer = create_normalizer()
        self.quality_controller = create_quality_controller()
        
        # Configuration
        self._include_debug_info = True
        self._enable_quality_checks = True
        self._max_retries = 2
        
        logger.info("🔮 NETRA v4.0 Orchestrator initialized")
        logger.info("  ├── Strategy: Gemini 2.5 Flash")
        logger.info("  ├── Image Gen: DALL-E 3")
        logger.info("  └── Teaching: Gemini 2.5 Flash")
    
    async def generate(
        self,
        request: VisualRequest,
        request_id: Optional[str] = None
    ) -> VisualResponse:
        """
        Generate a visual for the given request.
        
        This is the main entry point for visual generation.
        
        Args:
            request: The visual generation request
            request_id: Optional request ID for tracking
            
        Returns:
            Complete VisualResponse with image, metadata, and teaching layer
        """
        request_id = request_id or str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"🔮 [Netra] Starting generation for request {request_id}")
        logger.info(f"🔮 [Netra] Question: {request.question[:100]}...")
        
        try:
            # Step 1: Visual Need Detection
            needs_visual = await self._detect_visual_need(request)
            
            if not needs_visual:
                logger.info(f"🔮 [Netra] Visual not needed for this question")
                return self.normalizer.create_error_response(
                    "This question does not require a visual explanation",
                    "VISUAL_NOT_NEEDED"
                )
            
            # Step 2: Resolve Visual Strategy (Gemini)
            logger.info(f"🧠 [Netra] Step 2: Resolving visual strategy with Gemini...")
            concept, strategy, imagen_prompt = await self.strategy_resolver.resolve_complete(request)
            
            logger.info(f"✅ [Netra] Strategy: {strategy.intent.value} / {strategy.style.value}")
            logger.info(f"✅ [Netra] Concept: {concept.core_concept}")
            logger.info(f"✅ [Netra] Metaphor: {strategy.visual_metaphor or 'none'}")
            
            # Step 3: Generate Image with DALL-E 3 (OpenAI)
            logger.info(f"🎨 [Netra] Step 3: Generating image with DALL-E 3...")
            visual_data, generation_meta = await self.imagen_client.generate_with_retry(
                imagen_prompt,
                request_id,
                max_retries=self._max_retries
            )
            
            logger.info(f"✅ [Netra] DALL-E 3 image generated in {generation_meta.get('time_ms', 0)}ms")
            
            # Step 4: Quality Check
            if self._enable_quality_checks:
                visual_hash = self.normalizer.compute_visual_hash(visual_data)
                is_unique, reason = self.quality_controller.check_uniqueness(
                    concept.core_concept,
                    visual_hash
                )
                
                if not is_unique:
                    logger.warning(f"⚠️ [Netra] Quality check: {reason}")
                
                self.quality_controller.record_generation(
                    concept.core_concept,
                    visual_hash,
                    f"{strategy.intent.value}_{strategy.style.value}"
                )
            
            # Step 5: Generate Teaching Metadata (Gemini)
            logger.info(f"📚 [Netra] Step 5: Generating teaching metadata with Gemini...")
            teaching = await self.teaching_generator.generate_teaching_flow(
                request,
                concept,
                strategy,
                imagen_prompt.main_prompt
            )
            
            logger.info(f"✅ [Netra] Teaching: {len(teaching.hotspots)} hotspots, {len(teaching.steps)} steps")
            
            # Step 6: Normalize and Package Response
            logger.info(f"📦 [Netra] Step 6: Normalizing response...")
            response = self.normalizer.normalize_response(
                visual_data=visual_data,
                concept=concept,
                strategy=strategy,
                teaching=teaching,
                generation_meta=generation_meta,
                request=request,
                include_debug_info=self._include_debug_info
            )
            
            total_time = int((time.time() - start_time) * 1000)
            logger.info(f"🎉 [Netra] Generation complete in {total_time}ms")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ [Netra] Generation failed: {e}", exc_info=True)
            return self.normalizer.create_error_response(
                str(e),
                "GENERATION_FAILED"
            )
    
    async def _detect_visual_need(self, request: VisualRequest) -> bool:
        """
        Detect if the question actually needs a visual.
        
        Some questions are better answered with text only.
        Returns True if visual generation should proceed.
        """
        question_lower = request.question.lower()
        
        # Questions that typically need visuals
        visual_indicators = [
            "explain", "show", "diagram", "visualize", "illustrate",
            "how does", "what happens", "compare", "difference",
            "structure", "parts of", "process", "cycle", "flow",
            "draw", "picture", "image", "visual", "what is",
            "describe", "work", "mechanism", "concept"
        ]
        
        # Questions that typically don't need visuals
        no_visual_indicators = [
            "define", "what is the definition",
            "who invented", "when was",
            "calculate the value", "solve for x",
            "list the", "name the", "spell",
        ]
        
        # Check for visual need
        for indicator in visual_indicators:
            if indicator in question_lower:
                return True
        
        for indicator in no_visual_indicators:
            if indicator in question_lower:
                return False
        
        # Default: generate visual for educational content
        return True
    
    async def generate_simple(self, question: str) -> VisualResponse:
        """
        Simplified generation interface - just pass a question.
        
        Args:
            question: The student's question
            
        Returns:
            VisualResponse
        """
        request = VisualRequest(
            question=question,
            context=UserContext()
        )
        return await self.generate(request)
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current quality metrics from the quality controller"""
        return self.quality_controller.get_quality_metrics()
    
    def configure(
        self,
        include_debug_info: bool = None,
        enable_quality_checks: bool = None,
        max_retries: int = None
    ):
        """Configure orchestrator behavior"""
        if include_debug_info is not None:
            self._include_debug_info = include_debug_info
        if enable_quality_checks is not None:
            self._enable_quality_checks = enable_quality_checks
        if max_retries is not None:
            self._max_retries = max_retries


# ============================================
# FACTORY FUNCTIONS
# ============================================

def create_orchestrator(
    gemini_api_key: str,
    openai_api_key: str,
    gemini_model: str = "gemini-2.5-flash",
    dalle_model: str = "dall-e-3"
) -> NetraOrchestrator:
    """
    Factory function to create a Netra Orchestrator.
    
    Args:
        gemini_api_key: Google API key for strategy + teaching
        openai_api_key: OpenAI API key for DALL-E 3
        gemini_model: Model for reasoning
        dalle_model: DALL-E model version
        
    Returns:
        Configured NetraOrchestrator instance
    """
    return NetraOrchestrator(
        gemini_api_key=gemini_api_key,
        openai_api_key=openai_api_key,
        gemini_model=gemini_model,
        dalle_model=dalle_model
    )


def create_orchestrator_from_settings() -> NetraOrchestrator:
    """
    Create orchestrator using settings from core.config.
    
    Uses:
    - GEMINI_API_KEY for visual strategy and teaching metadata
    - OPENAI_API_KEY for DALL-E 3 image generation
    
    This is the recommended way to create an orchestrator in the app.
    """
    from core.config import settings
    
    gemini_key = settings.GEMINI_API_KEY
    openai_key = settings.OPENAI_API_KEY
    
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not configured in settings")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY not configured in settings (required for DALL-E 3)")
    
    return create_orchestrator(
        gemini_api_key=gemini_key,
        openai_api_key=openai_key,
        gemini_model=settings.GEMINI_MODEL
    )
