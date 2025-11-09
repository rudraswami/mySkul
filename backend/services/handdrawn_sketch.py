"""
Hand‑Drawn SVG Sketch Engine (Professor Chalkboard feel)
Generates a compact SVG (<~10KB) with 3 layers and 5-step progressive animation.
Rules:
- Use only <path> and <text> for shapes (no <circle>/<rect>/<line>/gradients)
- Indian palette: Saffron (#FF9933), Green (#138808), Navy (#000080)
"""
from __future__ import annotations

import base64
import random
from typing import Any, Dict, List, Optional, Tuple


Palette = {
    "saffron": "#FF9933",
    "green": "#138808",
    "navy": "#000080",
    "yellow": "#FFEB3B",
    "black": "#000000",
}


def _jitter(x: float, y: float, intensity: float = 2.0) -> Tuple[float, float]:
    return (
        x + random.uniform(-intensity, intensity),
        y + random.uniform(-intensity, intensity),
    )


def _path(points: List[Tuple[float, float]], curve: bool = False) -> str:
    if not points:
        return ""
    cmds = []
    x0, y0 = points[0]
    cmds.append(f"M {x0:.1f} {y0:.1f}")
    for i in range(1, len(points)):
        x, y = points[i]
        if curve:
            # Quadratic curve control midway with small jitter
            cx, cy = (points[i - 1][0] + x) / 2.0, (points[i - 1][1] + y) / 2.0
            cmds.append(f"Q {cx:.1f} {cy:.1f} {x:.1f} {y:.1f}")
        else:
            cmds.append(f"L {x:.1f} {y:.1f}")
    return " ".join(cmds)


def _stroke_width() -> str:
    return f"{random.uniform(1.2, 1.8):.1f}"


def _sticky_note_path(x: float, y: float, w: float, h: float) -> str:
    # Draw a rough rectangle using paths with slight offsets
    p = []
    p.append(_path([_jitter(x, y), _jitter(x + w, y)], curve=True))
    p.append(_path([_jitter(x + w, y), _jitter(x + w, y + h)], curve=True))
    p.append(_path([_jitter(x + w, y + h), _jitter(x, y + h)], curve=True))
    p.append(_path([_jitter(x, y + h), _jitter(x, y)], curve=True))
    return " ".join(p)


def _marks_badge(marks: int) -> str:
    text = f"\uD83D\uDCA1 Total: {marks}/ {marks} marks" if marks else "\uD83D\uDCA1 Marks view"
    return text


