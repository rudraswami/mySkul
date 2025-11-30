"""
🎨 Visual Concepts Database - Subject-wise Organization
========================================================

Complete visual configurations for ALL STEM concepts.
Organized by subject for easy maintenance and scaling.

Structure:
- physics.py     → 50+ Physics concepts
- chemistry.py   → 40+ Chemistry concepts  
- biology.py     → 45+ Biology concepts
- mathematics.py → 35+ Mathematics concepts

Total: 170+ concepts with visual templates
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Import all subject concepts
from .physics import PHYSICS_CONCEPTS
from .chemistry import CHEMISTRY_CONCEPTS
from .biology import BIOLOGY_CONCEPTS
from .mathematics import MATHEMATICS_CONCEPTS

# Aggregate all concepts
ALL_VISUAL_CONCEPTS: Dict[str, Dict[str, Any]] = {
    **PHYSICS_CONCEPTS,
    **CHEMISTRY_CONCEPTS,
    **BIOLOGY_CONCEPTS,
    **MATHEMATICS_CONCEPTS,
}


def get_visual_config(concept: str) -> Optional[Dict[str, Any]]:
    """Get visual configuration for a concept."""
    concept_lower = concept.lower().strip()
    
    # Direct match
    if concept_lower in ALL_VISUAL_CONCEPTS:
        config = ALL_VISUAL_CONCEPTS[concept_lower].copy()
        config['concept_id'] = concept_lower
        return config
    
    # Search by keywords in all concepts
    for concept_id, config in ALL_VISUAL_CONCEPTS.items():
        keywords = config.get('keywords', [])
        if any(kw in concept_lower for kw in keywords):
            result = config.copy()
            result['concept_id'] = concept_id
            return result
    
    return None


def get_all_concepts() -> List[str]:
    """Get list of all available visual concepts."""
    return list(ALL_VISUAL_CONCEPTS.keys())


def get_concepts_by_subject(subject: str) -> List[str]:
    """Get concepts for a specific subject."""
    subject_lower = subject.lower().strip()
    return [
        key for key, config in ALL_VISUAL_CONCEPTS.items()
        if config.get("subject", "").lower() == subject_lower
    ]


def get_concept_count() -> Dict[str, int]:
    """Get count of concepts by subject."""
    counts = {}
    for config in ALL_VISUAL_CONCEPTS.values():
        subject = config.get("subject", "other")
        counts[subject] = counts.get(subject, 0) + 1
    return counts


# Export for easy access
__all__ = [
    'ALL_VISUAL_CONCEPTS',
    'PHYSICS_CONCEPTS',
    'CHEMISTRY_CONCEPTS', 
    'BIOLOGY_CONCEPTS',
    'MATHEMATICS_CONCEPTS',
    'get_visual_config',
    'get_all_concepts',
    'get_concepts_by_subject',
    'get_concept_count',
]

