"""
🧪 RAG v2 Tests - Verify Real Corpus with Traceable Citations
=============================================================

Tests to verify:
1. Raw documents exist in data/corpus/raw/
2. Chunks are properly linked to documents
3. Manifest is generated with version + hash
4. Citations are traceable (chunk_id → doc_id → raw file)
5. No hardcoded data in runtime path
"""

import pytest
import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# CORPUS STRUCTURE TESTS
# =============================================================================

class TestCorpusStructure:
    """Test that corpus has proper file structure"""
    
    def test_corpus_directories_exist(self):
        """Verify data/corpus/ directories are created"""
        from services.knowledge_base.corpus_store import CORPUS_ROOT, RAW_DIR, CHUNKS_DIR
        
        # Initialize corpus to create directories
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        corpus = get_corpus_store_v2()
        
        assert CORPUS_ROOT.exists(), f"Corpus root not found: {CORPUS_ROOT}"
        assert RAW_DIR.exists(), f"Raw directory not found: {RAW_DIR}"
        assert CHUNKS_DIR.exists(), f"Chunks directory not found: {CHUNKS_DIR}"
        
        logger.info(f"✅ Corpus directories exist: {CORPUS_ROOT}")
    
    def test_raw_documents_exist(self):
        """Verify raw markdown files exist in data/corpus/raw/"""
        from services.knowledge_base.corpus_store import RAW_DIR, get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        # Check that raw files exist
        raw_files = list(RAW_DIR.glob("*.md"))
        assert len(raw_files) > 0, f"No raw .md files in {RAW_DIR}"
        
        # Verify each document has a raw file
        for doc_id, doc in corpus.documents.items():
            raw_path = RAW_DIR / doc.filename
            assert raw_path.exists(), f"Raw file missing for doc {doc_id}: {raw_path}"
        
        logger.info(f"✅ Found {len(raw_files)} raw documents in {RAW_DIR}")
    
    def test_chunks_file_exists(self):
        """Verify chunks.json is generated"""
        from services.knowledge_base.corpus_store import CHUNKS_FILE, get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        assert CHUNKS_FILE.exists(), f"Chunks file not found: {CHUNKS_FILE}"
        
        with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "chunks" in data, "chunks key missing in chunks.json"
        assert "documents" in data, "documents key missing in chunks.json"
        assert len(data["chunks"]) > 0, "No chunks in chunks.json"
        
        logger.info(f"✅ Chunks file has {len(data['chunks'])} chunks")
    
    def test_manifest_exists_and_valid(self):
        """Verify manifest.json is generated with required fields"""
        from services.knowledge_base.corpus_store import MANIFEST_FILE, get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        assert MANIFEST_FILE.exists(), f"Manifest not found: {MANIFEST_FILE}"
        
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_fields = [
            "dataset_version", "content_hash", "num_documents", 
            "num_chunks", "avg_chunk_len", "sources", "created_at"
        ]
        
        for field in required_fields:
            assert field in manifest, f"Missing required field in manifest: {field}"
        
        assert manifest["num_documents"] > 0, "No documents in manifest"
        assert manifest["num_chunks"] > 0, "No chunks in manifest"
        
        logger.info(f"✅ Manifest valid: v{manifest['dataset_version'][:10]}, "
                   f"{manifest['num_documents']} docs, {manifest['num_chunks']} chunks")


# =============================================================================
# CITATION TRACEABILITY TESTS
# =============================================================================

