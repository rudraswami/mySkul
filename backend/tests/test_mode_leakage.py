"""
🧪 Mode Leakage Prevention Tests
================================

These tests ensure that exam-coach language doesn't leak into non-exam queries.

COGNITIVE OS GUARANTEE:
- Simple conceptual questions → NO exam tips/tricks/weightage
- Emotional queries → NO academic pressure
- Explicit JEE/NEET requests → SHOULD have exam-specific content

Run: pytest backend/tests/test_mode_leakage.py -v
"""

import pytest
import re
from unittest.mock import MagicMock, AsyncMock


class TestExamCoachDetection:
    """Test that ExamCoachAgent.is_exam_strategy_query() is strict."""
    
    def test_simple_conceptual_not_exam_query(self):
        """Simple physics question should NOT trigger exam routing."""
        from agents.exam_coach import ExamCoachAgent
        
        queries = [
            "Explain Newton's Third Law with an example.",
            "What is force?",
            "How does photosynthesis work?",
            "Why is the sky blue?",
            "Explain the concept of momentum.",
            "What is the difference between speed and velocity?",
        ]
        
        for query in queries:
            result = ExamCoachAgent.is_exam_strategy_query(query)
            assert result == False, f"Query '{query}' incorrectly detected as exam strategy"
    
    def test_explicit_exam_queries_detected(self):
        """Explicit JEE/NEET prep queries should trigger exam routing."""
        from agents.exam_coach import ExamCoachAgent
        
        queries = [
            "Make me a JEE 30-day study plan for Mechanics",
            "How to prepare for NEET Biology?",
            "JEE preparation strategy for Physics",
            "What are important topics for NEET?",
            "Give me exam tips for JEE Main",
        ]
        
        for query in queries:
            result = ExamCoachAgent.is_exam_strategy_query(query)
            assert result == True, f"Query '{query}' should be detected as exam strategy"
    
    def test_ambiguous_not_exam_query(self):
        """Ambiguous queries without explicit exam keywords should NOT trigger."""
        from agents.exam_coach import ExamCoachAgent
        
        queries = [
            "Give me tips for understanding calculus",  # "tips" alone
            "I want to test my knowledge",  # "test" alone
            "What's the plan for today?",  # "plan" alone
            "This is really important to me",  # "important" alone
        ]
        
        for query in queries:
            result = ExamCoachAgent.is_exam_strategy_query(query)
            assert result == False, f"Ambiguous query '{query}' incorrectly detected as exam strategy"


class TestProfessorPersona:
    """Test that ProfessorAgent persona is context-aware."""
    
    def test_general_mode_no_jee_neet_mention(self):
        """In General mode, persona should NOT mention JEE/NEET."""
        from agents.professor import ProfessorAgent
        
        agent = ProfessorAgent({})
        persona = agent.get_agent_persona({'exam_mode': 'General'})
        
        # Should NOT contain JEE/NEET
        assert 'JEE' not in persona, "General mode persona should not mention JEE"
        assert 'NEET' not in persona, "General mode persona should not mention NEET"
        # Should still be a professor
        assert 'professor' in persona.lower() or 'Druv' in persona
    
    def test_jee_mode_has_jee_context(self):
        """In JEE mode, persona SHOULD include JEE context."""
        from agents.professor import ProfessorAgent
        
        agent = ProfessorAgent({})
        persona = agent.get_agent_persona({'exam_mode': 'JEE'})
        
        # SHOULD contain JEE
        assert 'JEE' in persona, "JEE mode persona should mention JEE"
    
    def test_tools_not_include_exam_strategy_in_general(self):
        """In General mode, exam_strategy tool should NOT be available."""
        from agents.professor import ProfessorAgent
        
        agent = ProfessorAgent({})
        tools = agent.get_available_tools({'exam_mode': 'General'})
        
        assert 'exam_strategy' not in tools, "exam_strategy should not be available in General mode"
    
    def test_tools_include_exam_strategy_in_jee(self):
        """In JEE mode, exam_strategy tool SHOULD be available."""
        from agents.professor import ProfessorAgent
        
        agent = ProfessorAgent({})
        tools = agent.get_available_tools({'exam_mode': 'JEE'})
        
        assert 'exam_strategy' in tools, "exam_strategy should be available in JEE mode"


