"""
📚 Corpus Store v2 - True RAG with Document Linkage
====================================================

Implements real RAG with:
1. Raw document storage (data/corpus/raw/)
2. Chunk store with doc_id linkage (data/corpus/chunks/)
3. Dataset versioning with manifest.json
4. Traceable citations (chunk_id → doc_id → raw file)

This replaces the hardcoded Python content with file-based corpus.
"""

import logging
import json
import hashlib
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# DATA DIRECTORIES
# =============================================================================
CORPUS_ROOT = Path(__file__).parent.parent.parent / "data" / "corpus"
RAW_DIR = CORPUS_ROOT / "raw"
CHUNKS_DIR = CORPUS_ROOT / "chunks"
MANIFEST_FILE = CORPUS_ROOT / "manifest.json"
CHUNKS_FILE = CHUNKS_DIR / "chunks.json"
CHUNK_INDEX_FILE = CHUNKS_DIR / "chunk_index.json"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CorpusManifest:
    """
    Dataset version manifest - tracks corpus state for reproducibility.
    
    Generated on every ingestion run.
    """
    dataset_version: str          # Timestamp-based version
    content_hash: str             # SHA256 of all chunk content
    num_documents: int            # Total raw documents
    num_chunks: int               # Total chunks
    avg_chunk_len: float          # Average chunk length
    total_tokens_estimate: int    # Rough token count
    sources: List[Dict[str, Any]] # [{source_id, doc_count, attribution}]
    created_at: str               # ISO timestamp
    updated_at: str               # ISO timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CorpusManifest':
        return cls(**data)


@dataclass
class RawDocument:
    """
    Raw document metadata (stored alongside .md/.txt files in raw/).
    """
    doc_id: str                   # Unique document ID
    filename: str                 # File in raw/ directory
    title: str                    # Document title
    source_id: str                # Source registry reference
    subject: str                  # Physics/Chemistry/Math/Biology
    class_level: str              # "11", "12", "JEE", "NEET"
    chapter: str                  # Chapter name
    attribution: str              # License/attribution
    fetched_at: str               # When content was obtained
    content_hash: str             # SHA256 of raw content
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RawDocument':
        return cls(**data)


@dataclass  
class ChunkV2:
    """
    Chunk with full document linkage for traceable citations.
    """
    chunk_id: str                 # Stable hash-based ID
    doc_id: str                   # Links to RawDocument
    section: str                  # "Chapter 5 > Newton's Laws > First Law"
    text: str                     # Chunk content
    start_char: int               # Position in raw doc
    end_char: int                 # Position in raw doc
    
    # Metadata for retrieval
    subject: str
    topic: str
    subtopic: str
    class_level: str
    keywords: List[str]
    formulas: List[str]
    key_concepts: List[str]
    exam_relevance: Dict[str, int]  # {"JEE": 5, "NEET": 4}
    
    # Citation info
    source_citation: str          # "NCERT Class 11 Physics Ch. 5, Section 5.2"
    page_reference: str           # "Page 98-99" if available
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChunkV2':
        return cls(**data)
    
    def get_full_citation(self) -> str:
        """Generate full auditable citation"""
        return f"{self.source_citation} [chunk:{self.chunk_id[:8]}, doc:{self.doc_id[:8]}]"


# =============================================================================
# CHUNK INDEX (Keyword + Topic based, upgraded from v1)
# =============================================================================