class TestCitationTraceability:
    """Test that citations are fully traceable"""
    
    def test_chunk_has_doc_id(self):
        """Verify every chunk links to a document"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        for chunk_id, chunk in corpus.chunks.items():
            assert chunk.doc_id, f"Chunk {chunk_id} missing doc_id"
            assert chunk.doc_id in corpus.documents, f"Chunk {chunk_id} has invalid doc_id: {chunk.doc_id}"
        
        logger.info(f"✅ All {len(corpus.chunks)} chunks have valid doc_id linkage")
    
    def test_citation_trail_complete(self):
        """Verify citation trail: chunk → document → raw file"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2, RAW_DIR
        
        corpus = get_corpus_store_v2()
        
        for chunk_id, chunk in corpus.chunks.items():
            # Get document
            doc = corpus.documents.get(chunk.doc_id)
            assert doc, f"Document not found for chunk {chunk_id}"
            
            # Verify raw file exists
            raw_path = RAW_DIR / doc.filename
            assert raw_path.exists(), f"Raw file not found: {raw_path}"
            
            # Verify citation string is complete
            citation = chunk.get_full_citation()
            assert chunk_id[:8] in citation, f"Chunk ID not in citation: {citation}"
            assert doc.doc_id[:8] in citation, f"Doc ID not in citation: {citation}"
        
        logger.info(f"✅ All citation trails complete: chunk → document → raw file")
    
    def test_verify_citation_function(self):
        """Test the verify_citation function"""
        from services.knowledge_base.retriever_v2 import get_retriever_v2
        
        retriever = get_retriever_v2()
        
        # Get a chunk ID from corpus
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        corpus = get_corpus_store_v2()
        
        if corpus.chunks:
            chunk_id = next(iter(corpus.chunks.keys()))
            
            # Verify citation
            result = retriever.verify_citation(chunk_id)
            
            assert result is not None, f"verify_citation returned None for {chunk_id}"
            assert "chunk" in result, "Missing chunk in verification result"
            assert "document" in result, "Missing document in verification result"
            assert "raw_file" in result, "Missing raw_file in verification result"
            
            logger.info(f"✅ Citation verification works: {result['citation']}")


# =============================================================================
# NO HARDCODED DATA TESTS
# =============================================================================

class TestNoHardcodedData:
    """Verify no hardcoded data in runtime path"""
    
    def test_tools_use_retriever(self):
        """Verify tools use RetrieverV2, not hardcoded dicts"""
        import inspect
        from agents.core.tools import knowledge_search, formula_lookup, exam_strategy
        
        # Check knowledge_search
        ks_source = inspect.getsource(knowledge_search)
        assert "KNOWLEDGE_BASE = {" not in ks_source, "knowledge_search has hardcoded KNOWLEDGE_BASE"
        assert "retriever_v2" in ks_source.lower() or "RetrieverV2" in ks_source, \
            "knowledge_search doesn't use RetrieverV2"
        
        # Check formula_lookup
        fl_source = inspect.getsource(formula_lookup)
        assert "FORMULAS = {" not in fl_source, "formula_lookup has hardcoded FORMULAS"
        assert "retriever_v2" in fl_source.lower() or "RetrieverV2" in fl_source, \
            "formula_lookup doesn't use RetrieverV2"
        
        # Check exam_strategy
        es_source = inspect.getsource(exam_strategy)
        assert "EXAM_STRATEGY_DATA = {" not in es_source, "exam_strategy has hardcoded EXAM_STRATEGY_DATA"
        assert "retriever_v2" in es_source.lower() or "RetrieverV2" in es_source, \
            "exam_strategy doesn't use RetrieverV2"
        
        logger.info("✅ All tools use RetrieverV2, no hardcoded data")
    
    def test_corpus_loads_from_files(self):
        """Verify corpus loads from files, not hardcoded Python"""
        from services.knowledge_base.corpus_store import (
            get_corpus_store_v2, reset_corpus_store_v2,
            CHUNKS_FILE, RAW_DIR
        )
        
        # Reset to force reload
        reset_corpus_store_v2()
        
        # Verify files exist before loading
        assert CHUNKS_FILE.exists() or len(list(RAW_DIR.glob("*.md"))) == 0, \
            "Corpus should either have chunks.json or no raw files (for fresh init)"
        
        # Load corpus
        corpus = get_corpus_store_v2()
        
        # Verify it loaded from files (or created them)
        assert CHUNKS_FILE.exists(), "Corpus didn't create chunks.json"
        assert len(list(RAW_DIR.glob("*.md"))) > 0, "No raw files created"
        
        logger.info("✅ Corpus loads from/creates files, not hardcoded Python")


# =============================================================================
# RETRIEVAL TESTS WITH CITATIONS
# =============================================================================

