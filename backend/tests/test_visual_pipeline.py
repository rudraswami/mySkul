import sys
import os
from pathlib import Path

# Ensure package import works in local env (repo root + backend package)
ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

from backend.services.metaphor_engine import select_metaphors
from backend.services.dynamic_visual_sketch import create_visual_sketch
from backend.utils.visual_validator import validate_visual


def test_select_metaphors_returns_three():
    res = select_metaphors("Explain recursion with base case [2+4]", {"interests": ["cricket"], "gender": "M"})
    top = res["top"]
    assert len(top) >= 3 or len(res["candidates"]) >= 3


def test_create_visual_and_validate():
    out = create_visual_sketch("Explain ionic bond", {"interests": ["farming", "cricket"], "gender": "M"})
    svg = out["svg"]
    assert isinstance(svg, str) and svg.startswith("<svg") and svg.endswith("</svg>")
    assert validate_visual(svg)
