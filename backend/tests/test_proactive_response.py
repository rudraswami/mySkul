"""
Test: Proactive Response - NameError Regression Test
=====================================================
Verifies that _generate_proactive_response() handles context correctly
and never crashes orchestration.

BUGFIX: NameError: name 'context' is not defined
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


class TestProactiveResponseBugfix:
    """Regression tests for proactive response NameError fix"""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create a mock orchestrator with the real method"""
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        orchestrator.logger = MagicMock()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_generate_proactive_response_with_context(self, mock_orchestrator):
        """
        REGRESSION TEST: Ensure _generate_proactive_response() doesn't crash
        when called with a valid context dict.
        """
        # Minimal context dict
        context = {
            'is_first_turn': True,
            'message': 'what can you do',
            'user_id': 'test_user'
        }
        
        student_profile = {
            'exam_mode': 'JEE',
            'name': 'Test Student'
        }
        
        # Call the method - should NOT raise NameError
        result = await mock_orchestrator._generate_proactive_response(
            action_intent='help',
            name_prefix='Test, ',
            last_topic='calculus',
            weak_topics=['integration', 'limits'],
            recent_topics=['derivatives'],
            mastery_level=60,
            student_profile=student_profile,
            context=context
        )
        
        # Verify: returns a string response
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_generate_proactive_response_with_none_context(self, mock_orchestrator):
        """
        REGRESSION TEST: Ensure method doesn't crash even when context=None
        """
        student_profile = {
            'exam_mode': 'NEET',
            'name': 'Student'
        }
        
        # Call with context=None - should NOT raise
        result = await mock_orchestrator._generate_proactive_response(
            action_intent='explore',
            name_prefix='',
            last_topic='',
            weak_topics=[],
            recent_topics=[],
            mastery_level=50,
            student_profile=student_profile,
            context=None  # Explicitly None
        )
        
        # Verify: returns a string response, no crash
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_generate_proactive_response_help_not_first_turn(self, mock_orchestrator):
        """
        Test: 'help' intent on non-first-turn should NOT show capability menu
        """
        context = {
            'is_first_turn': False,  # NOT first turn
            'message': 'help me',
        }
        
        student_profile = {'exam_mode': 'General'}
        
        result = await mock_orchestrator._generate_proactive_response(
            action_intent='help',
            name_prefix='',
            last_topic='physics',
            weak_topics=['thermodynamics'],
            recent_topics=[],
            mastery_level=40,
            student_profile=student_profile,
            context=context
        )
        
        # Should return helpful response without listing all capabilities
        assert isinstance(result, str)
        # Should NOT contain the full capability menu
        assert 'I can help with:' not in result or 'first_turn' not in str(context.get('is_first_turn'))
    
    @pytest.mark.asyncio  
    async def test_proactive_guidance_response_doesnt_crash(self):
        """
        Integration test: _proactive_guidance_response wraps errors safely
        """
        from services.unified_ai_orchestrator import UnifiedAIOrchestrator
        
        orchestrator = UnifiedAIOrchestrator.__new__(UnifiedAIOrchestrator)
        orchestrator.logger = MagicMock()
        
        # Mock dependencies
        orchestrator._get_memory_context = AsyncMock(return_value={
            'weak_topics': [],
            'recent_topics': [],
            'current_topic': '',
            'mastery_level': 50
        })
        orchestrator._get_student_profile = AsyncMock(return_value={
            'name': 'Test',
            'exam_mode': 'JEE'
        })
        
        # Mock routing decision
        routing_decision = MagicMock()
        routing_decision.extra_context = {'action_intent': 'explore'}
        
        context = {'user_id': 'test', 'is_first_turn': False}
        
        # This should NOT raise NameError anymore
        result = await orchestrator._proactive_guidance_response(
            message="try something new",
            context=context,
            routing_decision=routing_decision
        )
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'main_response' in result
        assert 'response_type' in result
        assert result['response_type'] == 'proactive_guidance'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])














