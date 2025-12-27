#!/usr/bin/env python3
"""
📚 Corpus Rebuild Script
=========================

Rebuilds the knowledge base corpus from raw markdown files.

Usage:
    cd backend
    python scripts/rebuild_corpus.py

Features:
- Reads all .md files from data/corpus/raw/
- Generates chunks with metadata
- Updates manifest with version and hash
- Rebuilds BM25 index
- Safe: preserves vector index if unchanged

Author: Druv AI
"""

import sys
import os
import json
import hashlib
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict

# Add backend to path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# PATHS
# =============================================================================
CORPUS_ROOT = BACKEND_DIR / "data" / "corpus"
RAW_DIR = CORPUS_ROOT / "raw"
CHUNKS_DIR = CORPUS_ROOT / "chunks"
MANIFEST_FILE = CORPUS_ROOT / "manifest.json"
CHUNKS_FILE = CHUNKS_DIR / "chunks.json"
CHUNK_INDEX_FILE = CHUNKS_DIR / "chunk_index.json"


# =============================================================================
# DATA CLASSES (matching corpus_store.py)
# =============================================================================

@dataclass
class RawDocument:
    doc_id: str
    filename: str
    title: str
    source_id: str
    subject: str
    class_level: str
    chapter: str
    attribution: str
    fetched_at: str
    content_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChunkV2:
    chunk_id: str
    doc_id: str
    section: str
    text: str
    start_char: int
    end_char: int
    subject: str
    topic: str
    subtopic: str
    class_level: str
    keywords: List[str]
    formulas: List[str]
    key_concepts: List[str]
    exam_relevance: Dict[str, int]
    source_citation: str
    page_reference: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_full_citation(self) -> str:
        return f"{self.source_citation} [chunk:{self.chunk_id[:8]}, doc:{self.doc_id[:8]}]"


# =============================================================================
# METADATA EXTRACTION FROM FILENAME
# =============================================================================

def extract_metadata_from_filename(filename: str) -> Dict[str, str]:
    """
    Extract metadata from filename like ncert_physics_11_ch5_laws_of_motion.md
    """
    name = filename.replace('.md', '')
    parts = name.split('_')
    
    metadata = {
        "source_id": "custom",
        "subject": "General",
        "class_level": "11",
        "chapter": name
    }
    
    if len(parts) >= 4 and parts[0] == 'ncert':
        subject = parts[1].capitalize()
        class_level = parts[2]
        chapter = '_'.join(parts[3:]).replace('_', ' ').title()
        
        metadata = {
            "source_id": f"ncert_{parts[1]}_{class_level}",
            "subject": subject,
            "class_level": class_level,
            "chapter": chapter
        }
    
    return metadata


def extract_title_from_content(content: str, filename: str) -> str:
    """Extract title from first # header or use filename"""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    # Fallback to filename
    return filename.replace('.md', '').replace('_', ' ').title()


# =============================================================================
# CHUNKING LOGIC
# =============================================================================

