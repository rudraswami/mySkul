"""
🔒 Consistency Engine - Cross-Session Contradiction Detection
=============================================================

This engine BUILDS TRUST by ensuring consistency across sessions.

PROBLEM:
- LLMs can give contradictory answers to similar questions
- Students lose trust when they notice inconsistencies
- No memory of previous explanations = same question, different answer

SOLUTION:
- Track explanations given per concept
- Detect when new explanation contradicts previous
- Either reconcile OR explicitly acknowledge: "I said X before, but Y is more accurate because..."
- Build a consistent knowledge model per student

THIS IS WHAT BUILDS TRUST.
A chatbot forgets. A teacher remembers.
"""

import logging
import re
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConsistencyStatus(Enum):
    """Status of consistency check"""
    CONSISTENT = "consistent"           # New explanation aligns with previous
    MINOR_VARIATION = "minor_variation" # Small differences, not contradictory
    POTENTIAL_CONFLICT = "potential_conflict"  # May contradict, needs review
    CONTRADICTION = "contradiction"     # Directly contradicts previous
    NO_HISTORY = "no_history"          # First time explaining this concept


@dataclass
class ConsistencyCheckResult:
    """Result of checking consistency with previous explanations"""
    status: ConsistencyStatus
    previous_explanation: Optional[str]   # What we said before
    new_explanation: str                   # What we're saying now
    conflict_points: List[str]            # Specific conflicts found
    reconciliation: Optional[str]         # How to reconcile if conflict
    should_acknowledge: bool               # Should we acknowledge the difference?
    acknowledgment_text: Optional[str]    # Text to use if acknowledging
    confidence: float                      # 0-1 confidence in this assessment


@dataclass
class ExplanationRecord:
    """Record of an explanation given"""
    concept_id: str
    concept_name: str
    explanation_summary: str             # Key points only (not full text)
    key_facts: List[str]                 # Extracted facts
    given_at: datetime
    session_id: str
    user_id: str
    subject: str


