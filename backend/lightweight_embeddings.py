"""
Lightweight embedding service using OpenAI API for production-grade embeddings.
Falls back to hash-based vectors if API unavailable.

PRODUCTION UPGRADE (Dec 2025):
- Primary: OpenAI text-embedding-3-small (1536 dimensions)
- Fallback: Hash-based embeddings (384 dimensions)
- Batching: Up to 100 texts per API call
- Caching: In-memory cache for repeated queries
"""
import asyncio
import hashlib
import os
import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# OpenAI embedding configuration
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions, cost-effective
OPENAI_EMBEDDING_DIMENSIONS = 1536
EMBEDDING_BATCH_SIZE = 100  # OpenAI limit
FALLBACK_DIMENSIONS = 384


class LightweightEmbeddingService:
    """
    Production-grade embedding service using OpenAI API.
    
    Features:
    - OpenAI text-embedding-3-small for high-quality embeddings
    - Batching for efficiency
    - In-memory caching for repeated queries
    - Hash-based fallback when API unavailable
    """
    
    def __init__(self):
        self._openai_client = None
        self._openai_available = False
        self.initialized = False
        self.model_name = OPENAI_EMBEDDING_MODEL
        self.dimensions = OPENAI_EMBEDDING_DIMENSIONS
        self._cache: Dict[str, List[float]] = {}
        self._stats = {
            "api_calls": 0,
            "cache_hits": 0,
            "fallback_used": 0
        }
    
    async def initialize(self):
        """Initialize the embedding service with OpenAI client"""
        if self.initialized:
            return
        
        try:
            # Try to initialize OpenAI client
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            
            if api_key:
                self._openai_client = openai.AsyncOpenAI(api_key=api_key)
                self._openai_available = True
                self.dimensions = OPENAI_EMBEDDING_DIMENSIONS
                logger.info(f"✅ Embedding service initialized: OpenAI {OPENAI_EMBEDDING_MODEL} ({self.dimensions}D)")
            else:
                logger.warning("⚠️ OPENAI_API_KEY not set. Using fallback embeddings.")
                self._openai_available = False
                self.dimensions = FALLBACK_DIMENSIONS
                self.model_name = "hash_fallback"
                
        except ImportError:
            logger.warning("⚠️ openai package not installed. Using fallback embeddings.")
            self._openai_available = False
            self.dimensions = FALLBACK_DIMENSIONS
            self.model_name = "hash_fallback"
        except Exception as e:
            logger.warning(f"⚠️ OpenAI init failed: {e}. Using fallback embeddings.")
            self._openai_available = False
            self.dimensions = FALLBACK_DIMENSIONS
            self.model_name = "hash_fallback"
        
        self.initialized = True
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts using OpenAI API.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        await self.initialize()
        
        if not texts:
            return []
        
        # Check cache first
        results = []
        uncached_indices = []
        uncached_texts = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                results.append((i, self._cache[cache_key]))
                self._stats["cache_hits"] += 1
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)
        
        # Embed uncached texts
        if uncached_texts:
            if self._openai_available:
                new_embeddings = await self._create_openai_embeddings(uncached_texts)
            else:
                new_embeddings = [self._create_fallback_embedding(t) for t in uncached_texts]
                self._stats["fallback_used"] += len(uncached_texts)
            
            # Cache and add to results
            for idx, text, embedding in zip(uncached_indices, uncached_texts, new_embeddings):
                cache_key = self._get_cache_key(text)
                self._cache[cache_key] = embedding
                results.append((idx, embedding))
        
        # Sort by original index and return embeddings only
        results.sort(key=lambda x: x[0])
        return [emb for _, emb in results]
    
    async def _create_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using OpenAI API with batching"""
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch = texts[i:i + EMBEDDING_BATCH_SIZE]
            
            try:
                response = await self._openai_client.embeddings.create(
                    model=OPENAI_EMBEDDING_MODEL,
                    input=batch
                )
                
                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                self._stats["api_calls"] += 1
                
                logger.debug(f"📊 OpenAI embeddings: batch {i//EMBEDDING_BATCH_SIZE + 1}, "
                            f"{len(batch)} texts embedded")
                
            except Exception as e:
                logger.error(f"❌ OpenAI embedding error: {e}")
                # Fallback for failed batch
                fallback_embeddings = [self._create_fallback_embedding(t) for t in batch]
                all_embeddings.extend(fallback_embeddings)
                self._stats["fallback_used"] += len(batch)
        
        return all_embeddings
    
    async def create_single_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        embeddings = await self.create_embeddings([text])
        return embeddings[0] if embeddings else self._create_fallback_embedding(text)
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        # Normalize and hash
        normalized = text.lower().strip()[:500]  # Limit for cache key
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _create_fallback_embedding(self, text: str) -> List[float]:
        """
        Create hash-based embedding as fallback.
        Dimensions match current model (OpenAI: 1536, Fallback: 384)
        """
        text = text.lower().strip()
        dim = self.dimensions
        
        embeddings = []
        for i in range(dim):
            seed_text = f"{text}_{i}"
            hash_value = hashlib.md5(seed_text.encode()).hexdigest()
            numeric_value = int(hash_value[:8], 16) / (16**8) * 2 - 1
            embeddings.append(numeric_value)
        
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            if len(embedding1) != len(embedding2):
                logger.warning(f"Embedding dimension mismatch: {len(embedding1)} vs {len(embedding2)}")
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics"""
        return {
            "model": self.model_name,
            "dimensions": self.dimensions,
            "openai_available": self._openai_available,
            "cache_size": len(self._cache),
            **self._stats
        }
    
    def clear_cache(self):
        """Clear embedding cache"""
        self._cache.clear()
        logger.info("🗑️ Embedding cache cleared")


# Global instance
embedding_service = LightweightEmbeddingService()


async def get_embedding_service() -> LightweightEmbeddingService:
    """Get the global embedding service instance"""
    await embedding_service.initialize()
    return embedding_service


def get_embedding_dimensions() -> int:
    """Get current embedding dimensions (for index configuration)"""
    if embedding_service.initialized:
        return embedding_service.dimensions
    # Default to OpenAI dimensions if not initialized
    return OPENAI_EMBEDDING_DIMENSIONS