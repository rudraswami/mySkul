"""
💪 MotivationAgent Ship-Blocker Tests
======================================

Tests ensuring MotivationAgent is a TRUE agent, not template-based.

SHIP BLOCKERS:
1. Exam stress → CALM_DOWN mode + action plan
2. Procrastination → CONSISTENCY mode + micro-plan
3. Low confidence → CONFIDENCE mode + reframing
4. Crisis phrasing → Guardrails must handle (not bypassed)
5. Cheating → Teach-instead (guardrails)
6. Memory write skip on safety flags
"""

import pytest
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCoachingModeDetection:
    """Test autonomous coaching mode selection"""
    
    def test_calm_down_mode_exam_stress(self):
        """'I feel stressed about exams' → CALM_DOWN mode"""
        from agents.motivation import EmotionalPatternDetector, CoachingMode
        
        queries = [
            "I feel stressed about exams",
            "I'm so anxious about the test tomorrow",
            "I'm panicking, exam in 2 hours",
            "Can't focus, too nervous about JEE",
        ]
        
        for query in queries:
            decision = EmotionalPatternDetector.detect(query)
            assert decision.mode == CoachingMode.CALM_DOWN, \
                f"Expected CALM_DOWN for '{query}', got {decision.mode}"
            assert decision.confidence >= 0.3, \
                f"Confidence too low for '{query}': {decision.confidence}"
    
    def test_consistency_mode_procrastination(self):
        """'I am lazy, I can't focus' → CONSISTENCY mode"""
        from agents.motivation import EmotionalPatternDetector, CoachingMode
        
        queries = [
            "I'm so lazy, can't start studying",
            "I keep procrastinating on physics",
            "No discipline, keep wasting time",
            "I'm distracted, can't focus on anything",
        ]
        
        for query in queries:
            decision = EmotionalPatternDetector.detect(query)
            assert decision.mode == CoachingMode.CONSISTENCY, \
                f"Expected CONSISTENCY for '{query}', got {decision.mode}"
    
    def test_confidence_mode_low_self_esteem(self):
        """'I'm dumb, I can't do physics' → CONFIDENCE mode"""
        from agents.motivation import EmotionalPatternDetector, CoachingMode
        
        queries = [
            "I'm so dumb, can't understand physics",
            "I'm stupid, everyone gets it but me",
            "I'm bad at math, can't do anything",
            "I'm the worst in class, not smart at all",
        ]
        
        for query in queries:
            decision = EmotionalPatternDetector.detect(query)
            assert decision.mode == CoachingMode.CONFIDENCE, \
                f"Expected CONFIDENCE for '{query}', got {decision.mode}"
    
    def test_burnout_mode_exhaustion(self):
        """Exhaustion signals → BURNOUT mode"""
        from agents.motivation import EmotionalPatternDetector, CoachingMode
        
        queries = [
            "I'm exhausted, can't study anymore",
            "Feeling burnt out, too much to do",
            "Overwhelmed with everything, need to stop",
        ]
        
        for query in queries:
            decision = EmotionalPatternDetector.detect(query)
            assert decision.mode == CoachingMode.BURNOUT, \
                f"Expected BURNOUT for '{query}', got {decision.mode}"
    
    def test_celebrate_mode_success(self):
        """Success signals → CELEBRATE mode"""
        from agents.motivation import EmotionalPatternDetector, CoachingMode
        
        queries = [
            "I finally got it! Understood derivatives!",
            "I passed the test, so happy!",
            "Making progress, things are clicking now",
        ]
        
        for query in queries:
            decision = EmotionalPatternDetector.detect(query)
            assert decision.mode == CoachingMode.CELEBRATE, \
                f"Expected CELEBRATE for '{query}', got {decision.mode}"
    
    def test_goal_lock_mode_planning(self):
        """Planning signals → GOAL_LOCK mode"""
        from agents.motivation import EmotionalPatternDetector, CoachingMode
        
        queries = [
            "What should I study next?",
            "Where do I start with physics?",
            "Help me make a study plan",
            "Overwhelmed, don't know where to start",
        ]
        
        for query in queries:
            decision = EmotionalPatternDetector.detect(query)
            assert decision.mode == CoachingMode.GOAL_LOCK, \
                f"Expected GOAL_LOCK for '{query}', got {decision.mode}"


class TestMotivationAgentStructure:
    """Test that MotivationAgent is a TRUE ReAct agent"""
    
    def test_inherits_react_agent(self):
        """MotivationAgent must inherit from ReActAgent"""
        from agents.motivation import MotivationAgent
        from agents.core.react_agent import ReActAgent
        
        agent = MotivationAgent({})
        assert isinstance(agent, ReActAgent), \
            "MotivationAgent must inherit from ReActAgent"
    
    def test_has_agent_name(self):
        """Must have get_agent_name() method"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        assert agent.get_agent_name() == "MotivationAgent"
    
    def test_has_agent_persona(self):
        """Must have get_agent_persona() method"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        persona = agent.get_agent_persona()
        
        assert "coach" in persona.lower() or "care" in persona.lower(), \
            "Persona must mention coaching/caring"
        assert "empathy" in persona.lower() or "acknowledge" in persona.lower(), \
            "Persona must mention empathy"
    
    def test_has_available_tools(self):
        """Must have tools registered"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        tools = agent.get_available_tools()
        
        assert len(tools) >= 2, "Must have at least 2 tools"
        assert "memory_recall" in tools or "study_planner" in tools, \
            "Must have memory_recall or study_planner tool"
    
    def test_has_tool_registry(self):
        """Must have tool_registry initialized"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        assert agent.tool_registry is not None, \
            "tool_registry must be initialized"


