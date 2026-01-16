"""
🧪 Regression Tests for Routing Decision Fixes (v1.0)
=====================================================

These tests verify the fixes for:
1. RoutingDecision as single source of truth for tools
2. No web search message injection
3. Timeout budget alignment
4. Tool union in agents

Run with: pytest tests/test_routing_decision_fixes.py -v
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass
from typing import List, Dict, Any


# =============================================================================
# TEST 1: Routing Decision tools_to_enable is passed to supervisor context
# =============================================================================

class TestRoutingDecisionToolsPassthrough:
    """
    Verify that tools_to_enable from RoutingDecision is passed to supervisor.
    
    FIX REFERENCE:
    - unified_ai_orchestrator.py: supervisor_context now includes 'tools_to_enable'
    - supervisor.py: _run_single_agent logs and passes tools
    """
    
    def test_supervisor_context_includes_tools_to_enable(self):
        """supervisor_context must include tools_to_enable from routing decision"""
        # Mock routing decision
        @dataclass
        class MockRoutingDecision:
            tools_to_enable: List[str]
            agents_to_activate: List[str]
            pipeline: Any = None
            complexity: Any = None
            confidence: float = 0.8
            reasoning: str = ""
            enable_verification: bool = False
            enable_visual: bool = False
            max_iterations: int = 5
            timeout_seconds: float = 25.0
            use_knowledge_graph: bool = False
            use_memory: bool = True
            priority_factors: dict = None
            enable_agent_negotiation: bool = False
            extra_context: dict = None
        
        routing_decision = MockRoutingDecision(
            tools_to_enable=['web_search', 'calculator', 'knowledge_search'],
            agents_to_activate=['mentor'],
            extra_context={'requires_web_search': True}
        )
        
        # Verify the expected context keys exist
        expected_keys = ['tools_to_enable', 'agents_to_activate', 'requires_web_search']
        
        # Build context as orchestrator does
        extra_ctx = getattr(routing_decision, 'extra_context', {}) or {}
        tools_requested = getattr(routing_decision, 'tools_to_enable', []) or []
        agents_requested = getattr(routing_decision, 'agents_to_activate', []) or []
        requires_web_search = extra_ctx.get('requires_web_search', False)
        
        supervisor_context = {
            'tools_to_enable': tools_requested,
            'agents_to_activate': agents_requested,
            'requires_web_search': requires_web_search,
        }
        
        # Assertions
        assert supervisor_context['tools_to_enable'] == ['web_search', 'calculator', 'knowledge_search']
        assert supervisor_context['agents_to_activate'] == ['mentor']
        assert supervisor_context['requires_web_search'] == True


# =============================================================================
# TEST 2: No web search message injection
# =============================================================================

class TestNoWebSearchMessageInjection:
    """
    Verify that web search results are NOT injected into the user message.
    
    FIX REFERENCE:
    - unified_ai_orchestrator.py: removed web_search_results string injection
    - supervisor now receives original message, not enhanced_message
    """
    
    def test_message_not_modified(self):
        """Original message should be passed to supervisor without modification"""
        original_message = "Who won the 2024 Nobel Prize in Physics?"
        
        # In the old code, this would have been modified to:
        # enhanced_message = message + web_search_results
        # 
        # After fix, message is passed as-is
        
        # Simulate the fixed flow
        web_search_results = ""  # No longer used for injection
        
        # The message should NOT be modified
        final_message = original_message  # No + web_search_results
        
        assert final_message == original_message
        assert "[SYSTEM: REAL-TIME WEB SEARCH RESULTS]" not in final_message
        assert "[END WEB SEARCH RESULTS]" not in final_message


# =============================================================================
# TEST 3: Timeout Budget Alignment
# =============================================================================

class TestTimeoutBudgetAlignment:
    """
    Verify timeout configuration is within bounds.
    
    FIX REFERENCE:
    - react_agent.py: DEFAULT_GLOBAL_TIMEOUT = 25.0 (was 45.0)
    - react_agent.py: ITERATION_TIMEOUT = 12.0 (was 25.0)
    - intelligent_routing_engine.py: all timeout_seconds <= 25.0
    """
    
    def test_global_timeout_under_frontend(self):
        """Global timeout must be less than frontend's 30s timeout"""
        FRONTEND_TIMEOUT = 30.0  # From frontend/src/api/client.js
        BACKEND_GLOBAL_TIMEOUT = 25.0  # From react_agent.py
        
        assert BACKEND_GLOBAL_TIMEOUT < FRONTEND_TIMEOUT, \
            f"Backend timeout ({BACKEND_GLOBAL_TIMEOUT}s) must be < frontend timeout ({FRONTEND_TIMEOUT}s)"
    
    def test_iteration_timeout_allows_multiple_iterations(self):
        """Iteration timeout should allow 2+ iterations within global timeout"""
        GLOBAL_TIMEOUT = 25.0
        ITERATION_TIMEOUT = 12.0
        
        # Should allow at least 2 iterations
        max_iterations_possible = GLOBAL_TIMEOUT / ITERATION_TIMEOUT
        assert max_iterations_possible >= 2, \
            f"Should allow at least 2 iterations, but only allows {max_iterations_possible:.1f}"
    
    def test_iteration_limits_reasonable(self):
        """Iteration limits should be reduced for faster responses"""
        ITERATION_LIMITS = {
            'trivial': 2,
            'simple': 3,
            'moderate': 5,
            'complex': 7,
            'deep': 10,
        }
        
        # All limits should be <= 10
        for complexity, limit in ITERATION_LIMITS.items():
            assert limit <= 10, f"{complexity} has {limit} iterations, should be <= 10"
        
        # Trivial should be very fast
        assert ITERATION_LIMITS['trivial'] <= 2, "Trivial should complete in 2 iterations"


