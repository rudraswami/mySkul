"""
💾 Memory System - Short-term and Long-term Memory
===================================================

Agents need memory to:
1. Remember conversation context (short-term)
2. Learn from past interactions (long-term)
3. Track student patterns and preferences
4. Build persistent knowledge about students

Architecture:
- ShortTermMemory: Current session context (last N turns)
- LongTermMemory: Persistent student profile and patterns
- MemorySystem: Unified interface to both
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """A single memory item"""
    content: str
    memory_type: str  # 'conversation', 'fact', 'preference', 'mistake', 'success'
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5  # 0 to 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "type": self.memory_type,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        return cls(
            content=data["content"],
            memory_type=data["type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            importance=data.get("importance", 0.5),
            metadata=data.get("metadata", {})
        )


class ShortTermMemory:
    """
    Short-term memory for current conversation context.
    
    Maintains a sliding window of recent interactions.
    Used to maintain conversation coherence.
    """
    
    def __init__(self, max_items: int = 20):
        self.max_items = max_items
        self._memories: deque = deque(maxlen=max_items)
        self._session_facts: Dict[str, Any] = {}  # Quick facts for this session
    
    def add(self, content: str, memory_type: str = "conversation", **metadata) -> None:
        """Add a memory item"""
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            metadata=metadata
        )
        self._memories.append(item)
    
    def add_fact(self, key: str, value: Any) -> None:
        """Add a quick session fact"""
        self._session_facts[key] = value
    
    def get_fact(self, key: str, default: Any = None) -> Any:
        """Get a session fact"""
        return self._session_facts.get(key, default)
    
    def get_recent(self, n: int = 5) -> List[MemoryItem]:
        """Get n most recent memories"""
        items = list(self._memories)
        return items[-n:] if len(items) > n else items
    
    def get_context_summary(self) -> str:
        """Get a summary of recent context for LLM prompts"""
        recent = self.get_recent(5)
        if not recent:
            return "No previous context."
        
        summary = ["Recent conversation:"]
        for item in recent:
            summary.append(f"- [{item.memory_type}] {item.content[:100]}...")
        
        if self._session_facts:
            summary.append("\nSession facts:")
            for k, v in self._session_facts.items():
                summary.append(f"- {k}: {v}")
        
        return "\n".join(summary)
    
    def clear(self) -> None:
        """Clear all short-term memories"""
        self._memories.clear()
        self._session_facts.clear()
    
    def search(self, query: str) -> List[MemoryItem]:
        """Search memories by content"""
        query_lower = query.lower()
        return [
            m for m in self._memories 
            if query_lower in m.content.lower()
        ]


class LongTermMemory:
    """
    Long-term memory for persistent student information.
    
    MEMORY CONTRACT: Uses MemoryService as the SINGLE SOURCE OF TRUTH.
    All data is persisted to MongoDB via MemoryService.
    
    Stores:
    - Learning patterns (what approaches work for this student)
    - Common mistakes (to proactively address)
    - Preferences (communication style, examples they relate to)
    - Progress tracking (topics mastered, weak areas)
    """
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self._memories: List[MemoryItem] = []
        self._patterns: Dict[str, Any] = {
            "learning_style": None,  # visual, auditory, kinesthetic
            "preferred_examples": [],  # cricket, bollywood, gaming
            "common_mistakes": [],
            "strong_topics": [],
            "weak_topics": [],
            "engagement_patterns": {}
        }
        self._loaded = False
        self._memory_service = None
        self._db = None
    
    def _get_memory_service(self, db=None):
        """Get or create MemoryService instance."""
        actual_db = db or self._db
        if actual_db and self._memory_service is None:
            try:
                from services.memory_service import MemoryService
                self._memory_service = MemoryService(actual_db)
            except ImportError:
                logger.warning("MemoryService not available")
        return self._memory_service
    
    async def load(self, db=None) -> None:
        """
        Load memories from REAL persistent storage (MongoDB via MemoryService).
        
        This is the SINGLE SOURCE OF TRUTH for long-term memory.
        """
        self._db = db or self._db
        memory_service = self._get_memory_service(db)
        
        if memory_service:
            try:
                # Load real student profile from MongoDB
                profile = await memory_service.get_student_profile(self.student_id)
                
                if profile:
                    # Map profile data to patterns
                    self._patterns["learning_style"] = profile.get("preferred_explanation", None)
                    self._patterns["preferred_examples"] = profile.get("preferred_analogies", [])
                    self._patterns["strong_topics"] = profile.get("strong_topics", [])
                    self._patterns["weak_topics"] = profile.get("weak_topics", [])
                    
                    # Load common mistakes from profile
                    mistakes_data = profile.get("common_mistakes", [])
                    self._patterns["common_mistakes"] = mistakes_data if isinstance(mistakes_data, list) else []
                    
                    # Load engagement patterns
                    self._patterns["engagement_patterns"] = profile.get("engagement_patterns", {})
                    
                    logger.info(f"💾 REAL memory loaded from MongoDB for student {self.student_id}")
                else:
                    logger.info(f"💾 No existing profile found for student {self.student_id}, starting fresh")
            except Exception as e:
                logger.warning(f"💾 Failed to load memory from MongoDB: {e}")
        else:
            logger.warning(f"💾 No database connection - memory will be session-only for {self.student_id}")
        
        self._loaded = True
    
    async def save(self, db=None) -> None:
        """
        Save memories to REAL persistent storage (MongoDB via MemoryService).
        
        This persists across restarts and is shared across all agents.
        """
        self._db = db or self._db
        memory_service = self._get_memory_service(db)
        
        if memory_service:
            try:
                # Build update dict from patterns
                updates = {
                    "preferred_explanation": self._patterns.get("learning_style"),
                    "preferred_analogies": self._patterns.get("preferred_examples", []),
                    "strong_topics": self._patterns.get("strong_topics", []),
                    "weak_topics": self._patterns.get("weak_topics", []),
                    "common_mistakes": self._patterns.get("common_mistakes", []),
                    "engagement_patterns": self._patterns.get("engagement_patterns", {}),
                    "last_updated": datetime.now().isoformat()
                }
                
                # Persist to MongoDB
                success = await memory_service.update_student_profile(self.student_id, updates)
                
                if success:
                    logger.info(f"💾 REAL memory saved to MongoDB for student {self.student_id}")
                else:
                    logger.warning(f"💾 Failed to save memory for {self.student_id}")
            except Exception as e:
                logger.error(f"💾 Error saving memory to MongoDB: {e}")
        else:
            logger.warning(f"💾 No database connection - memory NOT persisted for {self.student_id}")
    
    def add_memory(
        self, 
        content: str, 
        memory_type: str,
        importance: float = 0.5,
        **metadata
    ) -> None:
        """Add a long-term memory"""
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata
        )
        self._memories.append(item)
    
    def record_mistake(self, topic: str, mistake: str, context: str = "") -> None:
        """Record a common mistake for future reference"""
        self._patterns["common_mistakes"].append({
            "topic": topic,
            "mistake": mistake,
            "context": context,
            "count": 1,
            "last_seen": datetime.now().isoformat()
        })
        
        # Add to weak topics if not already there
        if topic not in self._patterns["weak_topics"]:
            self._patterns["weak_topics"].append(topic)
    
    def record_success(self, topic: str) -> None:
        """Record successful understanding of a topic"""
        if topic not in self._patterns["strong_topics"]:
            self._patterns["strong_topics"].append(topic)
        
        # Remove from weak topics if there
        if topic in self._patterns["weak_topics"]:
            self._patterns["weak_topics"].remove(topic)
    
    def set_learning_style(self, style: str) -> None:
        """Set the student's preferred learning style"""
        self._patterns["learning_style"] = style
    
    def add_preferred_example_type(self, example_type: str) -> None:
        """Add a preferred example type (e.g., cricket analogies)"""
        if example_type not in self._patterns["preferred_examples"]:
            self._patterns["preferred_examples"].append(example_type)
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get learning patterns"""
        return self._patterns.copy()
    
    def get_weak_topics(self) -> List[str]:
        """Get list of weak topics"""
        return self._patterns["weak_topics"].copy()
    
    def get_common_mistakes(self, topic: str = None) -> List[Dict]:
        """Get common mistakes, optionally filtered by topic"""
        mistakes = self._patterns["common_mistakes"]
        if topic:
            return [m for m in mistakes if topic.lower() in m["topic"].lower()]
        return mistakes
    
    def get_personalization_hints(self) -> Dict[str, Any]:
        """Get hints for personalizing responses"""
        return {
            "learning_style": self._patterns["learning_style"],
            "preferred_examples": self._patterns["preferred_examples"][:3],
            "avoid_topics": self._patterns["weak_topics"][:3],
            "celebrate_topics": self._patterns["strong_topics"][:3]
        }
    
    def search(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Search long-term memories"""
        query_lower = query.lower()
        matching = [
            m for m in self._memories
            if query_lower in m.content.lower()
        ]
        # Sort by importance and recency
        matching.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
        return matching[:limit]


