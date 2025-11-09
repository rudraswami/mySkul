"""
Metaphor Generation API
POST /api/metaphors/generate
Generates 3–5 metaphors (5‑Muse), ranks top 3, and returns a blended SVG sketch.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/metaphors", tags=["Metaphors"])


class GenerateRequest(BaseModel):
    question: str
    student_dna: Optional[Dict[str, Any]] = None
    n_candidates: Optional[int] = Field(default=5, ge=3, le=5)
    locale: Optional[str] = None
    script: Optional[str] = Field(default="latin", description="'latin' or 'native' (when available)")


class Candidate(BaseModel):
    name: str
    category: str
    text: str
    score: float
    scores: Dict[str, float]


class Blended(BaseModel):
    svg: str
    metaphors: List[Dict[str, str]]
    size_kb: float
    validated: bool


class GenerateResponse(BaseModel):
    finalists: List[Candidate]
    blended: Blended
    telemetry: Dict[str, Any]
    micro_check: Dict[str, Any]


def _extract_marks_type(text: str) -> tuple[int, str]:
    import re
    m = re.search(r"(\d+)\s*marks?", text.lower())
    marks = None
    if m:
        try:
            marks = int(m.group(1))
        except Exception:
            marks = None
    if marks is None:
        marks = 3
    mtype = "short" if marks <= 2 else ("medium" if marks <= 5 else "long")
    return marks, mtype


@router.post("/generate", response_model=GenerateResponse)
async def generate_metaphors(req: GenerateRequest):
    try:
        from services.muse_generator import generate_5_muse_candidates
        from services.metaphor_selector import select_top_metaphors
        from services.handdrawn_sketch import build_handdrawn_svg
        from services.visual_validation import validate_visual
        from services.concept_deconstruction import deconstruct
        from services.micro_check import make_micro_check
        from services.i18n import get_labels
        # Step 1: deconstruct concept
        concept = deconstruct(req.question, req.student_dna or {})
        marks = concept.marks.total_marks or 3
        marks_type = concept.marks.type

        # 5‑Muse candidates
        cands = generate_5_muse_candidates(req.question, req.student_dna or {})
        # Respect n_candidates (3–5)
        if req.n_candidates and len(cands) > req.n_candidates:
            cands = cands[: req.n_candidates]

        # Select top 3 (guided by marks type)
        top3 = select_top_metaphors(req.question, cands, req.student_dna or {}, marks_type)

        # Build blended SVG
        labels = get_labels(req.locale, req.script)
        svg = build_handdrawn_svg(
            req.question,
            top3,
            marks=marks,
            metadata={"concept": req.question},
            labels=labels,
        )
        ok = validate_visual(svg)

        finalists: List[Candidate] = [
            Candidate(
                name=m["name"],
                category=m["category"],
                text=m["text"],
                score=float(m["scores"]["total"]),
                scores={
                    "intuitiveness": float(m["scores"]["intuitiveness"]),
                    "exam_relevance": float(m["scores"]["exam_relevance"]),
                    "cultural_fit": float(m["scores"]["cultural_fit"]),
                    "freshness": float(m["scores"]["freshness"]),
                    "total": float(m["scores"]["total"]),
                },
            )
            for m in top3
        ]

        blended = Blended(
            svg=svg,
            metaphors=[{"name": m.name, "category": m.category} for m in finalists],
            size_kb=round(len(svg) / 1024.0, 2),
            validated=ok,
        )

        telemetry = {
            "generated_candidates": len(cands),
            "returned_finalists": len(finalists),
            "marks": marks,
            "marks_type": marks_type,
            "palette": ["#FF9933", "#138808", "#000080"],
            "core_actions": concept.core_actions,
            "domain": concept.domain,
            "locale": req.locale or "en-IN",
            "script": req.script or "latin",
        }
        micro = make_micro_check(
            req.question,
            concept.core_actions,
            [m.dict() for m in finalists],
            domain=concept.domain,
            locale=req.locale,
        )

        return GenerateResponse(finalists=finalists, blended=blended, telemetry=telemetry, micro_check=micro)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/metaphors/generate failed: {e}")
