"""
🔍 Retriever v2 - Unified Retrieval Interface for RAG v2
=========================================================

Provides unified retrieval interface over:
1. CorpusStoreV2 (knowledge chunks)
2. FormulaBank (structured formulas)
3. ExamStrategyBank (exam strategies)

All retrieval returns traceable citations with chunk_id → doc_id linkage.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResultV2:
    """
    Retrieval result with full citation trail.
    """
    query: str
    retrieval_method: str        # "corpus_v2", "formula_bank", "strategy_bank"
    total_hits: int
    results: List[Dict[str, Any]]  # Each result has content + citations
    confidence: float             # 0.0 to 1.0
    keywords_matched: List[str]
    
    def get_context_string(self, max_results: int = 3) -> str:
        """Get formatted context for LLM prompting"""
        if not self.results:
            return ""
        
        parts = []
        for result in self.results[:max_results]:
            citation = result.get("citation", "Unknown source")
            content = result.get("content", "")[:500]
            parts.append(f"--- {citation} ---\n{content}\n")
        
        return "\n".join(parts)
    
    def get_citations(self) -> List[str]:
        """Get list of citations"""
        return [r.get("citation", "") for r in self.results if r.get("citation")]


class RetrieverV2:
    """
    Unified retriever for RAG v2.
    
    Retrieves from:
    - CorpusStoreV2 for knowledge content
    - FormulaBank for formulas (with structured metadata)
    - ExamStrategyBank for exam strategies
    
    All results include traceable citations.
    """
    
    def __init__(self):
        self._corpus_store = None
        self._formula_bank = None
        self._strategy_bank = None
    
    def _get_corpus_store(self):
        """Lazy load corpus store"""
        if self._corpus_store is None:
            try:
                from services.knowledge_base.corpus_store import get_corpus_store_v2
                self._corpus_store = get_corpus_store_v2()
                logger.info(f"📚 RetrieverV2 connected to CorpusStoreV2 ({len(self._corpus_store.chunks)} chunks)")
            except Exception as e:
                logger.error(f"Failed to load CorpusStoreV2: {e}")
        return self._corpus_store
    
    def _get_formula_bank(self):
        """Lazy load formula bank"""
        if self._formula_bank is None:
            try:
                from services.knowledge_base.corpus_ingestion import get_formula_bank
                self._formula_bank = get_formula_bank()
                logger.info(f"📐 RetrieverV2 connected to FormulaBank ({len(self._formula_bank.formulas)} formulas)")
            except Exception as e:
                logger.error(f"Failed to load FormulaBank: {e}")
        return self._formula_bank
    
    def _get_strategy_bank(self):
        """Lazy load strategy bank"""
        if self._strategy_bank is None:
            try:
                from services.knowledge_base.corpus_ingestion import get_exam_strategy_bank
                self._strategy_bank = get_exam_strategy_bank()
                logger.info(f"🎯 RetrieverV2 connected to ExamStrategyBank ({len(self._strategy_bank.strategies)} strategies)")
            except Exception as e:
                logger.error(f"Failed to load ExamStrategyBank: {e}")
        return self._strategy_bank
    
    # =========================================================================
    # KEYWORD EXTRACTION
    # =========================================================================
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        stop_words = {
            'what', 'is', 'the', 'a', 'an', 'how', 'why', 'when', 'where',
            'which', 'who', 'do', 'does', 'did', 'can', 'could', 'would',
            'should', 'may', 'might', 'will', 'shall', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
            'and', 'or', 'but', 'if', 'then', 'else', 'so', 'because',
            'explain', 'describe', 'define', 'me', 'please', 'tell', 'about',
            'between', 'difference', 'compare', 'give', 'example', 'solve',
            'find', 'calculate', 'show', 'prove', 'derive', 'state'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        keywords = [w for w in words if w not in stop_words]
        
        # Add multi-word phrases
        phrases = re.findall(r"(?:newton'?s?\s+law|coulomb'?s?\s+law|ohm'?s?\s+law|kinetic\s+energy|potential\s+energy)", query.lower())
        keywords.extend(phrases)
        
        return list(set(keywords))
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _retrieve_bm25_only(self, corpus, query: str, subject: Optional[str], limit: int):
        """Synchronous BM25-only retrieval"""
        bm25_results = corpus.search_bm25(query, subject, limit=limit)
        return [(chunk, score, 'bm25') for chunk, score in bm25_results]
    
    # =========================================================================
    # KNOWLEDGE RETRIEVAL (from CorpusStoreV2)
    # =========================================================================
    
    def retrieve_knowledge(
        self,
        query: str,
        subject: Optional[str] = None,
        max_results: int = 5,
        use_hybrid: bool = True
    ) -> RetrievalResultV2:
        """
        Retrieve knowledge content from corpus using hybrid search.
        
        Uses BM25 (lexical) + Vector (semantic) retrieval for best results.
        Falls back to keyword search if hybrid unavailable.
        
        Returns chunks with full citations.
        """
        corpus = self._get_corpus_store()
        
        if corpus is None:
            return RetrievalResultV2(
                query=query,
                retrieval_method="corpus_v2_fallback",
                total_hits=0,
                results=[],
                confidence=0.0,
                keywords_matched=[]
            )
        
        keywords = self._extract_keywords(query)
        retrieval_method = "corpus_v2"
        
        # Try hybrid search first (BM25 + Vector)
        if use_hybrid:
            try:
                import asyncio
                # Run hybrid search
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're already in an async context, use the sync fallback
                    results = self._retrieve_bm25_only(corpus, query, subject, max_results)
                    retrieval_method = "corpus_v2_bm25"
                else:
                    results = loop.run_until_complete(
                        corpus.search_hybrid(query, subject, limit=max_results)
                    )
                    retrieval_method = "corpus_v2_hybrid"
            except Exception as e:
                logger.warning(f"Hybrid search failed, falling back to BM25: {e}")
                results = self._retrieve_bm25_only(corpus, query, subject, max_results)
                retrieval_method = "corpus_v2_bm25"
        else:
            results = self._retrieve_bm25_only(corpus, query, subject, max_results)
            retrieval_method = "corpus_v2_bm25"
        
        # Fallback to keyword search if no results
        if not results:
            results_simple = corpus.search_by_keywords(keywords, subject, limit=max_results)
            results = [(chunk, score, 'keyword') for chunk, score in results_simple]
            retrieval_method = "corpus_v2_keyword"
        
        # Format results with citations
        formatted_results = []
        for item in results:
            # Handle both hybrid (3-tuple) and simple (2-tuple) results
            if len(item) == 3:
                chunk, score, ret_type = item
            else:
                chunk, score = item
                ret_type = 'keyword'
            
            doc = corpus.get_document(chunk.doc_id)
            formatted_results.append({
                "content": chunk.text,
                "topic": chunk.topic,
                "subject": chunk.subject,
                "class_level": chunk.class_level,
                "formulas": chunk.formulas,
                "key_concepts": chunk.key_concepts,
                "exam_relevance": chunk.exam_relevance,
                "score": score,
                "retrieval_type": ret_type,
                # Full citation trail
                "citation": chunk.get_full_citation(),
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "section": chunk.section,
                "source_citation": chunk.source_citation,
                "raw_file": doc.filename if doc else None,
                "attribution": doc.attribution if doc else None
            })
        
        # Calculate confidence
        confidence = sum(r["score"] for r in formatted_results) / len(formatted_results) if formatted_results else 0.0
        
        logger.info(f"📚 Knowledge retrieval ({retrieval_method}): '{query[:50]}' → {len(formatted_results)} results, confidence={confidence:.2f}")
        
        return RetrievalResultV2(
            query=query,
            retrieval_method=retrieval_method,
            total_hits=len(formatted_results),
            results=formatted_results,
            confidence=confidence,
            keywords_matched=keywords
        )
    
    async def retrieve_knowledge_async(
        self,
        query: str,
        subject: Optional[str] = None,
        max_results: int = 5
    ) -> RetrievalResultV2:
        """
        Async version of retrieve_knowledge with proper hybrid search.
        
        Uses BM25 (lexical) + Vector (semantic) retrieval.
        """
        corpus = self._get_corpus_store()
        
        if corpus is None:
            return RetrievalResultV2(
                query=query,
                retrieval_method="corpus_v2_fallback",
                total_hits=0,
                results=[],
                confidence=0.0,
                keywords_matched=[]
            )
        
        keywords = self._extract_keywords(query)
        
        # Use hybrid search
        try:
            results = await corpus.search_hybrid(query, subject, limit=max_results)
            retrieval_method = "corpus_v2_hybrid"
        except Exception as e:
            logger.warning(f"Hybrid search failed: {e}")
            results = self._retrieve_bm25_only(corpus, query, subject, max_results)
            retrieval_method = "corpus_v2_bm25"
        
        # Format results
        formatted_results = []
        for item in results:
            if len(item) == 3:
                chunk, score, ret_type = item
            else:
                chunk, score = item
                ret_type = 'keyword'
            
            doc = corpus.get_document(chunk.doc_id)
            formatted_results.append({
                "content": chunk.text,
                "topic": chunk.topic,
                "subject": chunk.subject,
                "class_level": chunk.class_level,
                "formulas": chunk.formulas,
                "key_concepts": chunk.key_concepts,
                "exam_relevance": chunk.exam_relevance,
                "score": score,
                "retrieval_type": ret_type,
                "citation": chunk.get_full_citation(),
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "section": chunk.section,
                "source_citation": chunk.source_citation,
                "raw_file": doc.filename if doc else None,
                "attribution": doc.attribution if doc else None
            })
        
        confidence = sum(r["score"] for r in formatted_results) / len(formatted_results) if formatted_results else 0.0
        
        # Log with vector index type
        vec_type = "unknown"
        if corpus.vector_index:
            vec_stats = corpus.vector_index.get_stats()
            vec_type = vec_stats.get('index_type', 'unknown')
        
        logger.info(f"📚 Async retrieval ({retrieval_method}[{vec_type}]): '{query[:50]}' → {len(formatted_results)} results")
        
        return RetrievalResultV2(
            query=query,
            retrieval_method=f"{retrieval_method}_{vec_type}",
            total_hits=len(formatted_results),
            results=formatted_results,
            confidence=confidence,
            keywords_matched=keywords
        )
    
    # =========================================================================
    # FORMULA RETRIEVAL (from FormulaBank)
    # =========================================================================
    
    def retrieve_formulas(
        self,
        query: str,
        subject: Optional[str] = None,
        max_results: int = 8
    ) -> RetrievalResultV2:
        """
        Retrieve formulas from FormulaBank.
        
        Returns formulas with metadata and citations.
        """
        formula_bank = self._get_formula_bank()
        
        if formula_bank is None:
            return RetrievalResultV2(
                query=query,
                retrieval_method="formula_bank_fallback",
                total_hits=0,
                results=[],
                confidence=0.0,
                keywords_matched=[]
            )
        
        # Search formulas
        results = formula_bank.search(query, subject, limit=max_results)
        
        # Format results
        formatted_results = []
        for formula, score in results:
            formatted_results.append({
                "content": f"{formula.name}: {formula.formula}",
                "formula_name": formula.name,
                "formula": formula.formula,
                "variables": formula.variables,
                "units": formula.units,
                "constraints": formula.constraints,
                "common_mistakes": formula.common_mistakes,
                "tags": formula.tags,
                "subject": formula.subject,
                "topic": formula.topic,
                "exam_relevance": formula.exam_relevance,
                "score": score / 3.0,  # Normalize
                # Citation
                "citation": f"Formula Bank: {formula.name} [{formula.formula_id}]",
                "formula_id": formula.formula_id,
                "source_id": formula.source_id or "formula_bank"
            })
        
        confidence = sum(r["score"] for r in formatted_results) / len(formatted_results) if formatted_results else 0.0
        
        logger.info(f"📐 Formula retrieval: '{query[:50]}' → {len(formatted_results)} results, confidence={confidence:.2f}")
        
        return RetrievalResultV2(
            query=query,
            retrieval_method="formula_bank",
            total_hits=len(formatted_results),
            results=formatted_results,
            confidence=min(1.0, confidence),
            keywords_matched=self._extract_keywords(query)
        )
    
    # =========================================================================
    # EXAM STRATEGY RETRIEVAL (from ExamStrategyBank)
    # =========================================================================
    
    def retrieve_exam_strategy(
        self,
        topic: str,
        exam_type: str,
        subject: Optional[str] = None
    ) -> RetrievalResultV2:
        """
        Retrieve exam strategy from ExamStrategyBank.
        
        Returns strategy with metadata.
        """
        strategy_bank = self._get_strategy_bank()
        
        if strategy_bank is None:
            return RetrievalResultV2(
                query=f"{topic} ({exam_type})",
                retrieval_method="strategy_bank_fallback",
                total_hits=0,
                results=[],
                confidence=0.0,
                keywords_matched=[]
            )
        
        # Search for strategy
        strategy = strategy_bank.search(topic, exam_type, subject)
        
        if not strategy:
            return RetrievalResultV2(
                query=f"{topic} ({exam_type})",
                retrieval_method="strategy_bank",
                total_hits=0,
                results=[],
                confidence=0.0,
                keywords_matched=[topic.lower()]
            )
        
        # Format result
        formatted_results = [{
            "content": f"Strategy for {strategy.topic} ({strategy.exam_type})",
            "topic": strategy.topic,
            "exam_type": strategy.exam_type,
            "subject": strategy.subject,
            "weightage_percent": strategy.weightage_percent,
            "common_traps": strategy.common_traps,
            "shortcut_technique": strategy.shortcut_technique,
            "ncert_relevance": strategy.ncert_relevance,
            "pyq_pattern": strategy.pyq_pattern,
            "difficulty_rating": strategy.difficulty_rating,
            "recommended_time_percent": strategy.recommended_time_percent,
            "score": 0.9,
            # Citation
            "citation": f"Exam Strategy Bank: {strategy.topic} [{strategy.strategy_id}]",
            "strategy_id": strategy.strategy_id,
            "source_id": strategy.source_id or "exam_strategy_bank"
        }]
        
        logger.info(f"🎯 Strategy retrieval: '{topic}' ({exam_type}) → found, confidence=0.9")
        
        return RetrievalResultV2(
            query=f"{topic} ({exam_type})",
            retrieval_method="strategy_bank",
            total_hits=1,
            results=formatted_results,
            confidence=0.9,
            keywords_matched=[topic.lower()]
        )
    
    # =========================================================================
    # UNIFIED SEARCH
    # =========================================================================
    
    def search(
        self,
        query: str,
        search_type: str = "knowledge",  # "knowledge", "formula", "strategy"
        subject: Optional[str] = None,
        exam_type: Optional[str] = None,
        max_results: int = 5
    ) -> RetrievalResultV2:
        """
        Unified search interface.
        
        Args:
            query: Search query
            search_type: Type of search ("knowledge", "formula", "strategy")
            subject: Optional subject filter
            exam_type: Required for strategy search
            max_results: Maximum results to return
        
        Returns:
            RetrievalResultV2 with results and citations
        """
        if search_type == "formula":
            return self.retrieve_formulas(query, subject, max_results)
        elif search_type == "strategy" and exam_type:
            return self.retrieve_exam_strategy(query, exam_type, subject)
        else:
            return self.retrieve_knowledge(query, subject, max_results)
    
    # =========================================================================
    # CITATION VERIFICATION
    # =========================================================================
    
    def verify_citation(self, chunk_id: str) -> Optional[Dict]:
        """
        Verify a citation by retrieving full trail.
        
        Returns:
            Dict with chunk → document → raw file mapping
        """
        corpus = self._get_corpus_store()
        if corpus is None:
            return None
        
        return corpus.get_chunk_with_citation(chunk_id)
    
    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get corpus statistics including vector index info"""
        corpus = self._get_corpus_store()
        if corpus is None or corpus.manifest is None:
            return {"status": "not_initialized"}
        
        # Get vector index stats
        vector_stats = {}
        if corpus.vector_index:
            vector_stats = corpus.vector_index.get_stats()

        return {
            "status": "initialized",
            "dataset_version": corpus.manifest.dataset_version,
            "content_hash": corpus.manifest.content_hash,
            "num_documents": corpus.manifest.num_documents,
            "num_chunks": corpus.manifest.num_chunks,
            "avg_chunk_len": corpus.manifest.avg_chunk_len,
            "sources": corpus.manifest.sources,
            "vector_index": {
                "type": vector_stats.get("index_type", "unknown"),
                "num_vectors": vector_stats.get("num_vectors", 0),
                "dimensions": vector_stats.get("dimensions", 0),
                "initialized": vector_stats.get("initialized", False)
            }
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_retriever_v2: Optional[RetrieverV2] = None


def get_retriever_v2() -> RetrieverV2:
    """Get or create the global retriever v2 instance"""
    global _retriever_v2
    if _retriever_v2 is None:
        _retriever_v2 = RetrieverV2()
    return _retriever_v2