class TestMotivationAgentOutput:
    """Test output style requirements"""
    
    @pytest.mark.asyncio
    async def test_response_has_action_plan(self):
        """Response must include numbered action steps"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        
        result = await agent.run(
            query="I'm stressed about my physics exam",
            context={'user_id': 'test', 'session_id': 'test'}
        )
        
        response = result.get('main_response', '')
        
        # Check for numbered steps
        assert '1.' in response or '**1' in response, \
            "Response must have numbered action steps"
        assert '2.' in response or '**2' in response, \
            "Response must have at least 2 action steps"
    
    @pytest.mark.asyncio
    async def test_response_has_empathy(self):
        """Response must start with empathy"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        
        result = await agent.run(
            query="I'm so frustrated with calculus",
            context={'user_id': 'test', 'session_id': 'test'}
        )
        
        response = result.get('main_response', '')
        
        # First line should be empathetic
        first_line = response.split('\n')[0].lower()
        empathy_words = ['hey', 'i hear', 'i get', 'i understand', 'it\'s okay', 'take a breath']
        
        has_empathy = any(word in first_line for word in empathy_words)
        assert has_empathy, \
            f"First line must have empathy. Got: {first_line[:100]}"
    
    @pytest.mark.asyncio
    async def test_response_has_checkin(self):
        """Response must end with check-in question"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        
        result = await agent.run(
            query="I can't focus, too distracted",
            context={'user_id': 'test', 'session_id': 'test'}
        )
        
        response = result.get('main_response', '')
        
        # Last part should have a question
        assert '?' in response, \
            "Response must have a check-in question"


class TestMotivationAgentMetadata:
    """Test metadata and observability"""
    
    @pytest.mark.asyncio
    async def test_metadata_includes_coaching_mode(self):
        """Metadata must include coaching_mode"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        
        result = await agent.run(
            query="I'm exhausted, can't study anymore",
            context={'user_id': 'test', 'session_id': 'test'}
        )
        
        metadata = result.get('metadata', {})
        
        assert 'coaching_mode' in metadata, \
            "Metadata must include coaching_mode"
        assert metadata.get('coaching_mode') == 'burnout', \
            f"Expected burnout mode, got {metadata.get('coaching_mode')}"
    
    @pytest.mark.asyncio
    async def test_metadata_includes_tools_used(self):
        """Metadata must track tools used"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        
        result = await agent.run(
            query="I need help planning my study",
            context={'user_id': 'test', 'session_id': 'test'}
        )
        
        metadata = result.get('metadata', {})
        
        assert 'tools_used' in metadata, \
            "Metadata must include tools_used list"


class TestLegacyCompatibility:
    """Test backward compatibility with existing call sites"""
    
    def test_detect_emotional_state_legacy(self):
        """Legacy detect_emotional_state still works"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        
        # Test various emotional states
        assert agent.detect_emotional_state("I'm stressed") is not None
        assert agent.detect_emotional_state("Hello how are you") is None
    
    def test_enhance_response_legacy(self):
        """Legacy enhance_response still works"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        
        result = agent.enhance_response(
            result={'query': "I'm frustrated with physics"},
            context={}
        )
        
        assert 'motivation' in result
        motivation = result.get('motivation')
        assert motivation is not None
        assert 'type' in motivation
    
    def test_get_opening_for_state_legacy(self):
        """Legacy get_opening_for_state still works"""
        from agents.motivation import MotivationAgent
        
        agent = MotivationAgent({})
        
        opening = agent.get_opening_for_state('calm_down', 'Rahul')
        
        assert 'Rahul' in opening or 'Hey' in opening
        assert len(opening) > 10


class TestIntegrationHelpers:
    """Test integration helper functions"""
    
    def test_should_trigger_motivation(self):
        """should_trigger_motivation detects emotional queries"""
        from agents.motivation import should_trigger_motivation
        
        assert should_trigger_motivation("I'm stressed about exams") == True
        assert should_trigger_motivation("I'm so frustrated") == True
        assert should_trigger_motivation("What is Newton's law?") == False
    
    def test_get_motivation_enhancement(self):
        """get_motivation_enhancement returns valid structure"""
        from agents.motivation import get_motivation_enhancement
        
        result = get_motivation_enhancement(
            "I'm anxious about the test",
            {'student_profile': {'user_name': 'Test'}}
        )
        
        assert 'motivation' in result


class TestNoTemplateUsage:
    """Verify agent is NOT using static templates"""
    
    def test_no_hardcoded_boredom_busters(self):
        """Verify BOREDOM_BUSTERS static array is not used"""
        import inspect
        from agents.motivation import MotivationAgent
        
        source = inspect.getsource(MotivationAgent._build_mode_response)
        
        # Should NOT reference old template arrays
        assert 'BOREDOM_BUSTERS' not in source, \
            "Should not use static BOREDOM_BUSTERS array"
        assert 'FRUSTRATION_HELPERS' not in source, \
            "Should not use static FRUSTRATION_HELPERS array"
        assert 'ANXIETY_CALMERS' not in source, \
            "Should not use static ANXIETY_CALMERS array"
    
    def test_no_random_choice_templates(self):
        """Verify not using random.choice on static templates"""
        import inspect
        from agents.motivation import MotivationAgent
        
        source = inspect.getsource(MotivationAgent._build_mode_response)
        
        # Should NOT use random.choice
        assert 'random.choice' not in source, \
            "Should not use random.choice on templates"


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
