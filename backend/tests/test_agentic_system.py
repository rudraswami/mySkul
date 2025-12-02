"""
🧠 Test Suite for True Agentic System
=====================================

Tests the complete agentic architecture:
- ReAct reasoning loop
- Tool execution
- Memory system
- Planning
- Verification
"""

import pytest
import asyncio
from datetime import datetime


class TestToolRegistry:
    """Test the tool registry and individual tools"""
    
    def test_create_tool_registry(self):
        """Test creating a tool registry with default tools"""
        from agents.core.tool_registry import create_tool_registry
        
        registry = create_tool_registry(include_default=True)
        tools = registry.get_tool_names()
        
        assert 'calculator' in tools
        assert 'knowledge_search' in tools
        assert 'formula_lookup' in tools
        assert 'fact_checker' in tools
        assert len(tools) >= 4
    
    @pytest.mark.asyncio
    async def test_calculator_tool(self):
        """Test the calculator tool"""
        from agents.core.tool_registry import create_tool_registry
        
        registry = create_tool_registry(include_default=True)
        result = await registry.execute_tool('calculator', {}, expression="2 + 3 * 4")
        
        assert result.success
        assert result.output == 14  # 2 + 3*4 = 2 + 12 = 14
    
    @pytest.mark.asyncio
    async def test_formula_lookup_tool(self):
        """Test the formula lookup tool"""
        from agents.core.tool_registry import create_tool_registry
        
        registry = create_tool_registry(include_default=True)
        result = await registry.execute_tool('formula_lookup', {}, topic="kinetic_energy")
        
        assert result.success
        assert "formula" in result.output.lower() or "½" in result.output or "1/2" in result.output


class TestMemorySystem:
    """Test the memory system"""
    
    def test_short_term_memory(self):
        """Test short-term memory storage and retrieval"""
        from agents.core.memory import ShortTermMemory
        
        memory = ShortTermMemory(max_size=5)
        
        # Add entries
        memory.add("test_session", "conversation", "First message")
        memory.add("test_session", "conversation", "Second message")
        
        # Retrieve
        entries = memory.get_recent("test_session", limit=10)
        
        assert len(entries) == 2
        assert entries[0].content == "First message"
        assert entries[1].content == "Second message"
    
    def test_long_term_memory(self):
        """Test long-term memory storage"""
        from agents.core.memory import LongTermMemory
        
        memory = LongTermMemory()
        
        # Store student profile
        memory.store_student_pattern("user123", "strength", "mathematics")
        memory.store_student_pattern("user123", "weakness", "organic_chemistry")
        
        # Retrieve
        profile = memory.get_student_profile("user123")
        
        assert profile["strength"] == "mathematics"
        assert profile["weakness"] == "organic_chemistry"


class TestPlanner:
    """Test the planning system"""
    
    def test_create_plan(self):
        """Test creating an execution plan"""
        from agents.core.planner import Planner
        
        planner = Planner()
        
        plan = planner.create_plan(
            query="Explain why momentum is conserved in elastic collisions",
            context={"subject": "Physics"}
        )
        
        assert plan is not None
        assert len(plan.subtasks) > 0
        assert plan.status.value == "pending"


class TestVerifier:
    """Test the verification system"""
    
    def test_verify_calculation(self):
        """Test calculation verification"""
        from agents.core.verifier import Verifier
        
        verifier = Verifier()
        
        # Test correct calculation
        result = verifier.verify_calculation("2 + 2 = 4")
        assert result.status.value == "verified"
        
        # Test incorrect calculation
        result = verifier.verify_calculation("2 + 2 = 5")
        assert result.status.value == "failed"
    
    def test_verify_statement(self):
        """Test fact verification"""
        from agents.core.verifier import Verifier
        
        verifier = Verifier()
        
        # Test scientific fact
        result = verifier.verify_fact("Water boils at 100 degrees Celsius at standard pressure")
        
        # Should at least return a result (even if uncertain)
        assert result is not None
        assert result.status.value in ["verified", "uncertain", "failed"]


class TestReActAgent:
    """Test the ReAct reasoning agent"""
    
    def test_parse_thought(self):
        """Test parsing LLM thought responses"""
        from agents.core.react_agent import ReActAgent
        
        # Test thought with action
        response = """
        Thought: I need to calculate the kinetic energy of a 2kg object moving at 5m/s.
        Action: calculator
        Action Input: {"expression": "0.5 * 2 * 5**2"}
        """
        
        agent = ReActAgent(tools=None, llm_key=None)
        thought, action, action_input, is_final = agent._parse_response(response)
        
        assert "kinetic energy" in thought.lower()
        assert action == "calculator"
        assert action_input is not None
        assert not is_final
    
    def test_parse_final_answer(self):
        """Test parsing final answer"""
        from agents.core.react_agent import ReActAgent
        
        response = """
        Thought: I have all the information I need.
        Final Answer: The kinetic energy is 25 Joules.
        """
        
        agent = ReActAgent(tools=None, llm_key=None)
        thought, action, action_input, is_final = agent._parse_response(response)
        
        assert is_final
        assert "25 Joules" in action_input or "25 Joules" in thought


class TestAgenticDoubtResolver:
    """Test the complete agentic doubt resolver"""
    
    def test_create_agent(self):
        """Test creating the agentic doubt resolver"""
        from agents.agentic_doubt_resolver import create_agentic_doubt_resolver
        
        agent = create_agentic_doubt_resolver({
            'emergent_llm_key': 'test_key',
            'max_iterations': 5,
            'verbose': True
        })
        
        assert agent is not None
        assert agent.agent_type == "AgenticDoubtResolver"
        assert agent.max_iterations == 5
    
    def test_has_tools(self):
        """Test that agent has all required tools"""
        from agents.agentic_doubt_resolver import create_agentic_doubt_resolver
        
        agent = create_agentic_doubt_resolver()
        
        tool_names = agent.tools.get_tool_names()
        
        assert 'calculator' in tool_names
        assert 'knowledge_search' in tool_names
        assert 'formula_lookup' in tool_names


class TestIntegration:
    """Integration tests for the full pipeline"""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(True, reason="Requires LLM API key")
    async def test_full_doubt_resolution(self):
        """Test full doubt resolution with real LLM"""
        import os
        from agents.agentic_doubt_resolver import create_agentic_doubt_resolver
        
        llm_key = os.environ.get('EMERGENT_LLM_KEY') or os.environ.get('OPENAI_API_KEY')
        if not llm_key:
            pytest.skip("No LLM key available")
        
        agent = create_agentic_doubt_resolver({
            'emergent_llm_key': llm_key,
            'max_iterations': 5
        })
        
        result = await agent.run(
            query="Why is momentum conserved in collisions?",
            context={"subject": "Physics", "user_id": "test_user"}
        )
        
        assert result['success']
        assert 'content' in result
        assert len(result['content']) > 100  # Should have substantial explanation


# Run tests with: pytest backend/tests/test_agentic_system.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])