@dataclass
class ChunkIndex:
    """
    Inverted index for keyword and topic search.
    """
    keyword_index: Dict[str, List[str]] = field(default_factory=dict)  # keyword -> chunk_ids
    topic_index: Dict[str, List[str]] = field(default_factory=dict)    # topic -> chunk_ids
    subject_index: Dict[str, List[str]] = field(default_factory=dict)  # subject -> chunk_ids
    doc_index: Dict[str, List[str]] = field(default_factory=dict)      # doc_id -> chunk_ids
    
    def add_chunk(self, chunk: ChunkV2):
        """Index a chunk"""
        cid = chunk.chunk_id
        
        # Keyword index
        for kw in chunk.keywords:
            kw_lower = kw.lower()
            if kw_lower not in self.keyword_index:
                self.keyword_index[kw_lower] = []
            if cid not in self.keyword_index[kw_lower]:
                self.keyword_index[kw_lower].append(cid)
        
        # Topic index
        topic_lower = chunk.topic.lower()
        if topic_lower not in self.topic_index:
            self.topic_index[topic_lower] = []
        if cid not in self.topic_index[topic_lower]:
            self.topic_index[topic_lower].append(cid)
        
        # Subject index
        subj_lower = chunk.subject.lower()
        if subj_lower not in self.subject_index:
            self.subject_index[subj_lower] = []
        if cid not in self.subject_index[subj_lower]:
            self.subject_index[subj_lower].append(cid)
        
        # Doc index
        if chunk.doc_id not in self.doc_index:
            self.doc_index[chunk.doc_id] = []
        if cid not in self.doc_index[chunk.doc_id]:
            self.doc_index[chunk.doc_id].append(cid)
    
    def to_dict(self) -> Dict:
        return {
            "keyword_index": self.keyword_index,
            "topic_index": self.topic_index,
            "subject_index": self.subject_index,
            "doc_index": self.doc_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChunkIndex':
        return cls(
            keyword_index=data.get("keyword_index", {}),
            topic_index=data.get("topic_index", {}),
            subject_index=data.get("subject_index", {}),
            doc_index=data.get("doc_index", {})
        )


# =============================================================================
# BM25 INDEX (Lexical Search with TF-IDF scoring)
# =============================================================================

class BM25Index:
    """
    BM25 index for lexical search with proper TF-IDF scoring.
    
    Implements Okapi BM25 algorithm without external dependencies.
    """
    
    # BM25 parameters
    K1 = 1.5  # Term frequency saturation
    B = 0.75  # Length normalization
    
    def __init__(self):
        self.doc_count = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: Dict[str, int] = {}  # chunk_id -> token count
        self.term_freqs: Dict[str, Dict[str, int]] = {}  # term -> {chunk_id -> freq}
        self.doc_freqs: Dict[str, int] = {}  # term -> num docs containing term
        self.chunk_ids: List[str] = []
        self._initialized = False
    
    def build_index(self, chunks: Dict[str, 'ChunkV2']):
        """Build BM25 index from chunks"""
        self.chunk_ids = list(chunks.keys())
        self.doc_count = len(chunks)
        
        if self.doc_count == 0:
            return
        
        total_length = 0
        
        for chunk_id, chunk in chunks.items():
            # Tokenize
            tokens = self._tokenize(chunk.text)
            doc_len = len(tokens)
            self.doc_lengths[chunk_id] = doc_len
            total_length += doc_len
            
            # Count term frequencies
            term_counts: Dict[str, int] = {}
            for token in tokens:
                term_counts[token] = term_counts.get(token, 0) + 1
            
            # Update indices
            for term, freq in term_counts.items():
                if term not in self.term_freqs:
                    self.term_freqs[term] = {}
                    self.doc_freqs[term] = 0
                
                self.term_freqs[term][chunk_id] = freq
                self.doc_freqs[term] += 1
        
        self.avg_doc_len = total_length / self.doc_count if self.doc_count > 0 else 0
        self._initialized = True
        
        logger.info(f"📊 BM25 index built: {self.doc_count} docs, {len(self.term_freqs)} terms")
    
    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """
        Search using BM25 scoring.
        
        Returns list of (chunk_id, score) tuples.
        """
        if not self._initialized or self.doc_count == 0:
            return []
        
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        scores: Dict[str, float] = {}
        
        for term in query_tokens:
            if term not in self.term_freqs:
                continue
            
            # IDF calculation
            df = self.doc_freqs.get(term, 0)
            idf = self._calculate_idf(df)
            
            # Score each document containing this term
            for chunk_id, tf in self.term_freqs[term].items():
                doc_len = self.doc_lengths.get(chunk_id, 1)
                
                # BM25 term score
                numerator = tf * (self.K1 + 1)
                denominator = tf + self.K1 * (1 - self.B + self.B * (doc_len / self.avg_doc_len))
                term_score = idf * (numerator / denominator)
                
                scores[chunk_id] = scores.get(chunk_id, 0) + term_score
        
        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms"""
        # Simple tokenization: lowercase, split on non-alphanumeric
        text_lower = text.lower()
        tokens = re.findall(r'\b[a-z]{2,}\b', text_lower)
        
        # Remove common stopwords
        stopwords = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
            'in', 'with', 'to', 'for', 'of', 'as', 'by', 'from', 'be', 'are',
            'was', 'were', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'it', 'its'
        }
        
        return [t for t in tokens if t not in stopwords]
    
    def _calculate_idf(self, doc_freq: int) -> float:
        """Calculate IDF score"""
        import math
        if doc_freq == 0:
            return 0
        return math.log((self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1)


# =============================================================================
# VECTOR INDEX (FAISS + SQLite - Production-Grade)
# =============================================================================

VECTORS_DIR = CORPUS_ROOT / "vectors"
FAISS_INDEX_FILE = VECTORS_DIR / "index.faiss"
SQLITE_META_FILE = VECTORS_DIR / "meta.sqlite"
VECTOR_MANIFEST_FILE = VECTORS_DIR / "vector_manifest.json"

# Legacy JSON file (kept for migration only)
VECTOR_INDEX_FILE = CHUNKS_DIR / "vector_index.json"


class VectorIndex:
    """
    Production-grade vector index using FAISS + SQLite.
    
    Architecture:
    - FAISS: Fast similarity search on dense vectors
    - SQLite: Metadata storage (chunk_id -> FAISS index position)
    - Manifest: Dataset versioning for idempotent rebuilds
    
    Features:
    - OpenAI embeddings (text-embedding-3-small, 1536D)
    - Manifest-based rebuild detection
    - Persistent storage in data/corpus/vectors/
    - Backward compatible interface
    """
    
    def __init__(self):
        self._faiss_index = None
        self._sqlite_conn = None
        self._embedding_service = None
        self._initialized = False
        self._chunk_ids: List[str] = []  # Position -> chunk_id mapping
        self._dimensions = 1536  # OpenAI default
        self._manifest: Dict[str, Any] = {}
        self._stats = {
            "index_type": "faiss",
            "num_vectors": 0,
            "dimensions": 0,
            "last_query_time_ms": 0
        }
    
    async def _get_embedding_service(self):
        """Lazy load embedding service"""
        if self._embedding_service is None:
            try:
                from lightweight_embeddings import get_embedding_service, get_embedding_dimensions
                self._embedding_service = await get_embedding_service()
                self._dimensions = get_embedding_dimensions()
            except Exception as e:
                logger.error(f"Failed to load embedding service: {e}")
        return self._embedding_service
    
    def _ensure_directories(self):
        """Create vectors directory"""
        VECTORS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _init_sqlite(self):
        """Initialize SQLite metadata store"""
        import sqlite3
        
        self._sqlite_conn = sqlite3.connect(str(SQLITE_META_FILE))
        cursor = self._sqlite_conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunk_mapping (
                faiss_idx INTEGER PRIMARY KEY,
                chunk_id TEXT NOT NULL UNIQUE,
                doc_id TEXT,
                subject TEXT,
                section TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunk_id ON chunk_mapping(chunk_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_subject ON chunk_mapping(subject)
        """)
        
        self._sqlite_conn.commit()
        logger.debug("📊 SQLite metadata store initialized")
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load vector index manifest"""
        if VECTOR_MANIFEST_FILE.exists():
            try:
                with open(VECTOR_MANIFEST_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load vector manifest: {e}")
        return {}
    
    def _save_manifest(self, corpus_hash: str, dataset_version: str, num_vectors: int):
        """Save vector index manifest"""
        self._manifest = {
            "corpus_hash": corpus_hash,
            "dataset_version": dataset_version,
            "num_vectors": num_vectors,
            "dimensions": self._dimensions,
            "embedding_model": "text-embedding-3-small",
            "index_type": "faiss_flat_ip",
            "created_at": datetime.utcnow().isoformat(),
            "faiss_file": str(FAISS_INDEX_FILE),
            "sqlite_file": str(SQLITE_META_FILE)
        }
        
        with open(VECTOR_MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._manifest, f, indent=2)
        
        logger.info(f"💾 Vector manifest saved: {num_vectors} vectors, {self._dimensions}D")
    
    def _should_rebuild(self, corpus_hash: str, dataset_version: str) -> bool:
        """Check if index needs rebuilding based on manifest"""
        manifest = self._load_manifest()
        
        if not manifest:
            logger.info("📊 No vector manifest found - will build new index")
            return True
        
        if not FAISS_INDEX_FILE.exists() or not SQLITE_META_FILE.exists():
            logger.info("📊 FAISS/SQLite files missing - will rebuild")
            return True
        
        if manifest.get("corpus_hash") != corpus_hash:
            logger.info(f"📊 Corpus hash changed: {manifest.get('corpus_hash')[:8]} -> {corpus_hash[:8]}")
            return True
        
        if manifest.get("dataset_version") != dataset_version:
            logger.info(f"📊 Dataset version changed: {manifest.get('dataset_version')[:10]} -> {dataset_version[:10]}")
            return True
        
        logger.info(f"📊 Vector index up-to-date: {manifest.get('num_vectors')} vectors")
        return False
    
    async def build_index(
        self, 
        chunks: Dict[str, 'ChunkV2'], 
        force_rebuild: bool = False,
        corpus_hash: str = "",
        dataset_version: str = ""
    ):
        """
        Build FAISS vector index from chunks.
        
        Args:
            chunks: Dictionary of chunk_id -> ChunkV2
            force_rebuild: Force rebuild even if manifest matches
            corpus_hash: Hash of corpus content for versioning
            dataset_version: Dataset version string
        """
        import numpy as np
        
        self._ensure_directories()
        
        # Check if rebuild needed
        if not force_rebuild and not self._should_rebuild(corpus_hash, dataset_version):
            # Load existing index
            if await self._load_index():
                return
        
        logger.info(f"🔧 Building FAISS vector index for {len(chunks)} chunks...")
        
        # Get embedding service
        service = await self._get_embedding_service()
        if service is None:
            logger.error("❌ Embedding service not available")
            return
        
        self._dimensions = service.dimensions
        
        # Initialize FAISS index (Inner Product for normalized vectors = cosine similarity)
        try:
            import faiss
            self._faiss_index = faiss.IndexFlatIP(self._dimensions)
            logger.info(f"📊 FAISS IndexFlatIP created: {self._dimensions}D")
        except ImportError:
            logger.error("❌ FAISS not installed. Run: pip install faiss-cpu")
            return
        
        # Initialize SQLite
        self._init_sqlite()
        cursor = self._sqlite_conn.cursor()
        cursor.execute("DELETE FROM chunk_mapping")  # Clear existing
        
        # Process chunks in batches
        self._chunk_ids = list(chunks.keys())
        batch_size = 50  # OpenAI embedding batch size
        all_embeddings = []
        
        for i in range(0, len(self._chunk_ids), batch_size):
            batch_ids = self._chunk_ids[i:i + batch_size]
            batch_texts = [chunks[cid].text[:1000] for cid in batch_ids]  # First 1000 chars
            
            try:
                batch_embeddings = await service.create_embeddings(batch_texts)
                all_embeddings.extend(batch_embeddings)
                
                # Store metadata in SQLite
                for j, chunk_id in enumerate(batch_ids):
                    chunk = chunks[chunk_id]
                    faiss_idx = i + j
                    cursor.execute(
                        "INSERT INTO chunk_mapping (faiss_idx, chunk_id, doc_id, subject, section) VALUES (?, ?, ?, ?, ?)",
                        (faiss_idx, chunk_id, chunk.doc_id, chunk.subject, chunk.section)
                    )
                
                logger.debug(f"📊 Embedded batch {i//batch_size + 1}: {len(batch_ids)} chunks")
                
            except Exception as e:
                logger.error(f"❌ Embedding batch error: {e}")
                # Create fallback embeddings
                for text in batch_texts:
                    all_embeddings.append(self._create_fallback_embedding(text))
        
        # Normalize and add to FAISS
        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        
        # Normalize for cosine similarity (FAISS IP on normalized vectors = cosine)
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        embeddings_array = embeddings_array / norms
        
        self._faiss_index.add(embeddings_array)
        self._sqlite_conn.commit()
        
        # Save to disk
        import faiss
        faiss.write_index(self._faiss_index, str(FAISS_INDEX_FILE))
        
        self._save_manifest(corpus_hash, dataset_version, len(self._chunk_ids))
        
        self._initialized = True
        self._stats["num_vectors"] = len(self._chunk_ids)
        self._stats["dimensions"] = self._dimensions
        
        logger.info(f"✅ FAISS index built: {len(self._chunk_ids)} vectors, {self._dimensions}D")
        
        # Log embedding service stats
        if hasattr(service, 'get_stats'):
            stats = service.get_stats()
            logger.info(f"📊 Embedding stats: {stats}")
    
    async def _load_index(self) -> bool:
        """Load existing FAISS index and SQLite metadata"""
        try:
            import faiss
            import sqlite3
            
            if not FAISS_INDEX_FILE.exists() or not SQLITE_META_FILE.exists():
                return False
            
            # Load FAISS index
            self._faiss_index = faiss.read_index(str(FAISS_INDEX_FILE))
            self._dimensions = self._faiss_index.d
            
            # Load SQLite metadata
            self._sqlite_conn = sqlite3.connect(str(SQLITE_META_FILE))
            cursor = self._sqlite_conn.cursor()
            
            # Load chunk_ids in order
            cursor.execute("SELECT chunk_id FROM chunk_mapping ORDER BY faiss_idx")
            self._chunk_ids = [row[0] for row in cursor.fetchall()]
            
            self._initialized = True
            self._stats["num_vectors"] = len(self._chunk_ids)
            self._stats["dimensions"] = self._dimensions
            
            logger.info(f"📊 FAISS index loaded: {len(self._chunk_ids)} vectors, {self._dimensions}D")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load FAISS index: {e}")
            return False
    
    async def search(self, query: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """
        Search using FAISS vector similarity.
        
        Returns list of (chunk_id, score) tuples.
        Score is cosine similarity (0-1 range after normalization).
        """
        import time
        start_time = time.time()
        
        if not self._initialized or self._faiss_index is None:
            logger.warning("⚠️ Vector index not initialized")
            return []
        
        try:
            import numpy as np
            
            # Get query embedding
            service = await self._get_embedding_service()
            if service is None:
                query_embedding = self._create_fallback_embedding(query)
            else:
                query_embedding = await service.create_single_embedding(query)
            
            # Normalize query vector
            query_array = np.array([query_embedding], dtype=np.float32)
            norm = np.linalg.norm(query_array)
            if norm > 0:
                query_array = query_array / norm
            
            # Search FAISS
            distances, indices = self._faiss_index.search(query_array, min(top_k, len(self._chunk_ids)))
            
            # Convert to (chunk_id, score) tuples
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self._chunk_ids):
                    chunk_id = self._chunk_ids[idx]
                    # Inner product of normalized vectors = cosine similarity
                    # Normalize to 0-1 range (cosine can be -1 to 1)
                    score = (dist + 1) / 2
                    results.append((chunk_id, float(score)))
            
            elapsed_ms = (time.time() - start_time) * 1000
            self._stats["last_query_time_ms"] = elapsed_ms
            
            logger.debug(f"🔍 FAISS search: '{query[:30]}...' → {len(results)} results in {elapsed_ms:.1f}ms")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ FAISS search error: {e}")
            return []
    
    def _create_fallback_embedding(self, text: str) -> List[float]:
        """Create hash-based fallback embedding"""
        text = text.lower().strip()
        embeddings = []
        for i in range(self._dimensions):
            seed_text = f"{text}_{i}"
            hash_value = hashlib.md5(seed_text.encode()).hexdigest()
            numeric_value = int(hash_value[:8], 16) / (16**8) * 2 - 1
            embeddings.append(numeric_value)
        return embeddings
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector index statistics"""
        return {
            **self._stats,
            "initialized": self._initialized,
            "manifest": self._manifest
        }
    
    def close(self):
        """Close SQLite connection"""
        if self._sqlite_conn:
            self._sqlite_conn.close()
            self._sqlite_conn = None


