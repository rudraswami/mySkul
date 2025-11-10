"""
Visual Teaching Contract (v1)

Defines a minimal, question-agnostic schema for teaching visuals that the
frontend can render with small, reusable blocks. This avoids ad-hoc animation
types and guarantees a meaningful fallback visual for any question.
"""
from __future__ import annotations

from typing import Dict, List, Literal, Optional, TypedDict, Union


class TitleCard(TypedDict, total=False):
    type: Literal["title_card"]
    title: str
    subtitle: Optional[str]


class ConceptNode(TypedDict):
    id: str
    label: str


class ConceptNodes(TypedDict, total=False):
    type: Literal["concept_nodes"]
    nodes: List[ConceptNode]
    layout: Literal["row", "grid"]


class Relation(TypedDict, total=False):
    from_: str
    to: str
    label: Optional[str]
    style: Optional[Literal["direct", "inhibit", "double"]]


class RelationArrows(TypedDict, total=False):
    type: Literal["relation_arrows"]
    relations: List[Relation]


class EquationBlock(TypedDict, total=False):
    type: Literal["equation"]
    tex: str
    highlight: Optional[str]


class CompareSide(TypedDict, total=False):
    title: str
    points: List[str]


class CompareGrid(TypedDict, total=False):
    type: Literal["compare_grid"]
    left: CompareSide
    right: CompareSide


class WorkedStep(TypedDict, total=False):
    label: str
    detail: Optional[str]


class WorkedExample(TypedDict, total=False):
    type: Literal["worked_example"]
    steps: List[WorkedStep]
    icon: Optional[Literal["cricket", "train", "family", "food", "gaming"]]


class TipCard(TypedDict, total=False):
    type: Literal["tip_card"]
    text: str
    tip_type: Literal["mistake", "hack", "pyq", "exam"]


class TimelineItem(TypedDict, total=False):
    label: str
    icon: Optional[str]


class Timeline(TypedDict, total=False):
    type: Literal["timeline"]
    items: List[TimelineItem]


# New, richer blocks
class DefinitionCard(TypedDict, total=False):
    type: Literal["definition_card"]
    term: str
    definition: str


class LawItem(TypedDict, total=False):
    name: str
    summary: str


class LawList(TypedDict, total=False):
    type: Literal["law_list"]
    laws: List[LawItem]


class FlowEdge(TypedDict, total=False):
    from_: str
    to: str
    label: Optional[str]


class FlowMap(TypedDict, total=False):
    type: Literal["flow_map"]
    nodes: List[ConceptNode]
    edges: List[FlowEdge]


class DerivationStep(TypedDict, total=False):
    text: str
    highlight: Optional[str]


class DerivationSteps(TypedDict, total=False):
    type: Literal["derivation_steps"]
    steps: List[DerivationStep]


class MCQQuiz(TypedDict, total=False):
    type: Literal["mcq_quiz"]
    question: str
    options: List[str]
    correct: int
    explanation: Optional[str]


class EvidenceCallout(TypedDict, total=False):
    type: Literal["evidence_callout"]
    text: str
    source: Optional[str]


# Practical, hands‑on blocks
class Slider(TypedDict, total=False):
    id: str
    label: str
    min: float
    max: float
    step: float
    default: float


class Toggle(TypedDict, total=False):
    id: str
    label: str
    default: bool


class ControlPanel(TypedDict, total=False):
    type: Literal["control_panel"]
    sliders: List[Slider]
    toggles: List[Toggle]


class Meter(TypedDict, total=False):
    id: str
    label: str
    unit: str
    expr: str  # JS-like expression using params


class MeterPanel(TypedDict, total=False):
    type: Literal["meter_panel"]
    meters: List[Meter]


class LivePlot(TypedDict, total=False):
    type: Literal["live_plot"]
    x_label: str
    y_label: str
    expr: str      # y expression in terms of x and params
    x_min: float
    x_max: float
    samples: int


class SceneMotion1D(TypedDict, total=False):
    type: Literal["scene_motion_1d"]
    u: float
    a: float
    t_max: float


class SceneCircuitOhm(TypedDict, total=False):
    type: Literal["scene_circuit_ohm"]
    V: float
    R: float


class PredictCard(TypedDict, total=False):
    type: Literal["predict_card"]
    question: str
    expected: str


Block = Union[
    TitleCard,
    ConceptNodes,
    RelationArrows,
    EquationBlock,
    CompareGrid,
    WorkedExample,
    TipCard,
    Timeline,
    DefinitionCard,
    LawList,
    FlowMap,
    DerivationSteps,
    MCQQuiz,
    EvidenceCallout,
    ControlPanel,
    MeterPanel,
    LivePlot,
    SceneMotion1D,
    SceneCircuitOhm,
    PredictCard,
]


class Interaction(TypedDict, total=False):
    type: Literal["tap_to_continue", "quiz", "slider", "drag", "predict"]
    question: Optional[str]
    options: Optional[List[str]]
    correct: Optional[int]


class Stage(TypedDict, total=False):
    narration: str
    emphasis: Optional[str]
    duration_ms: int
    blocks: List[Block]
    interactions: Optional[List[Interaction]]


class TeachingVisual(TypedDict, total=False):
    visual_id: str
    type: Literal["teaching_visual"]
    total_duration_ms: int
    metadata: Dict[str, str]
    stages: List[Stage]
