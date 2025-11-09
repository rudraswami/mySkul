"""
Test Suite for Emotional Layer Features
Tests Hinglish annotations, topper hacks, PYQ matching, and Friend Test
"""
import pytest
from services.hinglish_annotations import (
    generate_annotation,
    get_common_mistake,
    generate_marks_annotation,
    get_regional_metaphor_label
)
from services.topper_hack_selector import TopperHackSelector, get_topper_hack
from services.pyq_matcher import PYQMatcher, PYQReference
from services.friend_test import friend_test_validation, quick_friend_test
from services.visual_library import VisualLibrary


class TestHinglishAnnotations:
    """Test Hinglish annotation generation"""

    def test_generate_warning_annotation(self):
        """Test warning annotation with marks"""
        result = generate_annotation(
            concept="recursion",
            annotation_type="warning",
            region="North",
            marks=3
        )

        assert "⚠️" in result
        assert "3 marks" in result.lower() or "marks" in result.lower()

    def test_regional_variation(self):
        """Test different regional annotations"""
        north = generate_annotation("concept", "attention", region="North")
        south = generate_annotation("concept", "attention", region="South")

        # Should be different
        assert north != south
        assert len(north) > 0
        assert len(south) > 0

    def test_common_mistake(self):
        """Test common mistake detection"""
        mistake = get_common_mistake("recursion", region="North")

        assert "❌" in mistake
        assert len(mistake) > 10  # Should have substantial content

    def test_marks_annotation(self):
        """Test marks breakdown"""
        result = generate_marks_annotation(
            total_marks=5,
            parts=[2, 3],
            region="North"
        )

        assert "5" in result
        assert "💯" in result or "marks" in result.lower()

    def test_regional_metaphor_labels(self):
        """Test metaphor localization"""
        north_family = get_regional_metaphor_label("family", "North")
        south_family = get_regional_metaphor_label("family", "South")

        assert len(north_family) > 0
        assert len(south_family) > 0
        # Should have regional flavor
        assert north_family != "family"


class TestTopperHacks:
    """Test topper hack selection and formatting"""

    def test_hack_selection_recursion(self):
        """Test finding hack for recursion"""
        selector = TopperHackSelector()
        hack = selector.get_hack(["recursion", "base", "case"])

        assert hack is not None
        assert "hack" in hack
        assert "rank" in hack
        assert len(hack["hack"]) > 20

    def test_hack_with_board_filter(self):
        """Test board-specific hack selection"""
        selector = TopperHackSelector()
        hack = selector.get_hack(["binary", "search"], board="CBSE")

        assert hack is not None
        if hack["board"] != "All boards":
            assert hack["board"] == "CBSE"

    def test_hack_formatting(self):
        """Test hack annotation formatting"""
        selector = TopperHackSelector()
        hack = selector.get_hack(["stack", "push", "pop"])

        if hack:
            formatted = selector.format_hack_annotation(hack)
            assert "🏆" in formatted
            assert hack["rank"] in formatted
            assert "marks" in formatted.lower()

    def test_quick_hack_access(self):
        """Test convenience function"""
        result = get_topper_hack("recursion with base case", board="CBSE")

        # May or may not find, but should not error
        assert result is None or isinstance(result, str)

    def test_get_all_hacks_for_concept(self):
        """Test getting all hacks for a concept"""
        selector = TopperHackSelector()
        hacks = selector.get_all_hacks_for_concept("recursion")

        assert isinstance(hacks, list)
        if hacks:
            assert "hack" in hacks[0]