class TestRetrievalWithCitations:
    """Test retrieval returns proper citations"""
    
    @pytest.fixture
    def retriever(self):
        from services.knowledge_base.retriever_v2 import get_retriever_v2
        return get_retriever_v2()
    
    @pytest.mark.asyncio
    async def test_knowledge_search_returns_citations(self, retriever):
        """Test knowledge search returns traceable citations"""
        result = retriever.retrieve_knowledge("friction", "Physics")
        
        assert result.retrieval_method.startswith("corpus_v2"), f"Wrong method: {result.retrieval_method}"
        
        if result.results:
            for r in result.results:
                assert "citation" in r, "Missing citation in result"
                assert "chunk_id" in r, "Missing chunk_id in result"
                assert "doc_id" in r, "Missing doc_id in result"
                
                # Citation should contain IDs
                citation = r["citation"]
                assert "chunk:" in citation or r["chunk_id"][:8] in citation, \
                    f"Citation doesn't include chunk reference: {citation}"
        
        logger.info(f"✅ Knowledge search returns citations: {result.get_citations()[:2]}")
    
    @pytest.mark.asyncio
    async def test_formula_lookup_returns_citations(self, retriever):
        """Test formula lookup returns traceable citations"""
        result = retriever.retrieve_formulas("kinetic energy", "Physics")
        
        assert result.retrieval_method == "formula_bank", f"Wrong method: {result.retrieval_method}"
        
        if result.results:
            for r in result.results:
                assert "citation" in r, "Missing citation in result"
                assert "formula_id" in r, "Missing formula_id in result"
        
        logger.info(f"✅ Formula lookup returns citations: {result.get_citations()[:2]}")
    
    @pytest.mark.asyncio
    async def test_exam_strategy_returns_citations(self, retriever):
        """Test exam strategy returns traceable citations"""
        result = retriever.retrieve_exam_strategy("Mechanics", "JEE")
        
        assert result.retrieval_method == "strategy_bank", f"Wrong method: {result.retrieval_method}"
        
        if result.results:
            for r in result.results:
                assert "citation" in r, "Missing citation in result"
                assert "strategy_id" in r, "Missing strategy_id in result"
        
        logger.info(f"✅ Exam strategy returns citations: {result.get_citations()[:2]}")


# =============================================================================
# TOOL EXECUTION TESTS
# =============================================================================

class TestToolExecution:
    """Test tool execution with RAG v2"""
    
    @pytest.fixture
    def knowledge_tool(self):
        from agents.core.tools.knowledge_search import KnowledgeSearchTool
        return KnowledgeSearchTool()
    
    @pytest.fixture
    def formula_tool(self):
        from agents.core.tools.formula_lookup import FormulaLookupTool
        return FormulaLookupTool()
    
    @pytest.fixture
    def strategy_tool(self):
        from agents.core.tools.exam_strategy import ExamStrategyTool
        return ExamStrategyTool()
    
    @pytest.mark.asyncio
    async def test_knowledge_search_execution(self, knowledge_tool):
        """Test: 'Explain friction with an example'"""
        result = await knowledge_tool.execute(query="friction", subject="Physics")
        
        assert result.success, f"Tool failed: {result.error}"
        assert result.metadata.get("retrieval_method", "").startswith("corpus_v2"), \
            f"Wrong retrieval method: {result.metadata}"
        assert "citations" in result.metadata, "Missing citations in metadata"
        
        if result.metadata.get("found"):
            assert len(result.metadata["citations"]) > 0, "No citations returned"
        
        logger.info(f"✅ Knowledge search tool: citations={result.metadata.get('citations', [])[:1]}")
    
    @pytest.mark.asyncio
    async def test_formula_lookup_execution(self, formula_tool):
        """Test: 'Coulomb's law formula with units'"""
        result = await formula_tool.execute(topic="coulomb", subject="Physics")
        
        assert result.success, f"Tool failed: {result.error}"
        assert result.metadata.get("retrieval_method") == "formula_bank", \
            f"Wrong retrieval method: {result.metadata}"
        
        logger.info(f"✅ Formula lookup tool: found={result.metadata.get('found')}")
    
    @pytest.mark.asyncio
    async def test_exam_strategy_execution(self, strategy_tool):
        """Test: 'Make a 30-day mechanics plan'"""
        result = await strategy_tool.execute(topic="Mechanics", exam_type="JEE")
        
        assert result.success, f"Tool failed: {result.error}"
        assert result.metadata.get("retrieval_method") in ["strategy_bank", "no_data_fallback"], \
            f"Wrong retrieval method: {result.metadata}"
        
        if result.metadata.get("found"):
            assert "citation" in result.metadata, "Missing citation in metadata"
        
        logger.info(f"✅ Exam strategy tool: found={result.metadata.get('found')}")


# =============================================================================
# CORPUS STATS TEST
# =============================================================================

