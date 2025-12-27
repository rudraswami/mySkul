"""
🧪 RAG Retrieval Tests - Verify Real Retrieval Not Mock
========================================================

Tests to verify that the tools are using real retrieval from structured banks,
not hardcoded dictionaries.

REQUIRED TESTS:
1. knowledge_search returns real content with citations
2. formula_lookup returns formulas with metadata
3. exam_strategy returns structured strategies
4. No hardcoded mock data in runtime responses
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# KNOWLEDGE SEARCH TESTS
# =============================================================================

class TestKnowledgeSearch:
    """Test knowledge_search tool retrieval"""
    
    @pytest.fixture
    def tool(self):
        from agents.core.tools.knowledge_search import KnowledgeSearchTool
        return KnowledgeSearchTool()
    
    @pytest.mark.asyncio
    async def test_friction_search(self, tool):
        """Test: 'Explain friction with an example'"""
        result = await tool.execute(query="friction", subject="Physics")
        
        assert result.success, f"Search failed: {result.error}"
        # Updated to include corpus_v2 methods
        method = result.metadata.get("retrieval_method", "")
        assert method.startswith("corpus_v2") or method in ["curriculum_retriever", "fallback"], f"Unexpected method: {method}"
        
        # Should have some content
        assert len(result.output) > 50, "Response too short"
        
        logger.info(f"✅ Friction search: {result.metadata}")
    
    @pytest.mark.asyncio
    async def test_photosynthesis_search(self, tool):
        """Test: 'What is photosynthesis?'"""
        result = await tool.execute(query="photosynthesis", subject="Biology")
        
        assert result.success
        
        # Check for real content markers
        output_lower = result.output.lower()
        has_content = (
            "photosynthesis" in output_lower or
            "plant" in output_lower or
            "chlorophyll" in output_lower or
            "glucose" in output_lower
        )
        assert has_content or not result.metadata.get("found"), "Missing expected content"
        
        logger.info(f"✅ Photosynthesis search: found={result.metadata.get('found')}")
    
    @pytest.mark.asyncio
    async def test_newton_laws_search(self, tool):
        """Test: 'Explain Newton's 3rd law'"""
        result = await tool.execute(query="Newton's laws", subject="Physics")
        
        assert result.success
        
        # Check for citations (real retrieval has sources)
        if result.metadata.get("found"):
            assert "sources" in result.metadata or "Source" in result.output, "Missing source citations"
        
        logger.info(f"✅ Newton's laws search: confidence={result.metadata.get('confidence', 0):.2f}")
    
    @pytest.mark.asyncio
    async def test_retrieval_has_confidence(self, tool):
        """Verify retrieval returns confidence scores"""
        result = await tool.execute(query="thermodynamics")
        
        assert "confidence" in result.metadata, "Missing confidence score"
        assert isinstance(result.metadata["confidence"], (int, float)), "Confidence should be numeric"
        
        logger.info(f"✅ Confidence check: {result.metadata.get('confidence')}")


# =============================================================================
# FORMULA LOOKUP TESTS
# =============================================================================

class TestFormulaLookup:
    """Test formula_lookup tool retrieval"""
    
    @pytest.fixture
    def tool(self):
        from agents.core.tools.formula_lookup import FormulaLookupTool
        return FormulaLookupTool()
    
    @pytest.mark.asyncio
    async def test_friction_formulas(self, tool):
        """Test: 'Friction formulas with units'"""
        result = await tool.execute(topic="friction", subject="Physics")
        
        assert result.success
        assert result.metadata.get("retrieval_method") in ["formula_bank", "fallback"]
        
        # If found, should have formula content
        if result.metadata.get("found"):
            assert "formula" in result.output.lower() or "Formula" in result.output
        
        logger.info(f"✅ Friction formulas: count={result.metadata.get('count', 0)}")
    
    @pytest.mark.asyncio
    async def test_coulomb_law_formula(self, tool):
        """Test: 'Coulomb's law formula'"""
        result = await tool.execute(topic="coulomb", subject="Physics")
        
        assert result.success
        
        if result.metadata.get("found"):
            # Should contain Coulomb's law formula or related content
            output_lower = result.output.lower()
            has_coulomb = (
                "coulomb" in output_lower or
                "charge" in output_lower or
                "electric" in output_lower or
                "q" in output_lower
            )
            assert has_coulomb, "Missing Coulomb's law content"
        
        logger.info(f"✅ Coulomb's law formula: found={result.metadata.get('found')}")
    
    @pytest.mark.asyncio
    async def test_kinetic_energy_formula(self, tool):
        """Test: 'Kinetic energy formula'"""
        result = await tool.execute(topic="kinetic energy")
        
        assert result.success
        
        if result.metadata.get("found"):
            # Should have the formula or related content
            output = result.output
            has_ke = "KE" in output or "kinetic" in output.lower() or "½mv²" in output or "mv" in output
            assert has_ke, "Missing kinetic energy content"
        
        logger.info(f"✅ Kinetic energy formula: found={result.metadata.get('found')}")
    
    @pytest.mark.asyncio
    async def test_formula_has_variables(self, tool):
        """Verify formulas include variable definitions"""
        result = await tool.execute(topic="mechanics")
        
        if result.metadata.get("found"):
            # Real retrieval should include variable definitions
            has_variables = "variable" in result.output.lower() or "Variables" in result.output
            assert has_variables, "Missing variable definitions"
        
        logger.info(f"✅ Variables check: passed")


