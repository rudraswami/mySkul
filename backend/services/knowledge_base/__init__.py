"""
Knowledge Base Module - RAG for Curriculum-Grounded Responses
==============================================================

Implements Retrieval-Augmented Generation (RAG) to ground AI responses
in verified curriculum content:

Components:
- CurriculumStore: Stores and indexes curriculum content
- Retriever: Semantic search over curriculum
- RAGEnhancer: Enhances AI responses with retrieved context

This prevents hallucinations by grounding responses in verified NCERT/JEE/NEET content.
"""

from .curriculum_store import CurriculumStore
from .retriever import CurriculumRetriever
from .rag_enhancer import RAGEnhancer, get_rag_enhancer

__all__ = [
    'CurriculumStore',
    'CurriculumRetriever',
    'RAGEnhancer',
    'get_rag_enhancer'
]

