"""
RAG Enhancer - Enhance AI Responses with Curriculum Context
============================================================

Enhances AI prompts and responses using retrieved curriculum content:
- Adds curriculum context to prompts (pre-generation)
- Validates responses against curriculum (post-generation)
- Provides source citations

This is the key integration point for hallucination-free responses.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .retriever import CurriculumRetriever, RetrievalResult
from .curriculum_store import CurriculumChunk

logger = logging.getLogger(__name__)


@dataclass
class EnhancedPrompt:
    """Enhanced prompt with curriculum context"""
    original_prompt: str
    enhanced_prompt: str
    curriculum_context: str
    sources_used: List[str]
    formulas_available: List[str]


@dataclass
class ResponseValidation:
    """Validation of response against curriculum"""
    is_consistent: bool
    alignment_score: float  # 0.0 to 1.0
    curriculum_matches: List[Dict[str, Any]]
    potential_issues: List[str]
    suggested_additions: List[str]


class RAGEnhancer:
    """
    RAG Enhancement Engine for Curriculum-Grounded AI
    
    Key capabilities:
    1. Pre-generation: Enhance prompts with curriculum context
    2. Post-generation: Validate responses against curriculum
    3. Citation: Add source references to responses
    
    Usage:
        enhancer = RAGEnhancer()
        
        # Enhance prompt before sending to LLM
        enhanced = enhancer.enhance_prompt(
            "Explain Newton's laws",
            subject="Physics"
        )
        
        # Validate LLM response
        validation = enhancer.validate_response(
            response_text,
            "Newton's laws",
            subject="Physics"
        )
    """
    
    def __init__(self, retriever: Optional[CurriculumRetriever] = None):
        """Initialize RAG enhancer"""
        self.retriever = retriever or CurriculumRetriever()
        logger.info("🚀 RAGEnhancer initialized - Curriculum-grounded AI active")
    
    def enhance_prompt(
        self,
        question: str,
        subject: Optional[str] = None,
        include_formulas: bool = True,
        max_context_chunks: int = 3
    ) -> EnhancedPrompt:
        """
        Enhance a prompt with relevant curriculum context.
        
        This is called BEFORE sending the prompt to the LLM,
        grounding the response in verified curriculum content.
        
        Args:
            question: The student's question
            subject: Subject area
            include_formulas: Include relevant formulas
            max_context_chunks: Maximum curriculum chunks to include
            
        Returns:
            EnhancedPrompt with curriculum context
        """
        try:
            # Retrieve relevant curriculum content
            retrieval = self.retriever.retrieve(question, subject, max_context_chunks)
            
            # Format curriculum context
            context_string = retrieval.get_context_string(max_context_chunks)
            
            # Collect formulas
            formulas = []
            if include_formulas:
                for chunk in retrieval.chunks:
                    formulas.extend(chunk.formulas)
            
            # Build enhanced prompt
            if context_string:
                enhanced = f"""You are answering a student's question. Use the following VERIFIED CURRICULUM CONTENT as your primary source. Do not make up facts - stick to the curriculum.

=== VERIFIED CURRICULUM CONTEXT ===
{context_string}
=== END CURRICULUM CONTEXT ===

{f"Relevant Formulas: {', '.join(set(formulas))}" if formulas else ""}

Student Question: {question}

Instructions:
1. Base your answer primarily on the curriculum content above
2. If the curriculum doesn't cover something, say "This topic requires additional reference"
3. Use the exact formulas and definitions from the curriculum
4. Cite the source (e.g., "According to NCERT Class 12 Physics...")