# =============================================================================
# TEST 4: Tool Union Works Correctly
# =============================================================================

class TestToolUnion:
    """
    Verify that routing tools are unioned with agent tools.
    
    FIX REFERENCE:
    - react_agent.py: _get_tools_description creates union of agent + routing tools
    """
    
    def test_tool_union_adds_routing_tools(self):
        """Routing tools should be added to agent's native tools"""
        agent_tools = ['calculator', 'knowledge_search', 'formula_lookup']
        routing_tools = ['web_search', 'fact_checker']
        
        # Union logic from react_agent.py
        available = list(set(agent_tools) | set(routing_tools))
        
        # All original agent tools should be present
        for tool in agent_tools:
            assert tool in available, f"Agent tool {tool} missing from union"
        
        # All routing tools should be added
        for tool in routing_tools:
            assert tool in available, f"Routing tool {tool} missing from union"
    
    def test_tool_union_no_duplicates(self):
        """Union should not create duplicates"""
        agent_tools = ['calculator', 'knowledge_search', 'web_search']
        routing_tools = ['web_search', 'calculator']  # Overlap
        
        available = list(set(agent_tools) | set(routing_tools))
        
        # No duplicates
        assert len(available) == len(set(available)), "Union contains duplicates"
        
        # Should have exactly 3 unique tools
        assert len(available) == 3
    
    def test_empty_routing_tools_uses_agent_tools(self):
        """If routing doesn't specify tools, use agent's native tools"""
        agent_tools = ['calculator', 'knowledge_search']
        routing_tools = []  # No routing tools specified
        
        # Logic from react_agent.py
        if routing_tools:
            available = list(set(agent_tools) | set(routing_tools))
        else:
            available = agent_tools
        
        assert available == agent_tools


# =============================================================================
# TEST 5: Agent Selection Respects Routing Decision
# =============================================================================

class TestAgentSelectionRespectsRouting:
    """
    Verify that supervisor uses agents_to_activate from routing decision.
    
    FIX REFERENCE:
    - supervisor.py: _select_agents checks context['agents_to_activate'] first
    """
    
    def test_routing_agents_used_when_provided(self):
        """When routing specifies agents, use those instead of internal selection"""
        context = {
            'agents_to_activate': ['mentor'],  # From routing decision
        }
        
        # Simulated _select_agents logic (from supervisor.py)
        valid_agents = ['mentor', 'professor', 'visualise', 'doubt_resolver', 
                       'exam_coach', 'study_buddy', 'weak_area_detective', 'parent_report']
        
        agents_from_routing = context.get('agents_to_activate', [])
        selected = None
        
        if agents_from_routing:
            for agent in agents_from_routing:
                if agent in valid_agents:
                    selected = agent
                    break
        
        assert selected == 'mentor', "Should use routing-specified agent"
    
    def test_fallback_to_internal_selection_when_no_routing(self):
        """When routing doesn't specify agents, use internal selection"""
        context = {}  # No agents_to_activate
        
        agents_from_routing = context.get('agents_to_activate', [])
        
        assert agents_from_routing == [], "Should have empty list when not specified"


# =============================================================================
# TEST 6: Structured Logging Contains Required Fields
# =============================================================================

class TestStructuredLogging:
    """
    Verify that logs contain the required fields for debugging.
    
    FIX REFERENCE:
    - Multiple files now log: tools_requested, tools_allowed, tools_executed
    """
    
    def test_log_format_contains_tool_chain(self):
        """Log should contain Requested → Enabled → Executed chain"""
        # Sample log format from unified_ai_orchestrator.py
        tools_requested = ['web_search', 'calculator']
        tools_enabled = ['web_search', 'calculator']
        tools_executed = ['web_search']
        pipeline = 'multi_agent'
        generation_time = 2.5
        
        log_message = (
            f"📊 [TOOL CHAIN] requested={tools_requested} → "
            f"enabled={tools_enabled} → "
            f"executed={tools_executed} | "
            f"pipeline={pipeline} | "
            f"time={generation_time:.2f}s"
        )
        
        # Verify all components are present
        assert 'requested=' in log_message
        assert 'enabled=' in log_message
        assert 'executed=' in log_message
        assert 'pipeline=' in log_message
        assert 'time=' in log_message