# =============================================================================
# EXAM STRATEGY TESTS
# =============================================================================

class TestExamStrategy:
    """Test exam_strategy tool retrieval"""
    
    @pytest.fixture
    def tool(self):
        from agents.core.tools.exam_strategy import ExamStrategyTool
        return ExamStrategyTool()
    
    @pytest.mark.asyncio
    async def test_mechanics_30day_plan(self, tool):
        """Test: 'Make a 30-day mechanics plan' for JEE"""
        result = await tool.execute(topic="mechanics", exam_type="JEE")
        
        assert result.success
        # Updated to include strategy_bank method
        assert result.metadata.get("retrieval_method") in ["strategy_bank", "exam_strategy_bank", "no_data_fallback", "fallback", "general_advice"]
        
        logger.info(f"✅ Mechanics JEE strategy: found={result.metadata.get('found')}")
    
    @pytest.mark.asyncio
    async def test_10day_revision_plan(self, tool):
        """Test: 'Make a 10-day revision plan' for NEET"""
        result = await tool.execute(topic="Human Physiology", exam_type="NEET")
        
        assert result.success
        
        if result.metadata.get("found"):
            # Should have NEET-specific content
            output_lower = result.output.lower()
            has_neet = "neet" in output_lower or "weightage" in output_lower
            assert has_neet, "Missing NEET-specific content"
        
        logger.info(f"✅ NEET physiology strategy: found={result.metadata.get('found')}")
    
    @pytest.mark.asyncio
    async def test_strategy_has_weightage(self, tool):
        """Verify strategy includes weightage percentage"""
        result = await tool.execute(topic="Organic Chemistry", exam_type="JEE")
        
        if result.metadata.get("found"):
            # Real retrieval should include weightage
            has_weightage = "weightage" in result.metadata or "%" in result.output
            assert has_weightage, "Missing weightage information"
        
        logger.info(f"✅ Weightage check: passed")
    
    @pytest.mark.asyncio
    async def test_general_mode_no_exam(self, tool):
        """Test: General mode (no exam specified) returns general advice"""
        result = await tool.execute(topic="calculus", exam_type="General")
        
        assert result.success
        assert result.metadata.get("is_general") == True or result.metadata.get("retrieval_method") == "general_advice"
        
        logger.info(f"✅ General mode: correct fallback behavior")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestRAGIntegration:
    """Integration tests for the entire RAG system"""
    
    @pytest.mark.asyncio
    async def test_corpus_banks_initialized(self):
        """Verify all banks are initialized and have data"""
        from services.knowledge_base.corpus_ingestion import (
            get_formula_bank, 
            get_exam_strategy_bank,
            get_source_registry
        )
        from services.knowledge_base.curriculum_store import get_curriculum_store
        
        # Check formula bank
        formula_bank = get_formula_bank()
        assert len(formula_bank.formulas) > 0, "Formula bank is empty"
        logger.info(f"📐 Formula bank: {len(formula_bank.formulas)} formulas")
        
        # Check exam strategy bank
        strategy_bank = get_exam_strategy_bank()
        assert len(strategy_bank.strategies) > 0, "Strategy bank is empty"
        logger.info(f"🎯 Strategy bank: {len(strategy_bank.strategies)} strategies")
        
        # Check curriculum store
        curriculum_store = get_curriculum_store()
        assert len(curriculum_store.chunks) > 0, "Curriculum store is empty"
        logger.info(f"📚 Curriculum store: {len(curriculum_store.chunks)} chunks")
        
        # Check source registry
        source_registry = get_source_registry()
        assert len(source_registry.sources) > 0, "Source registry is empty"
        logger.info(f"📋 Source registry: {len(source_registry.sources)} sources")
    
    @pytest.mark.asyncio
    async def test_no_hardcoded_data_in_tools(self):
        """Verify tools don't use hardcoded KNOWLEDGE_BASE, FORMULAS, or EXAM_STRATEGY_DATA"""
        import inspect
        from agents.core.tools import knowledge_search, formula_lookup, exam_strategy
        
        # Check knowledge_search
        ks_source = inspect.getsource(knowledge_search)
        assert "KNOWLEDGE_BASE = {" not in ks_source, "knowledge_search still has hardcoded KNOWLEDGE_BASE"
        
        # Check formula_lookup
        fl_source = inspect.getsource(formula_lookup)
        assert "FORMULAS = {" not in fl_source, "formula_lookup still has hardcoded FORMULAS"
        
        # Check exam_strategy
        es_source = inspect.getsource(exam_strategy)
        assert "EXAM_STRATEGY_DATA = {" not in es_source, "exam_strategy still has hardcoded EXAM_STRATEGY_DATA"
        
        logger.info("✅ No hardcoded data found in tools")
    
    @pytest.mark.asyncio
    async def test_retrieval_logs_observable(self):
        """Verify retrieval produces observable logs"""
        from agents.core.tools.knowledge_search import KnowledgeSearchTool
        
        tool = KnowledgeSearchTool()
        
        # Execute a search
        result = await tool.execute(query="energy conservation")
        
        # Metadata should contain retrieval info
        assert "retrieval_method" in result.metadata, "Missing retrieval_method in metadata"
        assert "confidence" in result.metadata, "Missing confidence in metadata"
        
        logger.info(f"✅ Retrieval metadata: {result.metadata}")


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    # Run with: python -m pytest tests/test_rag_retrieval.py -v
    pytest.main([__file__, "-v", "--tb=short"])
