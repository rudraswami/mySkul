"""
Curriculum Retriever - Semantic Search for RAG
===============================================

Retrieves relevant curriculum content for grounding AI responses.
Currently uses keyword-based retrieval, can be upgraded to
embedding-based semantic search.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .curriculum_store import CurriculumStore, CurriculumChunk, get_curriculum_store

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result of curriculum retrieval"""
    chunks: List[CurriculumChunk]
    query_keywords: List[str]
    relevance_scores: List[float]
    total_matches: int
    
    def get_context_string(self, max_chunks: int = 3) -> str:
        """Get formatted context string for LLM prompting"""
        if not self.chunks:
            return ""
        
        context_parts = []
        for chunk in self.chunks[:max_chunks]:
            context_parts.append(f"""
--- {chunk.source} ---
Topic: {chunk.topic}
{chunk.content}

Key Formulas: {', '.join(chunk.formulas) if chunk.formulas else 'N/A'}
""")
        
        return "\n".join(context_parts)
    
    def get_sources(self) -> List[str]:
        """Get list of sources used"""
        return [chunk.source for chunk in self.chunks]


class CurriculumRetriever:
    """
    Retrieves relevant curriculum content for RAG.
    
    Uses the CurriculumStore to find content relevant to a query,
    then formats it for inclusion in AI prompts.
    """
    
    # Keywords to extract from queries
    SUBJECT_KEYWORDS = {
        "physics": ["force", "motion", "energy", "wave", "electric", "magnetic", "optics", "nuclear", "thermodynamics"],
        "chemistry": ["reaction", "atom", "molecule", "bond", "acid", "base", "organic", "mole", "equilibrium"],
        "mathematics": ["equation", "function", "derivative", "integral", "matrix", "vector", "probability", "permutation", "combination"],
        "biology": ["cell", "dna", "plant", "animal", "photosynthesis", "respiration", "evolution", "genetics", "ecology"]
    }
    
    def __init__(self, store: Optional[CurriculumStore] = None):
        """Initialize retriever with curriculum store"""
        self.store = store or get_curriculum_store()
        logger.info("🔍 CurriculumRetriever initialized")
    
    def retrieve(
        self,
        query: str,
        subject: Optional[str] = None,
        max_results: int = 5
    ) -> RetrievalResult:
        """
        Retrieve relevant curriculum content for a query.
        
        Args:
            query: The student's question
            subject: Optional subject filter
            max_results: Maximum chunks to return
            
        Returns:
            RetrievalResult with relevant content
        """
        try:
            # Extract keywords from query
            keywords = self._extract_keywords(query)
            
            # Detect subject if not provided
            if not subject:
                subject = self._detect_subject(query, keywords)
            
            # Search curriculum store
            chunks = self.store.search_by_keywords(keywords, subject, max_results)
            
            # Calculate relevance scores
            relevance_scores = [
                self._calculate_relevance(chunk, keywords, query)
                for chunk in chunks
            ]
            
            # Sort by relevance
            sorted_pairs = sorted(
                zip(chunks, relevance_scores),
                key=lambda x: x[1],
                reverse=True
            )
            
            sorted_chunks = [c for c, _ in sorted_pairs]
            sorted_scores = [s for _, s in sorted_pairs]
            
            logger.info(f"📚 Retrieved {len(sorted_chunks)} chunks for query")
            
            return RetrievalResult(
                chunks=sorted_chunks,
                query_keywords=keywords,
                relevance_scores=sorted_scores,
                total_matches=len(chunks)
            )
            
        except Exception as e:
            logger.error(f"❌ Retrieval error: {e}", exc_info=True)
            return RetrievalResult(
                chunks=[],
                query_keywords=[],
                relevance_scores=[],
                total_matches=0
            )
    
    def retrieve_for_topic(
        self,
        topic: str,
        subject: str
    ) -> RetrievalResult:
        """Retrieve content for a specific topic"""
        chunks = self.store.search_by_topic(topic, subject)
        
        return RetrievalResult(
            chunks=chunks,
            query_keywords=[topic],
            relevance_scores=[1.0] * len(chunks),
            total_matches=len(chunks)
        )
    
    def get_formulas(
        self,
        topic: str,
        subject: str
    ) -> List[Dict[str, str]]:
        """Get formulas for a topic"""
        return self.store.get_formulas_for_topic(topic, subject)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Remove common words
        stop_words = {
            'what', 'is', 'the', 'a', 'an', 'how', 'why', 'when', 'where',
            'which', 'who', 'do', 'does', 'did', 'can', 'could', 'would',
            'should', 'may', 'might', 'will', 'shall', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
            'and', 'or', 'but', 'if', 'then', 'else', 'so', 'because',
            'explain', 'describe', 'define', 'me', 'please', 'tell', 'about',
            'between', 'difference', 'compare', 'give', 'example', 'solve'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        keywords = [w for w in words if w not in stop_words]
        
        # Add multi-word phrases
        phrases = re.findall(r'\b(newton\'?s?\s+law|coulomb\'?s?\s+law|ohm\'?s?\s+law)\b', query.lower())
        keywords.extend(phrases)
        
        return list(set(keywords))
    
    def _detect_subject(self, query: str, keywords: List[str]) -> Optional[str]:
        """Detect subject from query and keywords"""
        query_lower = query.lower()
        
        # Check for explicit subject mentions
        subject_names = {
            "physics": ["physics", "physical"],
            "chemistry": ["chemistry", "chemical", "chem"],
            "mathematics": ["mathematics", "math", "maths", "mathematical"],
            "biology": ["biology", "biological", "bio"]
        }
        
        for subject, names in subject_names.items():
            if any(name in query_lower for name in names):
                return subject.capitalize()
        
        # Check keyword overlap
        subject_scores = {}
        for subject, subj_keywords in self.SUBJECT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in subj_keywords)
            if score > 0:
                subject_scores[subject] = score
        
        if subject_scores:
            best_subject = max(subject_scores.keys(), key=lambda k: subject_scores[k])
            return best_subject.capitalize()
        
        return None
    
    def _calculate_relevance(
        self,
        chunk: CurriculumChunk,
        keywords: List[str],
        query: str
    ) -> float:
        """Calculate relevance score for a chunk"""
        score = 0.0
        
        chunk_text = f"{chunk.content} {chunk.topic} {' '.join(chunk.keywords)}".lower()
        
        # Keyword matches
        for keyword in keywords:
            if keyword in chunk_text:
                score += 0.2
        
        # Exact phrase matches
        query_lower = query.lower()
        if chunk.topic.lower() in query_lower:
            score += 0.5
        
        # Formula relevance (if query asks about formulas)
        if 'formula' in query_lower and chunk.formulas:
            score += 0.3
        
        return min(1.0, score)

