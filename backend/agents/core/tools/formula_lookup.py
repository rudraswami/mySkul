"""
📐 Formula Lookup Tool - RAG v2 with Traceable Citations
========================================================

Searches for formulas relevant to a given topic or problem.
Uses RetrieverV2 for real retrieval from FormulaBank.

RAG v2 FEATURES:
- Structured formula entries with full metadata
- Traceable citations (formula_id → source)
- Common mistakes and exam relevance
- Confidence scores based on retrieval quality
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class FormulaLookupTool(BaseTool):
    """
    Look up formulas relevant to a topic.
    
    Uses RetrieverV2 for structured retrieval with:
    - Formula expression with variables and units
    - Common mistakes to avoid
    - Exam relevance scores
    - Traceable citations
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
                logger.info("📐 FormulaLookupTool connected to RetrieverV2")
            except Exception as e:
                logger.error(f"Failed to load RetrieverV2: {e}")
                self._retriever = None
        return self._retriever
    
    @property
    def name(self) -> str:
        return "formula_lookup"
    
    @property
    def description(self) -> str:
        return (
            "Finds relevant formulas for a given topic with full metadata including "
            "variables, units, constraints, common mistakes, and exam relevance. "
            "Use when you need to recall a specific formula or find formulas related to a concept."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "topic": "The topic to find formulas for (e.g., 'mechanics', 'quadratic', 'electricity', 'friction')",
            "subject": "(Optional) Subject to filter: Physics, Chemistry, Mathematics"
        }
    
    async def execute(
        self, 
        topic: str = "", 
        subject: str = None,
        context: Dict = None, 
        **kwargs
    ) -> ToolResult:
        """
        Look up formulas using RetrieverV2.
        
        Returns structured formulas with:
        - Formula expression
        - Variables with units
        - Common mistakes to avoid
        - Exam relevance scores
        - Traceable citations
        """
        if not topic:
            return ToolResult.error_result("No topic provided")
        
        retriever = self._get_retriever()
        
        if retriever is None:
            logger.warning("RetrieverV2 not available, using fallback")
            return self._fallback_response(topic)
        
        try:
            # Retrieve formulas
            retrieval = retriever.retrieve_formulas(topic, subject, max_results=8)
            
            if not retrieval.results:
                logger.info(f"📐 No formulas found for '{topic}'")
                return ToolResult.success_result(
                    f"No formulas found for '{topic}'. Try searching with different keywords like "
                    f"'mechanics', 'calculus', 'electricity', 'thermodynamics', 'organic chemistry'.",
                    metadata={
                        "found": False, 
                        "topic": topic,
                        "retrieval_method": retrieval.retrieval_method,
                        "confidence": 0.0
                    }
                )
            
            # Format results with full metadata
            output = self._format_results(retrieval, topic)
            
            logger.info(f"📐 Formula lookup: '{topic}' → {len(retrieval.results)} formulas, "
                       f"confidence={retrieval.confidence:.2f}")
            
            return ToolResult.success_result(
                output,
                metadata={
                    "found": True, 
                    "count": len(retrieval.results), 
                    "topic": topic,
                    "retrieval_method": retrieval.retrieval_method,
                    "confidence": retrieval.confidence,
                    "citations": retrieval.get_citations(),
                    "formula_ids": [r.get("formula_id") for r in retrieval.results]
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Formula lookup error: {e}", exc_info=True)
            return self._fallback_response(topic)
    
    def _format_results(self, retrieval, topic: str) -> str:
        """Format formula results with full metadata"""
        parts = [f"**📐 Formulas for: {topic.title()}**\n"]
        parts.append(f"_Found {len(retrieval.results)} formulas (confidence: {retrieval.confidence:.0%})_\n")
        parts.append("---\n")
        
        for result in retrieval.results:
            # Main formula info
            parts.append(f"### {result.get('formula_name', 'Unknown')}")
            parts.append(f"**Formula**: `{result.get('formula', 'N/A')}`")
            parts.append(f"**Variables**: {result.get('variables', 'N/A')}")
            
            # Units and constraints if available
            units = result.get('units')
            if units:
                parts.append(f"**Units**: {units}")
            
            constraints = result.get('constraints')
            if constraints:
                parts.append(f"**Constraints**: {constraints}")
            
            # Common mistakes (high value for students)
            mistakes = result.get('common_mistakes', [])
            if mistakes:
                parts.append("\n**⚠️ Common Mistakes:**")
                for mistake in mistakes[:3]:
                    parts.append(f"- {mistake}")
            
            # Exam relevance
            exam_rel = result.get('exam_relevance', {})
            if exam_rel:
                relevance_str = ", ".join([f"{k}: {v}/5" for k, v in exam_rel.items()])
                parts.append(f"\n**📊 Exam Relevance**: {relevance_str}")
            
            # TRACEABLE CITATION
            parts.append(f"\n📖 **Citation:** {result.get('citation', 'Unknown')}")
            parts.append(f"_({result.get('subject', 'General')} - {result.get('topic', 'General')})_")
            parts.append("\n---\n")
        
        return "\n".join(parts)
    
    def _fallback_response(self, topic: str) -> ToolResult:
        """Fallback when retriever is not available"""
        return ToolResult.success_result(
            f"Formula database is currently initializing. For '{topic}', please check NCERT textbooks "
            f"or ask me to explain the relevant formulas directly.",
            metadata={
                "found": False,
                "topic": topic,
                "retrieval_method": "fallback",
                "confidence": 0.0
            }
        )