class MemorySystem:
    """
    Unified memory system combining short-term and long-term memory.
    
    MEMORY CONTRACT: Uses MemoryService as the SINGLE SOURCE OF TRUTH.
    All long-term data persists to MongoDB across restarts and agents.
    
    Usage:
        memory = MemorySystem(student_id="123", db=db)
        await memory.initialize()
        
        # Short-term operations
        memory.remember("Student asked about quadratic formula")
        memory.set_session_fact("current_topic", "algebra")
        
        # Long-term operations
        memory.record_mistake("quadratic", "forgot to check discriminant")
        memory.record_success("linear_equations")
        
        # Get context for LLM
        context = memory.get_context_for_prompt()
    """
    
    def __init__(self, student_id: str, short_term_size: int = 20, db=None):
        self.student_id = student_id
        self.short_term = ShortTermMemory(max_items=short_term_size)
        self.long_term = LongTermMemory(student_id)
        self._db = db
        self._initialized = False
    
    def set_db(self, db) -> None:
        """Set database connection for persistent memory."""
        self._db = db
        self.long_term._db = db
    
    async def initialize(self, db=None) -> None:
        """Initialize memory system with database connection."""
        actual_db = db or self._db
        if actual_db:
            self._db = actual_db
        await self.long_term.load(self._db)
        self._initialized = True
        logger.info(f"🧠 Memory system initialized for {self.student_id} (persistent={self._db is not None})")
    
    async def save(self, db=None) -> None:
        """Persist long-term memories to database."""
        actual_db = db or self._db
        await self.long_term.save(actual_db)
        logger.info(f"🧠 Memory saved for {self.student_id}")
    
    # Short-term operations
    def remember(self, content: str, memory_type: str = "conversation", **metadata) -> None:
        """Add to short-term memory"""
        self.short_term.add(content, memory_type, **metadata)
    
    def set_session_fact(self, key: str, value: Any) -> None:
        """Set a session fact"""
        self.short_term.add_fact(key, value)
    
    def get_session_fact(self, key: str, default: Any = None) -> Any:
        """Get a session fact"""
        return self.short_term.get_fact(key, default)
    
    def get_recent_context(self, n: int = 5) -> List[MemoryItem]:
        """Get recent conversation context"""
        return self.short_term.get_recent(n)
    
    # Long-term operations
    def record_mistake(self, topic: str, mistake: str, context: str = "") -> None:
        """Record a mistake for future reference"""
        self.long_term.record_mistake(topic, mistake, context)
        # Also add to short-term for immediate context
        self.short_term.add(f"Mistake: {mistake}", "mistake", topic=topic)
    
    def record_success(self, topic: str) -> None:
        """Record successful understanding"""
        self.long_term.record_success(topic)
    
    def set_learning_style(self, style: str) -> None:
        """Set learning style preference"""
        self.long_term.set_learning_style(style)
    
    def add_preferred_example(self, example_type: str) -> None:
        """Add preferred example type"""
        self.long_term.add_preferred_example_type(example_type)
    
    # Combined operations
    def get_context_for_prompt(self) -> str:
        """
        Get comprehensive context for LLM prompts.
        Combines short-term and long-term information.
        """
        parts = []
        
        # Short-term context
        short_context = self.short_term.get_context_summary()
        if short_context != "No previous context.":
            parts.append("## Recent Context\n" + short_context)
        
        # Long-term patterns
        patterns = self.long_term.get_patterns()
        
        if patterns["learning_style"]:
            parts.append(f"## Learning Style\n{patterns['learning_style']}")
        
        if patterns["preferred_examples"]:
            parts.append(f"## Preferred Examples\nStudent responds well to: {', '.join(patterns['preferred_examples'])}")
        
        if patterns["weak_topics"]:
            parts.append(f"## Areas to Focus\nStudent struggles with: {', '.join(patterns['weak_topics'][:3])}")
        
        if patterns["common_mistakes"]:
            recent_mistakes = patterns["common_mistakes"][-3:]
            mistakes_str = "\n".join([f"- {m['topic']}: {m['mistake']}" for m in recent_mistakes])
            parts.append(f"## Common Mistakes to Address\n{mistakes_str}")
        
        return "\n\n".join(parts) if parts else "No previous context available."
    
    def search_all(self, query: str) -> Dict[str, List[MemoryItem]]:
        """Search both short and long term memories"""
        return {
            "short_term": self.short_term.search(query),
            "long_term": self.long_term.search(query)
        }

