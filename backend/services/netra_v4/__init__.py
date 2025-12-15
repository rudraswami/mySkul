"""
🔮 NETRA v4.0 - Visual Intelligence Orchestrator
================================================

Production-grade visual intelligence module that generates unique,
modern, edtech-grade visuals for any educational question.

Architecture:
    User Question
        ↓
    Netra Orchestrator (decides when/what)
        ↓
    Visual Strategy Resolver (concept + intent based routing)
        ↓
    Imagen (Google's image generation)
        ↓
    Visual Normalizer (stable internal format)
        ↓
    Teaching Metadata Generator (hotspots, steps, annotations)
        ↓
    Frontend Renderer (teaching + interaction layer)

Key Principles:
    - NO subject hardcoding (route by concept + intent)
    - NO generic circle/box visuals
    - NO repeated layouts
    - UNIQUE visual per question
    - LLM for reasoning only, Imagen for creation
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
)

from .orchestrator import (
    NetraOrchestrator,
    create_orchestrator,
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
    # Orchestrator
    "NetraOrchestrator",
    "create_orchestrator",
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

