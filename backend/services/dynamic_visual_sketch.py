from __future__ import annotations

"""
Dynamic Visual Sketch Engine (Friend Explaining at 2 AM Feel)

Implements PRD Step 3 with emotional connection layer.
Now includes: Hinglish annotations, topper hacks, and PYQ references.

Constraints:
- Pure SVG (no JS), path-only shapes (no <circle>/<line>/<rect>), no gradients
- Indian palette: Saffron (#FF9933), Green (#138808), Navy (#000080)
- 3 layers: L1 scientific skeleton, L2 exam annotations (with emotion!), L3 cultural metaphor blend
- 5-step progressive drawing (SMIL; step1 auto, steps 2–5 on click)
"""

import random
import re
from typing import Any, Dict, List, Optional, Tuple

from .metaphor_engine import select_metaphors, ConceptBundle, MetaphorCandidate, StudentDNA
from .animation_library import resolve_animation_visual
from .hinglish_annotations import generate_annotation, get_common_mistake, generate_marks_annotation
from .topper_hack_selector import TopperHackSelector
from .pyq_matcher import PYQMatcher


PALETTE = {"saffron": "#FF9933", "green": "#138808", "navy": "#000080", "yellow": "#FFD54F"}


def _jitter_points(points: List[Tuple[float, float]], intensity: float = 2.0) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    for x, y in points:
        out.append((x + random.uniform(-intensity, intensity), y + random.uniform(-intensity, intensity)))
    return out


def _path_from_points(points: List[Tuple[float, float]]) -> str:
    parts = [f"M{points[0][0]:.1f},{points[0][1]:.1f}"]
    for x, y in points[1:]:
        parts.append(f"Q{(x+points[0][0]) / 2:.1f},{(y+points[0][1]) / 2:.1f} {x:.1f},{y:.1f}")
    return " ".join(parts)


def _text(x: float, y: float, txt: str, color: str, size: float = 12) -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="system-ui, Arial" font-size="{size}" fill="{color}">{_escape(txt)}</text>'


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _layer_skeleton(bundle: ConceptBundle) -> str:
    # Minimal diagram: two boxes as paths and arrows (as paths)
    stroke = PALETTE["navy"]
    imp1 = _path_from_points(_jitter_points([(60, 120), (200, 120), (200, 170), (60, 170), (60, 120)], 2.5))
    imp2 = _path_from_points(_jitter_points([(260, 120), (400, 120), (400, 170), (260, 170), (260, 120)], 2.5))
    arrow = _path_from_points(_jitter_points([(200, 145), (230, 140), (260, 145)], 2.0))
    txt1 = _text(90, 145, (bundle.entities[:1] or ["Part A"])[0], stroke, 12)
    txt2 = _text(290, 145, (bundle.entities[1:2] or ["Part B"])[0], stroke, 12)
    return (
        f'<path id="l1_box1" d="{imp1}" stroke="{stroke}" stroke-width="1.6" fill="none" />'
        f'<path id="l1_box2" d="{imp2}" stroke="{stroke}" stroke-width="1.5" fill="none" />'
        f'<path id="l1_arrow" d="{arrow}" stroke="{stroke}" stroke-width="1.8" fill="none" />'
        f"{txt1}{txt2}"
    )


