"""
🎯 Exam Strategy Tool - RAG v2 with Traceable Citations
=======================================================

Provides exam-specific insights: weightage, trap questions, shortcuts.
Uses RetrieverV2 for real retrieval from ExamStrategyBank.

RAG v2 FEATURES:
- Structured strategy entries with full metadata
- Traceable citations (strategy_id → source)
- Weightage, traps, shortcuts, NCERT relevance, PYQ patterns
- Confidence scores based on retrieval quality
"""

import logging
from typing import Dict, Any, Optional, List
from agents.core.tool_registry import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class ExamStrategyTool(BaseTool):
    """
    Exam Strategy Tool - Provides exam-specific insights.
    
    Uses RetrieverV2 for structured retrieval with:
    - Weightage percentages
    - Common trap questions
    - Shortcut techniques
    - NCERT relevance and PYQ patterns
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
                logger.info("🎯 ExamStrategyTool connected to RetrieverV2")
            except Exception as e:
                logger.error(f"Failed to load RetrieverV2: {e}")
                self._retriever = None
        return self._retriever
    
    @property
    def name(self) -> str:
        return "exam_strategy"
    
    @property
    def description(self) -> str:
        return (
            "Provides exam-specific strategy information for JEE, NEET, or CBSE. "
            "Use this tool when students ask about: exam weightage, common trap questions, "
            "shortcut techniques, or exam-specific tips. Returns structured strategy with "
            "traceable citations."
        )
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "topic": "The topic name (e.g., 'Mechanics', 'Organic Chemistry', 'Calculus', 'Human Physiology')",
            "exam_type": "Exam type: 'JEE' | 'NEET' | 'CBSE'"
        }
    
    async def execute(
        self,
        topic: str = "",
        exam_type: str = None,
        context: Dict = None,
        **kwargs
    ) -> ToolResult:
        """
        Get exam strategy using RetrieverV2.
        
        Returns structured strategy with:
        - Topic weightage percentage
        - Common trap questions
        - Shortcut techniques
        - NCERT relevance mapping
        - PYQ pattern analysis
        - Traceable citations
        """
        if not topic:
            return ToolResult.error_result("Topic is required")
        
        context = context or {}
        
        # Resolve exam_type from multiple sources
        if exam_type is None:
            exam_type = (
                context.get('exam_mode') or 
                context.get('exam_type') or 
                context.get('student_profile', {}).get('exam') or
                'General'
            )
        
        exam_type = exam_type.upper() if exam_type else 'GENERAL'
        
        # If exam_type is General or unrecognized, return general advice
        if exam_type not in ["JEE", "NEET", "CBSE"]:
            logger.info(f"📚 ExamStrategyTool: exam_type={exam_type} - returning general advice")
            return self._general_advice(topic, exam_type)
        
        retriever = self._get_retriever()
        
        if retriever is None:
            logger.warning("RetrieverV2 not available, using fallback")
            return self._fallback_response(topic, exam_type)
        
        try:
            # Retrieve strategy
            retrieval = retriever.retrieve_exam_strategy(topic, exam_type)
            
            if not retrieval.results:
                logger.info(f"⚠️ No strategy found for '{topic}' in {exam_type}")
                return self._no_data_response(topic, exam_type)
            
            # Format the strategy response
            result = retrieval.results[0]  # Single strategy
            output = self._format_strategy(result)
            
            logger.info(f"🎯 Exam strategy: '{topic}' ({exam_type}) → found, "
                       f"confidence={retrieval.confidence:.2f}")
            
            return ToolResult.success_result(
                output,
                metadata={
                    "found": True,
                    "topic": result.get("topic"),
                    "exam_type": exam_type,
                    "weightage": result.get("weightage_percent"),
                    "difficulty": result.get("difficulty_rating"),
                    "retrieval_method": retrieval.retrieval_method,
                    "confidence": retrieval.confidence,
                    "citation": result.get("citation"),
                    "strategy_id": result.get("strategy_id")
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Exam strategy error: {e}", exc_info=True)
            return self._fallback_response(topic, exam_type)
    
    def _format_strategy(self, result: Dict) -> str:
        """Format strategy with full metadata"""
        parts = [
            f"**📊 Exam Strategy: {result.get('topic', 'Unknown')} ({result.get('exam_type', 'Unknown')})**\n",
            f"### Weightage",
            f"**{result.get('weightage_percent', 'N/A')}%** of {result.get('exam_type', 'exam')} questions come from this topic.\n",
        ]
        
        # Difficulty and time
        difficulty = result.get('difficulty_rating')
        if difficulty:
            stars = "⭐" * difficulty
            parts.append(f"**Difficulty**: {stars} ({difficulty}/5)")
        
        time_percent = result.get('recommended_time_percent')
        if time_percent:
            parts.append(f"**Recommended Time**: {time_percent}% of total prep time\n")
        
        # Common traps
        traps = result.get('common_traps', [])
        if traps:
            parts.append("### ⚠️ Common Trap Questions")
            for i, trap in enumerate(traps, 1):
                parts.append(f"{i}. {trap}")
        
        # Shortcut technique
        shortcut = result.get('shortcut_technique')
        if shortcut:
            parts.extend([
                f"\n### 🎯 Shortcut Technique",
                shortcut,
            ])
        
        # NCERT relevance
        ncert = result.get('ncert_relevance')
        if ncert:
            parts.extend([
                f"\n### 📚 NCERT Relevance",
                ncert,
            ])
        
        # PYQ pattern
        pyq = result.get('pyq_pattern')
        if pyq:
            parts.extend([
                f"\n### 📈 Previous Year Question Pattern",
                pyq
            ])
        
        # TRACEABLE CITATION
        parts.append(f"\n📖 **Citation:** {result.get('citation', 'Unknown')}")
        
        return "\n".join(parts)
    
    def _general_advice(self, topic: str, exam_type: str) -> ToolResult:
        """Return general advice when no specific exam context"""
        return ToolResult.success_result(
            f"**Study Tips for {topic}**:\n\n"
            f"For conceptual understanding of **{topic}**, focus on:\n\n"
            f"1. **Fundamentals first** - Master the basic principles before applications\n"
            f"2. **Practice problems** - Work through varied problems to build intuition\n"
            f"3. **Connect concepts** - See how this topic relates to others you've learned\n"
            f"4. **Real-world applications** - Understanding 'why' helps remember 'what'\n\n"
            f"_If you're preparing for a specific exam (JEE, NEET, CBSE), let me know and I can provide targeted advice!_",
            metadata={
                "exam_mode": exam_type, 
                "is_general": True, 
                "topic": topic,
                "retrieval_method": "general_advice",
                "confidence": 0.5
            }
        )
    
    def _no_data_response(self, topic: str, exam_type: str) -> ToolResult:
        """Response when no specific data is found"""
        return ToolResult.success_result(
            f"**Exam Strategy for {topic} ({exam_type})**:\n\n"
            f"While I don't have specific strategy data for '{topic}' in my database right now, here's general advice for {exam_type}:\n\n"
            f"1. **Focus on NCERT**: {exam_type} questions are often based on NCERT concepts.\n"
            f"2. **Practice PYQs**: Previous year questions help identify patterns.\n"
            f"3. **Time Management**: Allocate time based on topic difficulty.\n"
            f"4. **Common Mistakes**: Always double-check units and sign conventions.\n\n"
            f"_Note: For specific weightage and trap questions, please check official {exam_type} analysis._",
            metadata={
                "found": False, 
                "topic": topic, 
                "exam_type": exam_type,
                "retrieval_method": "no_data_fallback",
                "confidence": 0.3
            }
        )
    
    def _fallback_response(self, topic: str, exam_type: str) -> ToolResult:
        """Fallback when retriever is not available"""
        return ToolResult.success_result(
            f"Strategy database is currently initializing. For '{topic}' ({exam_type}), "
            f"focus on NCERT basics and practice previous year questions.",
            metadata={
                "found": False,
                "topic": topic,
                "exam_type": exam_type,
                "retrieval_method": "fallback",
                "confidence": 0.0
            }
        )