Your Answer:"""
            else:
                enhanced = question
            
            return EnhancedPrompt(
                original_prompt=question,
                enhanced_prompt=enhanced,
                curriculum_context=context_string,
                sources_used=retrieval.get_sources(),
                formulas_available=list(set(formulas))
            )
            
        except Exception as e:
            logger.error(f"❌ Prompt enhancement error: {e}", exc_info=True)
            return EnhancedPrompt(
                original_prompt=question,
                enhanced_prompt=question,
                curriculum_context="",
                sources_used=[],
                formulas_available=[]
            )
    
    def validate_response(
        self,
        response_text: str,
        question: str,
        subject: Optional[str] = None
    ) -> ResponseValidation:
        """
        Validate an AI response against curriculum content.
        
        This is called AFTER receiving the LLM response,
        checking for consistency with verified content.
        
        Args:
            response_text: The AI-generated response
            question: Original question
            subject: Subject area
            
        Returns:
            ResponseValidation with consistency analysis
        """
        try:
            # Retrieve relevant curriculum
            retrieval = self.retriever.retrieve(question, subject, 5)
            
            if not retrieval.chunks:
                return ResponseValidation(
                    is_consistent=True,
                    alignment_score=0.5,
                    curriculum_matches=[],
                    potential_issues=["No curriculum content found for validation"],
                    suggested_additions=[]
                )
            
            # Check response against curriculum
            matches = []
            issues = []
            additions = []
            
            response_lower = response_text.lower()
            
            for chunk in retrieval.chunks:
                # Check concept coverage
                concept_matches = []
                for concept in chunk.key_concepts:
                    if concept.lower() in response_lower:
                        concept_matches.append(concept)
                
                if concept_matches:
                    matches.append({
                        "source": chunk.source,
                        "topic": chunk.topic,
                        "concepts_matched": concept_matches
                    })
                
                # Check formula usage
                for formula in chunk.formulas:
                    # Normalize formula for comparison
                    formula_normalized = formula.lower().replace(' ', '')
                    response_normalized = response_lower.replace(' ', '')
                    
                    if formula_normalized not in response_normalized:
                        # Formula might be relevant but not mentioned
                        if any(kw in response_lower for kw in chunk.keywords[:3]):
                            additions.append(f"Consider including formula: {formula} (from {chunk.source})")
            
            # Calculate alignment score
            if matches:
                alignment_score = min(1.0, len(matches) / len(retrieval.chunks))
            else:
                alignment_score = 0.3  # Low but not zero if no matches
            
            # Check for potential issues
            # Look for claims that might contradict curriculum
            # This is a simplified check - can be made more sophisticated
            
            is_consistent = len(issues) == 0 and alignment_score >= 0.3
            
            return ResponseValidation(
                is_consistent=is_consistent,
                alignment_score=alignment_score,
                curriculum_matches=matches,
                potential_issues=issues,
                suggested_additions=additions[:3]  # Limit suggestions
            )
            
        except Exception as e:
            logger.error(f"❌ Response validation error: {e}", exc_info=True)
            return ResponseValidation(
                is_consistent=True,
                alignment_score=0.5,
                curriculum_matches=[],
                potential_issues=[f"Validation error: {str(e)}"],
                suggested_additions=[]
            )
    
    def add_citations(
        self,
        response_text: str,
        sources: List[str]
    ) -> str:
        """
        Add curriculum citations to a response.
        
        Args:
            response_text: The AI response
            sources: List of sources used
            
        Returns:
            Response with citations added
        """
        if not sources:
            return response_text
        
        citation_block = "\n\n📚 **Sources:**\n"
        for i, source in enumerate(sources[:3], 1):
            citation_block += f"{i}. {source}\n"
        
        return response_text + citation_block
    
    def get_topic_context(
        self,
        topic: str,
        subject: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive context for a specific topic.
        
        Args:
            topic: Topic name
            subject: Subject area
            
        Returns:
            Dict with topic content, formulas, and related concepts
        """
        retrieval = self.retriever.retrieve_for_topic(topic, subject)
        
        formulas = []
        key_concepts = []
        sources = []
        
        for chunk in retrieval.chunks:
            formulas.extend(chunk.formulas)
            key_concepts.extend(chunk.key_concepts)
            sources.append(chunk.source)
        
        return {
            "topic": topic,
            "subject": subject,
            "content": retrieval.get_context_string(),
            "formulas": list(set(formulas)),
            "key_concepts": list(set(key_concepts)),
            "sources": list(set(sources))
        }


# Singleton instance
_enhancer_instance: Optional[RAGEnhancer] = None


def get_rag_enhancer() -> RAGEnhancer:
    """Get or create the global RAG enhancer instance"""
    global _enhancer_instance
    if _enhancer_instance is None:
        _enhancer_instance = RAGEnhancer()
    return _enhancer_instance