class TestPYQMatcher:
    """Test PYQ pattern matching"""

    def test_find_similar_recursion(self):
        """Test finding PYQs for recursion"""
        matcher = PYQMatcher()
        pyqs = matcher.find_similar_pyqs(
            question="Explain recursion with base case",
            min_similarity=0.7
        )

        assert isinstance(pyqs, list)
        # May or may not find matches, but should not error

    def test_pyq_reference_dataclass(self):
        """Test PYQReference dataclass"""
        ref = PYQReference(
            board="CBSE",
            year=2023,
            question_number="Q12",
            marks=3,
            similarity=0.95
        )

        assert ref.board == "CBSE"
        assert ref.year == 2023
        assert str(ref) == "CBSE 2023 Q12 (3m)"

    def test_board_filter(self):
        """Test PYQ filtering by board"""
        matcher = PYQMatcher()
        pyqs = matcher.find_similar_pyqs(
            question="binary search algorithm",
            board="CBSE"
        )

        # All results should be from CBSE
        for pyq in pyqs:
            assert pyq.board == "CBSE"

    def test_pyq_formatting(self):
        """Test PYQ annotation formatting"""
        matcher = PYQMatcher()
        ref = PYQReference(
            board="CBSE",
            year=2023,
            question_number="Q12",
            marks=3,
            similarity=0.95
        )

        compact = matcher.format_pyq_annotation(ref, style="compact")
        detailed = matcher.format_pyq_annotation(ref, style="detailed")

        assert "📌" in compact
        assert "CBSE" in compact
        assert len(detailed) > len(compact)

    def test_pattern_stats(self):
        """Test getting pattern statistics"""
        matcher = PYQMatcher()
        stats = matcher.get_pattern_stats()

        assert "total_patterns" in stats
        assert "total_references" in stats
        assert isinstance(stats["total_patterns"], int)


