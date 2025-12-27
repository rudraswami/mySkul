"""
Weak Area Detective Agent - TRUE AGENTIC Data Analysis Agent
=============================================================

UPGRADED to TRUE AGENT with:
- ReAct Loop: Think → Act → Observe
- Tools: DatabaseQueryTool, AnalyticsTool
- Memory: Tracks improvement patterns over time
- Actions: ACTUALLY queries DB and analyzes real performance data

OLD: Guessed weak areas from conversation
NEW: ANALYZES actual performance data from MongoDB
"""

import logging
from typing import Dict, Any, Optional, List
from agents.core.react_agent import ReActAgent
from agents.core.tool_registry import ToolRegistry
from agents.core.tools.database_query_tool import DatabaseQueryTool
from agents.core.tools.analytics_tool import AnalyticsTool
from agents.core.memory import LongTermMemory

logger = logging.getLogger(__name__)


class WeakAreaDetectiveAgent(ReActAgent):
    """
    TRUE AGENTIC Weak Area Detective
    
    Capabilities:
    - Queries real user performance data from MongoDB
    - Performs statistical analysis on accuracy/time
    - Identifies patterns and trends
    - Generates data-driven recommendations
    - Tracks improvement over time
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Get DB client from config
        self.db = config.get('db_client') if config else None
        
        # Initialize tool registry with analytics tools
        self.tool_registry = ToolRegistry()
        self.tool_registry.register(DatabaseQueryTool(self.db))
        self.tool_registry.register(AnalyticsTool())
        
        # Initialize memory for tracking patterns (will be set per user)
        self.memory = None  # Set during process() with actual user_id
        
        logger.info("🔍 WeakAreaDetectiveAgent initialized as TRUE AGENT with data analysis")
    
    def get_agent_name(self) -> str:
        return "WeakAreaDetectiveAgent"
    
    def get_available_tools(self) -> list:
        """Return list of tools this agent can use"""
        return ['query_user_data', 'analyze_data']
    
    def get_agent_persona(self) -> str:
        return """You are a data-driven learning analyst who identifies weak areas.

Your role:
- Query actual user performance data from database
- Analyze accuracy, time spent, and engagement per topic
- Identify patterns and trends in learning behavior
- Generate data-driven recommendations (not guesses)
- Track improvement over time

