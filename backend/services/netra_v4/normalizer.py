"""
🔮 NETRA v4.0 - Visual Normalizer
=================================

Normalizes and validates visual generation outputs into a stable internal format.
This ensures consistency regardless of which image generation model is used.

Responsibilities:
    - Validate generated images
    - Normalize metadata across different sources
    - Apply quality checks
    - Prepare final response structure
"""

import logging
import base64
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import hashlib

from .contracts import (
    VisualRequest,
    VisualResponse,
    VisualData,
    VisualMetadata,
    TeachingFlow,
    GenerationInfo,
    ConceptAnalysis,
    VisualStrategy,
)

logger = logging.getLogger(__name__)


class VisualNormalizer:
    """
    Normalizes visual outputs into the stable Netra format.
    
    Ensures:
    - Image data is valid and properly encoded
    - Metadata is complete and consistent
    - Quality standards are met
    - Response structure is correct
    """
    
    # Quality thresholds
    MIN_IMAGE_SIZE_BYTES = 10000  # 10KB minimum (avoid blank images)
    MAX_IMAGE_SIZE_BYTES = 10000000  # 10MB maximum
    
    def __init__(self):
        self._quality_checks_enabled = True
    
    def normalize_response(
        self,
        visual_data: VisualData,
        concept: ConceptAnalysis,
        strategy: VisualStrategy,
        teaching: TeachingFlow,
        generation_meta: Dict[str, Any],
        request: VisualRequest,
        include_debug_info: bool = True
    ) -> VisualResponse:
        """
        Normalize all components into a complete VisualResponse.
        
        Args:
            visual_data: Generated image data
            concept: Analyzed concept
            strategy: Visual strategy used
            teaching: Teaching metadata
            generation_meta: Raw generation metadata
            request: Original request
            include_debug_info: Whether to include generation debug info
            
        Returns:
            Complete, validated VisualResponse
        """
        # Validate image data
        is_valid, validation_error = self._validate_image(visual_data)
        
        if not is_valid:
            logger.error(f"Image validation failed: {validation_error}")
            return VisualResponse(
                success=False,
                error=validation_error,
                error_code="IMAGE_VALIDATION_FAILED"
            )
        
        # Build metadata
        metadata = VisualMetadata(
            concept=concept.core_concept,
            intent=strategy.intent,
            style=strategy.style,
            complexity=strategy.complexity,
            visual_strategy=self._build_strategy_description(strategy),
            generation_model=generation_meta.get("model", "unknown")
        )
        
        # Build generation info (for debugging/analytics)
        generation_info = None
        if include_debug_info:
            generation_info = GenerationInfo(
                time_ms=generation_meta.get("time_ms", 0),
                prompt_used=generation_meta.get("prompt_used", ""),
                negative_prompt=generation_meta.get("negative_prompt", ""),
                model=generation_meta.get("model", "unknown"),
                request_id=generation_meta.get("request_id", ""),
                timestamp=datetime.fromisoformat(generation_meta.get("timestamp", datetime.utcnow().isoformat()))
            )
        
        return VisualResponse(
            success=True,
            visual=visual_data,
            metadata=metadata,
            teaching=teaching,
            generation_info=generation_info
        )
    
    def _validate_image(self, visual_data: VisualData) -> Tuple[bool, Optional[str]]:
        """
        Validate that the generated image meets quality standards.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not visual_data or not visual_data.image_base64:
            return False, "No image data received"
        
        try:
            # Decode and check size
            image_bytes = base64.b64decode(visual_data.image_base64)
            size = len(image_bytes)
            
            if size < self.MIN_IMAGE_SIZE_BYTES:
                return False, f"Image too small ({size} bytes) - likely blank or corrupted"
            
            if size > self.MAX_IMAGE_SIZE_BYTES:
                return False, f"Image too large ({size} bytes) - exceeds limit"
            
            # Basic format validation
            if visual_data.image_format == "png":
                if not image_bytes.startswith(b'\x89PNG'):
                    return False, "Invalid PNG format"
            elif visual_data.image_format == "jpeg":
                if not image_bytes.startswith(b'\xff\xd8'):
                    return False, "Invalid JPEG format"
            
            return True, None
            
        except Exception as e:
            return False, f"Image validation error: {str(e)}"
    
    def _build_strategy_description(self, strategy: VisualStrategy) -> str:
        """Build a human-readable description of the visual strategy"""
        parts = [
            f"{strategy.intent.value.replace('_', ' ').title()} visual",
            f"with {strategy.style.value.replace('_', ' ')} style",
            f"using {strategy.layout_type.replace('_', ' ')} layout"
        ]
        
        if strategy.visual_metaphor:
            parts.append(f"(metaphor: {strategy.visual_metaphor})")
        
        return ", ".join(parts)
    
    def create_error_response(
        self,
        error: str,
        error_code: str = "GENERATION_ERROR"
    ) -> VisualResponse:
        """Create a standardized error response"""
        return VisualResponse(
            success=False,
            error=error,
            error_code=error_code
        )
    
    def compute_visual_hash(self, visual_data: VisualData) -> str:
        """
        Compute a hash of the visual for caching/deduplication.
        """
        if not visual_data or not visual_data.image_base64:
            return ""
        
        return hashlib.sha256(visual_data.image_base64.encode()).hexdigest()[:16]
    
    def should_regenerate(
        self,
        previous_hash: str,
        new_hash: str,
        similarity_threshold: float = 0.9
    ) -> bool:
        """
        Determine if we should regenerate due to too-similar results.
        
        This helps ensure uniqueness - if two consecutive generations
        produce nearly identical results, we might want to try again
        with a modified prompt.
        """
        # For now, simple hash comparison
        # In production, could use perceptual hashing
        return previous_hash == new_hash


class QualityController:
    """
    Quality gate that ensures generated visuals meet standards.
    Implements the "stop condition" - if quality is not met, we refactor.
    """
    
    def __init__(self):
        self._generation_history = []
        self._similarity_threshold = 0.85
    
    def record_generation(
        self,
        concept: str,
        visual_hash: str,
        strategy_signature: str
    ):
        """Record a generation for quality tracking"""
        self._generation_history.append({
            "concept": concept,
            "hash": visual_hash,
            "strategy": strategy_signature,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 100 generations in memory
        if len(self._generation_history) > 100:
            self._generation_history = self._generation_history[-100:]
    
    def check_uniqueness(
        self,
        concept: str,
        visual_hash: str
    ) -> Tuple[bool, str]:
        """
        Check if this generation is unique enough.
        
        Returns:
            Tuple of (is_unique, reason)
        """
        # Check for exact duplicates
        for record in self._generation_history[-20:]:  # Check last 20
            if record["hash"] == visual_hash:
                return False, "Exact duplicate of recent generation"
        
        # Check for similar concepts producing same visuals
        similar_concepts = [
            r for r in self._generation_history[-20:]
            if r["concept"].lower() in concept.lower() or concept.lower() in r["concept"].lower()
        ]
        
        if len(similar_concepts) >= 3:
            hashes = [r["hash"] for r in similar_concepts]
            if len(set(hashes)) == 1:
                return False, "Similar concepts producing identical visuals - need more variation"
        
        return True, "Unique"
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current quality metrics"""
        if not self._generation_history:
            return {"total": 0, "unique_ratio": 1.0}
        
        total = len(self._generation_history)
        unique_hashes = len(set(r["hash"] for r in self._generation_history))
        
        return {
            "total": total,
            "unique_count": unique_hashes,
            "unique_ratio": unique_hashes / total if total > 0 else 1.0,
            "recent_concepts": [r["concept"] for r in self._generation_history[-5:]]
        }


def create_normalizer() -> VisualNormalizer:
    """Factory function to create a visual normalizer"""
    return VisualNormalizer()


def create_quality_controller() -> QualityController:
    """Factory function to create a quality controller"""
    return QualityController()

