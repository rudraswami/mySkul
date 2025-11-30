"""
🔍 WEAK AREA DETECTIVE AGENT - Knowledge Gap Analyzer

This agent helps students identify and address their weak areas:
- Performance analysis based on history
- Topic-level weakness detection
- Personalized improvement plans
- Priority recommendations

Philosophy: Every weakness is a potential strength waiting to be unlocked
"""

import logging
from typing import Dict, Any, Optional, List
from agents.intelligent_agent_base import IntelligentAgentBase

logger = logging.getLogger(__name__)


class WeakAreaDetectiveAgent(IntelligentAgentBase):
    """
    Intelligent weak area analyzer that uses LLM for personalized analysis
    """
    
    @staticmethod
    def is_weak_area_query(query: str) -> bool:
        """Detect if this is a weak area analysis query"""
        query_lower = query.lower()
        
        weak_area_phrases = [
            # Direct requests
            'weak areas', 'weaknesses', 'where am i weak',
            'what should i improve', 'improve', 'improvement',
            'struggling with', 'hard for me', 'difficult for me',
            
            # Analysis requests
            'analyze', 'analyse', 'check my', 'review my',
            'gaps', 'missing', 'lacking',
            
            # Performance queries
            'why am i failing', 'not scoring', 'low marks',
            'where am i going wrong', 'mistakes',
            
            # Recommendation requests
            'what to focus on', 'priority', 'focus areas',
            'where should i spend time'
        ]
        
        return any(phrase in query_lower for phrase in weak_area_phrases)
    
    def get_agent_type(self) -> str:
        return 'weak_area_detective'
    
    def get_agent_persona(self) -> str:
        """Analytical coach persona"""
        return """You are a skilled learning analyst who helps students identify and overcome weak areas.

YOUR CHARACTER:
- You're like a sports coach reviewing game footage
- Analytical but supportive
- Focus on growth, not blame
- Every weakness is a growth opportunity

YOUR APPROACH:
- Be specific about what's weak (not vague "you need to improve")
- Explain WHY something might be weak (conceptual gap? practice issue? exam technique?)
- Give concrete steps to improve
- Prioritize: "Fix this first, then this"

YOUR STYLE:
- "Based on your pattern, I notice..."
- "Here's the good news - this is very fixable!"
- "Most students struggle here because..."
- Give time estimates: "With 1 hour daily for 2 weeks, you can master this"
"""
    
    def get_specialized_instructions(self, query: str, context: Dict[str, Any]) -> str:
        """Instructions for weak area analysis"""
        
        subject = context.get('subject', 'General')
        session_data = context.get('session_data', {})
        
        # Check if we have actual performance data
        has_performance_data = session_data.get('performance_history') or session_data.get('quiz_scores')
        
        if has_performance_data:
            return f"""
SUBJECT: {subject}
PERFORMANCE DATA AVAILABLE: Yes

Analyze based on:
- Quiz/test scores provided
- Topics where mistakes occurred
- Time taken on different topics
- Pattern of errors (conceptual vs calculation vs silly)

RESPONSE STRUCTURE:
1. **Overall Assessment** (1-2 lines)
2. **Top 3 Weak Areas** (specific, ranked by priority)
   - What's weak
   - Why it matters (exam weightage)
   - Root cause hypothesis
3. **Improvement Plan** (actionable)
   - Time investment needed
   - Specific resources/methods
   - Checkpoints
4. **Quick Win** (one thing they can fix today)
5. **Encouragement** (genuine, not generic)
"""
        else:
            return f"""
SUBJECT: {subject}
PERFORMANCE DATA: Not available

Since we don't have test history, offer to help identify weak areas by:
1. Asking diagnostic questions about {subject}
2. Offering a quick self-assessment quiz
3. Asking which topics feel hardest

Alternatively, provide general advice on common weak areas in {subject} for exam preparation.

RESPONSE STRUCTURE:
1. Acknowledge we need more data
2. Offer diagnostic options
3. Share common weak areas in {subject}
4. Encourage them to share what feels hardest
"""
    
    def _get_fallback_response(self, query: str, context: Dict[str, Any]) -> str:
        """Fallback if LLM fails"""
        subject = context.get('subject', 'your subjects')
        
        return f"""Let's identify your weak areas in {subject}! 🔍

To give you the best analysis, I can help in two ways:

**Option 1: Quick Self-Assessment**
Tell me which topics feel hardest for you - I'll analyze why and give you a plan.

**Option 2: Diagnostic Quiz**
Take a 5-question mini-quiz. I'll analyze your responses to spot patterns.

**Option 3: Review Your History**
If you've done practice tests here, I can analyze your performance.

💡 **Common Weak Areas in {subject}:**
Most students struggle with foundational concepts that everything else builds on. Once we fix those, other topics often become easier automatically!

Which option works for you?"""
    
    async def get_performance_analysis(
        self,
        user_id: str,
        subject: str,
        db_client: Any = None
    ) -> Dict[str, Any]:
        """
        Get detailed performance analysis from user history
        This can be called to fetch actual data before processing
        """
        if not db_client:
            return {}
        
        try:
            # Get user's quiz/test history
            performance = await db_client.user_performance.find(
                {"user_id": user_id, "subject": subject}
            ).sort("timestamp", -1).limit(20).to_list(20)
            
            if not performance:
                return {}
            
            # Analyze patterns
            topic_scores = {}
            error_patterns = []
            
            for record in performance:
                topic = record.get('topic')
                score = record.get('score', 0)
                max_score = record.get('max_score', 100)
                
                if topic:
                    if topic not in topic_scores:
                        topic_scores[topic] = []
                    topic_scores[topic].append(score / max_score if max_score else 0)
                
                if record.get('errors'):
                    error_patterns.extend(record['errors'])
            
            # Calculate weak areas
            weak_areas = []
            for topic, scores in topic_scores.items():
                avg_score = sum(scores) / len(scores)
                if avg_score < 0.6:  # Below 60%
                    weak_areas.append({
                        'topic': topic,
                        'average_score': avg_score,
                        'attempts': len(scores),
                        'priority': 'high' if avg_score < 0.4 else 'medium'
                    })
            
            # Sort by priority
            weak_areas.sort(key=lambda x: x['average_score'])
            
            return {
                'weak_areas': weak_areas[:5],
                'total_attempts': len(performance),
                'error_patterns': error_patterns[:10]
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {}


# ============================================
# COMPATIBILITY
# ============================================

def is_weak_area_query(query: str) -> bool:
    """Module-level function for import compatibility"""
    return WeakAreaDetectiveAgent.is_weak_area_query(query)
