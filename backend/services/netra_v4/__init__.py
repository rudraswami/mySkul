"""
🔮 NETRA v4.0 - Visual Intelligence Orchestrator
================================================

Production-grade visual intelligence module that generates unique,
modern, edtech-grade visuals for any educational question.

Architecture:
    User Question
        ↓
    Netra Orchestrator (coordinates all components)
        ↓
    Visual Strategy Resolver (Gemini - concept + intent analysis)
        ↓
    DALL-E 3 (OpenAI - actual image generation)
        ↓
    Visual Normalizer (stable internal format)
        ↓
    Teaching Metadata Generator (Gemini - hotspots, steps, annotations)
        ↓
    Frontend Renderer (teaching + interaction layer)

Key Principles:
    - NO subject hardcoding (route by concept + intent)
    - NO generic circle/box visuals (DALL-E 3 generates rich scenes)
    - NO PIL fallbacks or placeholders (real AI images only)
    - UNIQUE visual per question
    - Gemini for reasoning, DALL-E 3 for image creation
"""

from .contracts import (
    VisualRequest,
    VisualResponse,
    VisualMetadata,
    TeachingFlow,
    Hotspot,
    TeachingStep,
    Annotation,
    GenerationInfo,
    VisualStrategy,
    ConceptAnalysis,
    UserContext,
    TeachingIntent,
    VisualStyle,
    ComplexityLevel,
)

from .orchestrator import (
    NetraOrchestrator,
    create_orchestrator,
    create_orchestrator_from_settings,
)

from .visual_strategy import (
    VisualStrategyResolver,
    create_strategy_resolver,
)

from .imagen_client import (
    ImagenClient,
    create_imagen_client,
)

from .normalizer import (
    VisualNormalizer,
    create_normalizer,
)

from .teaching_metadata import (
    TeachingMetadataGenerator,
    create_teaching_generator,
)

__all__ = [
    # Contracts
    "VisualRequest",
    "VisualResponse",
    "VisualMetadata",
    "TeachingFlow",
    "Hotspot",
    "TeachingStep",
    "Annotation",
    "GenerationInfo",
    "VisualStrategy",
    "ConceptAnalysis",
    "UserContext",
    "TeachingIntent",
    "VisualStyle",
    "ComplexityLevel",
    # Orchestrator
    "NetraOrchestrator",
    "create_orchestrator",
    "create_orchestrator_from_settings",
    # Strategy
    "VisualStrategyResolver",
    "create_strategy_resolver",
    # Imagen
    "ImagenClient",
    "create_imagen_client",
    # Normalizer
    "VisualNormalizer",
    "create_normalizer",
    # Teaching
    "TeachingMetadataGenerator",
    "create_teaching_generator",
]

__version__ = "4.0.0"