def chunk_document(doc: RawDocument, content: str) -> List[ChunkV2]:
    """
    Chunk a document by sections (marked with ##).
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
        metadata = extract_chunk_metadata(section_content, doc, section_title)
        
        # Generate stable chunk ID
        chunk_id = generate_chunk_id(doc.doc_id, section_title, section_content[:100])
        
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


def extract_chunk_metadata(content: str, doc: RawDocument, section_title: str) -> Dict:
    """Extract keywords, formulas, concepts from chunk content"""
    content_lower = content.lower()
    
    # Extract formulas
    formula_patterns = [
        r'[A-Za-z]\s*=\s*[^,\n]+',
        r'\$[^$]+\$',
        r'\\[a-z]+\{[^}]+\}',
    ]
    formulas = []
    for pattern in formula_patterns:
        matches = re.findall(pattern, content)
        formulas.extend([m.strip() for m in matches[:5]])
    
    # Extract keywords based on subject
    keywords = []
    
    # Subject-specific keywords
    physics_kw = ["force", "energy", "momentum", "velocity", "acceleration", "mass", 
                  "work", "power", "potential", "kinetic", "gravity", "friction",
                  "electric", "magnetic", "charge", "current", "voltage", "resistance",
                  "wave", "frequency", "wavelength", "amplitude", "photon", "electron",
                  "newton", "motion", "projectile", "circular", "torque", "angular"]
    
    chemistry_kw = ["atom", "molecule", "bond", "reaction", "equilibrium", "acid", "base",
                    "pH", "mole", "concentration", "oxidation", "reduction", "organic",
                    "inorganic", "catalyst", "entropy", "enthalpy", "gibbs", "orbital",
                    "electron", "proton", "neutron", "isotope", "ion", "solution"]
    
    math_kw = ["derivative", "integral", "function", "equation", "polynomial", "matrix",
               "vector", "limit", "calculus", "algebra", "trigonometry", "geometry",
               "permutation", "combination", "probability", "sequence", "series",
               "set", "relation", "logarithm", "exponential", "graph"]
    
    biology_kw = ["cell", "DNA", "RNA", "protein", "enzyme", "photosynthesis", "respiration",
                  "mitosis", "meiosis", "chromosome", "gene", "evolution", "ecology",
                  "organism", "species", "metabolism", "hormone", "membrane", "nucleus"]
    
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
    subj_lower = doc.subject.lower()
    if subj_lower == "physics":
        exam_relevance = {"JEE": 5, "NEET": 4}
    elif subj_lower == "chemistry":
        exam_relevance = {"JEE": 5, "NEET": 5}
    elif subj_lower == "biology":
        exam_relevance = {"JEE": 1, "NEET": 5}
    elif subj_lower == "mathematics":
        exam_relevance = {"JEE": 5, "NEET": 2}
    
    return {
        "topic": topic,
        "subtopic": subtopic,
        "keywords": keywords[:15],
        "formulas": formulas[:5],
        "key_concepts": keywords[:5],
        "exam_relevance": exam_relevance
    }


def generate_chunk_id(doc_id: str, section: str, content_preview: str) -> str:
    """Generate stable chunk ID from content"""
    hash_input = f"{doc_id}:{section}:{content_preview}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


# =============================================================================
# INDEX BUILDING
# =============================================================================

def build_keyword_index(chunks: Dict[str, ChunkV2]) -> Dict:
    """Build inverted index for keyword search"""
    keyword_index = {}
    topic_index = {}
    subject_index = {}
    doc_index = {}
    
    for chunk_id, chunk in chunks.items():
        # Keyword index
        for kw in chunk.keywords:
            kw_lower = kw.lower()
            if kw_lower not in keyword_index:
                keyword_index[kw_lower] = []
            if chunk_id not in keyword_index[kw_lower]:
                keyword_index[kw_lower].append(chunk_id)
        
        # Topic index
        topic_lower = chunk.topic.lower()
        if topic_lower not in topic_index:
            topic_index[topic_lower] = []
        if chunk_id not in topic_index[topic_lower]:
            topic_index[topic_lower].append(chunk_id)
        
        # Subject index
        subj_lower = chunk.subject.lower()
        if subj_lower not in subject_index:
            subject_index[subj_lower] = []
        if chunk_id not in subject_index[subj_lower]:
            subject_index[subj_lower].append(chunk_id)
        
        # Doc index
        if chunk.doc_id not in doc_index:
            doc_index[chunk.doc_id] = []
        if chunk_id not in doc_index[chunk.doc_id]:
            doc_index[chunk.doc_id].append(chunk_id)
    
    return {
        "keyword_index": keyword_index,
        "topic_index": topic_index,
        "subject_index": subject_index,
        "doc_index": doc_index
    }


# =============================================================================
# MAIN REBUILD FUNCTION
# =============================================================================

def rebuild_corpus():
    """
    Main function to rebuild corpus from raw files.
    """
    logger.info("=" * 60)
    logger.info("📚 CORPUS REBUILD STARTED")
    logger.info("=" * 60)
    
    # Ensure directories exist
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Find all raw files
    raw_files = list(RAW_DIR.glob("*.md"))
    logger.info(f"📁 Found {len(raw_files)} raw markdown files in {RAW_DIR}")
    
    if not raw_files:
        logger.error("❌ No raw files found! Add content to data/corpus/raw/")
        return False
    
    # Step 2: Process each file
    documents: Dict[str, RawDocument] = {}
    chunks: Dict[str, ChunkV2] = {}
    
    for filepath in raw_files:
        logger.info(f"📄 Processing: {filepath.name}")
        
        # Read content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        meta = extract_metadata_from_filename(filepath.name)
        title = extract_title_from_content(content, filepath.name)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Create document record
        doc_id = hashlib.sha256(filepath.name.encode()).hexdigest()[:16]
        doc = RawDocument(
            doc_id=doc_id,
            filename=filepath.name,
            title=title,
            source_id=meta["source_id"],
            subject=meta["subject"],
            class_level=meta["class_level"],
            chapter=meta["chapter"],
            attribution="NCERT, Govt. of India. Educational use only.",
            fetched_at=datetime.utcnow().isoformat(),
            content_hash=content_hash
        )
        documents[doc_id] = doc
        
        # Chunk the document
        doc_chunks = chunk_document(doc, content)
        for chunk in doc_chunks:
            chunks[chunk.chunk_id] = chunk
        
        logger.info(f"   → {len(doc_chunks)} chunks created")
    
    logger.info(f"📊 Total: {len(documents)} documents, {len(chunks)} chunks")
    
    # Step 3: Build keyword index
    logger.info("🔧 Building keyword index...")
    index = build_keyword_index(chunks)
    
    # Step 4: Generate manifest
    all_content = "".join(c.text for c in chunks.values())
    content_hash = hashlib.sha256(all_content.encode()).hexdigest()[:16]
    
    chunk_lengths = [len(c.text) for c in chunks.values()]
    avg_chunk_len = sum(chunk_lengths) / len(chunk_lengths) if chunk_lengths else 0
    total_tokens = sum(chunk_lengths) // 4  # Rough estimate
    
    # Group by source
    sources = []
    source_counts: Dict[str, int] = {}
    for doc in documents.values():
        if doc.source_id not in source_counts:
            source_counts[doc.source_id] = 0
        source_counts[doc.source_id] += 1
    
    for source_id, count in source_counts.items():
        doc = next((d for d in documents.values() if d.source_id == source_id), None)
        sources.append({
            "source_id": source_id,
            "doc_count": count,
            "attribution": doc.attribution if doc else "Unknown"
        })
    
    now = datetime.utcnow().isoformat()
    manifest = {
        "dataset_version": now,
        "content_hash": content_hash,
        "num_documents": len(documents),
        "num_chunks": len(chunks),
        "avg_chunk_len": avg_chunk_len,
        "total_tokens_estimate": total_tokens,
        "sources": sources,
        "created_at": now,
        "updated_at": now
    }
    
    # Step 5: Save everything
    logger.info("💾 Saving to files...")
    
    # Save chunks + documents
    with open(CHUNKS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "chunks": [c.to_dict() for c in chunks.values()],
            "documents": [d.to_dict() for d in documents.values()],
            "chunk_count": len(chunks),
            "doc_count": len(documents)
        }, f, indent=2)
    
    # Save index
    with open(CHUNK_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    # Save manifest
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    # Step 6: Print summary
    logger.info("=" * 60)
    logger.info("✅ CORPUS REBUILD COMPLETE")
    logger.info("=" * 60)
    logger.info(f"📄 Documents: {len(documents)}")
    logger.info(f"📝 Chunks: {len(chunks)}")
    logger.info(f"📊 Estimated tokens: {total_tokens:,}")
    logger.info(f"📏 Average chunk length: {avg_chunk_len:.0f} chars")
    logger.info(f"🔑 Keywords indexed: {len(index['keyword_index'])}")
    logger.info(f"📚 Topics indexed: {len(index['topic_index'])}")
    logger.info("")
    logger.info("Files written:")
    logger.info(f"  - {CHUNKS_FILE}")
    logger.info(f"  - {CHUNK_INDEX_FILE}")
    logger.info(f"  - {MANIFEST_FILE}")
    logger.info("")
    logger.info("⚠️  NOTE: Vector index will rebuild on next search query.")
    
    return True


if __name__ == "__main__":
    success = rebuild_corpus()
    sys.exit(0 if success else 1)