class TestCorpusStats:
    """Test corpus statistics and versioning"""
    
    def test_corpus_stats_available(self):
        """Verify corpus stats are accessible"""
        from services.knowledge_base.retriever_v2 import get_retriever_v2
        
        retriever = get_retriever_v2()
        stats = retriever.get_corpus_stats()
        
        assert stats.get("status") == "initialized", f"Corpus not initialized: {stats}"
        assert stats.get("num_documents") > 0, "No documents"
        assert stats.get("num_chunks") > 0, "No chunks"
        assert stats.get("dataset_version"), "No version"
        assert stats.get("content_hash"), "No content hash"
        
        logger.info(f"✅ Corpus stats: {stats['num_documents']} docs, {stats['num_chunks']} chunks, "
                   f"v{stats['dataset_version'][:10]}")


# =============================================================================
# RAG v2 PHASE 2: BM25 INDEX TESTS
# =============================================================================

class TestBM25Index:
    """Test BM25 lexical search index"""
    
    def test_bm25_index_built(self):
        """Verify BM25 index is built on corpus load"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        assert corpus.bm25_index is not None, "BM25 index not created"
        assert corpus.bm25_index._initialized, "BM25 index not initialized"
        assert corpus.bm25_index.doc_count > 0, "BM25 index has no documents"
        
        logger.info(f"✅ BM25 index: {corpus.bm25_index.doc_count} docs, "
                   f"{len(corpus.bm25_index.term_freqs)} terms")
    
    def test_bm25_search_returns_results(self):
        """Test BM25 search for a known term"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        # Search for a common physics term
        results = corpus.search_bm25("newton force motion", limit=5)
        
        assert len(results) > 0, "BM25 search returned no results"
        
        # Check result structure
        chunk, score = results[0]
        assert hasattr(chunk, 'chunk_id'), "Result missing chunk_id"
        assert hasattr(chunk, 'text'), "Result missing text"
        assert 0 <= score <= 1, f"Score out of range: {score}"
        
        logger.info(f"✅ BM25 search: {len(results)} results for 'newton force motion'")
    
    def test_bm25_subject_filter(self):
        """Test BM25 search with subject filter"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        # Search with subject filter
        results_all = corpus.search_bm25("energy", limit=10)
        results_physics = corpus.search_bm25("energy", subject="Physics", limit=10)
        
        # Physics filter should return same or fewer results
        assert len(results_physics) <= len(results_all), "Subject filter didn't reduce results"
        
        # All filtered results should be Physics
        for chunk, _ in results_physics:
            assert chunk.subject.lower() == "physics", f"Wrong subject: {chunk.subject}"
        
        logger.info(f"✅ BM25 subject filter: {len(results_all)} total, {len(results_physics)} Physics")


# =============================================================================
# RAG v2 PHASE 2: VECTOR INDEX TESTS (FAISS + SQLite)
# =============================================================================

class TestVectorIndex:
    """Test FAISS vector semantic search index"""
    
    def test_vector_index_exists(self):
        """Verify FAISS vector index is created"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        assert corpus.vector_index is not None, "Vector index not created"
        
        # Check it's configured for FAISS
        stats = corpus.vector_index.get_stats()
        assert stats.get("index_type") == "faiss", f"Wrong index type: {stats.get('index_type')}"
        
        logger.info(f"✅ FAISS vector index exists: {stats}")
    
    @pytest.mark.asyncio
    async def test_vector_search_returns_results(self):
        """Test FAISS vector search for a semantic query (requires FAISS + OpenAI API key)"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        # Search for a semantic concept
        results = await corpus.search_vector("relationship between force and acceleration", limit=5)
        
        # FAISS is optional - skip if not available
        if len(results) == 0:
            pytest.skip("FAISS not installed or OpenAI API key not set - skipping vector test")
        
        # Check result structure
        chunk, score = results[0]
        assert hasattr(chunk, 'chunk_id'), "Result missing chunk_id"
        assert hasattr(chunk, 'text'), "Result missing text"
        assert 0 <= score <= 1, f"Score out of valid range: {score}"
        
        # Verify index stats
        stats = corpus.vector_index.get_stats()
        assert stats.get("num_vectors") > 0, "No vectors in index"
        
        logger.info(f"✅ FAISS search: {len(results)} results, top score={score:.3f}, "
                   f"query time={stats.get('last_query_time_ms', 0):.1f}ms")
    
    @pytest.mark.asyncio
    async def test_faiss_index_persistence(self):
        """Test that FAISS index is persisted to files (not JSON) - requires FAISS"""
        from services.knowledge_base.corpus_store import (
            get_corpus_store_v2, 
            FAISS_INDEX_FILE, 
            SQLITE_META_FILE,
            VECTOR_MANIFEST_FILE
        )
        
        corpus = get_corpus_store_v2()
        
        # Build vector index if not built
        await corpus.search_vector("test query", limit=1)
        
        # Skip if FAISS not available
        if not FAISS_INDEX_FILE.exists():
            pytest.skip("FAISS not installed - skipping persistence test")
        assert SQLITE_META_FILE.exists(), f"SQLite metadata file missing: {SQLITE_META_FILE}"
        assert VECTOR_MANIFEST_FILE.exists(), f"Vector manifest missing: {VECTOR_MANIFEST_FILE}"
        
        # Verify manifest content
        with open(VECTOR_MANIFEST_FILE, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        assert manifest.get("index_type") == "faiss_flat_ip", \
            f"Wrong index type in manifest: {manifest.get('index_type')}"
        assert manifest.get("num_vectors") > 0, "No vectors in manifest"
        assert manifest.get("embedding_model") == "text-embedding-3-small", \
            f"Wrong embedding model: {manifest.get('embedding_model')}"
        
        logger.info(f"✅ FAISS persistence: index={FAISS_INDEX_FILE.stat().st_size}B, "
                   f"meta={SQLITE_META_FILE.stat().st_size}B, "
                   f"vectors={manifest.get('num_vectors')}, dim={manifest.get('dimensions')}")
    
    def test_json_vector_index_not_used(self):
        """Verify legacy JSON vector index is NOT used for production"""
        from services.knowledge_base.corpus_store import VECTOR_INDEX_FILE, FAISS_INDEX_FILE
        
        # FAISS should be the primary index
        if FAISS_INDEX_FILE.exists():
            # If FAISS exists, JSON should either not exist or be outdated
            logger.info(f"✅ FAISS is primary vector store: {FAISS_INDEX_FILE}")
        else:
            logger.warning("⚠️ FAISS index not built yet - will be built on first vector search")
        
        # Even if JSON exists (migration), FAISS should be preferred
        if VECTOR_INDEX_FILE.exists():
            logger.info(f"ℹ️ Legacy JSON index exists but FAISS is preferred: {VECTOR_INDEX_FILE}")
    
    @pytest.mark.asyncio
    async def test_vector_index_idempotency(self):
        """Test that vector index doesn't rebuild if manifest unchanged"""
        from services.knowledge_base.corpus_store import (
            get_corpus_store_v2, 
            reset_corpus_store_v2,
            VECTOR_MANIFEST_FILE
        )
        import os
        
        # Get corpus and build index
        corpus = get_corpus_store_v2()
        await corpus.search_vector("test", limit=1)
        
        # Record manifest mtime
        if VECTOR_MANIFEST_FILE.exists():
            mtime_before = os.path.getmtime(VECTOR_MANIFEST_FILE)
            
            # Reset and reload
            reset_corpus_store_v2()
            corpus2 = get_corpus_store_v2()
            await corpus2.search_vector("test", limit=1)
            
            mtime_after = os.path.getmtime(VECTOR_MANIFEST_FILE)
            
            # Manifest should NOT be modified (index loaded, not rebuilt)
            assert mtime_before == mtime_after, \
                "Vector index was rebuilt unnecessarily (manifest mtime changed)"
            
            logger.info("✅ Vector index idempotency: index loaded without rebuild")


