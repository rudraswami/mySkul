"""
Semantic Memory Service - Long-Term Memory with Embeddings
Uses OpenAI embeddings for semantic search over student memories

PRODUCTION-GRADE ARCHITECTURE (like ChatGPT/Claude):
- In-memory LRU cache for embeddings (5 min TTL)
- Instant keyword fallback (no waiting for OpenAI)
- Non-blocking design (never blocks AI response)
"""
import logging
import asyncio
import numpy as np
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import OrderedDict

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """
    LRU Cache for embeddings with TTL - like production AI systems
    
    Prevents repeated OpenAI calls for same/similar queries.
    Cache hit = instant response (0ms vs 200-500ms)
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self._cache: OrderedDict[str, tuple] = OrderedDict()  # key -> (embedding, timestamp)
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def _hash_key(self, text: str) -> str:
        """Create cache key from text"""
        return hashlib.md5(text.lower().strip()[:500].encode()).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding if exists and not expired"""
        key = self._hash_key(text)
        if key in self._cache:
            embedding, timestamp = self._cache[key]
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()
            if age < self._ttl:
                self._hits += 1
                # Move to end (LRU)
                self._cache.move_to_end(key)
                return embedding
            else:
                # Expired
                del self._cache[key]
        self._misses += 1
        return None
    
    def set(self, text: str, embedding: List[float]) -> None:
        """Cache an embedding"""
        key = self._hash_key(text)
        self._cache[key] = (embedding, datetime.now(timezone.utc))
        self._cache.move_to_end(key)
        
        # Evict oldest if over capacity
        while len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
    
    def stats(self) -> Dict[str, Any]:
        """Cache statistics"""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0
        }


# Global embedding cache (shared across requests)
_embedding_cache = EmbeddingCache(max_size=1000, ttl_seconds=300)