def build_handdrawn_svg(
    question: str,
    top_metaphors: List[Dict[str, Any]],
    marks: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    labels: Optional[Dict[str, str]] = None,
) -> str:
    """Create a compact layered SVG with progressive animation.

    Returns raw SVG string (can be base64'd by caller if needed).
    """
    random.seed(42)  # deterministic jitter for caching
    width, height = 400, 300

    # Skeleton elements (Layer 1): a simple flow diagram with two nodes and an arrow
    n1 = [_jitter(60, 140), _jitter(140, 120), _jitter(140, 160), _jitter(60, 180), _jitter(60, 140)]
    n2 = [_jitter(240, 140), _jitter(320, 120), _jitter(320, 160), _jitter(240, 180), _jitter(240, 140)]
    arrow = _path([_jitter(150, 150), _jitter(235, 150)], curve=True)
    arrow_head = _path([_jitter(232, 146), _jitter(240, 150), _jitter(232, 154)], curve=False)

    # Exam annotations (Layer 2): sticky note and labels
    sticky = _sticky_note_path(20, 20, 160, 60)
    badge_text = _marks_badge(marks or 3)

    # Metaphor motifs (Layer 3): faint diagonal lanes + small motif strokes
    lanes = [
        _path([_jitter(10, 260), _jitter(390, 210)], curve=True),
        _path([_jitter(10, 280), _jitter(390, 230)], curve=True),
    ]

    # Metaphor captions (subtle, small)
    m_primary = top_metaphors[0]["name"] if top_metaphors else "Family"
    m_secondary = top_metaphors[1]["name"] if len(top_metaphors) > 1 else "Food"
    m_tertiary = top_metaphors[2]["name"] if len(top_metaphors) > 2 else "Cricket"

    # Assemble SVG
    svg_parts: List[str] = []
    svg_parts.append(
        f"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 {width} {height}'>"
    )

    # Metadata in <defs>
    meta = metadata or {}
    meta_concept = (meta.get("concept") or question)[:80]
    meta_marks = str(marks or 3)
    meta_muses = ",".join([m.get("category", "") for m in top_metaphors[:3]])
    svg_parts.append("<defs>")
    svg_parts.append(f"<concept>{_escape(meta_concept)}</concept>")
    svg_parts.append(f"<marks>{_escape(meta_marks)}</marks>")
    svg_parts.append(f"<metaphors>{_escape(meta_muses)}</metaphors>")
    svg_parts.append("</defs>")

    # Layer 3: Metaphor soul (opacity 0.1)
    svg_parts.append("<g id='layer3-metaphor' opacity='0.10'>")
    for l in lanes:
        svg_parts.append(
            f"<path d='{l}' stroke='{Palette['navy']}' stroke-width='{_stroke_width()}' fill='none'/>"
        )
    svg_parts.append(
        f"<text x='200' y='290' text-anchor='middle' font-size='8' fill='{Palette['navy']}'>"
        f"{_escape(m_primary)} + {_escape(m_secondary)} + {_escape(m_tertiary)}</text>"
    )
    svg_parts.append("</g>")

    # Layer 1: Scientific skeleton
    svg_parts.append("<g id='layer1-skeleton'>")
    svg_parts.append(
        f"<path id='node1' d='{_path(n1, curve=True)}' stroke='{Palette['saffron']}' stroke-width='{_stroke_width()}' fill='none'/>"
    )
    svg_parts.append(
        f"<path id='node2' d='{_path(n2, curve=True)}' stroke='{Palette['green']}' stroke-width='{_stroke_width()}' fill='none'/>"
    )
    svg_parts.append(
        f"<path id='edge' d='{arrow}' stroke='{Palette['black']}' stroke-width='{_stroke_width()}' fill='none'/>"
    )
    svg_parts.append(
        f"<path id='edge_head' d='{arrow_head}' stroke='{Palette['black']}' stroke-width='{_stroke_width()}' fill='none'/>"
    )
    concept_label = (labels or {}).get("concept", "Concept")
    answer_label = (labels or {}).get("answer", "Answer")
    svg_parts.append(
        f"<text x='100' y='120' font-size='11' fill='{Palette['saffron']}'>{_escape(concept_label)}</text>"
    )
    svg_parts.append(
        f"<text x='260' y='120' font-size='11' fill='{Palette['green']}'>{_escape(answer_label)}</text>"
    )
    svg_parts.append("</g>")

    # Layer 2: Exam annotations
    svg_parts.append("<g id='layer2-exam'>")
    svg_parts.append(
        f"<path d='{sticky}' stroke='{Palette['navy']}' stroke-width='{_stroke_width()}' fill='none'/>"
    )
    marks_label = (labels or {}).get("marks", "Marks")
    forget_label = (labels or {}).get("students_forget", "90% students forget this")
    topper_label = (labels or {}).get("topper_hack", "Topper hack: three keywords bold")
    svg_parts.append(
        f"<text x='30' y='40' font-size='10' fill='{Palette['navy']}'>{_escape(marks_label)}: {_escape(str(marks or 3))}</text>"
    )
    svg_parts.append(
        f"<text x='30' y='56' font-size='9' fill='{Palette['navy']}'>{_escape(forget_label)}</text>"
    )
    svg_parts.append(
        f"<text x='30' y='72' font-size='9' fill='{Palette['navy']}'>{_escape(topper_label)}</text>"
    )
    svg_parts.append("</g>")

    # Progressive animation (5 steps). Use SMIL begin times and IDs; taps can target IDs.
    svg_parts.append("<style> .hide{opacity:0} .show{opacity:1} </style>")
    # Step animations via SMIL animate opacity
    svg_parts.append(
        "<g id='animation'>"
        "<animate xlink:href='#layer1-skeleton' attributeName='opacity' from='0' to='1' dur='0.8s' begin='0.5s' fill='freeze'/>"
        "<animate xlink:href='#edge' attributeName='opacity' from='0' to='1' dur='0.6s' begin='1.5s' fill='freeze'/>"
        "<animate xlink:href='#layer2-exam' attributeName='opacity' from='0' to='1' dur='0.6s' begin='2.1s' fill='freeze'/>"
        "<animate xlink:href='#layer3-metaphor' attributeName='opacity' from='0' to='0.1' dur='0.6s' begin='2.7s' fill='freeze'/>"
        "</g>"
    )

    svg_parts.append("</svg>")
    return "".join(svg_parts)


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&apos;")
    )