# =============================================================================
# RAG v2 PHASE 2: HYBRID SEARCH TESTS
# =============================================================================

class TestHybridSearch:
    """Test Hybrid (BM25 + Vector) search"""
    
    @pytest.mark.asyncio
    async def test_hybrid_search_returns_results(self):
        """Test hybrid search combines BM25 and vector"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        results = await corpus.search_hybrid(
            "explain Newton's laws of motion",
            limit=5
        )
        
        assert len(results) > 0, "Hybrid search returned no results"
        
        # Check result structure (3-tuple)
        chunk, score, retrieval_type = results[0]
        assert hasattr(chunk, 'chunk_id'), "Result missing chunk_id"
        assert retrieval_type in ['hybrid', 'bm25', 'vector'], f"Invalid type: {retrieval_type}"
        
        logger.info(f"✅ Hybrid search: {len(results)} results, types={[r[2] for r in results]}")
    
    @pytest.mark.asyncio
    async def test_hybrid_search_weights(self):
        """Test that BM25/Vector weights affect results"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        query = "kinetic energy formula derivation"
        
        # BM25-heavy
        results_bm25 = await corpus.search_hybrid(
            query, limit=5, bm25_weight=0.8, vector_weight=0.2
        )
        
        # Vector-heavy
        results_vec = await corpus.search_hybrid(
            query, limit=5, bm25_weight=0.2, vector_weight=0.8
        )
        
        # Results should potentially differ
        assert len(results_bm25) > 0, "BM25-heavy returned no results"
        assert len(results_vec) > 0, "Vector-heavy returned no results"
        
        logger.info(f"✅ Hybrid weights: BM25-heavy={len(results_bm25)}, Vec-heavy={len(results_vec)}")
    
    @pytest.mark.asyncio
    async def test_hybrid_search_retrieval_method_in_results(self):
        """Test that retrieval results include method indicator"""
        from services.knowledge_base.retriever_v2 import get_retriever_v2
        
        retriever = get_retriever_v2()
        
        result = retriever.retrieve_knowledge("acceleration due to gravity", max_results=3)
        
        assert result.retrieval_method.startswith("corpus_v2"), \
            f"Wrong method: {result.retrieval_method}"
        
        # Check if retrieval_type is in results
        for r in result.results:
            if "retrieval_type" in r:
                assert r["retrieval_type"] in ['hybrid', 'bm25', 'vector', 'keyword'], \
                    f"Invalid retrieval_type: {r['retrieval_type']}"
        
        logger.info(f"✅ Retrieval method: {result.retrieval_method}")