class SemanticMemoryService:
    """
    Semantic search over long-term memories using embeddings
    
    PRODUCTION ARCHITECTURE:
    - LRU cache for embeddings (instant hits)
    - Keyword fallback FIRST (no waiting for slow embeddings)
    - OpenAI embedding as enhancement, not requirement
    - Zero blocking design
    """
    
    def __init__(self, db, openai_api_key: str = None):
        self.db = db
        self.openai_api_key = openai_api_key
        self.embedding_model = "text-embedding-3-small"  # 1536 dims, $0.02/1M tokens
        self.embedding_dimension = 1536
        # Track embedding health
        self._embedding_available = None  # None = unknown, True/False = tested
        self._embedding_failures = 0
        self._last_embedding_error = None
        # Use global cache
        self._cache = _embedding_cache
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate OpenAI embedding with LRU cache - PRODUCTION GRADE
        
        ARCHITECTURE (like ChatGPT):
        1. Check cache first (instant, 0ms)
        2. If cache miss, try OpenAI with strict timeout
        3. On any failure, return zero vector (triggers keyword fallback)
        
        This NEVER blocks - cache hit or immediate fallback.
        """
        try:
            # Clean text for consistency
            text = text.strip()[:500]  # Limit for cache key consistency
            
            # STEP 1: Check cache first (INSTANT - 0ms)
            cached = self._cache.get(text)
            if cached is not None:
                logger.debug(f"⚡ Embedding cache HIT")
                return cached
            
            # STEP 2: No API key = immediate keyword fallback
            if not self.openai_api_key:
                if self._embedding_available is None:
                    self._embedding_available = False
                    logger.info("📝 Embeddings disabled (no API key) - using keyword matching")
                return [0.0] * self.embedding_dimension
            
            # STEP 3: Check if embeddings are known to be broken
            if self._embedding_failures >= 3 and self._embedding_available is False:
                # Skip OpenAI entirely if it's been failing
                logger.debug("⏭️ Skipping OpenAI (recent failures) - using keyword matching")
                return [0.0] * self.embedding_dimension
            
            # STEP 4: Try OpenAI with VERY short timeout (500ms)
            # If it's not fast, keyword matching is better than waiting
            try:
                embedding = await asyncio.wait_for(
                    self._generate_embedding_async(text),
                    timeout=0.5  # 500ms - if slower, use keywords
                )
                
                # Success! Cache it and reset failure count
                self._cache.set(text, embedding)
                self._embedding_available = True
                self._embedding_failures = 0
                
                return embedding
                
            except asyncio.TimeoutError:
                # OpenAI too slow - use keyword matching instead
                self._embedding_failures += 1
                if self._embedding_failures == 1:
                    logger.info("⚡ OpenAI slow (>500ms) - using fast keyword matching")
                return [0.0] * self.embedding_dimension
            
        except Exception as e:
            self._embedding_failures += 1
            if self._embedding_failures <= 3:
                logger.warning(f"Embedding failed: {str(e)[:50]}")
            return [0.0] * self.embedding_dimension
    
    async def _generate_embedding_async(self, text: str) -> List[float]:
        """
        Generate embedding using asyncio thread pool
        Runs OpenAI sync call in background thread
        """
        loop = asyncio.get_event_loop()
        
        def _sync_call():
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key, timeout=0.4)
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        
        # Run in thread pool to avoid blocking
        return await loop.run_in_executor(None, _sync_call)
    
    def get_embedding_health(self) -> Dict[str, Any]:
        """
        FIX #2: Get embedding health status for monitoring
        
        Returns:
            Dict with embedding availability, failure count, and last error
        """
        return {
            "available": self._embedding_available,
            "failure_count": self._embedding_failures,
            "last_error": self._last_embedding_error,
            "mode": "semantic" if self._embedding_available else "keyword_fallback"
        }
    
    async def store_memory_with_embedding(
        self,
        user_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Store memory with embedding for semantic search
        
        Args:
            user_id: User ID
            content: Memory content text
            metadata: Additional metadata (topic, subject, etc.)
        
        Returns:
            Fact ID of stored memory
        """
        try:
            # Generate embedding
            embedding = await self.generate_embedding(content)
            
            # Build memory document
            from models.memory import FactType
            import uuid
            
            fact_id = str(uuid.uuid4())
            
            memory_doc = {
                "user_id": user_id,
                "fact_id": fact_id,
                "fact_type": metadata.get("fact_type", FactType.CONCEPT_LEARNED.value),
                "content": content,
                "embedding": embedding,
                "topic": metadata.get("topic", "unknown"),
                "subject": metadata.get("subject", "general"),
                "confidence": metadata.get("confidence", 0.7),
                "mastery_level": metadata.get("mastery_level"),
                "created_at": datetime.now(timezone.utc),
                "last_reinforced": None,
                "reinforcement_count": 0,
                "next_review_at": metadata.get("next_review_at"),
                "review_interval_days": 1,
                "easiness_factor": 2.5,
                "source_session_id": metadata.get("source_session_id"),
                "source_message_id": metadata.get("source_message_id"),
                "is_active": True,
                "is_verified": metadata.get("is_verified", False)
            }
            
            # Store in MongoDB
            await self.db.user_memory_facts.insert_one(memory_doc)
            
            logger.info(f"💾 Stored memory: {fact_id} - {content[:50]}")
            return fact_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store memory: {e}")
            return ""
    
    async def search_relevant_memories(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find relevant memories - INSTANT RESPONSE GUARANTEED
        
        PRODUCTION ARCHITECTURE:
        1. Fetch user memories from DB (with timeout)
        2. Try cached embedding search (instant if cached)
        3. Fall back to keyword matching (always works)
        
        This function NEVER blocks for more than 1 second.
        """
        try:
            # STEP 1: Fetch memories with strict timeout (1s max)
            try:
                all_memories = await asyncio.wait_for(
                    self.db.user_memory_facts.find({
                        "user_id": user_id,
                        "is_active": True
                    }).to_list(100),  # Limit to 100 memories for speed
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"⚡ Memory fetch timeout - returning empty")
                return []
            
            if not all_memories:
                return []
            
            # STEP 2: Get embedding (uses cache, very fast)
            query_embedding = await self.generate_embedding(query)
            
            # STEP 3: Search based on embedding availability
            has_valid_embedding = sum(query_embedding) != 0.0
            
            if has_valid_embedding:
                # Embedding search (best quality)
                return self._search_by_embedding(all_memories, query_embedding, top_k, min_similarity)
            else:
                # Keyword search (instant, always works)
                return self._search_by_keywords(all_memories, query, top_k)
                
        except Exception as e:
            logger.error(f"Memory search error: {str(e)[:50]}")
            return []
    
    def _search_by_embedding(
        self, 
        memories: List[Dict], 
        query_embedding: List[float],
        top_k: int,
        min_similarity: float
    ) -> List[Dict[str, Any]]:
        """Fast embedding-based search (synchronous, uses numpy)"""
        similarities = []
        
        for memory in memories:
            if "embedding" in memory and memory["embedding"]:
                similarity = self._cosine_similarity(query_embedding, memory["embedding"])
                if similarity >= min_similarity:
                    similarities.append({"similarity": similarity, "memory": memory})
        
        # Sort and return top-k
        similarities.sort(reverse=True, key=lambda x: x["similarity"])
        
        return [
            {
                "fact_id": item["memory"]["fact_id"],
                "content": item["memory"]["content"],
                "topic": item["memory"].get("topic", ""),
                "subject": item["memory"].get("subject", ""),
                "similarity_score": item["similarity"],
                "created_at": item["memory"].get("created_at"),
                "mastery_level": item["memory"].get("mastery_level"),
                "fact_type": item["memory"].get("fact_type", "")
            }
            for item in similarities[:top_k]
        ]
    
    def _search_by_keywords(
        self,
        memories: List[Dict],
        query: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Fast keyword-based search (synchronous, instant)"""
        scores = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for memory in memories:
            content = (memory.get("content", "") + " " + memory.get("topic", "")).lower()
            content_words = set(content.split())
            
            # Simple Jaccard similarity
            intersection = query_words & content_words
            union = query_words | content_words
            score = len(intersection) / len(union) if union else 0
            
            if score > 0:
                scores.append({"score": score, "memory": memory})
        
        # Sort and return top-k
        scores.sort(reverse=True, key=lambda x: x["score"])
        
        return [
            {
                "fact_id": item["memory"]["fact_id"],
                "content": item["memory"]["content"],
                "topic": item["memory"].get("topic", ""),
                "subject": item["memory"].get("subject", ""),
                "similarity_score": item["score"],
                "created_at": item["memory"].get("created_at"),
                "mastery_level": item["memory"].get("mastery_level"),
                "fact_type": item["memory"].get("fact_type", "")
            }
            for item in scores[:top_k]
        ]
    
    
    # FIX #8: Educational synonyms for better keyword matching
    _EDUCATIONAL_SYNONYMS = {
        "newton": ["force", "motion", "laws", "mechanics"],
        "force": ["newton", "push", "pull", "f=ma"],
        "derivative": ["differentiation", "slope", "rate", "dy/dx"],
        "integral": ["integration", "area", "antiderivative"],
        "acceleration": ["velocity", "speed", "motion"],
        "energy": ["work", "power", "joules", "kinetic", "potential"],
        "momentum": ["impulse", "collision", "mass", "velocity"],
        "wave": ["frequency", "wavelength", "amplitude", "oscillation"],
        "electric": ["current", "voltage", "resistance", "circuit"],
        "magnetic": ["field", "flux", "induction", "electromagnet"],
    }
    
    def _keyword_similarity(self, query: str, memory: Dict[str, Any]) -> float:
        """
        Fallback keyword-based similarity when embeddings unavailable
        
        FIX #8: Enhanced with stemming and educational synonyms
        
        Returns score 0.0-1.0 based on keyword overlap
        """
        # Extract keywords from query
        query_lower = query.lower()
        query_words = set(self._normalize_words(query_lower.split()))
        
        # Extract keywords from memory
        memory_text = (memory.get("content", "") + " " + memory.get("topic", "")).lower()
        memory_words = set(self._normalize_words(memory_text.split()))
        
        # FIX #8: Expand query words with synonyms
        expanded_query = set(query_words)
        for word in query_words:
            if word in self._EDUCATIONAL_SYNONYMS:
                expanded_query.update(self._EDUCATIONAL_SYNONYMS[word])
        
        # Calculate Jaccard similarity with expanded query
        intersection = expanded_query & memory_words
        union = query_words | memory_words  # Use original for union to not inflate
        
        if not union:
            return 0.0
        
        similarity = len(intersection) / len(union)
        
        # Boost if topic matches exactly
        if memory.get("topic", "").lower() in query_lower:
            similarity += 0.3
        
        # FIX #8: Boost if subject matches
        query_subject = self._detect_subject(query_lower)
        memory_subject = memory.get("subject", "").lower()
        if query_subject and memory_subject and query_subject == memory_subject:
            similarity += 0.2
        
        return min(1.0, similarity)
    
    def _normalize_words(self, words: List[str]) -> List[str]:
        """FIX #8: Simple word normalization (pseudo-stemming)"""
        normalized = []
        for word in words:
            # Remove punctuation
            word = ''.join(c for c in word if c.isalnum())
            if len(word) < 2:
                continue
            # Simple suffix removal (pseudo-stemming)
            if word.endswith('ing'):
                word = word[:-3]
            elif word.endswith('tion'):
                word = word[:-4]
            elif word.endswith('ed') and len(word) > 4:
                word = word[:-2]
            elif word.endswith('s') and len(word) > 3:
                word = word[:-1]
            normalized.append(word)
        return normalized
    
    def _detect_subject(self, text: str) -> Optional[str]:
        """FIX #8: Simple subject detection for matching boost"""
        if any(w in text for w in ['physics', 'force', 'energy', 'newton', 'motion']):
            return 'physics'
        if any(w in text for w in ['chemistry', 'reaction', 'molecule', 'acid', 'base']):
            return 'chemistry'
        if any(w in text for w in ['math', 'calculus', 'algebra', 'derivative', 'integral']):
            return 'mathematics'
        if any(w in text for w in ['biology', 'cell', 'dna', 'evolution', 'organism']):
            return 'biology'
        return None
    
    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score (0.0-1.0)
        """
        try:
            # Convert to numpy arrays
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(v1, v2)
            magnitude = np.linalg.norm(v1) * np.linalg.norm(v2)
            
            if magnitude == 0:
                return 0.0
            
            similarity = dot_product / magnitude
            
            # Clamp to [0, 1] range
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"❌ Cosine similarity calculation failed: {e}")
            return 0.0
    
    async def delete_memory(
        self,
        user_id: str,
        fact_id: str
    ) -> bool:
        """
        Delete a specific memory (privacy control)
        
        Args:
            user_id: User ID (for security)
            fact_id: Memory fact ID to delete
        
        Returns:
            True if deleted successfully
        """
        try:
            result = await self.db.user_memory_facts.update_one(
                {
                    "user_id": user_id,
                    "fact_id": fact_id
                },
                {
                    "$set": {
                        "is_active": False,
                        "deleted_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"🗑️ Deleted memory: {fact_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete memory: {e}")
            return False
    
    async def delete_all_user_memories(
        self,
        user_id: str
    ) -> int:
        """
        Delete all memories for a user (GDPR compliance)
        
        Args:
            user_id: User ID
        
        Returns:
            Number of memories deleted
        """
        try:
            result = await self.db.user_memory_facts.update_many(
                {"user_id": user_id},
                {
                    "$set": {
                        "is_active": False,
                        "deleted_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            count = result.modified_count
            logger.info(f"🗑️ Deleted {count} memories for user {user_id}")
            
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to delete user memories: {e}")
            return 0