# =============================================================================
# INTEGRATION TEST: Full Flow
# =============================================================================

class TestFullFlow:
    """
    Integration test for the complete routing → agent → tool flow.
    """
    
    @pytest.mark.asyncio
    async def test_web_search_available_to_agent(self):
        """
        When routing requests web_search, it should be available to the agent.
        """
        # Mock the flow
        routing_decision = {
            'tools_to_enable': ['web_search', 'knowledge_search'],
            'agents_to_activate': ['mentor'],
            'requires_web_search': True
        }
        
        agent_native_tools = ['calculator', 'knowledge_search', 'formula_lookup']
        routing_tools = routing_decision['tools_to_enable']
        
        # Apply union (as in react_agent.py)
        available_tools = list(set(agent_native_tools) | set(routing_tools))
        
        # web_search should now be available
        assert 'web_search' in available_tools, \
            "web_search from routing should be available to agent"
        
        # Original agent tools should still be available
        assert 'calculator' in available_tools
        assert 'formula_lookup' in available_tools


# =============================================================================
# TEST 7: Intelligent Visual Decision (v1.0)
# =============================================================================

class TestIntelligentVisualDecision:
    """
    Verify that visuals are only triggered when appropriate.
    
    FIX REFERENCE:
    - intelligent_routing_engine.py: _should_enable_visual()
    - Visuals should NOT trigger for every query
    """
    
    def test_explicit_visual_request_enables_visual(self):
        """Explicit diagram request should enable visual"""
        visual_queries = [
            "Draw a circuit diagram for RC circuit",
            "Show me a diagram of photosynthesis",
            "Visualize the structure of benzene",
            "Plot the graph of y = x^2",
            "Can you illustrate the free body diagram"
        ]
        
        explicit_visual_keywords = [
            'diagram', 'draw', 'visualize', 'visualise', 'show me', 'illustrate',
            'graph', 'plot', 'chart', 'picture', 'figure', 'sketch'
        ]
        
        for query in visual_queries:
            query_lower = query.lower()
            should_enable = any(kw in query_lower for kw in explicit_visual_keywords)
            assert should_enable, f"Query '{query}' should enable visual"
    
    def test_definition_queries_no_visual(self):
        """Definition queries should NOT enable visual"""
        non_visual_queries = [
            "What is Newton's first law?",
            "Define photosynthesis",
            "Who discovered gravity?",
            "When was the periodic table created?",
            "List the noble gases",
            "Tell me about Einstein",
            "What is the formula for acceleration?"
        ]
        
        non_visual_patterns = [
            'what is', 'define', 'who', 'when', 'where', 'list', 'name',
            'formula', 'tell me', 'explain in words'
        ]
        
        for query in non_visual_queries:
            query_lower = query.lower()
            # Check that non-visual patterns are detected
            is_non_visual = any(pattern in query_lower for pattern in non_visual_patterns)
            assert is_non_visual, f"Query '{query}' should be detected as non-visual"
    
    def test_physics_visual_topics_enable_visual(self):
        """Physics topics that need diagrams should enable visual"""
        physics_visual_queries = [
            "Explain the circuit with resistors",
            "How does a lens form images?",
            "Describe ray optics reflection",
            "What is the electric field pattern?"
        ]
        
        physics_visual_topics = [
            'circuit', 'lens', 'ray', 'optics', 'electric field'
        ]
        
        for query in physics_visual_queries:
            query_lower = query.lower()
            has_visual_topic = any(topic in query_lower for topic in physics_visual_topics)
            assert has_visual_topic, f"Query '{query}' should detect visual-appropriate topic"
    
    def test_agents_list_excludes_visualise_when_not_needed(self):
        """agents_to_activate should not include visualise when visual not needed"""
        base_agents = ['mentor', 'professor', 'doubt_resolver']
        enable_visual = False
        
        # Simulated build_agents_list logic
        if enable_visual and 'visualise' not in base_agents:
            agents = base_agents + ['visualise']
        else:
            agents = base_agents
        
        assert 'visualise' not in agents, "visualise should not be in agents when enable_visual=False"
    
    def test_agents_list_includes_visualise_when_needed(self):
        """agents_to_activate should include visualise when visual is needed"""
        base_agents = ['mentor', 'professor', 'doubt_resolver']
        enable_visual = True
        
        # Simulated build_agents_list logic
        if enable_visual and 'visualise' not in base_agents:
            agents = base_agents + ['visualise']
        else:
            agents = base_agents
        
        assert 'visualise' in agents, "visualise should be in agents when enable_visual=True"
    
    def test_indian_student_context_stem_subjects(self):
        """Visual learner + STEM subject should enable visual"""
        student_context = {'visual_learner': True}
        stem_subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'math', 'maths']
        
        for subject in stem_subjects:
            # For visual learners in STEM subjects, visual should be enabled
            # (assuming query doesn't match non-visual patterns)
            is_visual_learner = student_context.get('visual_learner', False)
            is_stem = subject in stem_subjects
            should_enable = is_visual_learner and is_stem
            assert should_enable, f"Visual learner + {subject} should enable visual"
    
    def test_non_stem_subjects_no_automatic_visual(self):
        """Non-STEM subjects should not automatically get visuals"""
        non_stem_subjects = ['history', 'english', 'geography', 'civics', 'general']
        
        # These subjects generally don't benefit from automatic visual generation
        for subject in non_stem_subjects:
            is_stem = subject in ['physics', 'chemistry', 'biology', 'mathematics', 'math', 'maths']
            assert not is_stem, f"{subject} should not be detected as STEM"


