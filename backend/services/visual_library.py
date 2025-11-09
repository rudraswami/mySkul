"""
Visual Library - Codebase-First Approach
Check existing visuals before generating new ones
Implements "Student Council Tests" - track what works

System Prompt Rule #0: Before generating ANY new visual, you MUST:
1. Analyze existing codebase
2. Use existing assets if good
3. Enhance, never duplicate
4. Create only if missing
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class VisualLibrary:
    """Manages visual caching, reuse, and quality tracking"""

    def __init__(self, base_path: str = "visual_library/"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self._ensure_subject_dirs()

    def _ensure_subject_dirs(self):
        """Create subject directories if they don't exist"""
        subjects = ["cs", "physics", "math", "chemistry", "biology"]
        for subject in subjects:
            (self.base_path / subject).mkdir(exist_ok=True)

    def _create_fingerprint(self, question: str, marks: int) -> str:
        """
        Create content-based fingerprint for a question

        Args:
            question: The question text
            marks: Total marks

        Returns:
            12-character hex fingerprint
        """
        # Normalize question (remove punctuation, lowercase, remove numbers)
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        normalized = re.sub(r'\d+', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Create fingerprint
        key = f"{normalized}_{marks}"
        return hashlib.md5(key.encode('utf-8')).hexdigest()[:12]

    def find_existing(
        self,
        question: str,
        marks: int,
        subject: str = "cs"
    ) -> Optional[Dict[str, Any]]:
        """
        Search for existing visual by concept fingerprint

        Args:
            question: Question text
            marks: Total marks
            subject: Subject category (cs, physics, etc.)

        Returns:
            Visual data dict or None if not found/needs regeneration
        """
        fingerprint = self._create_fingerprint(question, marks)
        subject_path = self.base_path / subject
        visual_file = subject_path / f"{fingerprint}.json"

        if not visual_file.exists():
            return None

        try:
            with open(visual_file, encoding='utf-8') as f:
                visual_data = json.load(f)

            # Check if needs regeneration (Student Council Test)
            if self._should_regenerate(visual_data):
                return None  # Force regeneration

            return visual_data

        except (json.JSONDecodeError, IOError):
            return None

    def _should_regenerate(self, visual_metadata: Dict) -> bool:
        """
        Student Council Tests - did visual perform well?

        Regenerate if:
        - Low marks conversion (<70%)
        - Not popular (<10 screenshots in 30 days)
        - Very old (>180 days) - we have better techniques now
        - Low friend test score (<6/8)

        Args:
            visual_metadata: Cached visual metadata

        Returns:
            True if should regenerate, False if can reuse
        """
        analytics = visual_metadata.get("analytics", {})

        # Marks conversion rate
        marks_conversion = analytics.get("marks_conversion", 0.0)
        if marks_conversion < 0.7:
            return True

        # Screenshot popularity
        screenshot_count = analytics.get("screenshots", 0)
        created_at_str = visual_metadata.get("created_at")

        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str)
                age_days = (datetime.now() - created_at).days

                # Not popular enough for age
                if screenshot_count < 10 and age_days > 30:
                    return True

                # Too old - techniques have improved
                if age_days > 180:
                    return True

            except (ValueError, TypeError):
                pass

        # Friend test score
        friend_score = analytics.get("friend_test_score", 0)
        if friend_score < 6:
            return True

        return False

    def save_visual(
        self,
        question: str,
        marks: int,
        svg: str,
        metadata: Dict[str, Any],
        subject: str = "cs",
        friend_test_score: int = 0
    ) -> str:
        """
        Cache generated visual for future reuse

        Args:
            question: Question text
            marks: Total marks
            svg: Generated SVG code
            metadata: Visual metadata (metaphors, hacks, etc.)
            subject: Subject category
            friend_test_score: Score from friend test (0-8)

        Returns:
            Fingerprint ID of saved visual
        """
        fingerprint = self._create_fingerprint(question, marks)
        subject_path = self.base_path / subject
        subject_path.mkdir(exist_ok=True)

        visual_data = {
            "fingerprint": fingerprint,
            "question": question,
            "marks": marks,
            "svg": svg,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "analytics": {
                "screenshots": 0,
                "marks_conversion": 0.0,
                "views": 0,
                "friend_test_score": friend_test_score,
                "shares": 0
            },
            "version": "2.0"  # Track version for future migrations
        }

        visual_file = subject_path / f"{fingerprint}.json"

        with open(visual_file, 'w', encoding='utf-8') as f:
            json.dump(visual_data, f, indent=2, ensure_ascii=False)

        return fingerprint

    def update_analytics(
        self,
        fingerprint: str,
        subject: str = "cs",
        screenshots: Optional[int] = None,
        marks_conversion: Optional[float] = None,
        views: Optional[int] = None
    ) -> bool:
        """
        Update analytics for an existing visual

        Args:
            fingerprint: Visual fingerprint ID
            subject: Subject category
            screenshots: New screenshot count
            marks_conversion: Updated conversion rate
            views: New view count

        Returns:
            True if updated successfully
        """
        visual_file = self.base_path / subject / f"{fingerprint}.json"

        if not visual_file.exists():
            return False

        try:
            with open(visual_file, encoding='utf-8') as f:
                visual_data = json.load(f)

            # Update analytics
            analytics = visual_data.get("analytics", {})

            if screenshots is not None:
                analytics["screenshots"] = screenshots

            if marks_conversion is not None:
                analytics["marks_conversion"] = marks_conversion

            if views is not None:
                analytics["views"] = views

            visual_data["analytics"] = analytics
            visual_data["last_updated"] = datetime.now().isoformat()

            with open(visual_file, 'w', encoding='utf-8') as f:
                json.dump(visual_data, f, indent=2, ensure_ascii=False)

            return True

        except (json.JSONDecodeError, IOError):
            return False

    def get_library_stats(self, subject: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about the visual library

        Args:
            subject: Optional subject filter

        Returns:
            Dict with library statistics
        """
        if subject:
            subjects = [subject]
        else:
            subjects = ["cs", "physics", "math", "chemistry", "biology"]

        total_visuals = 0
        total_views = 0
        total_screenshots = 0
        high_performers = []

        for subj in subjects:
            subj_path = self.base_path / subj
            if not subj_path.exists():
                continue

            for visual_file in subj_path.glob("*.json"):
                try:
                    with open(visual_file, encoding='utf-8') as f:
                        data = json.load(f)

                    total_visuals += 1
                    analytics = data.get("analytics", {})
                    total_views += analytics.get("views", 0)
                    total_screenshots += analytics.get("screenshots", 0)

                    # Track high performers (friend score >= 7)
                    if analytics.get("friend_test_score", 0) >= 7:
                        high_performers.append({
                            "fingerprint": data["fingerprint"],
                            "question": data["question"][:60],
                            "score": analytics["friend_test_score"]
                        })

                except (json.JSONDecodeError, IOError):
                    continue

        return {
            "total_visuals": total_visuals,
            "total_views": total_views,
            "total_screenshots": total_screenshots,
            "avg_screenshots_per_visual": round(total_screenshots / total_visuals, 2) if total_visuals else 0,
            "high_performers": sorted(high_performers, key=lambda x: x["score"], reverse=True)[:10]
        }

    def search_similar(
        self,
        concept_keywords: List[str],
        subject: str = "cs",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for visuals with similar concepts

        Args:
            concept_keywords: List of keywords to match
            subject: Subject category
            limit: Maximum results

        Returns:
            List of matching visual metadata
        """
        results = []
        subject_path = self.base_path / subject

        if not subject_path.exists():
            return []

        keywords_lower = [kw.lower() for kw in concept_keywords]

        for visual_file in subject_path.glob("*.json"):
            try:
                with open(visual_file, encoding='utf-8') as f:
                    data = json.load(f)

                question_lower = data["question"].lower()

                # Count keyword matches
                matches = sum(1 for kw in keywords_lower if kw in question_lower)

                if matches >= 1:
                    results.append({
                        "fingerprint": data["fingerprint"],
                        "question": data["question"],
                        "marks": data["marks"],
                        "match_score": matches,
                        "friend_test_score": data.get("analytics", {}).get("friend_test_score", 0)
                    })

            except (json.JSONDecodeError, IOError):
                continue

        # Sort by match score and friend test score
        results.sort(key=lambda x: (x["match_score"], x["friend_test_score"]), reverse=True)
        return results[:limit]

    def cleanup_low_performers(self, subject: str = "cs", min_score: int = 4, min_age_days: int = 30) -> int:
        """
        Remove visuals with low friend test scores that are old enough

        Args:
            subject: Subject category
            min_score: Minimum friend test score to keep
            min_age_days: Minimum age before deletion

        Returns:
            Number of visuals removed
        """
        subject_path = self.base_path / subject
        removed_count = 0

        if not subject_path.exists():
            return 0

        for visual_file in subject_path.glob("*.json"):
            try:
                with open(visual_file, encoding='utf-8') as f:
                    data = json.load(f)

                # Check friend test score
                friend_score = data.get("analytics", {}).get("friend_test_score", 0)

                if friend_score >= min_score:
                    continue  # Keep high performers

                # Check age
                created_at_str = data.get("created_at")
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                    age_days = (datetime.now() - created_at).days

                    if age_days >= min_age_days:
                        visual_file.unlink()  # Delete file
                        removed_count += 1

            except (json.JSONDecodeError, IOError, ValueError):
                continue

        return removed_count


# Convenience functions
def get_or_generate_visual(
    question: str,
    marks: int,
    generator_func,
    subject: str = "cs",
    **generator_kwargs
) -> Dict[str, Any]:
    """
    Check library first, generate if not found

    Args:
        question: Question text
        marks: Total marks
        generator_func: Function to call if visual not cached
        subject: Subject category
        **generator_kwargs: Additional args for generator

    Returns:
        Visual data dict with 'source' indicating 'cached' or 'generated'
    """
    library = VisualLibrary()

    # Try to find existing
    existing = library.find_existing(question, marks, subject)

    if existing:
        existing["source"] = "cached"
        return existing

    # Generate new
    result = generator_func(question=question, **generator_kwargs)

    # Cache it (if it has friend test score)
    if "friend_test_score" in result:
        library.save_visual(
            question=question,
            marks=marks,
            svg=result["svg"],
            metadata=result,
            subject=subject,
            friend_test_score=result["friend_test_score"]
        )

    result["source"] = "generated"
    return result
