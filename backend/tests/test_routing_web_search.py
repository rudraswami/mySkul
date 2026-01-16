"""
🧪 Unit Tests for Web Search Routing Decision
==============================================

Tests that the routing engine correctly enables web_search based on 
semantic analysis, NOT keyword matching.

Run with:
    cd c:\\Users\\DELL\\DruvAI\\personal\\backend
    python -m pytest tests/test_routing_web_search.py -v

Expected:
    test_web_search_enabled_for_current_events - PASS
    test_web_search_disabled_for_static_content - PASS
    test_no_duplicate_tools - PASS
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from services.intelligent_routing_engine import IntelligentRoutingEngine


class MockSemanticAnalysis:
    """Mock SemanticAnalysis for testing"""
    def __init__(
        self,
        temporal_scope='unspecified',
        urgency_level='medium',
        reasoning='',
        topic_mentioned=None,
        intent=None
    ):
        self.temporal_scope = temporal_scope
        self.urgency_level = urgency_level
        self.reasoning = reasoning
        self.topic_mentioned = topic_mentioned
        self.intent = intent
        self.confidence = 0.9
        self.emotional_tone = 'neutral'
        self.emotional_intensity = 0.3
        self.is_follow_up = False
        self.needs_empathy = False
        self.needs_encouragement = False
        self.needs_clarification = False
        self.suggested_response_style = 'educational'
        self.has_actionable_request = False
        self.requested_output_type = None
        self.response_expectation = 'conversational_advice'
        self.delivery_mode = 'conversational'
    
    def to_dict(self):
        return {
            'temporal_scope': self.temporal_scope,
            'urgency_level': self.urgency_level,
            'reasoning': self.reasoning,
            'topic_mentioned': self.topic_mentioned,
            'intent': self.intent.value if self.intent else 'question',
            'confidence': self.confidence
        }


class TestWebSearchRouting:
    """Test web search routing decision"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.engine = IntelligentRoutingEngine()
    
    # =========================================================================
    # TEST 1: Web search ENABLED for current events queries
    # =========================================================================
    def test_web_search_enabled_for_current_events(self):
        """
        Query: "What are the latest Nobel Prize winners?"
        Expected: tools_to_enable contains "web_search"
        
        The semantic classifier would classify this with:
        - topic_mentioned: "Nobel Prize"
        - reasoning: "asking about latest/recent winners"
        """
        # Mock semantic analysis for current events query
        analysis = MockSemanticAnalysis(
            temporal_scope='today',  # LLM classifies as current/recent
            urgency_level='medium',
            reasoning='Student asking about latest Nobel Prize winners - current events',
            topic_mentioned='Nobel Prize'
        )
        
        # Call _requires_web_search directly
        requires, reason = self.engine._requires_web_search(
            "What are the latest Nobel Prize winners?",
            analysis
        )
        
        assert requires is True, f"Expected requires_web_search=True, got {requires}. Reason: {reason}"
        assert 'web_search' in reason or 'temporal' in reason.lower() or 'topic' in reason.lower(), \
            f"Reason should indicate semantic detection, got: {reason}"
        
        print(f"✅ TEST PASSED: requires_web_search={requires}")
        print(f"   Reason: {reason}")
    
    # =========================================================================
    # TEST 2: Web search DISABLED for static educational content
    # =========================================================================
    def test_web_search_disabled_for_static_content(self):
        """
        Query: "Explain Newton's laws of motion"
        Expected: tools_to_enable does NOT contain "web_search"
        
        The semantic classifier would classify this with:
        - temporal_scope: 'unspecified' (timeless physics concept)
        - reasoning: 'explanation request for physics laws'
        """
        # Mock semantic analysis for static educational query
        analysis = MockSemanticAnalysis(
            temporal_scope='unspecified',  # No time reference
            urgency_level='medium',
            reasoning='Student asking for explanation of Newton physics laws',
            topic_mentioned='Newton laws'
        )
        
        # Call _requires_web_search directly
        requires, reason = self.engine._requires_web_search(
            "Explain Newton's laws of motion",
            analysis
        )
        
        assert requires is False, f"Expected requires_web_search=False, got {requires}. Reason: {reason}"
        assert 'static' in reason.lower() or 'no web search' in reason.lower(), \
            f"Reason should indicate static content, got: {reason}"
        
        print(f"✅ TEST PASSED: requires_web_search={requires}")
        print(f"   Reason: {reason}")
    
    # =========================================================================
    # TEST 3: No duplicate tools in tools_to_enable
    # =========================================================================
    @pytest.mark.asyncio
    async def test_no_duplicate_tools(self):
        """
        Verify that tools_to_enable never contains duplicate entries
        when web_search is appended.
        """
        from services.intelligent_routing_engine import QueryComplexity
        
        # Mock analysis that triggers web search
        analysis = MockSemanticAnalysis(
            temporal_scope='immediate',
            reasoning='current events'
        )
        
        # Get routing decision
        decision = self.engine._select_pipeline(
            query="What happened today?",
            complexity=QueryComplexity.SIMPLE,
            context={'subject': 'General'},
            student_context={},
            semantic_analysis=analysis
        )
        
        # Check for duplicates
        tools = decision.tools_to_enable
        tools_set = set(tools)
        
        assert len(tools) == len(tools_set), \
            f"Duplicate tools found: {tools}"
        
        # Verify web_search is present (since temporal_scope='immediate')
        assert 'web_search' in tools, \
            f"Expected 'web_search' in tools, got: {tools}"
        
        print(f"✅ TEST PASSED: No duplicates in tools_to_enable={tools}")
    
    # =========================================================================
    # TEST 4: High urgency triggers web search
    # =========================================================================
    def test_high_urgency_triggers_web_search(self):
        """
        Query: "Quick update on today's matches"
        Expected: requires_web_search=True due to high urgency
        """
        analysis = MockSemanticAnalysis(
            temporal_scope='today',
            urgency_level='high',
            reasoning='urgent request for current sports info'
        )
        
        requires, reason = self.engine._requires_web_search(
            "Quick update on today's matches",
            analysis
        )
        
        assert requires is True, f"Expected True for high urgency, got {requires}"
        print(f"✅ TEST PASSED: High urgency triggers web_search")
    
    # =========================================================================
    # TEST 5: Reasoning-based detection (LLM reasoning contains indicators)
    # =========================================================================
    def test_reasoning_based_detection(self):
        """
        The LLM's reasoning field contains 'latest' or 'current' indicators
        that should trigger web search.
        """
        analysis = MockSemanticAnalysis(
            temporal_scope='unspecified',  # Even if temporal is unspecified
            reasoning='User is asking about the latest developments in AI research'
        )
        
        requires, reason = self.engine._requires_web_search(
            "Tell me about AI developments",
            analysis
        )
        
        assert requires is True, f"Expected True due to 'latest' in reasoning, got {requires}"
        print(f"✅ TEST PASSED: Reasoning-based detection works")


# ============================================================================
# RUN TESTS
# ============================================================================
if __name__ == '__main__':
    # Run synchronous tests
    test = TestWebSearchRouting()
    test.setup_method()
    
    print("\\n" + "="*60)
    print("Running Web Search Routing Tests")
    print("="*60 + "\\n")
    
    try:
        test.test_web_search_enabled_for_current_events()
        test.test_web_search_disabled_for_static_content()
        
        # Run async test
        asyncio.run(test.test_no_duplicate_tools())
        
        test.test_high_urgency_triggers_web_search()
        test.test_reasoning_based_detection()
        
        print("\\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
    except AssertionError as e:
        print(f"\\n❌ TEST FAILED: {e}")
        raise