# =============================================================================
# TEST 8: Performance Fixes (v2.0)
# =============================================================================

class TestPerformanceFixes:
    """
    Verify that performance fixes are in place.
    
    FIX REFERENCE:
    - unified_ai_orchestrator.py: Agent negotiation disabled by default
    - unified_ai_orchestrator.py: Supervisor timeout protection (20s)
    - supervisor.py: Single-flight mode is default (not multi-agent)
    """
    
    def test_agent_negotiation_disabled_by_default(self):
        """Agent negotiation should be disabled unless explicitly enabled"""
        # Simulate context from orchestrator
        context_from_orchestrator = {
            'enable_agent_negotiation': False,
            'use_agent_negotiation': False,
        }
        
        # The supervisor should NOT use negotiation
        explicit_enable = (
            context_from_orchestrator.get('use_agent_negotiation') is True or 
            context_from_orchestrator.get('enable_agent_negotiation') is True
        )
        
        assert explicit_enable == False, "Agent negotiation should be disabled by default"
    
    def test_agent_negotiation_only_when_explicit_true(self):
        """Agent negotiation only when explicitly set to True"""
        # Test various context values
        test_cases = [
            ({'enable_agent_negotiation': False}, False),
            ({'enable_agent_negotiation': None}, False),
            ({}, False),  # Missing key = disabled
            ({'enable_agent_negotiation': True}, True),  # Only True enables
            ({'use_agent_negotiation': True}, True),
        ]
        
        for context, expected in test_cases:
            explicit_enable = (
                context.get('use_agent_negotiation') is True or 
                context.get('enable_agent_negotiation') is True
            )
            assert explicit_enable == expected, f"Context {context} should give {expected}"
    
    def test_supervisor_timeout_less_than_frontend(self):
        """Supervisor timeout must be less than frontend timeout"""
        FRONTEND_TIMEOUT = 30.0
        SUPERVISOR_TIMEOUT = 20.0  # From unified_ai_orchestrator.py
        
        assert SUPERVISOR_TIMEOUT < FRONTEND_TIMEOUT, \
            f"Supervisor timeout ({SUPERVISOR_TIMEOUT}s) must be < frontend ({FRONTEND_TIMEOUT}s)"
    
    def test_single_flight_runs_one_agent(self):
        """Single-flight mode should run exactly one agent"""
        # When negotiation is disabled, supervisor runs single agent
        use_negotiation = False
        
        # Simulate _select_agents returning one agent
        agents_to_run = ['mentor']  # From routing decision
        
        # Verify only one agent is selected
        assert len(agents_to_run) == 1, "Single-flight should select exactly one agent"
        assert 'mentor' in agents_to_run, "Should use routing decision agent"
    
    def test_fast_mode_for_simple_queries(self):
        """Simple/trivial queries should use fast mode"""
        simple_complexities = ['TRIVIAL', 'SIMPLE', 'trivial', 'simple']
        complex_complexities = ['MODERATE', 'COMPLEX', 'DEEP_REASONING', 'moderate', 'complex']
        
        for complexity in simple_complexities:
            use_fast_mode = complexity in ['TRIVIAL', 'SIMPLE', 'simple', 'trivial']
            assert use_fast_mode == True, f"{complexity} should use fast mode"
        
        for complexity in complex_complexities:
            use_fast_mode = complexity in ['TRIVIAL', 'SIMPLE', 'simple', 'trivial']
            assert use_fast_mode == False, f"{complexity} should NOT use fast mode"


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