class TestExamStrategyTool:
    """Test that ExamStrategyTool respects exam_mode."""
    
    @pytest.mark.asyncio
    async def test_general_mode_returns_general_advice(self):
        """In General mode, tool should return general study advice, not JEE-specific."""
        from agents.core.tools.exam_strategy import ExamStrategyTool
        
        tool = ExamStrategyTool()
        result = await tool.execute(
            topic="Force",
            context={'exam_mode': 'General'}
        )
        
        assert result.success == True
        # Should NOT contain JEE/NEET specific language
        assert 'weightage' not in result.output.lower()
        assert 'JEE' not in result.output or 'let me know' in result.output.lower()
    
    @pytest.mark.asyncio
    async def test_jee_mode_returns_jee_advice(self):
        """In JEE mode, tool SHOULD return JEE-specific advice."""
        from agents.core.tools.exam_strategy import ExamStrategyTool
        
        tool = ExamStrategyTool()
        result = await tool.execute(
            topic="Thermodynamics",
            exam_type="JEE",
            context={'exam_mode': 'JEE'}
        )
        
        assert result.success == True
        # SHOULD contain JEE-specific language
        assert 'JEE' in result.output or 'weightage' in result.output.lower()


class TestDynamicMentorPrompts:
    """Test that prompt style selection doesn't over-trigger exam_focused."""
    
    def test_conceptual_question_not_exam_focused(self):
        """Conceptual questions should NOT use exam_focused style."""
        from services.dynamic_mentor_prompts import DynamicMentorPrompts
        
        queries = [
            "What is force?",
            "Explain photosynthesis",
            "How does gravity work?",
        ]
        
        for query in queries:
            style = DynamicMentorPrompts._select_prompt_style(
                user_id="test",
                query=query,
                student_profile={}
            )
            assert style != 'exam_focused', f"Query '{query}' should not use exam_focused style"
    
    def test_explicit_exam_query_uses_exam_focused(self):
        """Explicit JEE/NEET queries SHOULD use exam_focused style."""
        from services.dynamic_mentor_prompts import DynamicMentorPrompts
        
        queries = [
            "What's important for JEE in this topic?",
            "NEET exam tips for biology",
        ]
        
        for query in queries:
            style = DynamicMentorPrompts._select_prompt_style(
                user_id="test",
                query=query,
                student_profile={}
            )
            assert style == 'exam_focused', f"Query '{query}' should use exam_focused style"


class TestResponseContentValidation:
    """Integration tests to validate response content doesn't leak exam language."""
    
    def _contains_exam_language(self, text: str) -> bool:
        """Check if text contains exam-specific language."""
        exam_patterns = [
            r'\bweightage\b',
            r'\bJEE\s+(Main|Advanced|tip|trick|question|pattern)',
            r'\bNEET\s+(tip|trick|question|pattern)',
            r'\bexam\s+(tip|trick|important)',
            r'\btopper\s+(secret|trick|hack)',
            r'\bprevious\s+year\s+question',
            r'\bPYQ\b',
        ]
        
        for pattern in exam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def test_exam_language_detector(self):
        """Test the exam language detector works."""
        # Should detect
        assert self._contains_exam_language("JEE Main tip: Focus on...")
        assert self._contains_exam_language("This has 5% weightage")
        assert self._contains_exam_language("Topper trick: Use this formula")
        
        # Should NOT detect
        assert not self._contains_exam_language("Force equals mass times acceleration")
        assert not self._contains_exam_language("This is how photosynthesis works")
        assert not self._contains_exam_language("Newton discovered this principle")
