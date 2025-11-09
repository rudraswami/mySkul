"""
Topper Hack Selector
Maps concepts to verified topper tricks with specific rank attributions
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, List


class TopperHackSelector:
    """Selects relevant topper hacks based on concept and student profile"""

    def __init__(self, data_path: str = "backend/data/topper_hacks.json"):
        self.hacks = self._load_hacks(data_path)

    def _load_hacks(self, path: str) -> Dict:
        """Load topper hacks database from JSON"""
        path_obj = Path(path)

        # Handle both absolute and relative paths
        if not path_obj.exists():
            # Try from project root
            project_root = Path(__file__).parent.parent.parent
            path_obj = project_root / path

        if not path_obj.exists():
            # Fallback: return default hacks
            return {"default": self._get_default_hacks()}

        with open(path_obj, encoding='utf-8') as f:
            return json.load(f)

    def _get_default_hacks(self) -> Dict:
        """Default hacks if file not found"""
        return {
            "concept": "General programming",
            "keywords": ["algorithm", "code"],
            "hacks": [
                {
                    "rank": "Multiple toppers",
                    "hack": "Steps ko number karo aur diagram banao - 2 marks pakka",
                    "marks_saved": 2,
                    "board": "All boards",
                    "subject": "Computer Science",
                    "applicable_levels": ["class_11", "class_12"]
                }
            ]
        }

    def get_hack(
        self,
        concept_keywords: List[str],
        board: Optional[str] = None,
        subject: Optional[str] = None,
        level: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Find most relevant topper hack for given concept

        Args:
            concept_keywords: List of keywords from the concept (e.g., ["recursion", "base"])
            board: Education board (CBSE, ICSE, etc.)
            subject: Subject name
            level: Education level (class_11, class_12, jee, etc.)

        Returns:
            Dict with hack details or None if no match found
        """
        # Convert keywords to lowercase for matching
        keywords_lower = [kw.lower() for kw in concept_keywords]

        best_match = None
        best_score = 0

        # Iterate through all hack categories
        for key, data in self.hacks.items():
            # Calculate match score based on keyword overlap
            match_score = 0

            # Check if any concept keyword matches the hack key
            for kw in keywords_lower:
                if kw in key.lower():
                    match_score += 3  # Strong match with category name

            # Check keyword list in hack data
            hack_keywords = data.get("keywords", [])
            for kw in keywords_lower:
                for hack_kw in hack_keywords:
                    if kw in hack_kw.lower() or hack_kw.lower() in kw:
                        match_score += 1

            if match_score > best_score:
                # Filter hacks by board/level if specified
                matching_hacks = self._filter_hacks(
                    data["hacks"],
                    board=board,
                    level=level
                )

                if matching_hacks:
                    best_match = {
                        "concept": data["concept"],
                        "category": key,
                        **matching_hacks[0]  # Return best (first) match
                    }
                    best_score = match_score

        # Fallback to default hack if no match
        if best_match is None and "default" in self.hacks:
            default_hacks = self._filter_hacks(
                self.hacks["default"]["hacks"],
                board=board,
                level=level
            )
            if default_hacks:
                best_match = {
                    "concept": self.hacks["default"]["concept"],
                    "category": "default",
                    **default_hacks[0]
                }

        return best_match

    def _filter_hacks(
        self,
        hacks: List[Dict],
        board: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[Dict]:
        """Filter hacks by board and level"""
        filtered = hacks

        # Filter by board
        if board:
            board_filtered = [
                h for h in filtered
                if h.get("board") == board or h.get("board") == "All boards"
            ]
            if board_filtered:
                filtered = board_filtered

        # Filter by level
        if level:
            level_filtered = [
                h for h in filtered
                if level in h.get("applicable_levels", [])
            ]
            if level_filtered:
                filtered = level_filtered

        return filtered

    def format_hack_annotation(self, hack: Dict, include_rank: bool = True) -> str:
        """
        Format hack for SVG display

        Args:
            hack: Hack dictionary
            include_rank: Whether to include rank attribution

        Returns:
            Formatted string for display
        """
        if include_rank:
            return (
                f"🏆 {hack['rank']} trick:\n"
                f"{hack['hack']}\n"
                f"💡 Saves {hack['marks_saved']} marks"
            )
        else:
            return f"💡 Topper tip: {hack['hack']}"

    def format_hack_short(self, hack: Dict) -> str:
        """
        Short format for space-constrained displays

        Args:
            hack: Hack dictionary

        Returns:
            Compact formatted string
        """
        return f"🏆 {hack['rank']}: {hack['hack'][:60]}..."

    def get_all_hacks_for_concept(self, concept_key: str) -> List[Dict]:
        """
        Get all hacks for a specific concept category

        Args:
            concept_key: Key like "recursion", "sorting", etc.

        Returns:
            List of all hacks for that concept
        """
        if concept_key in self.hacks:
            return self.hacks[concept_key]["hacks"]
        return []

    def get_hack_by_board(self, board: str) -> List[Dict]:
        """
        Get all hacks applicable to a specific board

        Args:
            board: Board name (CBSE, ICSE, etc.)

        Returns:
            List of hacks for that board
        """
        result = []
        for concept_key, data in self.hacks.items():
            for hack in data["hacks"]:
                if hack.get("board") == board or hack.get("board") == "All boards":
                    result.append({
                        "concept": data["concept"],
                        "category": concept_key,
                        **hack
                    })
        return result


# Convenience function for quick access
def get_topper_hack(
    concept: str,
    board: Optional[str] = None,
    level: Optional[str] = None
) -> Optional[str]:
    """
    Quick function to get a topper hack annotation

    Args:
        concept: Concept description or keywords
        board: Education board
        level: Education level

    Returns:
        Formatted topper hack string or None
    """
    selector = TopperHackSelector()
    keywords = concept.lower().split()
    hack = selector.get_hack(keywords, board=board, level=level)

    if hack:
        return selector.format_hack_annotation(hack)

    return None
