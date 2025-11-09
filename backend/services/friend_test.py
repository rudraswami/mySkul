"""
Friend Test - The Real Validation
8-point checklist for emotional connection and student engagement

This is the test that matters: Would a student screenshot this within 30 seconds
and WhatsApp it to 5 friends?
"""
from __future__ import annotations

import re
from typing import Dict, List, Any


def friend_test_validation(
    svg: str,
    metadata: Dict[str, Any],
    concept: str = ""
) -> Dict[str, Any]:
    """
    The ultimate test: Would a student screenshot this?

    8 criteria from the system prompt:
    1. Screenshot-worthy (visual appeal)
    2. WhatsApp-ready (file size, shareability)
    3. Hand-drawn feel (imperfection, jitter)
    4. Topper hack present (with specific attribution)
    5. Marks breakdown visible (exam-focused)
    6. Multi-metaphor blend (2-3 metaphors overlaid)
    7. Common mistake shown (specific warning)
    8. Instant load (performance)

    Args:
        svg: The SVG code to validate
        metadata: Visual metadata (metaphors, marks, etc.)
        concept: The concept being taught

    Returns:
        Dict with test results, score, and actionable feedback
    """

    tests = {
        "screenshot_worthy": _check_visual_appeal(svg, metadata),
        "whatsapp_ready": _check_shareability(svg),
        "hand_drawn_feel": _check_imperfection(svg),
        "topper_hack_present": _check_specific_hack(metadata),
        "marks_breakdown_visible": _check_marks_clarity(svg),
        "multi_metaphor_blend": _check_metaphor_count(metadata),
        "common_mistake_shown": _check_mistake_warning(svg),
        "instant_load": _check_performance(svg)
    }

    score = sum(tests.values())
    passed = score >= 6  # Need at least 6/8 to pass

    return {
        "tests": tests,
        "score": f"{score}/8",
        "score_value": score,
        "passed": passed,
        "feedback": _generate_feedback(tests),
        "recommendation": "Ship it! 🚀" if passed else "Needs more friend energy ⚡"
    }


def _check_visual_appeal(svg: str, metadata: Dict) -> bool:
    """Has colors, emojis, Hinglish text?"""
    # Check for emojis (emotional connection)
    emojis = ["⚠️", "📌", "🏆", "💡", "💯", "❌", "✓", "🎯", "📝", "👀"]
    has_emojis = sum(1 for emoji in emojis if emoji in svg) >= 3

    # Check for Hinglish or emotional keywords
    hinglish_keywords = ["yaar", "bhai", "sir", "madam", "ma'am", "kal exam", "marks", "trick"]
    has_hinglish = any(keyword in svg.lower() for keyword in hinglish_keywords)

    # Check for Indian color palette
    indian_colors = ["#FF9933", "#138808", "#000080"]
    has_colors = sum(1 for color in indian_colors if color in svg) >= 2

    # Check metadata for emotional content
    has_emotional_metadata = metadata.get("has_emotional_content", False)

    # Pass if at least 2 of 3 criteria met
    criteria_met = sum([has_emojis, has_hinglish or has_emotional_metadata, has_colors])
    return criteria_met >= 2


def _check_shareability(svg: str) -> bool:
    """File size reasonable for WhatsApp?"""
    size_bytes = len(svg.encode('utf-8'))
    size_kb = size_bytes / 1024

    # Must be under 10KB for instant sharing
    return size_kb <= 10.0


def _check_imperfection(svg: str) -> bool:
    """Looks hand-drawn, not computer-perfect?"""
    # Check for path elements (hand-drawn style)
    path_count = svg.count("<path")

    # Check for jitter-related patterns (varied coordinates)
    # Look for decimal coordinates which indicate jitter
    has_jitter = ".1f" in svg or ".0f" in svg

    # Check for NO forbidden shapes (circles, rects, lines)
    no_circles = "<circle" not in svg
    no_rects = svg.count("<rect") <= 5  # Allow up to 5 rects for tap zones
    no_lines = "<line" not in svg

    # Pass if has paths, some jitter, and avoids geometric shapes
    return path_count >= 5 and has_jitter and no_circles and no_lines


def _check_specific_hack(metadata: Dict) -> bool:
    """Has topper hack with rank attribution (not generic)?"""
    # Check if topper hack exists
    if "topper_hack" not in metadata and "topper_rank" not in metadata:
        return False

    topper_rank = str(metadata.get("topper_rank", ""))
    topper_hack = str(metadata.get("topper_hack", ""))

    # Must have specific rank attribution (AIR, State Topper, etc.)
    rank_indicators = ["AIR", "State", "Topper", "Rank", "%ile", "99"]
    has_attribution = any(indicator in topper_rank for indicator in rank_indicators)

    # Must have actual hack content
    has_content = len(topper_hack) > 20

    return has_attribution and has_content