Always base your analysis on REAL DATA, not assumptions.
Use the query_user_data tool to get actual performance metrics.
Use the analyze_data tool to generate insights."""
    
    @staticmethod
    def is_weak_area_query(
        query: str,
        semantic_analysis: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if query is about weak areas.
        
        PHASE 1 FIX: Uses semantic analysis when available.
        Keyword patterns only run as fallback.
        """
        # ================================================================
        # PHASE 1: SEMANTIC ANALYSIS IS AUTHORITATIVE
        # ================================================================
        if semantic_analysis and semantic_analysis.get('confidence', 0) >= 0.5:
            intent = semantic_analysis.get('intent', '')
            topic_mentioned = semantic_analysis.get('topic_mentioned', '')
            
            # Check if semantic analysis detected self-assessment intent
            # This is inferred from the reasoning/context, not keywords
            if intent == 'question' and topic_mentioned:
                # Check if topic is self-referential (about student's own abilities)
                reasoning = semantic_analysis.get('reasoning', '').lower()
                if any(signal in reasoning for signal in ['self-assessment', 'weak', 'strength', 'gap', 'improvement']):
                    logger.info(f"🧠 SEMANTIC: Weak area query detected via reasoning")
                    return True
            
            # Not detected by semantic - trust it
            return False
        
        # ================================================================
        # LEGACY FALLBACK: Minimal keyword detection
        # ================================================================
        logger.debug("📋 Using legacy weak area detection (semantic unavailable)")
        
        query_lower = query.lower()
        
        # Minimal set of structural patterns (explicit self-assessment)
        explicit_patterns = [
            'where am i weak', 'what should i focus', 'what are my weak',
            'analyze my', 'my weak areas', 'my weaknesses'
        ]
        return any(pattern in query_lower for pattern in explicit_patterns)
    
    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze weak areas using ReAct loop with real data.
        
        Think: What data do I need to identify weak areas?
        Act: Query database for performance metrics
        Observe: Analyze results and generate insights
        """
        try:
            user_id = context.get('user_id')
            subject = context.get('subject')
            
            logger.info(f"🔍 WeakAreaDetective analyzing for user {user_id}")
            
            # THINK: What analysis is needed?
            thought = f"To identify weak areas, I need to query user performance data and analyze patterns."
            
            # ACT 1: Query user performance
            logger.info("🔍 Step 1: Querying user performance data...")
            performance_result = await self.tool_registry.execute_tool(
                'query_user_data',
                user_id=user_id,
                query_type='user_performance',
                subject=subject,
                time_range=30
            )
            
            # ACT 2: Query weak areas specifically
            logger.info("🔍 Step 2: Querying weak areas...")
            weak_areas_result = await self.tool_registry.execute_tool(
                'query_user_data',
                user_id=user_id,
                query_type='weak_areas',
                subject=subject,
                time_range=30
            )
            
            # ACT 3: Analyze the data
            logger.info("🔍 Step 3: Analyzing data...")
            analysis_result = await self.tool_registry.execute_tool(
                'analyze_data',
                analysis_type='recommendation_generation',
                data={
                    **performance_result.data,
                    **weak_areas_result.data
                },
                context=context
            )
            
            # OBSERVE: Check results
            if not performance_result.success or not weak_areas_result.success:
                observation = "Data query failed - using fallback analysis"
                return await self._fallback_analysis(query, context)
            
            observation = f"Found {len(weak_areas_result.data.get('weak_areas', []))} weak areas from real data"
            
            # Generate comprehensive response
            weak_areas = weak_areas_result.data.get('weak_areas', [])
            recommendations = analysis_result.data.get('recommendations', []) if analysis_result.success else []
            performance = performance_result.data
            
            response = self._format_analysis_response(
                weak_areas=weak_areas,
                recommendations=recommendations,
                performance=performance,
                query=query
            )
            
            return {
                'success': True,
                'content': response,
                'weak_areas': weak_areas,
                'recommendations': recommendations,
                'performance_summary': performance,
                'thought': thought,
                'actions': ['query_user_data (performance)', 'query_user_data (weak_areas)', 'analyze_data'],
                'observation': observation,
                'data_driven': True  # Flag that this is based on real data
            }
            
        except Exception as e:
            logger.error(f"❌ WeakAreaDetective error: {e}", exc_info=True)
            return await self._fallback_analysis(query, context)
    
    def _format_analysis_response(
        self,
        weak_areas: List[Dict],
        recommendations: List[Dict],
        performance: Dict[str, Any],
        query: str
    ) -> str:
        """Format analysis into readable response"""
        response = "📊 **Weak Area Analysis** (Based on Your Actual Performance)\n\n"
        
        # Performance overview
        total_sessions = performance.get('total_sessions', 0)
        response += f"I analyzed your last {performance.get('time_range_days', 30)} days of study data ({total_sessions} sessions).\n\n"
        
        # Weak areas
        if weak_areas:
            response += "🎯 **Your Weak Areas:**\n\n"
            for i, area in enumerate(weak_areas[:5], 1):
                topic = area.get('topic', 'Unknown')
                confidence = area.get('confidence', 'unknown')
                engagement = area.get('avg_engagement', 0)
                response += f"{i}. **{topic}**\n"
                response += f"   - Engagement: {engagement:.1f}/10 (low)\n"
                response += f"   - Confidence: {confidence}\n\n"
        else:
            response += "✅ Great news! No significant weak areas detected in your recent study data.\n\n"
        
        # Recommendations
        if recommendations:
            response += "💡 **Recommended Actions:**\n\n"
            priority_recs = [r for r in recommendations if r.get('priority') in ['critical', 'high']]
            for i, rec in enumerate(priority_recs[:3], 1):
                response += f"{i}. {rec.get('action', 'Study more')}\n"
                response += f"   Reason: {rec.get('reason', 'To improve performance')}\n\n"
        
        # Subject breakdown
        if 'subjects' in performance:
            subjects = performance['subjects']
            if subjects:
                response += "📚 **Subject Breakdown:**\n\n"
                for subj, data in list(subjects.items())[:3]:
                    response += f"- {subj}: {data.get('sessions', 0)} sessions, {data.get('messages', 0)} questions\n"
        
        return response
    
    async def _fallback_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback when data analysis fails"""
        logger.warning("⚠️ Using fallback analysis (no real data)")
        
        return {
            'success': True,
            'content': """I'd love to analyze your weak areas, but I need more study data to give you accurate insights.

Keep studying for a few more days, and I'll be able to show you:
- Exact topics where you struggle
- Time spent per subject
- Performance trends
- Personalized study recommendations

For now, focus on consistent daily practice! 📚""",
            'weak_areas': [],
            'recommendations': [],
            'data_driven': False
        }


# Factory function for backward compatibility
def create_weak_area_detective(config: Optional[Dict[str, Any]] = None) -> WeakAreaDetectiveAgent:
    """Create WeakAreaDetectiveAgent instance"""
    return WeakAreaDetectiveAgent(config)
