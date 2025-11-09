import sys
import os

# Ensure package import works in local env
sys.path.insert(0, os.getcwd())

from services.metaphor_engine import select_metaphors
from services.dynamic_visual_sketch import create_visual_sketch
from utils.visual_validator import validate_visual


def test_select_metaphors_returns_three():
    res = select_metaphors("Explain recursion with base case [2+4]", {"interests": ["cricket"], "gender": "M"})
    top = res["top"]
    assert len(top) >= 3 or len(res["candidates"]) >= 3


def test_create_visual_and_validate():
    out = create_visual_sketch("Explain ionic bond", {"interests": ["farming", "cricket"], "gender": "M"})
    svg = out["svg"]
    assert isinstance(svg, str) and svg.startswith("<svg") and svg.endswith("</svg>")
    assert validate_visual(svg)