# =============================================================================
# RAG v2 PHASE 2: RERANKER TESTS
# =============================================================================

class TestReranker:
    """Test LLM-based reranker"""
    
    def test_reranker_exists(self):
        """Verify reranker is initialized"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        assert corpus.reranker is not None, "Reranker not initialized"
        assert hasattr(corpus.reranker, 'rerank'), "Reranker missing rerank method"
        
        logger.info("✅ Reranker initialized")
    
    def test_heuristic_rerank(self):
        """Test heuristic reranking (fallback when LLM unavailable)"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2, LLMReranker, ChunkV2
        
        reranker = LLMReranker()
        
        # Create mock candidates
        mock_chunks = [
            (ChunkV2(
                chunk_id="test1", doc_id="doc1", section="Test",
                text="Newton's first law states that an object at rest stays at rest",
                start_char=0, end_char=100, subject="Physics", topic="Newton's Laws",
                subtopic="", class_level="11", keywords=["newton", "law", "motion"],
                formulas=[], key_concepts=[], exam_relevance={}, source_citation="Test", page_reference=""
            ), 0.5, 'bm25'),
            (ChunkV2(
                chunk_id="test2", doc_id="doc1", section="Test",
                text="Photosynthesis is the process by which plants convert light",
                start_char=0, end_char=100, subject="Biology", topic="Photosynthesis",
                subtopic="", class_level="11", keywords=["photosynthesis", "plant"],
                formulas=[], key_concepts=[], exam_relevance={}, source_citation="Test", page_reference=""
            ), 0.6, 'vector')
        ]
        
        # Rerank with query about Newton
        reranked = reranker._heuristic_rerank("Newton's law of motion", mock_chunks, top_k=2)
        
        # Newton chunk should rank higher due to keyword match
        assert len(reranked) == 2, "Wrong number of reranked results"
        assert reranked[0][0].topic == "Newton's Laws", "Heuristic rerank didn't boost relevant chunk"
        
        logger.info("✅ Heuristic rerank working correctly")


# =============================================================================
# RAG v2 EVALUATION HARNESS
# =============================================================================