def _layer_exam(
    bundle: ConceptBundle,
    student_dna: Optional[StudentDNA] = None,
    topper_selector: Optional[TopperHackSelector] = None,
    pyq_matcher: Optional[PYQMatcher] = None
) -> str:
    """Enhanced Layer 2 with Hinglish, topper hacks, and PYQ references"""
    # Initialize services if not provided
    if topper_selector is None:
        topper_selector = TopperHackSelector()
    if pyq_matcher is None:
        pyq_matcher = PYQMatcher()

    # Determine region from student DNA
    region = "North"
    if student_dna and student_dna.locale_language:
        locale_map = {
            "hi": "North", "pa": "North", "ur": "North",
            "ta": "South", "te": "South", "kn": "South", "ml": "South",
            "mr": "West", "gu": "West",
            "bn": "East", "or": "East", "as": "East"
        }
        lang_code = student_dna.locale_language[:2].lower()
        region = locale_map.get(lang_code, "North")

    # Yellow sticky note background
    stroke = PALETTE["navy"]
    note = _path_from_points(_jitter_points([(430, 90), (560, 95), (555, 190), (425, 185), (430, 90)], 2.5))

    # Marks annotation with Hinglish
    marks_text = generate_marks_annotation(
        total_marks=bundle.marks_distribution["total"],
        parts=bundle.marks_distribution.get("parts", []),
        region=region
    )

    # Common mistake warning
    concept = bundle.entities[0] if bundle.entities else "concept"
    mistake = get_common_mistake(concept, region)

    # Topper hack
    hack_obj = topper_selector.get_hack(
        concept_keywords=bundle.entities,
        board=student_dna.board if student_dna else None,
        level=student_dna.level if student_dna else None
    )

    # PYQ references
    pyqs = pyq_matcher.find_similar_pyqs(
        question=bundle.question,
        board=student_dna.board if student_dna else None,
        max_results=1  # Only show top match for space
    )

    # Build SVG text elements
    y_offset = 105
    elements = []

    # Marks
    elements.append(_text(440, y_offset, marks_text, stroke, 11))
    y_offset += 18

    # Common mistake
    if len(mistake) < 50:  # Short enough to fit
        elements.append(_text(440, y_offset, mistake, stroke, 9))
        y_offset += 16

    # Topper hack (split into multiple lines if needed)
    if hack_obj:
        hack_line1 = f"🏆 {hack_obj['rank']}:"
        elements.append(_text(440, y_offset, hack_line1, stroke, 9))
        y_offset += 14

        hack_line2 = hack_obj['hack'][:45] + "..." if len(hack_obj['hack']) > 45 else hack_obj['hack']
        elements.append(_text(440, y_offset, hack_line2, stroke, 8))
        y_offset += 14

    # PYQ reference
    if pyqs:
        pyq = pyqs[0]
        pyq_text = f"📌 {pyq.board} {pyq.year} {pyq.question_number} ({int(pyq.similarity*100)}%)"
        elements.append(_text(440, y_offset, pyq_text, stroke, 9))

    return f'<path id="l2_note" d="{note}" stroke="{stroke}" stroke-width="1.3" fill="{PALETTE["yellow"]}" />{"".join(elements)}'


def _layer_culture_blended(
    primary: MetaphorCandidate,
    secondary: MetaphorCandidate,
    tertiary: MetaphorCandidate,
    region: str = "North"
) -> str:
    """Enhanced Layer 3: All metaphors blended at low opacity with icons"""
    from .hinglish_annotations import get_regional_metaphor_label

    # Create 3 overlapping organic blob shapes
    metaphors = [primary, secondary, tertiary]
    colors = [PALETTE["saffron"], PALETTE["green"], PALETTE["navy"]]

    svg_parts = ['<g id="l3_meta" opacity="0.10">']

    # Metaphor icons for better visual appeal
    icon_map = {
        "family": "👨‍👩‍👦",
        "food": "🍲",
        "cricket": "🏏",
        "bollywood": "🎬",
        "gaming": "🎮"
    }

    for i, (metaphor, color) in enumerate(zip(metaphors, colors)):
        # Create organic blob shape for each metaphor (overlapping)
        x_offset = 60 + (i * 160)
        y_base = 220 + (i * 8)  # Slight vertical offset for depth

        # Wavy blob path (more organic shapes)
        blob_points = [
            (x_offset, y_base),
            (x_offset + 95, y_base - 12),
            (x_offset + 115, y_base + 25),
            (x_offset + 90, y_base + 55),
            (x_offset + 25, y_base + 45),
            (x_offset, y_base)
        ]

        jittered = _jitter_points(blob_points, 4.0)  # More jitter for hand-drawn feel
        path = _path_from_points(jittered)

        # Add metaphor shape with fill
        svg_parts.append(
            f'<path d="{path}" stroke="{color}" stroke-width="1.6" '
            f'fill="{color}" fill-opacity="0.25" />'
        )

        # Add icon + label
        icon = icon_map.get(metaphor.muse, "•")
        label = get_regional_metaphor_label(metaphor.muse, region)

        svg_parts.append(
            _text(x_offset + 35, y_base + 28, f"{icon} {label}", color, 9)
        )

    # Add blend explanation at bottom
    blend_text = f"Memory Hook: {primary.muse} + {secondary.muse} + {tertiary.muse} blend"
    svg_parts.append(_text(320, 295, blend_text, PALETTE["navy"], 7))

    svg_parts.append('</g>')
    return ''.join(svg_parts)


