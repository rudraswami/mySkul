"""
Knowledge Tracker - Tracks Student's Knowledge State
=====================================================

Maintains a real-time model of what each student knows:
- Topics they've covered
- Concepts they've mastered vs. struggling with
- Knowledge gaps to address
- Prerequisites they need

This is the foundation of the Student Cognitive Model.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ConceptKnowledge:
    """Represents knowledge of a single concept"""
    concept_id: str
    concept_name: str
    subject: str
    topic: str
    
    # Knowledge state
    exposure_count: int = 0  # How many times they've seen this
    correct_count: int = 0   # How many times they got it right
    incorrect_count: int = 0 # How many times they got it wrong
    last_seen: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    
    # Mastery indicators
    mastery_score: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.0     # How confident are we in this score
    is_mastered: bool = False
    needs_review: bool = False
    
    # Spaced repetition
    review_interval_days: int = 1
    next_review_date: Optional[datetime] = None
    
    def update_exposure(self, correct: bool) -> None:
        """Update knowledge state after an interaction"""
        self.exposure_count += 1
        self.last_seen = datetime.now(timezone.utc)
        
        if self.first_seen is None:
            self.first_seen = self.last_seen
        
        if correct:
            self.correct_count += 1
        else:
            self.incorrect_count += 1
        
        # Recalculate mastery
        self._recalculate_mastery()
    
    def _recalculate_mastery(self) -> None:
        """Recalculate mastery score based on performance"""
        if self.exposure_count == 0:
            self.mastery_score = 0.0
            self.confidence = 0.0
            return
        
        # Base accuracy
        accuracy = self.correct_count / self.exposure_count if self.exposure_count > 0 else 0.0
        
        # Confidence increases with more exposures
        self.confidence = min(1.0, self.exposure_count / 10.0)
        
        # Mastery considers recency
        if self.last_seen:
            days_since = (datetime.now(timezone.utc) - self.last_seen).days
            recency_factor = max(0.5, 1.0 - (days_since / 30.0))  # Decay over 30 days
        else:
            recency_factor = 1.0
        
        self.mastery_score = accuracy * recency_factor
        
        # Determine mastery status
        self.is_mastered = self.mastery_score >= 0.8 and self.confidence >= 0.6
        self.needs_review = (
            self.mastery_score < 0.7 or 
            (self.last_seen and (datetime.now(timezone.utc) - self.last_seen).days > 14)
        )
        
        # Update spaced repetition interval
        if self.is_mastered:
            self.review_interval_days = min(30, self.review_interval_days * 2)
        elif self.mastery_score < 0.5:
            self.review_interval_days = 1
        
        if self.last_seen:
            from datetime import timedelta
            self.next_review_date = self.last_seen + timedelta(days=self.review_interval_days)


@dataclass
class TopicKnowledge:
    """Aggregated knowledge for a topic"""
    topic_name: str
    subject: str
    concepts: Dict[str, ConceptKnowledge] = field(default_factory=dict)
    
    @property
    def mastery_score(self) -> float:
        """Average mastery across all concepts in topic"""
        if not self.concepts:
            return 0.0
        return sum(c.mastery_score for c in self.concepts.values()) / len(self.concepts)
    
    @property
    def coverage(self) -> float:
        """Percentage of concepts the student has been exposed to"""
        if not self.concepts:
            return 0.0
        exposed = sum(1 for c in self.concepts.values() if c.exposure_count > 0)
        return exposed / len(self.concepts)
    
    @property
    def weak_concepts(self) -> List[ConceptKnowledge]:
        """Concepts that need more work"""
        return [c for c in self.concepts.values() if c.mastery_score < 0.6 and c.exposure_count > 0]
    
    @property
    def review_needed(self) -> List[ConceptKnowledge]:
        """Concepts that need review"""
        return [c for c in self.concepts.values() if c.needs_review]


class KnowledgeTracker:
    """
    Tracks a student's knowledge state across all subjects and topics.
    
    This is the core of the cognitive model - it knows what each student
    knows, what they're struggling with, and what they need to learn next.
    """
    
    def __init__(self, db=None):
        """Initialize the knowledge tracker"""
        self.db = db
        self._cache: Dict[str, Dict[str, TopicKnowledge]] = {}  # user_id -> subject -> TopicKnowledge
        logger.info("🧠 KnowledgeTracker initialized")
    
    async def get_student_knowledge(
        self,
        user_id: str,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive knowledge state for a student.
        
        Args:
            user_id: Student's user ID
            subject: Optional filter by subject
            
        Returns:
            Dict with knowledge state, mastery levels, gaps, etc.
        """
        # Load from cache or database
        knowledge = await self._load_knowledge(user_id)
        
        if subject:
            knowledge = {k: v for k, v in knowledge.items() if k.lower() == subject.lower()}
        
        # Build summary
        summary = {
            "user_id": user_id,
            "subjects": {},
            "overall_mastery": 0.0,
            "total_concepts_learned": 0,
            "concepts_mastered": 0,
            "concepts_struggling": 0,
            "recommended_topics": [],
            "knowledge_gaps": []
        }
        
        total_mastery = 0.0
        subject_count = 0
        
        for subj, topics in knowledge.items():
            subject_data = {
                "topics": {},
                "mastery": 0.0,
                "weak_areas": [],
                "strong_areas": []
            }
            
            topic_mastery_sum = 0.0
            for topic_name, topic_knowledge in topics.items():
                topic_data = {
                    "mastery": topic_knowledge.mastery_score,
                    "coverage": topic_knowledge.coverage,
                    "concepts_count": len(topic_knowledge.concepts),
                    "weak_concepts": [c.concept_name for c in topic_knowledge.weak_concepts[:3]]
                }
                subject_data["topics"][topic_name] = topic_data
                topic_mastery_sum += topic_knowledge.mastery_score
                
                # Categorize as weak or strong
                if topic_knowledge.mastery_score < 0.5:
                    subject_data["weak_areas"].append(topic_name)
                elif topic_knowledge.mastery_score > 0.8:
                    subject_data["strong_areas"].append(topic_name)
                
                # Count concepts
                for concept in topic_knowledge.concepts.values():
                    summary["total_concepts_learned"] += 1 if concept.exposure_count > 0 else 0
                    if concept.is_mastered:
                        summary["concepts_mastered"] += 1
                    elif concept.mastery_score < 0.5 and concept.exposure_count > 0:
                        summary["concepts_struggling"] += 1
            
            if len(topics) > 0:
                subject_data["mastery"] = topic_mastery_sum / len(topics)
                total_mastery += subject_data["mastery"]
                subject_count += 1
            
            summary["subjects"][subj] = subject_data
        
        if subject_count > 0:
            summary["overall_mastery"] = total_mastery / subject_count
        
        # Find knowledge gaps
        summary["knowledge_gaps"] = self._identify_gaps(knowledge)
        
        # Get recommendations
        summary["recommended_topics"] = self._get_recommendations(knowledge)
        
        return summary
    
    async def record_interaction(
        self,
        user_id: str,
        subject: str,
        topic: str,
        concepts: List[str],
        performance: Dict[str, bool]  # concept_id -> correct/incorrect
    ) -> None:
        """
        Record a learning interaction to update knowledge state.
        
        Args:
            user_id: Student's user ID
            subject: Subject area
            topic: Topic name
            concepts: List of concepts covered
            performance: Dict mapping concept_id to whether student got it right
        """
        knowledge = await self._load_knowledge(user_id)
        
        # Ensure subject exists
        if subject not in knowledge:
            knowledge[subject] = {}
        
        # Ensure topic exists
        if topic not in knowledge[subject]:
            knowledge[subject][topic] = TopicKnowledge(
                topic_name=topic,
                subject=subject
            )
        
        topic_knowledge = knowledge[subject][topic]
        
        # Update each concept
        for concept_name in concepts:
            concept_id = f"{subject}:{topic}:{concept_name}".lower().replace(" ", "_")
            
            if concept_id not in topic_knowledge.concepts:
                topic_knowledge.concepts[concept_id] = ConceptKnowledge(
                    concept_id=concept_id,
                    concept_name=concept_name,
                    subject=subject,
                    topic=topic
                )
            
            correct = performance.get(concept_id, performance.get(concept_name, True))
            topic_knowledge.concepts[concept_id].update_exposure(correct)
        
        # Save to cache
        self._cache[user_id] = knowledge
        
        # Persist to database
        await self._save_knowledge(user_id, knowledge)
        
        logger.info(f"📝 Recorded interaction for {user_id}: {topic} ({len(concepts)} concepts)")
    
    async def get_mastery_level(
        self,
        user_id: str,
        subject: str,
        topic: Optional[str] = None
    ) -> float:
        """Get mastery level (0.0 to 1.0) for a subject/topic"""
        knowledge = await self._load_knowledge(user_id)
        
        if subject not in knowledge:
            return 0.0
        
        if topic:
            topic_knowledge = knowledge[subject].get(topic)
            return topic_knowledge.mastery_score if topic_knowledge else 0.0
        else:
            # Average across all topics in subject
            topics = knowledge[subject]
            if not topics:
                return 0.0
            return sum(t.mastery_score for t in topics.values()) / len(topics)
    
    async def get_weak_areas(
        self,
        user_id: str,
        subject: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get areas where student needs improvement"""
        knowledge = await self._load_knowledge(user_id)
        
        weak_areas = []
        
        for subj, topics in knowledge.items():
            if subject and subj.lower() != subject.lower():
                continue
            
            for topic_name, topic_knowledge in topics.items():
                if topic_knowledge.mastery_score < 0.6 and topic_knowledge.coverage > 0:
                    weak_areas.append({
                        "subject": subj,
                        "topic": topic_name,
                        "mastery": topic_knowledge.mastery_score,
                        "weak_concepts": [c.concept_name for c in topic_knowledge.weak_concepts[:3]],
                        "priority": 1.0 - topic_knowledge.mastery_score
                    })
        
        # Sort by priority (lower mastery = higher priority)
        weak_areas.sort(key=lambda x: x["priority"], reverse=True)
        
        return weak_areas[:limit]
    
    async def get_review_queue(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get concepts that need review (spaced repetition)"""
        knowledge = await self._load_knowledge(user_id)
        
        review_items = []
        now = datetime.now(timezone.utc)
        
        for subject, topics in knowledge.items():
            for topic_name, topic_knowledge in topics.items():
                for concept in topic_knowledge.concepts.values():
                    if concept.needs_review or (
                        concept.next_review_date and concept.next_review_date <= now
                    ):
                        review_items.append({
                            "subject": subject,
                            "topic": topic_name,
                            "concept": concept.concept_name,
                            "mastery": concept.mastery_score,
                            "days_since_review": (now - concept.last_seen).days if concept.last_seen else None,
                            "priority": (1.0 - concept.mastery_score) * 2 if concept.mastery_score < 0.5 else 1.0
                        })
        
        # Sort by priority
        review_items.sort(key=lambda x: x["priority"], reverse=True)
        
        return review_items[:limit]
    
    def _identify_gaps(self, knowledge: Dict) -> List[Dict[str, Any]]:
        """Identify knowledge gaps based on prerequisites"""
        gaps = []
        
        # Define prerequisite relationships
        prerequisites = {
            "calculus": ["algebra", "trigonometry"],
            "electromagnetism": ["electrostatics", "magnetism"],
            "organic chemistry": ["chemical bonding", "basic organic"],
            "integration": ["differentiation", "limits"],
            "thermodynamics": ["heat", "work", "energy"]
        }
        
        for subject, topics in knowledge.items():
            for topic_name, topic_knowledge in topics.items():
                topic_lower = topic_name.lower()
                
                # Check if student is trying advanced topic without prerequisites
                if topic_knowledge.coverage > 0.3 and topic_knowledge.mastery_score < 0.4:
                    for prereq_key, prereqs in prerequisites.items():
                        if prereq_key in topic_lower:
                            for prereq in prereqs:
                                prereq_mastery = self._get_topic_mastery(knowledge, subject, prereq)
                                if prereq_mastery < 0.6:
                                    gaps.append({
                                        "type": "prerequisite_gap",
                                        "subject": subject,
                                        "topic": topic_name,
                                        "missing_prerequisite": prereq,
                                        "current_mastery": topic_knowledge.mastery_score,
                                        "suggestion": f"Review {prereq} before continuing with {topic_name}"
                                    })
        
        return gaps[:5]  # Limit to top 5 gaps
    
    def _get_topic_mastery(self, knowledge: Dict, subject: str, topic_search: str) -> float:
        """Helper to find mastery for a topic (partial match)"""
        if subject not in knowledge:
            return 0.0
        
        for topic_name, topic_knowledge in knowledge[subject].items():
            if topic_search.lower() in topic_name.lower():
                return topic_knowledge.mastery_score
        
        return 0.0
    
    def _get_recommendations(self, knowledge: Dict) -> List[Dict[str, Any]]:
        """Get recommended topics to study next"""
        recommendations = []
        
        for subject, topics in knowledge.items():
            for topic_name, topic_knowledge in topics.items():
                # Recommend topics with low coverage but some exposure
                if 0 < topic_knowledge.coverage < 0.5:
                    recommendations.append({
                        "subject": subject,
                        "topic": topic_name,
                        "reason": "incomplete_coverage",
                        "coverage": topic_knowledge.coverage,
                        "priority": topic_knowledge.coverage  # Higher coverage = more priority to finish
                    })
                
                # Recommend topics ready for advancement
                elif topic_knowledge.mastery_score > 0.7 and topic_knowledge.coverage > 0.8:
                    recommendations.append({
                        "subject": subject,
                        "topic": topic_name,
                        "reason": "ready_for_advanced",
                        "mastery": topic_knowledge.mastery_score,
                        "priority": topic_knowledge.mastery_score
                    })
        
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return recommendations[:5]
    
    async def _load_knowledge(self, user_id: str) -> Dict[str, Dict[str, TopicKnowledge]]:
        """Load knowledge state from cache or database"""
        if user_id in self._cache:
            return self._cache[user_id]
        
        # Try to load from database
        if self.db is not None:
            try:
                record = await self.db.student_knowledge.find_one({"user_id": user_id})
                if record:
                    knowledge = self._deserialize_knowledge(record.get("knowledge", {}))
                    self._cache[user_id] = knowledge
                    return knowledge
            except Exception as e:
                logger.warning(f"Failed to load knowledge from DB: {e}")
        
        # Return empty knowledge state
        self._cache[user_id] = {}
        return {}
    
    async def _save_knowledge(self, user_id: str, knowledge: Dict) -> None:
        """Save knowledge state to database"""
        if self.db is None:
            return
        
        try:
            serialized = self._serialize_knowledge(knowledge)
            await self.db.student_knowledge.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "knowledge": serialized,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to save knowledge to DB: {e}")
    
    def _serialize_knowledge(self, knowledge: Dict) -> Dict:
        """Serialize knowledge for database storage"""
        serialized = {}
        for subject, topics in knowledge.items():
            serialized[subject] = {}
            for topic_name, topic_knowledge in topics.items():
                serialized[subject][topic_name] = {
                    "topic_name": topic_knowledge.topic_name,
                    "subject": topic_knowledge.subject,
                    "concepts": {
                        cid: {
                            "concept_id": c.concept_id,
                            "concept_name": c.concept_name,
                            "exposure_count": c.exposure_count,
                            "correct_count": c.correct_count,
                            "incorrect_count": c.incorrect_count,
                            "mastery_score": c.mastery_score,
                            "last_seen": c.last_seen.isoformat() if c.last_seen else None
                        }
                        for cid, c in topic_knowledge.concepts.items()
                    }
                }
        return serialized
    
    def _deserialize_knowledge(self, data: Dict) -> Dict[str, Dict[str, TopicKnowledge]]:
        """Deserialize knowledge from database"""
        knowledge = {}
        for subject, topics in data.items():
            knowledge[subject] = {}
            for topic_name, topic_data in topics.items():
                topic_knowledge = TopicKnowledge(
                    topic_name=topic_data.get("topic_name", topic_name),
                    subject=topic_data.get("subject", subject)
                )
                
                for cid, cdata in topic_data.get("concepts", {}).items():
                    concept = ConceptKnowledge(
                        concept_id=cdata.get("concept_id", cid),
                        concept_name=cdata.get("concept_name", ""),
                        subject=subject,
                        topic=topic_name,
                        exposure_count=cdata.get("exposure_count", 0),
                        correct_count=cdata.get("correct_count", 0),
                        incorrect_count=cdata.get("incorrect_count", 0),
                        mastery_score=cdata.get("mastery_score", 0.0)
                    )
                    if cdata.get("last_seen"):
                        concept.last_seen = datetime.fromisoformat(cdata["last_seen"])
                    topic_knowledge.concepts[cid] = concept
                
                knowledge[subject][topic_name] = topic_knowledge
        
        return knowledge