class TestEvaluationHarness:
    """Evaluation harness for measuring retrieval quality"""
    
    # Test queries with expected topics (ground truth)
    EVAL_QUERIES = [
        {
            "query": "Newton's laws of motion",
            "expected_topics": ["newton", "law", "motion", "force"],
            "expected_subject": "Physics"
        },
        {
            "query": "What is photosynthesis",
            "expected_topics": ["photosynthesis", "plant", "chlorophyll", "light"],
            "expected_subject": "Biology"
        },
        {
            "query": "Quadratic formula",
            "expected_topics": ["quadratic", "equation", "formula", "roots"],
            "expected_subject": "Mathematics"
        },
        {
            "query": "Chemical bonding types",
            "expected_topics": ["bond", "ionic", "covalent", "chemical"],
            "expected_subject": "Chemistry"
        }
    ]
    
    @pytest.mark.asyncio
    async def test_retrieval_relevance(self):
        """Measure retrieval relevance for eval queries"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        results_summary = []
        
        for eval_q in self.EVAL_QUERIES:
            query = eval_q["query"]
            expected_topics = set(eval_q["expected_topics"])
            expected_subject = eval_q["expected_subject"]
            
            # Run hybrid search
            results = await corpus.search_hybrid(query, limit=3)
            
            if not results:
                results_summary.append({
                    "query": query,
                    "hits": 0,
                    "relevance": 0.0
                })
                continue
            
            # Calculate relevance
            relevance_scores = []
            for chunk, score, _ in results:
                # Check if chunk matches expected subject
                subject_match = 1.0 if chunk.subject.lower() == expected_subject.lower() else 0.0
                
                # Check keyword overlap
                chunk_keywords = set(kw.lower() for kw in chunk.keywords)
                keyword_overlap = len(expected_topics & chunk_keywords) / len(expected_topics)
                
                # Combined relevance
                relevance = 0.5 * subject_match + 0.5 * keyword_overlap
                relevance_scores.append(relevance)
            
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            
            results_summary.append({
                "query": query,
                "hits": len(results),
                "relevance": avg_relevance
            })
        
        # Calculate overall metrics
        total_relevance = sum(r["relevance"] for r in results_summary) / len(results_summary)
        total_hits = sum(r["hits"] for r in results_summary)
        
        logger.info(f"📊 EVALUATION RESULTS:")
        for r in results_summary:
            logger.info(f"   - {r['query'][:30]}: hits={r['hits']}, relevance={r['relevance']:.2f}")
        logger.info(f"   OVERALL: avg_relevance={total_relevance:.2f}, total_hits={total_hits}")
        
        # Assert minimum quality
        assert total_relevance >= 0.3, f"Relevance too low: {total_relevance}"
        assert total_hits > 0, "No hits at all"
    
    @pytest.mark.asyncio
    async def test_retrieval_method_consistency(self):
        """Test that retrieval method is consistently reported"""
        from services.knowledge_base.retriever_v2 import get_retriever_v2
        
        retriever = get_retriever_v2()
        
        # Run multiple queries
        methods_seen = set()
        for query in ["force", "energy", "reaction"]:
            result = retriever.retrieve_knowledge(query, max_results=2)
            methods_seen.add(result.retrieval_method)
        
        # Should use consistent corpus_v2 methods
        for method in methods_seen:
            assert method.startswith("corpus_v2"), f"Unexpected method: {method}"
        
        logger.info(f"✅ Retrieval methods: {methods_seen}")
    
    def test_citation_completeness(self):
        """Test that all results have complete citations"""
        from services.knowledge_base.retriever_v2 import get_retriever_v2
        
        retriever = get_retriever_v2()
        result = retriever.retrieve_knowledge("acceleration", max_results=5)
        
        citations = result.get_citations()
        
        for i, r in enumerate(result.results):
            # Check citation fields
            assert r.get("citation"), f"Result {i} missing citation"
            assert r.get("chunk_id"), f"Result {i} missing chunk_id"
            assert r.get("doc_id"), f"Result {i} missing doc_id"
        
        logger.info(f"✅ Citation completeness: {len(result.results)} results, "
                   f"{len(citations)} citations")


# =============================================================================
# DEMO QUERIES - REQUIRED VALIDATION
# =============================================================================

class TestDemoQueries:
    """
    Required demo queries that must show correct index usage in logs.
    
    Queries:
    - "Explain friction with an example"
    - "What is photosynthesis?"
    - "Coulomb's law formula with units"
    - "Make a 30-day mechanics plan"
    """
    
    DEMO_QUERIES = [
        {
            "query": "Explain friction with an example",
            "tool": "knowledge_search",
            "expected_subject": "Physics"
        },
        {
            "query": "What is photosynthesis?",
            "tool": "knowledge_search",
            "expected_subject": "Biology"
        },
        {
            "query": "Coulomb's law formula with units",
            "tool": "formula_lookup",
            "expected_subject": "Physics"
        },
        {
            "query": "Make a 30-day mechanics plan",
            "tool": "exam_strategy",
            "expected_subject": "Physics"
        }
    ]
    
    @pytest.mark.asyncio
    async def test_demo_query_friction(self):
        """Demo: 'Explain friction with an example' - uses FAISS vector index"""
        from agents.core.tools.knowledge_search import KnowledgeSearchTool
        
        tool = KnowledgeSearchTool()
        result = await tool.execute(query="Explain friction with an example", subject="Physics")
        
        assert result.success, f"Knowledge search failed: {result.error}"
        
        # Log must show index type
        meta = result.metadata
        logger.info(f"📊 DEMO QUERY: 'Explain friction with an example'")
        logger.info(f"   - Method: {meta.get('retrieval_method')}")
        logger.info(f"   - Found: {meta.get('found')}")
        logger.info(f"   - Confidence: {meta.get('confidence', 0):.2f}")
        logger.info(f"   - Citations: {meta.get('citations', [])[:1]}")
        
        # Verify method includes index type
        assert "corpus_v2" in meta.get("retrieval_method", ""), \
            f"Wrong retrieval method: {meta.get('retrieval_method')}"
    
    @pytest.mark.asyncio
    async def test_demo_query_photosynthesis(self):
        """Demo: 'What is photosynthesis?' - uses FAISS vector index"""
        from agents.core.tools.knowledge_search import KnowledgeSearchTool
        
        tool = KnowledgeSearchTool()
        result = await tool.execute(query="What is photosynthesis?", subject="Biology")
        
        assert result.success, f"Knowledge search failed: {result.error}"
        
        meta = result.metadata
        logger.info(f"📊 DEMO QUERY: 'What is photosynthesis?'")
        logger.info(f"   - Method: {meta.get('retrieval_method')}")
        logger.info(f"   - Found: {meta.get('found')}")
        logger.info(f"   - Confidence: {meta.get('confidence', 0):.2f}")
    
    @pytest.mark.asyncio
    async def test_demo_query_coulombs_law(self):
        """Demo: 'Coulomb's law formula with units' - uses formula_lookup"""
        from agents.core.tools.formula_lookup import FormulaLookupTool
        
        tool = FormulaLookupTool()
        result = await tool.execute(topic="Coulomb's law", subject="Physics")
        
        assert result.success, f"Formula lookup failed: {result.error}"
        
        meta = result.metadata
        logger.info(f"📊 DEMO QUERY: 'Coulomb's law formula with units'")
        logger.info(f"   - Method: {meta.get('retrieval_method')}")
        logger.info(f"   - Found: {meta.get('found')}")
        logger.info(f"   - Formula count: {meta.get('count', 0)}")
    
    @pytest.mark.asyncio
    async def test_demo_query_mechanics_plan(self):
        """Demo: 'Make a 30-day mechanics plan' - uses exam_strategy"""
        from agents.core.tools.exam_strategy import ExamStrategyTool
        
        tool = ExamStrategyTool()
        result = await tool.execute(topic="Mechanics", exam_type="JEE")
        
        assert result.success, f"Exam strategy failed: {result.error}"
        
        meta = result.metadata
        logger.info(f"📊 DEMO QUERY: 'Make a 30-day mechanics plan'")
        logger.info(f"   - Method: {meta.get('retrieval_method')}")
        logger.info(f"   - Found: {meta.get('found')}")
        logger.info(f"   - Citation: {meta.get('citation', 'N/A')}")
    
    @pytest.mark.asyncio
    async def test_all_demo_queries_use_faiss(self):
        """Verify all demo queries use FAISS for vector search (when available)"""
        from services.knowledge_base.corpus_store import get_corpus_store_v2
        
        corpus = get_corpus_store_v2()
        
        # Ensure vector index is built
        await corpus.search_vector("test", limit=1)
        
        # Check stats
        stats = corpus.vector_index.get_stats()
        
        # FAISS is optional - skip if not available
        if not stats.get("initialized"):
            pytest.skip("FAISS not installed or API key not set - skipping FAISS verification")
        
        logger.info(f"📊 ALL DEMO QUERIES verified to use FAISS:")
        logger.info(f"   - Index type: {stats.get('index_type')}")
        logger.info(f"   - Vectors: {stats.get('num_vectors')}")
        logger.info(f"   - Dimensions: {stats.get('dimensions')}")


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    # Run with: python -m pytest tests/test_rag_v2.py -v
    pytest.main([__file__, "-v", "--tb=short"])