class TestFriendTest:
    """Test Friend Test validation"""

    def test_basic_friend_test(self):
        """Test basic friend test validation"""
        # Sample SVG with emotional elements
        svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360">
            <path d="M10,10 L100,100" stroke="#FF9933" />
            <path d="M20,20 L110,110" stroke="#138808" />
            <path d="M30,30 L120,120" stroke="#000080" />
            <path d="M40,40 L130,130" />
            <path d="M50,50 L140,140" />
            <text>🏆 AIR 124 trick: base case pehle</text>
            <text>❌ 90% yaha bhoolte hain</text>
            <text>💯 Marks: 3</text>
            <text>📌 CBSE 2023 Q12</text>
        </svg>
        """

        metadata = {
            "metaphors_used": ["family", "food", "cricket"],
            "topper_hack": "base case pehle likhna",
            "topper_rank": "AIR 124 (JEE 2023)",
            "has_emotional_content": True
        }

        result = friend_test_validation(svg, metadata)

        assert "tests" in result
        assert "score" in result
        assert "passed" in result
        assert isinstance(result["score_value"], int)
        assert result["score_value"] >= 0
        assert result["score_value"] <= 8

    def test_screenshot_worthy_check(self):
        """Test visual appeal detection"""
        svg_good = """<svg>
            <text>🏆 AIR 124</text>
            <text>📌 CBSE 2023</text>
            <text>sir ne bola</text>
            <path stroke="#FF9933" />
            <path stroke="#138808" />
        </svg>"""

        svg_bad = "<svg><circle r='10'/></svg>"

        result_good = friend_test_validation(svg_good, {"has_emotional_content": True})
        result_bad = friend_test_validation(svg_bad, {})

        # Good should score higher
        assert result_good["score_value"] >= result_bad["score_value"]

    def test_file_size_check(self):
        """Test file size validation"""
        small_svg = "<svg>" + "A" * 1000 + "</svg>"
        large_svg = "<svg>" + "A" * 20000 + "</svg>"

        result_small = friend_test_validation(small_svg, {})
        result_large = friend_test_validation(large_svg, {})

        # Small should pass size test
        assert result_small["tests"]["whatsapp_ready"]
        assert not result_large["tests"]["whatsapp_ready"]

    def test_quick_friend_test(self):
        """Test quick pass/fail test"""
        svg_good = """<svg>
            <path d="M10,10 L20.5,20.3" />
            <path d="M30,30 L40,40" />
            <path d="M50,50 L60,60" />
            <path d="M70,70 L80,80" />
            <path d="M90,90 L100,100" />
            <text>🏆 marks sir</text>
        </svg>"""

        result = quick_friend_test(svg_good)
        assert isinstance(result, bool)

    def test_feedback_generation(self):
        """Test feedback for improvements"""
        svg_minimal = "<svg><path d='M10,10 L20,20'/></svg>"

        result = friend_test_validation(svg_minimal, {})

        assert "feedback" in result
        assert len(result["feedback"]) > 0
        # Should have suggestions for improvement
        assert any("❌" in fb for fb in result["feedback"])


class TestVisualLibrary:
    """Test visual caching and reuse"""

    def test_fingerprint_generation(self):
        """Test fingerprint creation"""
        library = VisualLibrary()

        fp1 = library._create_fingerprint("Explain recursion", 3)
        fp2 = library._create_fingerprint("Explain recursion", 3)
        fp3 = library._create_fingerprint("Explain iteration", 3)

        # Same question should give same fingerprint
        assert fp1 == fp2
        # Different question should give different fingerprint
        assert fp1 != fp3
        # Should be 12 characters
        assert len(fp1) == 12

    def test_save_and_find(self):
        """Test saving and retrieving visuals"""
        library = VisualLibrary()

        test_svg = "<svg>test</svg>"
        test_metadata = {
            "metaphors_used": ["family"],
            "topper_hack": "test hack"
        }

        # Save
        fingerprint = library.save_visual(
            question="Test question",
            marks=3,
            svg=test_svg,
            metadata=test_metadata,
            subject="cs",
            friend_test_score=7
        )

        assert len(fingerprint) == 12

        # Find
        found = library.find_existing("Test question", 3, subject="cs")

        assert found is not None
        assert found["svg"] == test_svg
        assert found["metadata"]["metaphors_used"] == ["family"]

    def test_should_regenerate(self):
        """Test regeneration logic"""
        library = VisualLibrary()

        # Low friend score - should regenerate
        low_score = {
            "analytics": {"friend_test_score": 3}
        }
        assert library._should_regenerate(low_score)

        # High friend score - should keep
        high_score = {
            "analytics": {"friend_test_score": 8, "screenshots": 50},
            "created_at": "2025-01-09T00:00:00"
        }
        assert not library._should_regenerate(high_score)

    def test_library_stats(self):
        """Test library statistics"""
        library = VisualLibrary()
        stats = library.get_library_stats(subject="cs")

        assert "total_visuals" in stats
        assert "total_views" in stats
        assert "high_performers" in stats
        assert isinstance(stats["total_visuals"], int)

    def test_search_similar(self):
        """Test searching for similar visuals"""
        library = VisualLibrary()

        results = library.search_similar(
            concept_keywords=["recursion", "base"],
            subject="cs",
            limit=5
        )

        assert isinstance(results, list)
        assert len(results) <= 5


class TestIntegration:
    """Integration tests for the complete flow"""

    def test_complete_visual_generation_flow(self):
        """Test end-to-end visual generation with all features"""
        from services.dynamic_visual_sketch import create_visual_sketch

        result = create_visual_sketch(
            question="Explain recursion with base case [3 marks]",
            student_profile={
                "locale_language": "hi-IN",
                "board": "CBSE",
                "level": "class_12"
            }
        )

        # Check all expected fields
        assert "svg" in result
        assert "metaphors_used" in result
        assert "estimated_marks" in result
        assert "topper_hack" in result
        assert "pyq_references" in result
        assert "region" in result
        assert "has_emotional_content" in result

        # Validate SVG structure
        svg = result["svg"]
        assert "<svg" in svg
        assert "</svg>" in svg

        # Check for emotional elements
        assert len(result["metaphors_used"]) >= 2

    def test_friend_test_integration(self):
        """Test Friend Test on generated visual"""
        from services.dynamic_visual_sketch import create_visual_sketch

        result = create_visual_sketch(
            question="Explain binary search [4 marks]",
            student_profile={"locale_language": "hi-IN", "board": "CBSE"}
        )

        friend_result = friend_test_validation(
            svg=result["svg"],
            metadata=result,
            concept="binary search"
        )

        # Should get a score
        assert friend_result["score_value"] >= 0
        assert friend_result["score_value"] <= 8

        # Should have feedback
        assert len(friend_result["feedback"]) > 0

        # Friend result with score >= 6 should pass
        if friend_result["score_value"] >= 6:
            assert friend_result["passed"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