class _FallbackEmbeddingService:
    """Fallback embedding service when main service unavailable"""
    
    def __init__(self):
        self.dimensions = 1536
    
    def _create_simple_embedding(self, text: str, dimension: int = 1536) -> List[float]:
        text = text.lower().strip()
        embeddings = []
        for i in range(dimension):
            seed_text = f"{text}_{i}"
            hash_value = hashlib.md5(seed_text.encode()).hexdigest()
            numeric_value = int(hash_value[:8], 16) / (16**8) * 2 - 1
            embeddings.append(numeric_value)
        return embeddings


# =============================================================================
# RERANKER (LLM-based scoring for precision)
# =============================================================================

class LLMReranker:
    """
    LLM-based reranker for improving retrieval precision.
    
    Uses LLM to score relevance of retrieved chunks to the query.
    This is computationally expensive, so use only on top-N candidates.
    """
    
    def __init__(self, max_candidates: int = 10):
        self.max_candidates = max_candidates
        self._llm_service = None
    
    async def _get_llm_service(self):
        """Lazy load LLM service"""
        if self._llm_service is None:
            try:
                from services.llm_service import LLMService
                self._llm_service = LLMService()
            except Exception as e:
                logger.error(f"Failed to load LLM service for reranking: {e}")
        return self._llm_service
    
    async def rerank(
        self,
        query: str,
        candidates: List[Tuple['ChunkV2', float, str]],
        top_k: int = 5
    ) -> List[Tuple['ChunkV2', float, str]]:
        """
        Rerank candidates using LLM scoring.
        
        Args:
            query: Search query
            candidates: List of (chunk, score, retrieval_type) tuples
            top_k: Number of results to return
            
        Returns:
            Reranked list of (chunk, score, retrieval_type) tuples
        """
        if not candidates:
            return []
        
        # Limit candidates for efficiency
        candidates = candidates[:self.max_candidates]
        
        llm = await self._get_llm_service()
        
        if llm is None:
            logger.warning("LLM service not available, using heuristic reranking")
            return self._heuristic_rerank(query, candidates, top_k)
        
        try:
            # Build reranking prompt
            reranked = await self._llm_rerank(llm, query, candidates)
            return reranked[:top_k]
        except Exception as e:
            logger.error(f"LLM reranking failed: {e}")
            return self._heuristic_rerank(query, candidates, top_k)
    
    async def _llm_rerank(
        self,
        llm,
        query: str,
        candidates: List[Tuple['ChunkV2', float, str]]
    ) -> List[Tuple['ChunkV2', float, str]]:
        """Use LLM to score relevance"""
        # Format candidates for LLM
        candidate_texts = []
        for i, (chunk, _, _) in enumerate(candidates):
            # Truncate to first 200 chars
            preview = chunk.text[:200].replace('\n', ' ')
            candidate_texts.append(f"[{i}] {chunk.topic}: {preview}...")
        
        prompt = f"""Rate the relevance of each document to the query on a scale of 0-10.

Query: "{query}"

Documents:
{chr(10).join(candidate_texts)}

Return ONLY a JSON array of scores in order, e.g., [8, 5, 9, 3, ...]
No explanation needed."""

        try:
            response = await llm.generate(
                prompt=prompt,
                max_tokens=100,
                temperature=0.0
            )
            
            # Parse scores
            import json as json_module
            scores_text = response.strip()
            # Extract JSON array
            if '[' in scores_text and ']' in scores_text:
                start = scores_text.index('[')
                end = scores_text.rindex(']') + 1
                scores = json_module.loads(scores_text[start:end])
            else:
                raise ValueError("No JSON array in response")
            
            # Apply scores
            reranked = []
            for i, (chunk, orig_score, ret_type) in enumerate(candidates):
                if i < len(scores):
                    # Combine original score with LLM score
                    llm_score = float(scores[i]) / 10.0
                    combined = 0.3 * orig_score + 0.7 * llm_score
                    reranked.append((chunk, combined, 'reranked'))
                else:
                    reranked.append((chunk, orig_score * 0.5, ret_type))
            
            # Sort by combined score
            reranked.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"🔄 LLM reranked {len(reranked)} candidates")
            return reranked
            
        except Exception as e:
            logger.error(f"LLM reranking parse error: {e}")
            return self._heuristic_rerank(query, candidates, len(candidates))
    
    def _heuristic_rerank(
        self,
        query: str,
        candidates: List[Tuple['ChunkV2', float, str]],
        top_k: int
    ) -> List[Tuple['ChunkV2', float, str]]:
        """
        Heuristic reranking when LLM is not available.
        
        Boosts scores based on:
        - Query terms in topic
        - Query terms in content
        - Keyword overlap
        """
        query_terms = set(query.lower().split())
        
        reranked = []
        for chunk, score, ret_type in candidates:
            boost = 0.0
            
            # Topic match boost
            topic_terms = set(chunk.topic.lower().split())
            topic_overlap = len(query_terms & topic_terms)
            boost += topic_overlap * 0.1
            
            # Content term boost
            content_lower = chunk.text.lower()
            for term in query_terms:
                if term in content_lower:
                    boost += 0.05
            
            # Keyword overlap boost
            chunk_keywords = set(kw.lower() for kw in chunk.keywords)
            keyword_overlap = len(query_terms & chunk_keywords)
            boost += keyword_overlap * 0.15
            
            new_score = min(1.0, score + boost)
            reranked.append((chunk, new_score, ret_type))
        
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:top_k]


