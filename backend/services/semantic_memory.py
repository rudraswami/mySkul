"""
Semantic Memory Service - Long-Term Memory with Embeddings
Uses OpenAI embeddings for semantic search over student memories
"""
import logging
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SemanticMemoryService:
    """
    Semantic search over long-term memories using embeddings
    
    Features:
    - Generate OpenAI embeddings (text-embedding-3-small)
    - Store memories with vector representations
    - Cosine similarity search
    - Top-k relevant memory retrieval
    """
    
    def __init__(self, db, openai_api_key: str = None):
        self.db = db
        self.openai_api_key = openai_api_key
        self.embedding_model = "text-embedding-3-small"  # 1536 dims, $0.02/1M tokens
        self.embedding_dimension = 1536
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate OpenAI embedding for text
        
        Args:
            text: Text to embed
        
        Returns:
            1536-dimensional embedding vector
        """
        try:
            if not self.openai_api_key:
                logger.warning("⚠️ OpenAI API key not provided, returning zero vector")
                return [0.0] * self.embedding_dimension
            
            # Import OpenAI client
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # Clean text
            text = text.strip()[:8000]  # Max 8k chars
            
            # Generate embedding
            response = client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"✅ Generated embedding: {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            # Embeddings unavailable (expected with Emergent key, not OpenAI key)
            logger.warning(f"⚠️ Embeddings unavailable (using keyword matching instead): {str(e)[:100]}")
            # Return zero vector as fallback (triggers keyword matching)
            return [0.0] * self.embedding_dimension
    
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
        Find relevant memories using cosine similarity OR keyword matching
        
        Args:
            user_id: User ID
            query: Query text
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold (0.0-1.0)
        
        Returns:
            List of relevant memories sorted by similarity
        """
        try:
            # Get all active user memories
            all_memories = await self.db.user_memory_facts.find({
                "user_id": user_id,
                "is_active": True
            }).to_list(None)
            
            if not all_memories:
                logger.info(f"📝 No memories found for user {user_id}")
                return []
            
            # Try embedding-based search first
            query_embedding = await self.generate_embedding(query)
            
            # Check if we have valid embeddings
            has_valid_embeddings = sum(query_embedding) != 0.0  # Not all zeros
            
            if has_valid_embeddings:
                # Use cosine similarity (preferred)
                similarities = []
                for memory in all_memories:
                    if "embedding" in memory and memory["embedding"]:
                        similarity = self._cosine_similarity(
                            query_embedding,
                            memory["embedding"]
                        )
                        
                        if similarity >= min_similarity:
                            similarities.append({
                                "similarity": similarity,
                                "memory": memory
                            })
                
                # Sort by similarity (descending)
                similarities.sort(reverse=True, key=lambda x: x["similarity"])
                
                logger.info(f"🔍 Using embedding-based search")
            else:
                # Fallback to keyword matching (when embeddings unavailable)
                logger.warning("⚠️ Embeddings unavailable, using keyword matching fallback")
                similarities = []
                for memory in all_memories:
                    score = self._keyword_similarity(query.lower(), memory)
                    if score > 0:
                        similarities.append({
                            "similarity": score,
                            "memory": memory
                        })
                
                # Sort by score
                similarities.sort(reverse=True, key=lambda x: x["similarity"])
            
            # Return top-k
            results = []
            for item in similarities[:top_k]:
                memory = item["memory"]
                results.append({
                    "fact_id": memory["fact_id"],
                    "content": memory["content"],
                    "topic": memory["topic"],
                    "subject": memory["subject"],
                    "similarity_score": item["similarity"],
                    "created_at": memory["created_at"],
                    "mastery_level": memory.get("mastery_level"),
                    "fact_type": memory["fact_type"]
                })
            
            logger.info(f"🔍 Found {len(results)} relevant memories (top-{top_k})")
            return results
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    def _keyword_similarity(self, query: str, memory: Dict[str, Any]) -> float:
        """
        Fallback keyword-based similarity when embeddings unavailable
        
        Returns score 0.0-1.0 based on keyword overlap
        """
        # Extract keywords from query
        query_words = set(query.lower().split())
        
        # Extract keywords from memory
        memory_text = (memory.get("content", "") + " " + memory.get("topic", "")).lower()
        memory_words = set(memory_text.split())
        
        # Calculate Jaccard similarity
        intersection = query_words & memory_words
        union = query_words | memory_words
        
        if not union:
            return 0.0
        
        similarity = len(intersection) / len(union)
        
        # Boost if topic matches exactly
        if memory.get("topic", "").lower() in query.lower():
            similarity += 0.3
        
        return min(1.0, similarity)
    
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