def _animation_block_interactive() -> str:
    """
    True tap-to-advance with invisible click zones and progress indicator
    5 steps: Auto-draw skeleton, then click to reveal each layer
    """
    return '''
    <style><![CDATA[
        text{pointer-events:none}
        .tap-zone{fill:transparent;cursor:pointer;opacity:0}
        .tap-zone:hover{opacity:0.05;fill:#FFD700}
        .progress-text{font-family:system-ui,Arial;font-size:11px;fill:#666}
    ]]></style>

    <!-- Progress indicator -->
    <text id="progress1" class="progress-text" x="10" y="350" visibility="visible">Tap anywhere to continue →</text>
    <text id="progress2" class="progress-text" x="10" y="350" visibility="hidden">Tap for arrows →</text>
    <text id="progress3" class="progress-text" x="10" y="350" visibility="hidden">Tap for exam tips →</text>
    <text id="progress4" class="progress-text" x="10" y="350" visibility="hidden">Tap for memory hooks →</text>
    <text id="progress5" class="progress-text" x="10" y="350" visibility="hidden">Complete! 🎯</text>

    <!-- Step 1: Auto-draw skeleton (boxes only) -->
    <set xlink:href="#layer1" attributeName="visibility" to="visible" begin="0.5s" />
    <set xlink:href="#l1_arrow" attributeName="visibility" to="hidden" begin="0.5s" />

    <!-- Tap zone 1: Click anywhere to show arrows -->
    <rect id="tap1" class="tap-zone" width="640" height="360" />
    <set xlink:href="#l1_arrow" attributeName="visibility" to="visible" begin="tap1.click" />
    <set xlink:href="#tap1" attributeName="display" to="none" begin="tap1.click" />
    <set xlink:href="#progress1" attributeName="visibility" to="hidden" begin="tap1.click" />
    <set xlink:href="#progress2" attributeName="visibility" to="visible" begin="tap1.click" />

    <!-- Tap zone 2: Show second box fully -->
    <rect id="tap2" class="tap-zone" width="640" height="360" display="none" />
    <set xlink:href="#tap2" attributeName="display" to="block" begin="tap1.click" />
    <set xlink:href="#l1_box2" attributeName="opacity" from="0.5" to="1.0" begin="tap2.click" dur="0.3s" fill="freeze" />
    <set xlink:href="#tap2" attributeName="display" to="none" begin="tap2.click" />
    <set xlink:href="#progress2" attributeName="visibility" to="hidden" begin="tap2.click" />
    <set xlink:href="#progress3" attributeName="visibility" to="visible" begin="tap2.click" />

    <!-- Tap zone 3: Show exam layer (yellow sticky note) -->
    <rect id="tap3" class="tap-zone" width="640" height="360" display="none" />
    <set xlink:href="#tap3" attributeName="display" to="block" begin="tap2.click" />
    <set xlink:href="#layer2" attributeName="visibility" to="visible" begin="tap3.click" />
    <animate xlink:href="#layer2" attributeName="opacity" from="0" to="1" begin="tap3.click" dur="0.4s" fill="freeze" />
    <set xlink:href="#tap3" attributeName="display" to="none" begin="tap3.click" />
    <set xlink:href="#progress3" attributeName="visibility" to="hidden" begin="tap3.click" />
    <set xlink:href="#progress4" attributeName="visibility" to="visible" begin="tap3.click" />

    <!-- Tap zone 4: Show metaphor layer (cultural blend) -->
    <rect id="tap4" class="tap-zone" width="640" height="360" display="none" />
    <set xlink:href="#tap4" attributeName="display" to="block" begin="tap3.click" />
    <set xlink:href="#layer3" attributeName="visibility" to="visible" begin="tap4.click" />
    <animate xlink:href="#l3_meta" attributeName="opacity" from="0" to="0.10" begin="tap4.click" dur="0.5s" fill="freeze" />
    <set xlink:href="#progress4" attributeName="visibility" to="hidden" begin="tap4.click" />
    <set xlink:href="#progress5" attributeName="visibility" to="visible" begin="tap4.click" />
    '''


