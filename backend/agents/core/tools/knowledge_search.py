"""
📚 Knowledge Search Tool - RAG v2 with Traceable Citations
==========================================================

Searches the knowledge corpus for concepts, definitions, and explanations.
Uses RetrieverV2 for real retrieval from file-based corpus.

RAG v2 FEATURES:
- Real document corpus (data/corpus/raw/)
- Chunk store with doc_id linkage
- Traceable citations (chunk_id → doc_id → raw file)
- Confidence scores based on retrieval quality
"""

import logging
from typing import Dict, Any, Optional, List
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class KnowledgeSearchTool(BaseTool):
    """
    Search the knowledge corpus for concepts and definitions.
    
    Uses RetrieverV2 for real retrieval with:
    - Keyword-based search over chunked documents
    - Full citation trail (chunk_id → doc_id → raw file)
    - Confidence scores
    """
    
    def __init__(self):
        super().__init__()
        self._retriever = None
    
    def _get_retriever(self):
        """Lazy load retriever v2"""
        if self._retriever is None:
            try:
                from services.knowledge_base.retriever_v2 import get_retriever_v2
                self._retriever = get_retriever_v2()
                
                # Log corpus stats
                stats = self._retriever.get_corpus_stats()
                if stats.get("status") == "initialized":
                    logger.info(f"📚 KnowledgeSearchTool connected to CorpusV2: "
                               f"{stats['num_chunks']} chunks from {stats['num_documents']} docs, "
                               f"v{stats['dataset_version'][:10]}")
                else:
                    logger.warning("📚 KnowledgeSearchTool: Corpus not fully initialized")
            except Exception as e:
                logger.error(f"Failed to load RetrieverV2: {e}")
                self._retriever = None
        return self._retriever
    
    @property
    def name(self) -> str:
        return "knowledge_search"
    
    @property
    def description(self) -> str:
        return (
            "Searches the curriculum knowledge corpus for concepts, definitions, formulas, and exam tips. "
            "Returns verified NCERT-based content with traceable citations (chunk → document → source file). "
            "Use when you need to look up or verify factual information."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "query": "The concept or topic to search for",
            "subject": "(Optional) Subject to filter results (Physics, Chemistry, Biology, Mathematics)"
        }
    
    async def execute(
        self, 
        query: str = "", 
        subject: str = None,
        context: Dict = None, 
        **kwargs
    ) -> ToolResult:
        """
        Search knowledge corpus using RetrieverV2.
        
        Returns structured content with:
        - Verified definitions and explanations
        - Relevant formulas
        - Key concepts
        - Traceable citations (chunk_id → doc_id → raw file)
        - Confidence score
        """
        if not query:
            return ToolResult.error_result("No search query provided")
        
        retriever = self._get_retriever()
        
        if retriever is None:
            logger.warning("RetrieverV2 not available, using fallback")
            return self._fallback_response(query)
        
        try:
            # Retrieve from corpus
            retrieval = retriever.retrieve_knowledge(query, subject, max_results=5)
            
            if not retrieval.results:
                logger.info(f"📚 No results for '{query}'")
                return ToolResult.success_result(
                    f"No exact match found for '{query}'. Try searching with different keywords or broader terms.\n\n"
                    f"**Suggestions:**\n"
                    f"- Try more specific terms (e.g., 'Newton's laws' instead of 'physics')\n"
                    f"- Try related concepts\n"
                    f"- Ask me to explain the concept directly",
                    metadata={
                        "found": False, 
                        "query": query,
                        "retrieval_method": retrieval.retrieval_method,
                        "confidence": 0.0,
                        "corpus_version": self._get_corpus_version()
                    }
                )
            
            # Format results with full citations
            output = self._format_results(retrieval, query)
            
            logger.info(f"📚 Knowledge search: '{query[:50]}' → {len(retrieval.results)} results, "
                       f"confidence={retrieval.confidence:.2f}")
            
            return ToolResult.success_result(
                output,
                metadata={
                    "found": True, 
                    "count": len(retrieval.results), 
                    "query": query,
                    "retrieval_method": retrieval.retrieval_method,
                    "confidence": retrieval.confidence,
                    "keywords_matched": retrieval.keywords_matched,
                    "citations": retrieval.get_citations(),
                    "corpus_version": self._get_corpus_version()
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Knowledge search error: {e}", exc_info=True)
            return self._fallback_response(query)
    
    def _format_results(self, retrieval, query: str) -> str:
        """Format retrieval results with full citations"""
        parts = [f"**📚 Knowledge Search: {query.title()}**\n"]
        parts.append(f"_Found {len(retrieval.results)} results (confidence: {retrieval.confidence:.0%})_\n")
        parts.append("---\n")
        
        for result in retrieval.results:
            # Topic header
            parts.append(f"### {result.get('topic', 'Unknown')}")
            parts.append(f"**Subject**: {result.get('subject', 'General')} | **Level**: Class {result.get('class_level', 'N/A')}")
            
            # Main content (truncate if too long)
            content = result.get('content', '')
            if len(content) > 800:
                content = content[:800] + "..."
            parts.append(f"\n{content}\n")
            
            # Formulas if present
            formulas = result.get('formulas', [])
            if formulas:
                parts.append("**📐 Key Formulas:**")
                for formula in formulas[:5]:
                    parts.append(f"- `{formula}`")
            
            # Key concepts if present
            concepts = result.get('key_concepts', [])
            if concepts:
                parts.append(f"\n**💡 Key Concepts:** {', '.join(concepts[:5])}")
            
            # Exam relevance
            exam_rel = result.get('exam_relevance', {})
            if exam_rel:
                relevance_str = ", ".join([f"{k}: {v}/5" for k, v in exam_rel.items()])
                parts.append(f"\n**📊 Exam Relevance:** {relevance_str}")
            
            # TRACEABLE CITATION
            parts.append(f"\n📖 **Citation:** {result.get('citation', 'Unknown')}")
            parts.append(f"_Section: {result.get('section', 'N/A')} | Score: {result.get('score', 0):.0%}_")
            
            # Raw file reference (for audit)
            if result.get('raw_file'):
                parts.append(f"_Source file: `{result.get('raw_file')}`_")
            
            parts.append("\n---\n")
        
        return "\n".join(parts)
    
    def _get_corpus_version(self) -> str:
        """Get current corpus version"""
        if self._retriever:
            stats = self._retriever.get_corpus_stats()
            return stats.get("dataset_version", "unknown")[:10]
        return "not_loaded"
    
    def _fallback_response(self, query: str) -> ToolResult:
        """Fallback when retriever is not available"""
        return ToolResult.success_result(
            f"Knowledge corpus is currently initializing. For '{query}', I'll use my general knowledge. "
            f"Ask me to explain the concept directly and I'll provide a thorough explanation.",
            metadata={
                "found": False,
                "query": query,
                "retrieval_method": "fallback",
                "confidence": 0.0,
                "corpus_version": "not_loaded"
            }
        )