class ConsistencyEngine:
    """
    Engine that ensures consistency across explanations.
    
    This is critical for TRUST.
    Students need to know we remember what we taught them.
    """
    
    # Patterns that indicate factual claims (things that should be consistent)
    FACTUAL_PATTERNS = [
        r'is defined as',
        r'equals',
        r'is equal to',
        r'means',
        r'refers to',
        r'is measured in',
        r'has units of',
        r'is caused by',
        r'results in',
        r'always',
        r'never',
        r'must',
        r'cannot',
        r'is the formula',
        r'the equation is',
    ]
    
    # Contradiction indicators
    CONTRADICTION_INDICATORS = [
        ('always', 'never'),
        ('increases', 'decreases'),
        ('positive', 'negative'),
        ('directly', 'inversely'),
        ('greater', 'less'),
        ('more', 'less'),
        ('higher', 'lower'),
        ('true', 'false'),
        ('correct', 'incorrect'),
    ]
    
    def __init__(self, db):
        self.db = db
        logger.info("🔒 ConsistencyEngine initialized - Trust building active")
    
    async def check_consistency(
        self,
        user_id: str,
        concept_name: str,
        new_explanation: str,
        subject: str = "General"
    ) -> ConsistencyCheckResult:
        """
        Check if new explanation is consistent with previous explanations.
        
        This is the CORE function for trust building.
        """
        # Get previous explanations for this concept
        previous = await self._get_previous_explanations(user_id, concept_name, subject)
        
        if not previous:
            # First time explaining - no history to check
            return ConsistencyCheckResult(
                status=ConsistencyStatus.NO_HISTORY,
                previous_explanation=None,
                new_explanation=new_explanation,
                conflict_points=[],
                reconciliation=None,
                should_acknowledge=False,
                acknowledgment_text=None,
                confidence=1.0
            )
        
        # Get the most recent relevant explanation
        latest = previous[0]
        
        # Extract key facts from both
        new_facts = self._extract_key_facts(new_explanation)
        old_facts = latest.get('key_facts', [])
        old_summary = latest.get('explanation_summary', '')
        
        # Check for contradictions
        conflicts = self._find_contradictions(new_facts, old_facts, new_explanation, old_summary)
        
        # Determine status
        if not conflicts:
            status = ConsistencyStatus.CONSISTENT
            should_acknowledge = False
            acknowledgment = None
            reconciliation = None
        elif len(conflicts) == 1 and self._is_minor_variation(conflicts[0]):
            status = ConsistencyStatus.MINOR_VARIATION
            should_acknowledge = False
            acknowledgment = None
            reconciliation = None
        elif len(conflicts) <= 2:
            status = ConsistencyStatus.POTENTIAL_CONFLICT
            should_acknowledge = True
            reconciliation = self._generate_reconciliation(conflicts, old_summary, new_explanation)
            acknowledgment = self._generate_acknowledgment(conflicts, reconciliation)
        else:
            status = ConsistencyStatus.CONTRADICTION
            should_acknowledge = True
            reconciliation = self._generate_reconciliation(conflicts, old_summary, new_explanation)
            acknowledgment = self._generate_acknowledgment(conflicts, reconciliation)
        
        result = ConsistencyCheckResult(
            status=status,
            previous_explanation=old_summary,
            new_explanation=new_explanation[:500],
            conflict_points=conflicts,
            reconciliation=reconciliation,
            should_acknowledge=should_acknowledge,
            acknowledgment_text=acknowledgment,
            confidence=0.8 if conflicts else 1.0
        )
        
        logger.info(f"🔒 Consistency check: {status.value}, conflicts={len(conflicts)}")
        
        return result
    
    async def record_explanation(
        self,
        user_id: str,
        session_id: str,
        concept_name: str,
        explanation: str,
        subject: str = "General"
    ):
        """
        Record an explanation for future consistency checking.
        """
        concept_id = self._generate_concept_id(concept_name, subject)
        key_facts = self._extract_key_facts(explanation)
        summary = self._generate_summary(explanation)
        
        record = {
            "concept_id": concept_id,
            "concept_name": concept_name,
            "user_id": user_id,
            "session_id": session_id,
            "subject": subject,
            "explanation_summary": summary,
            "key_facts": key_facts,
            "given_at": datetime.now(timezone.utc),
            "full_text_hash": hashlib.md5(explanation.encode()).hexdigest()
        }
        
        await self.db.explanation_history.insert_one(record)
        
        logger.info(f"📝 Recorded explanation for '{concept_name}' ({len(key_facts)} facts)")
    
    async def get_explanation_history(
        self,
        user_id: str,
        concept_name: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get history of explanations given to this student."""
        query = {"user_id": user_id}
        if concept_name:
            # Fuzzy match on concept name
            query["concept_name"] = {"$regex": concept_name, "$options": "i"}
        
        cursor = self.db.explanation_history.find(
            query,
            sort=[("given_at", -1)],
            limit=limit
        )
        
        history = []
        async for doc in cursor:
            history.append({
                "concept": doc.get("concept_name"),
                "summary": doc.get("explanation_summary"),
                "facts": doc.get("key_facts"),
                "given_at": doc.get("given_at"),
                "session_id": doc.get("session_id")
            })
        
        return history
    
    async def _get_previous_explanations(
        self,
        user_id: str,
        concept_name: str,
        subject: str
    ) -> List[Dict[str, Any]]:
        """Get previous explanations for this concept."""
        # Normalize concept name for matching
        concept_normalized = concept_name.lower().strip()
        
        # Search for similar concepts
        cursor = self.db.explanation_history.find(
            {
                "user_id": user_id,
                "$or": [
                    {"concept_name": {"$regex": concept_normalized, "$options": "i"}},
                    {"concept_id": self._generate_concept_id(concept_name, subject)}
                ]
            },
            sort=[("given_at", -1)],
            limit=5
        )
        
        results = []
        async for doc in cursor:
            results.append(doc)
        
        return results
    
    def _extract_key_facts(self, text: str) -> List[str]:
        """Extract key factual claims from explanation."""
        facts = []
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Check if sentence contains factual pattern
            sentence_lower = sentence.lower()
            for pattern in self.FACTUAL_PATTERNS:
                if re.search(pattern, sentence_lower):
                    # Clean and add fact
                    fact = sentence[:150]  # Truncate
                    if fact not in facts:
                        facts.append(fact)
                    break
        
        return facts[:10]  # Max 10 facts
    
    def _find_contradictions(
        self,
        new_facts: List[str],
        old_facts: List[str],
        new_text: str,
        old_text: str
    ) -> List[str]:
        """Find contradictions between old and new explanations."""
        conflicts = []
        
        new_lower = new_text.lower()
        old_lower = old_text.lower()
        
        # Check for direct contradictions using indicator pairs
        for pos, neg in self.CONTRADICTION_INDICATORS:
            # Check if old says one thing and new says opposite
            if pos in old_lower and neg in new_lower:
                # Find context
                pos_context = self._extract_context(old_text, pos)
                neg_context = self._extract_context(new_text, neg)
                
                if pos_context and neg_context:
                    conflict = f"Previously said '{pos_context}', now saying '{neg_context}'"
                    conflicts.append(conflict)
            
            elif neg in old_lower and pos in new_lower:
                pos_context = self._extract_context(new_text, pos)
                neg_context = self._extract_context(old_text, neg)
                
                if pos_context and neg_context:
                    conflict = f"Previously said '{neg_context}', now saying '{pos_context}'"
                    conflicts.append(conflict)
        
        # Check for numerical contradictions (different values for same thing)
        old_numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(units?|m|kg|s|N|J|W|V|A|Hz|°C|K)', old_text)
        new_numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(units?|m|kg|s|N|J|W|V|A|Hz|°C|K)', new_text)
        
        if old_numbers and new_numbers:
            for old_num, old_unit in old_numbers:
                for new_num, new_unit in new_numbers:
                    if old_unit == new_unit and old_num != new_num:
                        conflict = f"Previously gave {old_num} {old_unit}, now giving {new_num} {new_unit}"
                        conflicts.append(conflict)
        
        return conflicts[:5]  # Max 5 conflicts
    
    def _extract_context(self, text: str, keyword: str, window: int = 50) -> Optional[str]:
        """Extract context around a keyword."""
        text_lower = text.lower()
        idx = text_lower.find(keyword)
        
        if idx == -1:
            return None
        
        start = max(0, idx - window)
        end = min(len(text), idx + len(keyword) + window)
        
        context = text[start:end].strip()
        
        # Clean up
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    def _is_minor_variation(self, conflict: str) -> bool:
        """Check if a conflict is a minor variation (not a real contradiction)."""
        minor_indicators = [
            'approximately',
            'about',
            'roughly',
            'around',
            'simplified',
            'detailed',
        ]
        
        conflict_lower = conflict.lower()
        return any(ind in conflict_lower for ind in minor_indicators)
    
    def _generate_reconciliation(
        self,
        conflicts: List[str],
        old_summary: str,
        new_explanation: str
    ) -> str:
        """Generate a reconciliation statement for conflicts."""
        if not conflicts:
            return ""
        
        # Simple reconciliation
        if len(conflicts) == 1:
            return f"To clarify from our previous discussion: {conflicts[0][:100]}. The current explanation provides more detail."
        else:
            return f"I want to clarify some points from before. The key updates are in how I'm explaining this - the current explanation is more comprehensive."
    
    def _generate_acknowledgment(
        self,
        conflicts: List[str],
        reconciliation: str
    ) -> str:
        """Generate acknowledgment text for inconsistency."""
        if not conflicts:
            return ""
        
        if len(conflicts) == 1:
            return f"Quick note: {reconciliation}"
        else:
            return f"Before I continue, let me clarify: {reconciliation}"
    
    def _generate_summary(self, explanation: str, max_length: int = 300) -> str:
        """Generate a summary of the explanation."""
        # Take first few sentences or truncate
        sentences = re.split(r'[.!?]', explanation)
        
        summary = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            if len(summary) + len(sentence) < max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip() or explanation[:max_length]
    
    def _generate_concept_id(self, concept_name: str, subject: str) -> str:
        """Generate unique ID for a concept."""
        normalized = f"{concept_name.lower().strip()}_{subject.lower().strip()}"
        return hashlib.md5(normalized.encode()).hexdigest()[:16]


# Singleton
_consistency_engine: Optional[ConsistencyEngine] = None


def get_consistency_engine(db) -> ConsistencyEngine:
    """Get or create the consistency engine."""
    global _consistency_engine
    if _consistency_engine is None:
        _consistency_engine = ConsistencyEngine(db)
    return _consistency_engine
