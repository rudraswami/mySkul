"""
PYQ (Previous Year Question) Pattern Matcher
Identifies similar past year questions to help students recognize patterns
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class PYQReference:
    """Represents a past year question reference"""
    board: str
    year: int
    question_number: str
    marks: int
    similarity: float
    exam_type: str = "Annual"

    def __str__(self) -> str:
        return f"{self.board} {self.year} {self.question_number} ({self.marks}m)"


class PYQMatcher:
    """Matches current questions to similar PYQs"""

    def __init__(self, data_path: str = "backend/data/pyq_patterns.json"):
        self.patterns = self._load_patterns(data_path)

    def _load_patterns(self, path: str) -> Dict:
        """Load PYQ patterns database from JSON"""
        path_obj = Path(path)

        # Handle both absolute and relative paths
        if not path_obj.exists():
            # Try from project root
            project_root = Path(__file__).parent.parent.parent
            path_obj = project_root / path

        if not path_obj.exists():
            # Fallback: return empty patterns
            return {}

        with open(path_obj, encoding='utf-8') as f:
            return json.load(f)

    def find_similar_pyqs(
        self,
        question: str,
        board: Optional[str] = None,
        min_similarity: float = 0.7,
        max_results: int = 3
    ) -> List[PYQReference]:
        """
        Find PYQs with similar patterns to the current question

        Args:
            question: The current question text
            board: Education board filter (CBSE, ISC, etc.)
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            max_results: Maximum number of results to return

        Returns:
            List of PYQReference objects sorted by similarity
        """
        results = []
        q_lower = question.lower()

        for pattern_id, pattern_data in self.patterns.items():
            # Calculate keyword match score
            keywords = pattern_data.get("keywords", [])
            keyword_matches = sum(
                1 for kw in keywords
                if kw.lower() in q_lower
            )

            # Need at least 2 keyword matches
            if keyword_matches >= 2:
                # Get all references for this pattern
                for ref_data in pattern_data.get("references", []):
                    similarity = ref_data.get("similarity", 0.0)

                    # Apply filters
                    if similarity >= min_similarity:
                        if board is None or ref_data.get("board") == board:
                            pyq_ref = PYQReference(
                                board=ref_data["board"],
                                year=ref_data["year"],
                                question_number=ref_data["question_number"],
                                marks=ref_data["marks"],
                                similarity=similarity,
                                exam_type=ref_data.get("exam_type", "Annual")
                            )
                            results.append(pyq_ref)

        # Sort by similarity (descending) and return top results
        results.sort(key=lambda x: x.similarity, reverse=True)
        return results[:max_results]

    def find_by_pattern_id(self, pattern_id: str) -> Optional[Dict]:
        """
        Get pattern information by pattern ID

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern data dictionary or None
        """
        return self.patterns.get(pattern_id)

    def find_by_board(self, board: str, year: Optional[int] = None) -> List[PYQReference]:
        """
        Find all PYQs for a specific board

        Args:
            board: Education board (CBSE, ISC, etc.)
            year: Optional year filter

        Returns:
            List of PYQ references for that board
        """
        results = []

        for pattern_id, pattern_data in self.patterns.items():
            for ref_data in pattern_data.get("references", []):
                if ref_data.get("board") == board:
                    if year is None or ref_data.get("year") == year:
                        pyq_ref = PYQReference(
                            board=ref_data["board"],
                            year=ref_data["year"],
                            question_number=ref_data["question_number"],
                            marks=ref_data["marks"],
                            similarity=ref_data.get("similarity", 1.0),
                            exam_type=ref_data.get("exam_type", "Annual")
                        )
                        results.append(pyq_ref)

        return results

    def format_pyq_annotation(self, pyq: PYQReference, style: str = "detailed") -> str:
        """
        Format PYQ reference for SVG display

        Args:
            pyq: PYQReference object
            style: "detailed" or "compact"

        Returns:
            Formatted string for display
        """
        if style == "compact":
            return f"📌 {pyq.board} {pyq.year} {pyq.question_number}"
        else:
            return (
                f"📌 {pyq.board} {pyq.year} {pyq.question_number}\n"
                f"Same pattern! ({pyq.marks} marks)\n"
                f"✓ {int(pyq.similarity * 100)}% similar"
            )

    def format_pyq_list(self, pyqs: List[PYQReference], max_display: int = 3) -> str:
        """
        Format multiple PYQ references in a concise way

        Args:
            pyqs: List of PYQReference objects
            max_display: Maximum number to display

        Returns:
            Formatted string with multiple PYQs
        """
        if not pyqs:
            return ""

        pyqs = pyqs[:max_display]
        lines = ["📌 Similar PYQs:"]

        for i, pyq in enumerate(pyqs, 1):
            sim_percent = int(pyq.similarity * 100)
            lines.append(f"  {i}. {pyq.board} {pyq.year} {pyq.question_number} ({sim_percent}%)")

        return "\n".join(lines)

    def get_pattern_stats(self) -> Dict:
        """
        Get statistics about loaded patterns

        Returns:
            Dictionary with pattern statistics
        """
        total_patterns = len(self.patterns)
        total_references = sum(
            len(p.get("references", []))
            for p in self.patterns.values()
        )

        boards = set()
        years = set()

        for pattern_data in self.patterns.values():
            for ref in pattern_data.get("references", []):
                boards.add(ref.get("board", "Unknown"))
                years.add(ref.get("year", 0))

        return {
            "total_patterns": total_patterns,
            "total_references": total_references,
            "boards_covered": sorted(boards),
            "years_covered": sorted(years),
            "average_refs_per_pattern": round(total_references / total_patterns, 2) if total_patterns else 0
        }

    def suggest_practice_questions(
        self,
        concept_keywords: List[str],
        board: Optional[str] = None,
        limit: int = 5
    ) -> List[PYQReference]:
        """
        Suggest practice questions based on concept keywords

        Args:
            concept_keywords: Keywords related to the concept
            board: Optional board filter
            limit: Maximum number of suggestions

        Returns:
            List of suggested PYQ references
        """
        # Create a pseudo-question from keywords
        pseudo_question = " ".join(concept_keywords)
        return self.find_similar_pyqs(
            question=pseudo_question,
            board=board,
            min_similarity=0.6,
            max_results=limit
        )


# Convenience functions for quick access
def get_pyq_references(
    question: str,
    board: Optional[str] = None,
    max_results: int = 3
) -> List[str]:
    """
    Quick function to get formatted PYQ references

    Args:
        question: Question text
        board: Optional board filter
        max_results: Maximum results to return

    Returns:
        List of formatted PYQ reference strings
    """
    matcher = PYQMatcher()
    pyqs = matcher.find_similar_pyqs(question, board=board, max_results=max_results)

    return [matcher.format_pyq_annotation(pyq, style="compact") for pyq in pyqs]


def has_similar_pyqs(question: str, min_similarity: float = 0.8) -> bool:
    """
    Check if there are highly similar PYQs

    Args:
        question: Question text
        min_similarity: Minimum similarity threshold

    Returns:
        True if similar PYQs found, False otherwise
    """
    matcher = PYQMatcher()
    pyqs = matcher.find_similar_pyqs(question, min_similarity=min_similarity)
    return len(pyqs) > 0
