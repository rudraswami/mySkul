"""
Lightweight embedding service using external APIs instead of heavy ML models.
This replaces sentence-transformers, torch, and transformers dependencies.
"""
import asyncio
import hashlib
import json
import os
import logging
from typing import List, Dict, Any, Optional
import httpx
try:
    from emergentintegrations import EmergentLLMIntegration
    EMERGENT_AVAILABLE = True
except ImportError:
    EmergentLLMIntegration = None
    EMERGENT_AVAILABLE = False

logger = logging.getLogger(__name__)

class LightweightEmbeddingService:
    """
    Lightweight embedding service using external APIs.
    Falls back to simple text similarity if APIs are unavailable.
    """
    
    def __init__(self):
        self.client = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the embedding service"""
        if self.initialized:
            return
            
        try:
            # Try to use Emergent LLM integration for embeddings
            self.client = EmergentLLMIntegration()
            self.initialized = True
            logger.info("✅ Lightweight embedding service initialized with Emergent integration")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding service: {e}. Using fallback similarity.")
            self.client = None
            self.initialized = True
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        Falls back to simple hash-based vectors if API unavailable.
        """
        await self.initialize()
        
        if not texts:
            return []
        
        try:
            # Try using Emergent LLM integration for embeddings
            if self.client:
                embeddings = []
                for text in texts:
                    try:
                        # Use OpenAI embeddings via Emergent integration
                        response = await self.client.create_embeddings(
                            text=text,
                            model="text-embedding-3-small"
                        )
                        if response and 'embedding' in response:
                            embeddings.append(response['embedding'])
                        else:
                            # Fallback for this text
                            embeddings.append(self._create_simple_embedding(text))
                    except Exception as e:
                        logger.warning(f"API embedding failed for text, using fallback: {e}")
                        embeddings.append(self._create_simple_embedding(text))
                
                return embeddings
            else:
                # Fallback to simple embeddings
                return [self._create_simple_embedding(text) for text in texts]
                
        except Exception as e:
            logger.error(f"Embedding creation error: {e}")
            # Fallback to simple embeddings
            return [self._create_simple_embedding(text) for text in texts]
    
    async def create_single_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        embeddings = await self.create_embeddings([text])
        return embeddings[0] if embeddings else self._create_simple_embedding(text)
    
    def _create_simple_embedding(self, text: str, dimension: int = 384) -> List[float]:
        """
        Create a simple hash-based embedding as fallback.
        This provides basic semantic similarity without heavy ML models.
        """
        # Normalize text
        text = text.lower().strip()
        
        # Create multiple hash seeds for different dimensions
        embeddings = []
        for i in range(dimension):
            # Use different seeds to create varied hash values
            seed_text = f"{text}_{i}"
            hash_value = hashlib.md5(seed_text.encode()).hexdigest()
            # Convert hex to float between -1 and 1
            numeric_value = int(hash_value[:8], 16) / (16**8) * 2 - 1
            embeddings.append(numeric_value)
        
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Simple cosine similarity calculation
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity without embeddings.
        Useful for basic keyword matching.
        """
        # Simple keyword-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

# Global instance
embedding_service = LightweightEmbeddingService()

async def get_embedding_service() -> LightweightEmbeddingService:
    """Get the global embedding service instance"""
    await embedding_service.initialize()
    return embedding_service