def _metadata_defs(bundle: ConceptBundle, metaphors: List[MetaphorCandidate]) -> str:
    concept = _escape(" ".join(bundle.entities) or bundle.question[:40])
    marks = str(bundle.marks_distribution.get("total", 3))
    return (
        "<defs><metadata>"
        f"<concept>{concept}</concept>"
        f"<marks>{marks}</marks>"
        "<pyq>n/a</pyq>"
        f"<metaphors>{', '.join(m.muse for m in metaphors[:3])}</metaphors>"
        "</metadata></defs>"
    )


def create_visual_sketch(question: str, student_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Enhanced facade: question -> Emotionally resonant SVG visual sketch.

    Now includes:
    - Hinglish annotations (region-aware)
    - Topper hacks with rank attribution
    - PYQ pattern references
    - Multi-metaphor blending

    Returns dict with svg (string), metaphors used, and metadata
    """
    # Initialize services
    topper_selector = TopperHackSelector()
    pyq_matcher = PYQMatcher()

    # Select metaphors
    sel = select_metaphors(question, student_profile)
    bundle: ConceptBundle = sel["bundle"]
    top: List[MetaphorCandidate] = sel["top"]

    # Ensure 3 metaphors by padding if needed
    while len(top) < 3 and sel["candidates"]:
        top.append(sel["candidates"][len(top) % len(sel["candidates"])])

    # Convert student profile to StudentDNA if provided
    student_dna = None
    if student_profile:
        student_dna = StudentDNA(**student_profile)

    # Determine region for Hinglish
    region = "North"
    if student_dna and student_dna.locale_language:
        locale_map = {
            "hi": "North", "pa": "North", "ur": "North",
            "ta": "South", "te": "South", "kn": "South", "ml": "South",
            "mr": "West", "gu": "West",
            "bn": "East", "or": "East", "as": "East"
        }
        lang_code = student_dna.locale_language[:2].lower()
        region = locale_map.get(lang_code, "North")

    # Build layers with enhanced emotional content
    l1 = _layer_skeleton(bundle)
    l2 = _layer_exam(bundle, student_dna, topper_selector, pyq_matcher)
    l3 = _layer_culture_blended(top[0], top[1], top[2], region)
    anim = _animation_block_interactive()
    defs = _metadata_defs(bundle, top)

    # Assemble SVG
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 640 360" width="640" height="360">'
        f"{defs}"
        f'<g id="layer1" visibility="hidden">{l1}</g>'
        f'<g id="layer2" visibility="hidden">{l2}</g>'
        f'<g id="layer3" visibility="hidden">{l3}</g>'
        f"{anim}"
        f"</svg>"
    )

    # Get topper hack info for metadata
    hack_obj = topper_selector.get_hack(
        concept_keywords=bundle.entities,
        board=student_dna.board if student_dna else None
    )

    # Get PYQ info for metadata
    pyqs = pyq_matcher.find_similar_pyqs(
        question=question,
        board=student_dna.board if student_dna else None,
        max_results=3
    )

    # Optional Tier X: Animation descriptor (non-blocking; augments existing flow)
    depth_target = bundle.marks_distribution.get("depth_target") if bundle and bundle.marks_distribution else None
    animation = resolve_animation_visual(
        question=question,
        metaphors_used=[m.muse for m in top[:3]],
        depth_target=depth_target,
        topic_hint=None,
    )

    return {
        "svg": svg,
        "metaphors_used": [m.muse for m in top[:3]],
        "estimated_marks": bundle.marks_distribution.get("total", 3),
        "topper_hack": hack_obj["hack"] if hack_obj else None,
        "topper_rank": hack_obj["rank"] if hack_obj else None,
        "pyq_references": [f"{pyq.board} {pyq.year} {pyq.question_number}" for pyq in pyqs],
        "region": region,
        "has_emotional_content": True,
        # New optional field; consumers must treat as additive
        "animation": animation,
    }