def _check_marks_clarity(svg: str) -> bool:
    """Shows clear marks breakdown?"""
    # Check for marks-related text
    marks_indicators = ["marks", "💯", "Total:", "Marks:"]
    has_marks_text = any(indicator in svg for indicator in marks_indicators)

    # Check for numeric marks (e.g., "3 marks", "[2+3]")
    has_numbers = bool(re.search(r'\d+\s*marks?', svg, re.IGNORECASE))

    return has_marks_text or has_numbers


def _check_metaphor_count(metadata: Dict) -> bool:
    """Uses 2-3 metaphors, not just one?"""
    metaphors_used = metadata.get("metaphors_used", [])

    # Should have 2-3 distinct metaphors
    if not metaphors_used:
        return False

    unique_metaphors = len(set(metaphors_used))
    return 2 <= unique_metaphors <= 3


def _check_mistake_warning(svg: str) -> bool:
    """Mentions specific common mistake (not generic)?"""
    # Warning indicators
    warning_keywords = [
        "90%", "cut", "forget", "bhool", "galti", "mistake",
        "❌", "⚠️", "common", "lose marks", "deduct"
    ]

    matches = sum(1 for kw in warning_keywords if kw.lower() in svg.lower())

    # Need at least 2 indicators for specificity
    return matches >= 2


def _check_performance(svg: str) -> bool:
    """Loads instantly (under 10KB)?"""
    size_bytes = len(svg.encode('utf-8'))
    size_kb = size_bytes / 1024

    # Under 10KB = instant load on 4G
    return size_kb < 10.0


def _generate_feedback(tests: Dict[str, bool]) -> List[str]:
    """Generate actionable feedback for failed tests"""
    feedback = []

    if not tests["screenshot_worthy"]:
        feedback.append(
            "❌ Visual appeal: Add more emojis (🏆📌💡) and Hinglish phrases "
            "(yaar, bhai, kal exam hai)"
        )

    if not tests["whatsapp_ready"]:
        feedback.append(
            "❌ File size: Reduce to <10KB by optimizing paths and removing extra elements"
        )

    if not tests["hand_drawn_feel"]:
        feedback.append(
            "❌ Hand-drawn feel: Add more jitter to paths, avoid geometric shapes "
            "(circles/rects/lines)"
        )

    if not tests["topper_hack_present"]:
        feedback.append(
            "❌ Topper hack: Include specific hack with rank attribution "
            "(e.g., 'AIR 124 trick: ...')"
        )

    if not tests["marks_breakdown_visible"]:
        feedback.append(
            "❌ Marks clarity: Show clear marks breakdown with 💯 emoji "
            "(e.g., 'Total: 5 marks [2+3]')"
        )

    if not tests["multi_metaphor_blend"]:
        feedback.append(
            "❌ Metaphor blend: Use 2-3 distinct metaphors overlaid in Layer 3 "
            "(not just one)"
        )

    if not tests["common_mistake_shown"]:
        feedback.append(
            "❌ Mistake warning: Add specific common mistake "
            "(e.g., '90% yaha base case bhoolte hain ⚠️')"
        )

    if not tests["instant_load"]:
        feedback.append(
            "❌ Performance: Optimize to load instantly (target <10KB)"
        )

    if not feedback:
        feedback.append("✅ All tests passed! This visual has strong friend energy! 🎉")

    return feedback


def quick_friend_test(svg: str) -> bool:
    """
    Quick pass/fail friend test without detailed feedback

    Args:
        svg: SVG code to test

    Returns:
        True if passes (6+ criteria), False otherwise
    """
    # Quick checks
    has_emojis = svg.count("🏆") > 0 or svg.count("📌") > 0
    has_hinglish = "sir" in svg.lower() or "yaar" in svg.lower()
    is_small = len(svg.encode('utf-8')) < 10240  # 10KB
    has_paths = svg.count("<path") >= 5
    has_marks = "marks" in svg.lower() or "💯" in svg

    quick_score = sum([has_emojis, has_hinglish, is_small, has_paths, has_marks])
    return quick_score >= 4


def get_friend_score(svg: str, metadata: Dict) -> int:
    """
    Get numerical friend score (0-8)

    Args:
        svg: SVG code
        metadata: Visual metadata

    Returns:
        Score from 0 to 8
    """
    result = friend_test_validation(svg, metadata)
    return result["score_value"]


# Test templates for common scenarios
PASSING_CRITERIA = {
    "minimum_score": 6,
    "critical_tests": [
        "screenshot_worthy",
        "topper_hack_present",
        "common_mistake_shown"
    ],
    "nice_to_have": [
        "multi_metaphor_blend",
        "whatsapp_ready",
        "instant_load"
    ]
}