# =============================================================================
# CORPUS STORE V2
# =============================================================================

class CorpusStoreV2:
    """
    True RAG Corpus Store with:
    - Raw document storage
    - Chunk store with doc linkage
    - Traceable citations
    - Dataset versioning
    - BM25 index (lexical search)
    - Vector index (semantic search)
    - Hybrid retrieval (BM25 + Vector merge)
    - LLM Reranker (precision improvement)
    """
    
    def __init__(self, auto_init: bool = True):
        self.documents: Dict[str, RawDocument] = {}
        self.chunks: Dict[str, ChunkV2] = {}
        self.index: ChunkIndex = ChunkIndex()
        self.bm25_index: BM25Index = BM25Index()
        self.vector_index: VectorIndex = VectorIndex()
        self.reranker: LLMReranker = LLMReranker()
        self.manifest: Optional[CorpusManifest] = None
        self._vector_index_built = False
        
        if auto_init:
            self._ensure_directories()
            self._load_or_initialize()
    
    def _ensure_directories(self):
        """Create corpus directories if they don't exist"""
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Corpus directories ready: {CORPUS_ROOT}")
    
    def _load_or_initialize(self):
        """Load existing corpus or initialize with seed data"""
        if CHUNKS_FILE.exists() and MANIFEST_FILE.exists():
            self._load_from_files()
        else:
            logger.info("📚 No existing corpus found, initializing seed corpus...")
            self._initialize_seed_corpus()
    
    def _load_from_files(self):
        """Load corpus from JSON files"""
        try:
            # Load manifest
            with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
                self.manifest = CorpusManifest.from_dict(json.load(f))
            
            # Load chunks
            with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for chunk_data in data.get("chunks", []):
                    chunk = ChunkV2.from_dict(chunk_data)
                    self.chunks[chunk.chunk_id] = chunk
                for doc_data in data.get("documents", []):
                    doc = RawDocument.from_dict(doc_data)
                    self.documents[doc.doc_id] = doc
            
            # Load keyword index
            if CHUNK_INDEX_FILE.exists():
                with open(CHUNK_INDEX_FILE, 'r', encoding='utf-8') as f:
                    self.index = ChunkIndex.from_dict(json.load(f))
            else:
                # Rebuild index
                for chunk in self.chunks.values():
                    self.index.add_chunk(chunk)
            
            # Build BM25 index (fast, always rebuild)
            self.bm25_index.build_index(self.chunks)
            
            logger.info(f"📚 Loaded corpus: {len(self.documents)} docs, {len(self.chunks)} chunks, v{self.manifest.dataset_version[:10]}")
            
        except Exception as e:
            logger.error(f"Failed to load corpus: {e}, reinitializing...")
            self._initialize_seed_corpus()
    
    def _initialize_seed_corpus(self):
        """Create seed corpus from raw documents"""
        # Create raw documents
        self._create_seed_raw_documents()
        
        # Process raw docs into chunks
        self._process_raw_documents()
        
        # Build keyword index
        for chunk in self.chunks.values():
            self.index.add_chunk(chunk)
        
        # Build BM25 index
        self.bm25_index.build_index(self.chunks)
        
        # Generate manifest
        self._generate_manifest()
        
        # Persist
        self._save_to_files()
        
        logger.info(f"📚 Initialized seed corpus: {len(self.documents)} docs, {len(self.chunks)} chunks")
    
    def _create_seed_raw_documents(self):
        """Create seed raw documents in data/corpus/raw/"""
        seed_docs = self._get_seed_documents()
        
        for doc_meta, content in seed_docs:
            # Write raw content file
            filepath = RAW_DIR / doc_meta["filename"]
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create document record
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            doc = RawDocument(
                doc_id=doc_meta["doc_id"],
                filename=doc_meta["filename"],
                title=doc_meta["title"],
                source_id=doc_meta["source_id"],
                subject=doc_meta["subject"],
                class_level=doc_meta["class_level"],
                chapter=doc_meta["chapter"],
                attribution=doc_meta["attribution"],
                fetched_at=datetime.utcnow().isoformat(),
                content_hash=content_hash
            )
            self.documents[doc.doc_id] = doc
        
        logger.info(f"📄 Created {len(self.documents)} raw documents in {RAW_DIR}")
    
    def _process_raw_documents(self):
        """Process raw documents into chunks"""
        for doc in self.documents.values():
            filepath = RAW_DIR / doc.filename
            if not filepath.exists():
                logger.warning(f"Raw file not found: {filepath}")
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse and chunk the document
            chunks = self._chunk_document(doc, content)
            for chunk in chunks:
                self.chunks[chunk.chunk_id] = chunk
        
        logger.info(f"🔪 Created {len(self.chunks)} chunks from {len(self.documents)} documents")
    
    def _chunk_document(self, doc: RawDocument, content: str) -> List[ChunkV2]:
        """
        Chunk a document by sections (marked with ##).
        
        Each chunk gets a stable ID and full metadata.
        """
        chunks = []
        
        # Split by section headers (## Header)
        sections = re.split(r'\n(?=## )', content)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Extract section title
            lines = section.strip().split('\n')
            if lines[0].startswith('## '):
                section_title = lines[0][3:].strip()
                section_content = '\n'.join(lines[1:]).strip()
            elif lines[0].startswith('# '):
                section_title = lines[0][2:].strip()
                section_content = '\n'.join(lines[1:]).strip()
            else:
                section_title = f"Section {i+1}"
                section_content = section.strip()
            
            if not section_content or len(section_content) < 50:
                continue
            
            # Extract metadata from content
            metadata = self._extract_chunk_metadata(section_content, doc, section_title)
            
            # Generate stable chunk ID
            chunk_id = self._generate_chunk_id(doc.doc_id, section_title, section_content[:100])
            
            # Find position in original
            start_char = content.find(section)
            end_char = start_char + len(section) if start_char >= 0 else 0
            
            chunk = ChunkV2(
                chunk_id=chunk_id,
                doc_id=doc.doc_id,
                section=f"{doc.chapter} > {section_title}",
                text=section_content,
                start_char=start_char,
                end_char=end_char,
                subject=doc.subject,
                topic=metadata.get("topic", section_title),
                subtopic=metadata.get("subtopic", ""),
                class_level=doc.class_level,
                keywords=metadata.get("keywords", []),
                formulas=metadata.get("formulas", []),
                key_concepts=metadata.get("key_concepts", []),
                exam_relevance=metadata.get("exam_relevance", {}),
                source_citation=f"{doc.title}, {section_title}",
                page_reference=""
            )
            chunks.append(chunk)
        
        return chunks
    
    def _extract_chunk_metadata(self, content: str, doc: RawDocument, section_title: str) -> Dict:
        """Extract keywords, formulas, concepts from chunk content"""
        content_lower = content.lower()
        
        # Extract formulas (LaTeX-like patterns and common physics/math expressions)
        formula_patterns = [
            r'[A-Za-z]\s*=\s*[^,\n]+',  # F = ma style
            r'\$[^$]+\$',                # LaTeX inline
            r'\\[a-z]+\{[^}]+\}',        # LaTeX commands
        ]
        formulas = []
        for pattern in formula_patterns:
            matches = re.findall(pattern, content)
            formulas.extend([m.strip() for m in matches[:5]])  # Limit to 5
        
        # Extract keywords based on subject
        keywords = []
        
        # Physics keywords
        physics_kw = ["force", "energy", "momentum", "velocity", "acceleration", "mass", 
                      "work", "power", "potential", "kinetic", "gravity", "friction",
                      "electric", "magnetic", "charge", "current", "voltage", "resistance",
                      "wave", "frequency", "wavelength", "amplitude", "photon", "electron"]
        
        # Chemistry keywords  
        chemistry_kw = ["atom", "molecule", "bond", "reaction", "equilibrium", "acid", "base",
                        "pH", "mole", "concentration", "oxidation", "reduction", "organic",
                        "inorganic", "catalyst", "entropy", "enthalpy", "gibbs"]
        
        # Math keywords
        math_kw = ["derivative", "integral", "function", "equation", "polynomial", "matrix",
                   "vector", "limit", "calculus", "algebra", "trigonometry", "geometry",
                   "permutation", "combination", "probability", "sequence", "series"]
        
        # Biology keywords
        biology_kw = ["cell", "DNA", "RNA", "protein", "enzyme", "photosynthesis", "respiration",
                      "mitosis", "meiosis", "chromosome", "gene", "evolution", "ecology",
                      "organism", "species", "metabolism", "hormone"]
        
        all_keywords = physics_kw + chemistry_kw + math_kw + biology_kw
        for kw in all_keywords:
            if kw in content_lower:
                keywords.append(kw)
        
        # Add section title words as keywords
        for word in section_title.lower().split():
            if len(word) > 3 and word not in keywords:
                keywords.append(word)
        
        # Determine topic from section title
        topic = section_title
        subtopic = ""
        if " > " in section_title:
            parts = section_title.split(" > ")
            topic = parts[0]
            subtopic = parts[-1] if len(parts) > 1 else ""
        
        # Exam relevance based on subject
        exam_relevance = {}
        if doc.subject.lower() == "physics":
            exam_relevance = {"JEE": 5, "NEET": 4}
        elif doc.subject.lower() == "chemistry":
            exam_relevance = {"JEE": 5, "NEET": 5}
        elif doc.subject.lower() == "biology":
            exam_relevance = {"JEE": 1, "NEET": 5}
        elif doc.subject.lower() == "mathematics":
            exam_relevance = {"JEE": 5, "NEET": 2}
        
        return {
            "topic": topic,
            "subtopic": subtopic,
            "keywords": keywords[:15],  # Limit
            "formulas": formulas[:5],
            "key_concepts": keywords[:5],
            "exam_relevance": exam_relevance
        }
    
    def _generate_chunk_id(self, doc_id: str, section: str, content_preview: str) -> str:
        """Generate stable chunk ID from content"""
        hash_input = f"{doc_id}:{section}:{content_preview}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _generate_manifest(self):
        """Generate corpus manifest"""
        # Calculate content hash
        all_content = "".join(c.text for c in self.chunks.values())
        content_hash = hashlib.sha256(all_content.encode()).hexdigest()[:16]
        
        # Calculate stats
        chunk_lengths = [len(c.text) for c in self.chunks.values()]
        avg_chunk_len = sum(chunk_lengths) / len(chunk_lengths) if chunk_lengths else 0
        total_tokens = sum(chunk_lengths) // 4  # Rough estimate
        
        # Group by source
        sources = []
        source_counts: Dict[str, int] = {}
        for doc in self.documents.values():
            if doc.source_id not in source_counts:
                source_counts[doc.source_id] = 0
            source_counts[doc.source_id] += 1
        
        for source_id, count in source_counts.items():
            doc = next((d for d in self.documents.values() if d.source_id == source_id), None)
            sources.append({
                "source_id": source_id,
                "doc_count": count,
                "attribution": doc.attribution if doc else "Unknown"
            })
        
        now = datetime.utcnow().isoformat()
        self.manifest = CorpusManifest(
            dataset_version=now,
            content_hash=content_hash,
            num_documents=len(self.documents),
            num_chunks=len(self.chunks),
            avg_chunk_len=avg_chunk_len,
            total_tokens_estimate=total_tokens,
            sources=sources,
            created_at=now,
            updated_at=now
        )
    
    def _save_to_files(self):
        """Persist corpus to JSON files"""
        # Save chunks + documents
        with open(CHUNKS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "chunks": [c.to_dict() for c in self.chunks.values()],
                "documents": [d.to_dict() for d in self.documents.values()],
                "chunk_count": len(self.chunks),
                "doc_count": len(self.documents)
            }, f, indent=2)
        
        # Save index
        with open(CHUNK_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.index.to_dict(), f, indent=2)
        
        # Save manifest
        with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.manifest.to_dict(), f, indent=2)
        
        logger.info(f"💾 Saved corpus: {CHUNKS_FILE}")
    
    # =========================================================================
    # RETRIEVAL METHODS
    # =========================================================================
    
    def search_by_keywords(
        self,
        keywords: List[str],
        subject: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[ChunkV2, float]]:
        """
        Search chunks by keywords with scoring.
        
        Returns list of (chunk, score) tuples.
        """
        scores: Dict[str, float] = {}
        
        for keyword in keywords:
            kw_lower = keyword.lower()
            
            # Direct keyword match
            matching_ids = self.index.keyword_index.get(kw_lower, [])
            for cid in matching_ids:
                scores[cid] = scores.get(cid, 0) + 2.0
            
            # Partial match
            for indexed_kw, chunk_ids in self.index.keyword_index.items():
                if kw_lower in indexed_kw or indexed_kw in kw_lower:
                    for cid in chunk_ids:
                        scores[cid] = scores.get(cid, 0) + 1.0
        
        # Filter by subject
        if subject:
            subj_lower = subject.lower()
            subj_chunks = set(self.index.subject_index.get(subj_lower, []))
            scores = {k: v for k, v in scores.items() if k in subj_chunks}
        
        # Sort and return
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        results = []
        for cid in sorted_ids[:limit]:
            if cid in self.chunks:
                chunk = self.chunks[cid]
                score = scores[cid] / (len(keywords) * 2) if keywords else 0  # Normalize
                results.append((chunk, min(1.0, score)))
        
        return results
    
    def search_by_topic(
        self,
        topic: str,
        subject: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[ChunkV2, float]]:
        """Search chunks by topic"""
        topic_lower = topic.lower()
        matching_ids = []
        
        for indexed_topic, chunk_ids in self.index.topic_index.items():
            if topic_lower in indexed_topic or indexed_topic in topic_lower:
                matching_ids.extend(chunk_ids)
        
        results = []
        for cid in set(matching_ids)[:limit]:
            if cid in self.chunks:
                chunk = self.chunks[cid]
                if subject and chunk.subject.lower() != subject.lower():
                    continue
                # Score based on match quality
                score = 1.0 if topic_lower == chunk.topic.lower() else 0.7
                results.append((chunk, score))
        
        return results
    
    def search_bm25(
        self,
        query: str,
        subject: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[ChunkV2, float]]:
        """
        Search using BM25 (lexical/TF-IDF based).
        
        Returns list of (chunk, score) tuples with normalized scores.
        """
        bm25_results = self.bm25_index.search(query, top_k=limit * 2)
        
        if not bm25_results:
            return []
        
        # Normalize scores
        max_score = max(score for _, score in bm25_results) if bm25_results else 1.0
        
        results = []
        for chunk_id, score in bm25_results:
            if chunk_id not in self.chunks:
                continue
            
            chunk = self.chunks[chunk_id]
            
            # Filter by subject if specified
            if subject and chunk.subject.lower() != subject.lower():
                continue
            
            normalized_score = score / max_score if max_score > 0 else 0
            results.append((chunk, normalized_score))
            
            if len(results) >= limit:
                break
        
        return results
    
    async def search_vector(
        self,
        query: str,
        subject: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[ChunkV2, float]]:
        """
        Search using FAISS vector similarity (semantic).
        
        Returns list of (chunk, score) tuples.
        Uses production-grade FAISS index with OpenAI embeddings.
        """
        # Build vector index if not done (with manifest-based versioning)
        if not self._vector_index_built:
            corpus_hash = self.manifest.content_hash if self.manifest else ""
            dataset_version = self.manifest.dataset_version if self.manifest else ""
            
            await self.vector_index.build_index(
                self.chunks,
                corpus_hash=corpus_hash,
                dataset_version=dataset_version
            )
            self._vector_index_built = True
            
            # Log vector index stats
            stats = self.vector_index.get_stats()
            logger.info(f"📊 Vector index ready: {stats.get('num_vectors', 0)} vectors, "
                       f"{stats.get('dimensions', 0)}D, type={stats.get('index_type', 'unknown')}")
        
        vector_results = await self.vector_index.search(query, top_k=limit * 2)
        
        if not vector_results:
            return []
        
        results = []
        for chunk_id, score in vector_results:
            if chunk_id not in self.chunks:
                continue
            
            chunk = self.chunks[chunk_id]
            
            # Filter by subject if specified
            if subject and chunk.subject.lower() != subject.lower():
                continue
            
            # Score is already normalized from FAISS search
            results.append((chunk, score))
            
            if len(results) >= limit:
                break
        
        return results
    
    async def search_hybrid(
        self,
        query: str,
        subject: Optional[str] = None,
        limit: int = 10,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
        use_reranker: bool = False
    ) -> List[Tuple[ChunkV2, float, str]]:
        """
        Hybrid search combining BM25 and vector retrieval.
        
        Args:
            query: Search query
            subject: Optional subject filter
            limit: Max results to return
            bm25_weight: Weight for BM25 scores (0-1)
            vector_weight: Weight for vector scores (0-1)
            use_reranker: Whether to apply LLM reranking for precision
        
        Returns list of (chunk, score, retrieval_type) tuples.
        retrieval_type is one of: 'hybrid', 'bm25', 'vector', 'reranked'
        """
        # Get BM25 results
        bm25_results = self.search_bm25(query, subject, limit=limit * 2)
        bm25_scores = {chunk.chunk_id: score for chunk, score in bm25_results}
        
        # Get vector results
        vector_results = await self.search_vector(query, subject, limit=limit * 2)
        vector_scores = {chunk.chunk_id: score for chunk, score in vector_results}
        
        # Merge results with weighted scoring
        all_chunk_ids = set(bm25_scores.keys()) | set(vector_scores.keys())
        
        combined_scores: Dict[str, Tuple[float, str]] = {}
        
        for chunk_id in all_chunk_ids:
            bm25_score = bm25_scores.get(chunk_id, 0)
            vec_score = vector_scores.get(chunk_id, 0)
            
            # Determine retrieval type
            if chunk_id in bm25_scores and chunk_id in vector_scores:
                retrieval_type = 'hybrid'
                combined = bm25_weight * bm25_score + vector_weight * vec_score
            elif chunk_id in bm25_scores:
                retrieval_type = 'bm25'
                combined = bm25_weight * bm25_score
            else:
                retrieval_type = 'vector'
                combined = vector_weight * vec_score
            
            combined_scores[chunk_id] = (combined, retrieval_type)
        
        # Sort by combined score
        sorted_ids = sorted(combined_scores.keys(), key=lambda x: combined_scores[x][0], reverse=True)
        
        results = []
        for chunk_id in sorted_ids[:limit * 2]:  # Get more for reranking
            if chunk_id in self.chunks:
                chunk = self.chunks[chunk_id]
                score, retrieval_type = combined_scores[chunk_id]
                results.append((chunk, score, retrieval_type))
        
        # Apply reranker if enabled
        if use_reranker and len(results) > 0:
            try:
                results = await self.reranker.rerank(query, results, top_k=limit)
                logger.info(f"🔍 Hybrid+Rerank: '{query[:30]}...' → {len(results)} results")
            except Exception as e:
                logger.warning(f"Reranking failed: {e}")
                results = results[:limit]
        else:
            results = results[:limit]
        
        # Log with vector index type
        vec_stats = self.vector_index.get_stats()
        vec_type = vec_stats.get('index_type', 'unknown')
        logger.info(f"🔍 Hybrid search: '{query[:30]}...' → {len(results)} results "
                   f"(BM25: {len(bm25_results)}, Vector[{vec_type}]: {len(vector_results)}, Rerank: {use_reranker})")
        
        return results
    
    def get_chunk(self, chunk_id: str) -> Optional[ChunkV2]:
        """Get chunk by ID"""
        return self.chunks.get(chunk_id)
    
    def get_document(self, doc_id: str) -> Optional[RawDocument]:
        """Get document by ID"""
        return self.documents.get(doc_id)
    
    def get_chunk_with_citation(self, chunk_id: str) -> Optional[Dict]:
        """Get chunk with full citation trail"""
        chunk = self.chunks.get(chunk_id)
        if not chunk:
            return None
        
        doc = self.documents.get(chunk.doc_id)
        
        return {
            "chunk": chunk.to_dict(),
            "citation": chunk.get_full_citation(),
            "document": doc.to_dict() if doc else None,
            "raw_file": str(RAW_DIR / doc.filename) if doc else None
        }
    
    # =========================================================================
    # SEED DOCUMENTS
    # =========================================================================
    
    def _get_seed_documents(self) -> List[Tuple[Dict, str]]:
        """
        Generate seed documents for the corpus.
        
        Returns list of (metadata_dict, content_string) tuples.
        """
        return [
            # Physics - Mechanics
            (
                {
                    "doc_id": "ncert_phy11_ch5",
                    "filename": "ncert_physics_11_ch5_laws_of_motion.md",
                    "title": "NCERT Class 11 Physics Chapter 5",
                    "source_id": "ncert_physics_11",
                    "subject": "Physics",
                    "class_level": "11",
                    "chapter": "Laws of Motion",
                    "attribution": "NCERT, Govt. of India. Educational use only."
                },
                """# Laws of Motion
## Newton's First Law (Law of Inertia)

An object at rest stays at rest, and an object in motion continues in motion with the same speed and in the same direction unless acted upon by an external unbalanced force.

**Key Points:**
- Inertia is the property of matter that resists changes in motion
- Mass is a measure of inertia - more mass means more inertia
- This law defines the concept of force as something that changes motion

**Examples:**
1. A book on a table remains at rest until pushed
2. A rolling ball eventually stops due to friction (an external force)
3. Passengers lurch forward when a bus stops suddenly

**Formula:** No specific formula, but leads to the concept: F = 0 implies Δv = 0

## Newton's Second Law (F = ma)

The rate of change of momentum of a body is directly proportional to the applied force and takes place in the direction in which the force acts.

**Mathematical Form:**
F = ma = m(dv/dt) = dp/dt

where:
- F = Force (Newtons, N)
- m = Mass (kg)
- a = Acceleration (m/s²)
- p = Momentum (kg·m/s)

**Key Points:**
- Force and acceleration are vectors - direction matters
- 1 Newton = force needed to accelerate 1 kg by 1 m/s²
- Weight W = mg is a special case where a = g

**Problem Solving Approach:**
1. Draw free body diagram
2. Choose coordinate system
3. Write F = ma for each direction
4. Solve equations

## Newton's Third Law (Action-Reaction)

For every action, there is an equal and opposite reaction. When one body exerts a force on another body, the second body simultaneously exerts a force equal in magnitude and opposite in direction on the first body.

**Key Points:**
- Action and reaction act on DIFFERENT bodies
- They are equal in magnitude, opposite in direction
- They occur simultaneously
- They do NOT cancel out (because they act on different objects)

**Examples:**
1. When you push a wall, the wall pushes back on you
2. Rocket propulsion: gases push rocket up, rocket pushes gases down
3. Walking: you push ground backward, ground pushes you forward

**Common Misconception:** "Action and reaction cancel out" - FALSE! They act on different bodies.

## Friction

Friction is the force that opposes relative motion between surfaces in contact.

**Types of Friction:**
1. **Static Friction (fs):** Prevents motion from starting
   - fs ≤ μs × N (maximum value)
   - Always equal and opposite to applied force (up to maximum)

2. **Kinetic Friction (fk):** Opposes motion when object is moving
   - fk = μk × N (constant value)
   - μk < μs (kinetic coefficient is less than static)

**Formulas:**
- f = μN
- fs(max) = μs × N
- fk = μk × N

where:
- μ = coefficient of friction (dimensionless)
- N = Normal force (N)

**Factors Affecting Friction:**
- Nature of surfaces in contact
- Normal force pressing surfaces together
- NOT dependent on area of contact (for dry friction)
"""
            ),
            
            # Physics - Work, Energy, Power
            (
                {
                    "doc_id": "ncert_phy11_ch6",
                    "filename": "ncert_physics_11_ch6_work_energy.md",
                    "title": "NCERT Class 11 Physics Chapter 6",
                    "source_id": "ncert_physics_11",
                    "subject": "Physics",
                    "class_level": "11",
                    "chapter": "Work, Energy and Power",
                    "attribution": "NCERT, Govt. of India. Educational use only."
                },
                """# Work, Energy and Power

## Work Done by a Force

Work is done when a force causes displacement. It is the product of force and displacement in the direction of force.

**Formula:**
W = F · d · cos(θ)

where:
- W = Work done (Joules, J)
- F = Force applied (N)
- d = Displacement (m)
- θ = Angle between force and displacement

**Key Points:**
- Work is a scalar quantity
- 1 Joule = 1 N × 1 m
- Work is positive when force and displacement are in same direction (θ < 90°)
- Work is negative when force opposes displacement (θ > 90°)
- Work is zero when force is perpendicular to displacement (θ = 90°)

**Examples:**
- Lifting a book: W = mgh (positive work by you)
- Friction on sliding block: W = -μmgd (negative work)
- Normal force: W = 0 (perpendicular to motion)

## Kinetic Energy

Energy possessed by a body due to its motion.

**Formula:**
KE = ½mv²

where:
- KE = Kinetic energy (J)
- m = Mass (kg)
- v = Velocity (m/s)

**Key Points:**
- Always positive (v² is always positive)
- Depends on reference frame
- Doubles when velocity doubles? No! Quadruples (v² relationship)

## Potential Energy

Energy stored in a body due to its position or configuration.

**Gravitational Potential Energy:**
PE = mgh

where:
- PE = Potential energy (J)
- m = Mass (kg)
- g = Acceleration due to gravity (9.8 m/s²)
- h = Height above reference (m)

**Key Points:**
- Reference point can be chosen arbitrarily
- Can be positive, negative, or zero depending on reference
- Only changes in PE are physically meaningful

## Work-Energy Theorem

The net work done on a body equals the change in its kinetic energy.

**Formula:**
W_net = ΔKE = ½mv² - ½mu²

**This is powerful because:**
- Avoids dealing with forces directly
- Works even with variable forces
- Connects force-based and energy-based approaches

## Conservation of Energy

Energy can neither be created nor destroyed, only transformed from one form to another.

**For conservative forces:**
Total Energy = KE + PE = constant

**Formula:**
½mv₁² + mgh₁ = ½mv₂² + mgh₂

**Conservative Forces:** Gravity, spring force, electrostatic force
**Non-conservative Forces:** Friction, air resistance

## Power

Rate of doing work or rate of energy transfer.

**Formulas:**
P = W/t = F · v

where:
- P = Power (Watts, W)
- W = Work done (J)
- t = Time (s)
- F = Force (N)
- v = Velocity (m/s)

**Units:**
- 1 Watt = 1 J/s
- 1 horsepower (hp) = 746 W
"""
            ),
            
            # Physics - Electrostatics
            (
                {
                    "doc_id": "ncert_phy12_ch1",
                    "filename": "ncert_physics_12_ch1_electrostatics.md",
                    "title": "NCERT Class 12 Physics Chapter 1",
                    "source_id": "ncert_physics_12",
                    "subject": "Physics",
                    "class_level": "12",
                    "chapter": "Electric Charges and Fields",
                    "attribution": "NCERT, Govt. of India. Educational use only."
                },
                """# Electric Charges and Fields

## Electric Charge

Electric charge is a fundamental property of matter that causes it to experience a force in an electric field.

**Properties:**
- Two types: positive and negative
- Like charges repel, unlike charges attract
- Charge is conserved (total charge in isolated system is constant)
- Charge is quantized: q = ne (n = integer, e = 1.6 × 10⁻¹⁹ C)

**SI Unit:** Coulomb (C)

## Coulomb's Law

The force between two point charges is directly proportional to the product of their magnitudes and inversely proportional to the square of the distance between them.

**Formula:**
F = k × q₁ × q₂ / r²

where:
- F = Force (N)
- k = Coulomb's constant = 9 × 10⁹ N·m²/C²
- q₁, q₂ = Charges (C)
- r = Distance between charges (m)

**Vector Form:**
F₁₂ = k × q₁ × q₂ × r̂₁₂ / r²

**Key Points:**
- Inverse square law (like gravity)
- Acts along the line joining the charges
- Force is attractive for unlike charges, repulsive for like charges

## Electric Field

Electric field is the region around a charge where another charge experiences a force.

**Definition:**
E = F / q₀

where q₀ is a small positive test charge.

**For a Point Charge:**
E = k × Q / r²

**Key Points:**
- Vector quantity - has magnitude and direction
- Direction: away from positive charge, toward negative charge
- Field lines never cross
- Closer field lines = stronger field

**Electric Field Lines Properties:**
1. Start from positive charges, end on negative charges
2. Never cross each other
3. Perpendicular to conductor surface
4. Density indicates field strength

## Electric Potential

Electric potential at a point is the work done per unit positive charge to bring a charge from infinity to that point.

**Formula:**
V = k × Q / r

where:
- V = Electric potential (Volts, V)
- Q = Source charge (C)
- r = Distance from charge (m)

**Potential Difference:**
V_AB = V_A - V_B = W_AB / q

**Relation to Electric Field:**
E = -dV/dr

**Key Points:**
- Scalar quantity (easier to work with than E)
- Potential due to multiple charges = algebraic sum
- Equipotential surfaces are perpendicular to field lines
"""
            ),
            
            # Chemistry - Mole Concept
            (
                {
                    "doc_id": "ncert_chem11_ch1",
                    "filename": "ncert_chemistry_11_ch1_basic_concepts.md",
                    "title": "NCERT Class 11 Chemistry Chapter 1",
                    "source_id": "ncert_chemistry_11",
                    "subject": "Chemistry",
                    "class_level": "11",
                    "chapter": "Some Basic Concepts of Chemistry",
                    "attribution": "NCERT, Govt. of India. Educational use only."
                },
                """# Some Basic Concepts of Chemistry

## The Mole Concept

A mole is the amount of substance that contains as many entities (atoms, molecules, ions) as there are atoms in exactly 12 grams of carbon-12.

**Avogadro's Number:**
Nₐ = 6.022 × 10²³ entities/mol

**Key Formulas:**
- Number of moles (n) = Given mass / Molar mass = m / M
- Number of moles (n) = Number of entities / Nₐ = N / Nₐ
- Number of moles (for gases at STP) = Volume / 22.4 L

**Molar Mass:**
- Mass of 1 mole of substance
- Numerically equal to molecular/atomic mass in g/mol
- Example: M(H₂O) = 2(1) + 16 = 18 g/mol

## Percentage Composition

Mass percentage of an element in a compound:

**Formula:**
Mass % of element = (Mass of element in formula / Molar mass of compound) × 100

**Example for H₂O:**
- Mass % of H = (2 × 1 / 18) × 100 = 11.11%
- Mass % of O = (16 / 18) × 100 = 88.89%

## Empirical and Molecular Formula

**Empirical Formula:** Simplest whole number ratio of atoms
**Molecular Formula:** Actual number of atoms in a molecule

Molecular Formula = n × Empirical Formula

where n = Molar mass / Empirical formula mass

**Steps to find formulas:**
1. Convert mass % to mass (assume 100g sample)
2. Convert mass to moles
3. Divide by smallest number of moles
4. Round to nearest whole numbers (empirical formula)
5. Find n and multiply for molecular formula

## Stoichiometry

Quantitative relationships in chemical reactions based on balanced equations.

**Key Concepts:**
- Coefficients represent mole ratios
- Limiting reagent: reactant that gets consumed first
- Theoretical yield: maximum product possible
- Actual yield: product actually obtained
- Percentage yield = (Actual yield / Theoretical yield) × 100

**Problem Solving Steps:**
1. Write balanced equation
2. Convert given quantities to moles
3. Use mole ratios to find moles of desired substance
4. Convert moles to required units
"""
            ),
            
            # Biology - Photosynthesis
            (
                {
                    "doc_id": "ncert_bio11_ch13",
                    "filename": "ncert_biology_11_ch13_photosynthesis.md",
                    "title": "NCERT Class 11 Biology Chapter 13",
                    "source_id": "ncert_biology_11",
                    "subject": "Biology",
                    "class_level": "11",
                    "chapter": "Photosynthesis in Higher Plants",
                    "attribution": "NCERT, Govt. of India. Educational use only."
                },
                """# Photosynthesis in Higher Plants

## Overview of Photosynthesis

Photosynthesis is the process by which green plants convert light energy into chemical energy, producing glucose and oxygen.

**Overall Equation:**
6CO₂ + 6H₂O + Light Energy → C₆H₁₂O₆ + 6O₂

**Location:** Chloroplasts (specifically in thylakoids and stroma)

## Light Reactions (Light-Dependent Reactions)

Occur in the thylakoid membrane.

**Key Events:**
1. Light absorption by photosystems (PS I and PS II)
2. Photolysis of water: 2H₂O → 4H⁺ + 4e⁻ + O₂
3. Electron transport chain
4. ATP synthesis (photophosphorylation)
5. NADPH formation

**Products:** ATP, NADPH, O₂

**Photosystems:**
- **PS II (P680):** Absorbs light at 680nm, splits water
- **PS I (P700):** Absorbs light at 700nm, produces NADPH

## Dark Reactions (Calvin Cycle)

Occur in the stroma. Also called light-independent reactions or C3 pathway.

**Key Steps:**
1. **Carbon Fixation:** CO₂ + RuBP → 2 × 3-PGA (catalyzed by RuBisCO)
2. **Reduction:** 3-PGA → G3P (uses ATP and NADPH)
3. **Regeneration:** G3P → RuBP (uses ATP)

**For 1 glucose:** 6 CO₂, 18 ATP, 12 NADPH required

**RuBisCO:**
- Most abundant enzyme on Earth
- Fixes CO₂ to RuBP
- Also has oxygenase activity (photorespiration)

## C3 vs C4 Plants

**C3 Plants:**
- First product: 3-carbon compound (3-PGA)
- Examples: Rice, wheat, potato
- Less efficient in hot, dry conditions
- Photorespiration occurs

**C4 Plants:**
- First product: 4-carbon compound (OAA)
- Examples: Maize, sugarcane, sorghum
- Kranz anatomy (bundle sheath cells)
- More efficient in hot conditions
- Minimal photorespiration

## Factors Affecting Photosynthesis

**1. Light Intensity:**
- Rate increases with light up to saturation point
- After saturation, rate plateaus

**2. CO₂ Concentration:**
- Rate increases with CO₂ up to 0.05%
- C4 plants respond better at low CO₂

**3. Temperature:**
- Optimum: 25-35°C for C3, higher for C4
- Enzymes denature at high temperatures

**4. Water:**
- Required for photolysis
- Stomatal closure in water stress reduces CO₂ entry
"""
            ),
            
            # Mathematics - Calculus Derivatives
            (
                {
                    "doc_id": "ncert_math12_ch5",
                    "filename": "ncert_mathematics_12_ch5_derivatives.md",
                    "title": "NCERT Class 12 Mathematics Chapter 5",
                    "source_id": "ncert_math_12",
                    "subject": "Mathematics",
                    "class_level": "12",
                    "chapter": "Continuity and Differentiability",
                    "attribution": "NCERT, Govt. of India. Educational use only."
                },
                """# Continuity and Differentiability

## Definition of Derivative

The derivative of a function f(x) at point x is defined as:

**Formula:**
f'(x) = lim[h→0] (f(x+h) - f(x)) / h

**Interpretation:**
- Geometrically: Slope of tangent at point x
- Physically: Instantaneous rate of change

## Standard Derivatives

**Power Functions:**
- d/dx(xⁿ) = nxⁿ⁻¹
- d/dx(1/x) = -1/x²
- d/dx(√x) = 1/(2√x)

**Exponential and Logarithmic:**
- d/dx(eˣ) = eˣ
- d/dx(aˣ) = aˣ ln(a)
- d/dx(ln x) = 1/x
- d/dx(logₐ x) = 1/(x ln a)

**Trigonometric:**
- d/dx(sin x) = cos x
- d/dx(cos x) = -sin x
- d/dx(tan x) = sec²x
- d/dx(cot x) = -csc²x
- d/dx(sec x) = sec x tan x
- d/dx(csc x) = -csc x cot x

**Inverse Trigonometric:**
- d/dx(sin⁻¹x) = 1/√(1-x²)
- d/dx(cos⁻¹x) = -1/√(1-x²)
- d/dx(tan⁻¹x) = 1/(1+x²)

## Differentiation Rules

**Sum/Difference Rule:**
d/dx(f ± g) = f' ± g'

**Product Rule:**
d/dx(f·g) = f'·g + f·g'

**Quotient Rule:**
d/dx(f/g) = (f'·g - f·g') / g²

**Chain Rule:**
d/dx[f(g(x))] = f'(g(x)) · g'(x)

**Implicit Differentiation:**
When y is defined implicitly by F(x,y) = 0, differentiate both sides with respect to x, treating y as a function of x.

## Applications of Derivatives

**Finding Maxima and Minima:**
1. Find f'(x) = 0 (critical points)
2. Use second derivative test:
   - f''(x) > 0 → local minimum
   - f''(x) < 0 → local maximum
   - f''(x) = 0 → inconclusive

**Rate of Change:**
If y = f(x), then dy/dx represents the rate of change of y with respect to x.

**Tangent and Normal:**
- Slope of tangent at (a, f(a)): m = f'(a)
- Equation of tangent: y - f(a) = f'(a)(x - a)
- Slope of normal: -1/f'(a)
"""
            ),
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_corpus_store_v2: Optional[CorpusStoreV2] = None


def get_corpus_store_v2() -> CorpusStoreV2:
    """Get or create the global corpus store v2 instance"""
    global _corpus_store_v2
    if _corpus_store_v2 is None:
        _corpus_store_v2 = CorpusStoreV2()
    return _corpus_store_v2


def reset_corpus_store_v2():
    """Reset the corpus store (useful for testing)"""
    global _corpus_store_v2
    _corpus_store_v2 = None
