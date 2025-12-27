#!/usr/bin/env python3
"""
🔍 Retrieval Verification Script
=================================

Verifies that RAG retrieval is working correctly with the expanded corpus.

Test Queries:
1. "Explain Newton's laws" (Physics)
2. "Give formula for projectile range" (Physics)
3. "What is mole concept?" (Chemistry)

For each query, prints:
- Retrieved chunk IDs
- Document sources
- Similarity scores (if available)

Usage:
    cd backend
    python scripts/verify_retrieval.py

Author: Druv AI
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test queries with expected topics
TEST_QUERIES = [
    {
        "query": "Explain Newton's laws",
        "subject": "Physics",
        "expected_keywords": ["newton", "force", "motion", "law"]
    },
    {
        "query": "Give formula for projectile range",
        "subject": "Physics", 
        "expected_keywords": ["projectile", "range", "motion", "velocity"]
    },
    {
        "query": "What is mole concept?",
        "subject": "Chemistry",
        "expected_keywords": ["mole", "avogadro", "mass", "concentration"]
    }
]


async def test_retrieval():
    """Test retrieval for all test queries."""
    logger.info("=" * 70)
    logger.info("📚 RETRIEVAL VERIFICATION TEST")
    logger.info("=" * 70)
    
    # Import retriever after path setup
    try:
        from services.knowledge_base.retriever_v2 import get_retriever_v2
        from services.knowledge_base.corpus_store import get_corpus_store_v2
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure you're running from the backend directory")
        return False
    
    # Get retriever and corpus stats
    retriever = get_retriever_v2()
    corpus = get_corpus_store_v2()
    
    # Print corpus stats
    stats = retriever.get_corpus_stats()
    logger.info(f"\n📊 Corpus Stats:")
    logger.info(f"   Documents: {stats.get('num_documents', 0)}")
    logger.info(f"   Chunks: {stats.get('num_chunks', 0)}")
    logger.info(f"   Version: {stats.get('dataset_version', 'unknown')[:20]}...")
    logger.info(f"   Content Hash: {stats.get('content_hash', 'unknown')}")
    
    all_passed = True
    results_summary = []
    
    for i, test in enumerate(TEST_QUERIES, 1):
        query = test["query"]
        subject = test["subject"]
        expected = test["expected_keywords"]
        
        logger.info(f"\n" + "=" * 70)
        logger.info(f"📝 TEST {i}: {query}")
        logger.info(f"   Subject filter: {subject}")
        logger.info("=" * 70)
        
        # Run retrieval
        try:
            result = retriever.retrieve_knowledge(query, subject=subject, max_results=5)
            
            logger.info(f"\n📋 RESULTS:")
            logger.info(f"   Retrieval method: {result.retrieval_method}")
            logger.info(f"   Total hits: {result.total_hits}")
            logger.info(f"   Confidence: {result.confidence:.3f}")
            logger.info(f"   Keywords matched: {result.keywords_matched}")
            
            if result.results:
                logger.info(f"\n   Retrieved chunks:")
                for j, r in enumerate(result.results[:5], 1):
                    chunk_id = r.get('chunk_id', 'N/A')
                    doc_id = r.get('doc_id', 'N/A')
                    topic = r.get('topic', 'N/A')
                    score = r.get('score', 0)
                    citation = r.get('citation', 'N/A')
                    keywords = r.get('keywords', [])[:5]
                    
                    logger.info(f"   [{j}] Chunk: {chunk_id[:12]}...")
                    logger.info(f"       Doc: {doc_id[:12]}...")
                    logger.info(f"       Topic: {topic}")
                    logger.info(f"       Score: {score:.3f}")
                    logger.info(f"       Keywords: {keywords}")
                    logger.info(f"       Citation: {citation[:60]}...")
                    
                    # Show content preview
                    content = r.get('content', '')[:150]
                    logger.info(f"       Preview: {content}...")
                    logger.info("")
                
                # Check if any expected keywords are found
                found_keywords = set()
                for r in result.results:
                    found_keywords.update(kw.lower() for kw in r.get('keywords', []))
                    found_keywords.update(kw.lower() for kw in r.get('key_concepts', []))
                
                matched_expected = set(expected) & found_keywords
                test_passed = len(result.results) > 0 and len(matched_expected) > 0
                
                status = "✅ PASS" if test_passed else "⚠️ PARTIAL"
                logger.info(f"   {status} - Found {len(result.results)} chunks, matched {len(matched_expected)}/{len(expected)} expected keywords")
                
                results_summary.append({
                    "query": query,
                    "hits": result.total_hits,
                    "confidence": result.confidence,
                    "passed": test_passed
                })
                
                if not test_passed:
                    all_passed = False
                    
            else:
                logger.info(f"   ❌ FAIL - No results returned!")
                all_passed = False
                results_summary.append({
                    "query": query,
                    "hits": 0,
                    "confidence": 0,
                    "passed": False
                })
                
        except Exception as e:
            logger.error(f"   ❌ ERROR: {e}")
            all_passed = False
            results_summary.append({
                "query": query,
                "hits": 0,
                "confidence": 0,
                "passed": False,
                "error": str(e)
            })
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("=" * 70)
    
    for r in results_summary:
        status = "✅" if r["passed"] else "❌"
        logger.info(f"   {status} {r['query'][:40]}: {r['hits']} hits, confidence={r['confidence']:.3f}")
    
    passed = sum(1 for r in results_summary if r["passed"])
    total = len(results_summary)
    
    logger.info(f"\n   Overall: {passed}/{total} tests passed")
    
    if all_passed:
        logger.info("\n🎉 ALL TESTS PASSED - Retrieval is working correctly!")
    else:
        logger.info("\n⚠️ SOME TESTS FAILED - Review results above")
    
    return all_passed


def main():
    """Main entry point."""
    try:
        success = asyncio.run(test_retrieval())
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


