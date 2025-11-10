from __future__ import annotations

"""
Subject Templates for Universal Visuals

Hand-authored, compact templates for common topics. Returns a
block-based TeachingVisual when a known topic is detected.
"""

from typing import Optional

from .visual_contract import TeachingVisual
from .universal_visual_planner import plan_universal_visual, cast_block
from .question_scope import build_scope


def plan_from_subject_templates(question: str, subject: Optional[str] = None, brief: Optional[dict] = None) -> Optional[TeachingVisual]:
    q = (question or "").lower()
    subj = (subject or "").lower()
    scope = brief or build_scope(question)

    # Physics: Newton's Laws
    if ("newton" in q and "law" in q) or (subj == "physics" and "newton" in q):
        # Narrow to specific law if asked
        if scope.get("subtopic") in {"first", "second", "third"}:
            # For First Law, return a practical, scoped visual that includes predict + friction toggle
            if scope.get("subtopic") == "first":
                return _newton_first_law_practical()
            return _newton_law_minimal(scope["subtopic"]) if scope.get("mode") in {"define", "explain"} else _newtons_laws()
        # If define mode, keep only compact view
        if scope.get("mode") == "define":
            return _newton_law_minimal("all")
        return _newtons_laws()

    # Physics: Ohm's Law
    if "ohm" in q or "v = i r" in q or "v=ir" in q or "ohms law" in q:
        if scope.get("mode") in {"derive", "define"}:
            return _ohms_minimal(scope.get("mode"))
        # Prefer practical (predict + control + meter + scene)
        return _ohms_practical()

    # Biology: Photosynthesis
    if "photosynthesis" in q:
        return _photosynthesis_practical()

    # Physics: Kinematics (1D motion)
    if any(k in q for k in ["kinematics", "uniform motion", "acceleration", "v=u+at", "s=ut"]):
        if scope.get("mode") == "define":
            return _kinematics_minimal()
        return _kinematics_practical()

    # Physics: Work–Energy–Power
    if any(k in q for k in ["work energy power", "work and energy", "kinetic energy", "power"]):
        return _wep_practical()

    # Physics: Projectile basics
    if any(k in q for k in ["projectile", "launch angle", "time of flight", "range of projectile"]):
        return _projectile_practical()

    # Chemistry: Ionic / Covalent bonding (practical toggle)
    if any(k in q for k in ["ionic bond", "ionic bonding", "transfer of electrons", "covalent bond", "covalent bonding", "sharing of electrons"]):
        return _ionic_covalent_practical()

    # Chemistry: Strong vs Weak acids
    if any(k in q for k in ["strong acid", "weak acid", "acids", "ph"]):
        return _acids_practical()

    # Biology: Cell division (Mitosis vs Meiosis)
    if any(k in q for k in ["mitosis", "meiosis", "cell division"]):
        return _cell_division()

    return None


def _newtons_laws() -> TeachingVisual:
    return {
        "visual_id": "tpl_newtons",
        "type": "teaching_visual",
        "total_duration_ms": 10400,
        "metadata": {"topic": "Newton's Laws of Motion", "subject": "physics", "concept_type": "laws"},
        "stages": [
            {
                "narration": "Three rules that govern motion.",
                "emphasis": "State names and one‑line idea.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Newton's Laws of Motion", "subtitle": "Overview"}),
                    cast_block({
                        "type": "law_list",
                        "laws": [
                            {"name": "1. Inertia", "summary": "State stays unless net force acts."},
                            {"name": "2. Dynamics", "summary": "F = m a (change in motion)."},
                            {"name": "3. Action‑Reaction", "summary": "Equal & opposite forces pair."}
                        ]
                    })
                ],
            },
            {
                "narration": "Try it yourself — change F and m.",
                "emphasis": "Watch a respond instantly (a = F/m).",
                "duration_ms": 2600,
                "blocks": [
                    cast_block({
                        "type": "control_panel",
                        "sliders": [
                            {"id": "F", "label": "Force (N)", "min": 0, "max": 20, "step": 1, "default": 10},
                            {"id": "m", "label": "Mass (kg)", "min": 0.1, "max": 5, "step": 0.1, "default": 1}
                        ]
                    }),
                    cast_block({
                        "type": "meter_panel",
                        "meters": [
                            {"id": "a", "label": "Acceleration", "unit": "m/s²", "expr": "F/m"}
                        ]
                    }),
                    cast_block({"type": "scene_motion_1d", "u": 0, "a": 0, "t_max": 2}),
                    cast_block({
                        "type": "flow_map",
                        "nodes": [
                            {"id": "force", "label": "Force (F)"},
                            {"id": "mass", "label": "Mass (m)"},
                            {"id": "accel", "label": "Accel (a)"}
                        ],
                        "edges": [
                            {"from_": "force", "to": "accel", "label": "+"},
                            {"from_": "mass", "to": "accel", "label": "− (for fixed F)"}
                        ]
                    }),
                    cast_block({"type": "equation", "tex": "F = m a"}),
                ],
            },
            {
                "narration": "Ball and bat example to cement ideas.",
                "emphasis": "Think cricket to remember.",
                "duration_ms": 2400,
                "blocks": [
                    cast_block({
                        "type": "worked_example",
                        "icon": "cricket",
                        "steps": [
                            {"label": "At rest", "detail": "Ball at rest; needs net F (L1)."},
                            {"label": "Hit", "detail": "Bat applies 12 N on 0.16 kg → a=75 m/s^2 (L2)."},
                            {"label": "Reaction", "detail": "Ball pushes bat back with 12 N (L3)."},
                        ],
                    })
                ],
            },
            {
                "narration": "How to score marks.",
                "emphasis": "State → Example → Equation.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({
                        "type": "compare_grid",
                        "left": {"title": "Inertia", "points": ["Rest/Uniform motion", "Needs external force"]},
                        "right": {"title": "Dynamics", "points": ["F causes a", "Equal & opposite"]},
                    }),
                    cast_block({"type": "tip_card", "tip_type": "exam", "text": "Name law + 1 line + cricket example."}),
                    cast_block({
                        "type": "mcq_quiz",
                        "question": "If F doubles and m doubles, a becomes?",
                        "options": ["Same", "Double", "Half", "Quadruple"],
                        "correct": 0,
                        "explanation": "a = F/m; both ×2 → ratio unchanged."
                    }),
                ],
            },
        ],
    }


def _ohms_law() -> TeachingVisual:
    return {
        "visual_id": "tpl_ohm",
        "type": "teaching_visual",
        "total_duration_ms": 9600,
        "metadata": {"topic": "Ohm's Law", "subject": "physics", "concept_type": "law"},
        "stages": [
            {
                "narration": "Relation between V, I and R.",
                "emphasis": "Linear relation at constant temperature.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Ohm's Law", "subtitle": "Overview"}),
                    cast_block({
                        "type": "control_panel",
                        "sliders": [
                            {"id": "V", "label": "Voltage (V)", "min": 0, "max": 20, "step": 1, "default": 10},
                            {"id": "R", "label": "Resistance (Ω)", "min": 1, "max": 10, "step": 1, "default": 5}
                        ]
                    }),
                    cast_block({
                        "type": "meter_panel",
                        "meters": [
                            {"id": "I", "label": "Current", "unit": "A", "expr": "V/R"}
                        ]
                    }),
                    cast_block({"type": "scene_circuit_ohm", "V": 10, "R": 5}),
                ],
            },
            {
                "narration": "V increases with I when R fixed.",
                "emphasis": "V = I R.",
                "duration_ms": 2000,
                "blocks": [
                    cast_block({"type": "equation", "tex": "V = I R"}),
                    cast_block({"type": "tip_card", "tip_type": "mistake", "text": "Don’t mix units: V(AΩ)."}),
                    cast_block({
                        "type": "derivation_steps",
                        "steps": [
                            {"text": "Ohmic conductor → V ∝ I"},
                            {"text": "Introduce constant R", "highlight": "V = I R"}
                        ]
                    })
                    ,
                    cast_block({
                        "type": "live_plot",
                        "x_label": "Current (I)",
                        "y_label": "Voltage (V)",
                        "expr": "y = R * x",
                        "x_min": 0,
                        "x_max": 10,
                        "samples": 20
                    })
                ],
            },
            {
                "narration": "Worked example with simple numbers.",
                "emphasis": "Use triangle trick V over I R.",
                "duration_ms": 2000,
                "blocks": [
                    cast_block({
                        "type": "worked_example",
                        "steps": [
                            {"label": "Given", "detail": "I=2A, R=5Ω"},
                            {"label": "Apply", "detail": "V = I R = 10V"},
                            {"label": "Check", "detail": "Units consistent"},
                        ],
                    })
                ],
            },
            {
                "narration": "Recap & quick exam line.",
                "emphasis": "State + equation + example.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "tip_card", "tip_type": "exam", "text": "Proportionality statement + V=IR + 1 example."}),
                    cast_block({
                        "type": "mcq_quiz",
                        "question": "If R doubles at constant V, current becomes?",
                        "options": ["Same", "Double", "Half", "Quarter"],
                        "correct": 2,
                        "explanation": "I = V/R → doubles R ⇒ I halves."
                    })
                ],
            },
        ],
    }


def _photosynthesis() -> TeachingVisual:
    return {
        "visual_id": "tpl_photo",
        "type": "teaching_visual",
        "total_duration_ms": 9000,
        "metadata": {"topic": "Photosynthesis", "subject": "biology", "concept_type": "process"},
        "stages": [
            {
                "narration": "What plants do to make food.",
                "emphasis": "Convert light → chemical energy.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Photosynthesis", "subtitle": "Overview"}),
                    cast_block({
                        "type": "flow_map",
                        "nodes": [
                            {"id": "l", "label": "Light"},
                            {"id": "co2", "label": "CO₂"},
                            {"id": "h2o", "label": "H₂O"},
                            {"id": "glucose", "label": "Glucose"},
                            {"id": "o2", "label": "O₂"},
                        ],
                        "edges": [
                            {"from_": "l", "to": "glucose", "label": "energy"},
                            {"from_": "co2", "to": "glucose", "label": "+"},
                            {"from_": "h2o", "to": "o2", "label": "byproduct"}
                        ]
                    }),
                ],
            },
            {
                "narration": "Inputs move to products.",
                "emphasis": "Glucose + O₂ formed.",
                "duration_ms": 2000,
                "blocks": [
                    cast_block({
                        "type": "equation",
                        "tex": "6CO_2 + 6H_2O \\xrightarrow{light} C_6H_{12}O_6 + 6O_2"
                    }),
                    cast_block({"type": "evidence_callout", "text": "Occurs in chloroplast (thylakoid, stroma)", "source": "NCERT"}),
                ],
            },
            {
                "narration": "Quick example to remember.",
                "emphasis": "Leaf as mini factory.",
                "duration_ms": 2200,
                "blocks": [
                    cast_block({
                        "type": "worked_example",
                        "steps": [
                            {"label": "Setup", "detail": "Light + CO₂ + Water"},
                            {"label": "Chlorophyll", "detail": "Captures light"},
                            {"label": "Result", "detail": "Glucose + Oxygen"},
                        ],
                    })
                ],
            },
            {
                "narration": "Recap in exam language.",
                "emphasis": "Inputs → Process → Outputs.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "tip_card", "tip_type": "exam", "text": "Write equation + organelle (chloroplast)."}),
                    cast_block({
                        "type": "mcq_quiz",
                        "question": "What is the byproduct of photosynthesis?",
                        "options": ["CO₂", "O₂", "N₂", "H₂"],
                        "correct": 1,
                        "explanation": "Oxygen is released."
                    })
                ],
            },
        ],
    }


def _photosynthesis_practical() -> TeachingVisual:
    return {
        "visual_id": "tpl_photo_practical",
        "type": "teaching_visual",
        "total_duration_ms": 7800,
        "metadata": {"topic": "Photosynthesis", "subject": "biology", "concept_type": "process"},
        "stages": [
            {
                "narration": "Predict oxygen rate with light.",
                "emphasis": None,
                "duration_ms": 3600,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "If light increases (CO₂ same), O₂ bubbles?", "expected": "Increase until saturation."}),
                    cast_block({"type": "control_panel", "sliders": [
                        {"id": "L", "label": "Light (arb)", "min": 0, "max": 10, "step": 1, "default": 3}
                    ], "toggles": [
                        {"id": "CO2", "label": "CO₂ high", "default": True}
                    ]}),
                    cast_block({"type": "meter_panel", "meters": [
                        {"id": "O2", "label": "O₂ rate", "unit": "rel", "expr": "CO2 ? Math.min(L*1.2, 10) : Math.min(L*0.7, 6)"}
                    ]}),
                    cast_block({"type": "equation", "tex": "6CO_2 + 6H_2O \\xrightarrow{light} C_6H_{12}O_6 + 6O_2"})
                ]
            }
        ]
    }



def _kinematics_1d() -> TeachingVisual:
    return {
        "visual_id": "tpl_kinematics_1d",
        "type": "teaching_visual",
        "total_duration_ms": 9800,
        "metadata": {"topic": "Kinematics (1D Motion)", "subject": "physics", "concept_type": "laws"},
        "stages": [
            {
                "narration": "Set u and a; see motion.",
                "emphasis": "Observe values rather than read.",
                "duration_ms": 2400,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Kinematics (1D)", "subtitle": "Try values"}),
                    cast_block({
                        "type": "control_panel",
                        "sliders": [
                            {"id": "u", "label": "u (m/s)", "min": 0, "max": 10, "step": 1, "default": 2},
                            {"id": "a", "label": "a (m/s²)", "min": 0, "max": 5, "step": 0.5, "default": 1}
                        ]
                    }),
                    cast_block({
                        "type": "meter_panel",
                        "meters": [
                            {"id": "v2s", "label": "v @2s", "unit": "m/s", "expr": "u + a*2"},
                            {"id": "s2s", "label": "s @2s", "unit": "m", "expr": "u*2 + 0.5*a*4"}
                        ]
                    }),
                    cast_block({"type": "scene_motion_1d", "u": 2, "a": 1, "t_max": 2}),
                ],
            },
            {
                "narration": "Equations of uniformly accelerated motion.",
                "emphasis": "Memorize these three.",
                "duration_ms": 2200,
                "blocks": [
                    cast_block({"type": "equation", "tex": "v = u + a t"}),
                    cast_block({"type": "equation", "tex": "s = u t + \\tfrac{1}{2} a t^2"}),
                    cast_block({"type": "equation", "tex": "v^2 = u^2 + 2 a s"}),
                    cast_block({
                        "type": "live_plot",
                        "x_label": "time (s)",
                        "y_label": "velocity (m/s)",
                        "expr": "y = u + a*x",
                        "x_min": 0,
                        "x_max": 5,
                        "samples": 20
                    })
                ],
            },
            {
                "narration": "Example with numbers.",
                "emphasis": "Identify u, a, t then pick equation.",
                "duration_ms": 2200,
                "blocks": [
                    cast_block({
                        "type": "worked_example",
                        "steps": [
                            {"label": "Given", "detail": "u=0 m/s, a=2 m/s^2, t=3 s"},
                            {"label": "Apply", "detail": "v = 0 + 2×3 = 6 m/s"},
                            {"label": "Find s", "detail": "s = 0 + 0.5×2×9 = 9 m"},
                        ],
                    })
                ],
            },
            {
                "narration": "Common confusions.",
                "emphasis": "Speed vs velocity; displacement vs distance.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({
                        "type": "compare_grid",
                        "left": {"title": "Velocity", "points": ["Vector", "Rate of displacement"]},
                        "right": {"title": "Speed", "points": ["Scalar", "Rate of distance"]},
                    }),
                    cast_block({"type": "tip_card", "tip_type": "exam", "text": "Underline knowns u,a,t and choose formula."}),
                ],
            },
        ],
    }


def _newton_first_law_practical() -> TeachingVisual:
    """A tight, professor-like visual for Newton's First Law with predict + friction toggle."""
    return {
        "visual_id": "tpl_newton_first_practical",
        "type": "teaching_visual",
        "total_duration_ms": 7600,
        "metadata": {"topic": "Newton — First Law (Inertia)", "subject": "physics", "concept_type": "law"},
        "stages": [
            {
                "narration": "Definition — state remains unless net force acts.",
                "emphasis": None,
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Newton — First Law (Inertia)", "subtitle": "Definition"}),
                    cast_block({"type": "law_list", "laws": [{"name":"1. Inertia","summary":"State stays unless net force acts."}]})
                ]
            },
            {
                "narration": "Socho: Force zero ho to a? Try sliders.",
                "emphasis": None,
                "duration_ms": 3000,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "If Net Force = 0, what happens to acceleration?", "expected": "a becomes 0 — motion continues at constant speed."}),
                    cast_block({
                        "type": "control_panel",
                        "sliders": [
                            {"id": "F", "label": "Net Force (N)", "min": 0, "max": 15, "step": 1, "default": 0},
                            {"id": "m", "label": "Mass (kg)", "min": 0.5, "max": 5, "step": 0.5, "default": 1.0},
                            {"id": "u", "label": "Initial v (m/s)", "min": 0, "max": 6, "step": 1, "default": 2}
                        ],
                        "toggles": [
                            {"id": "friction", "label": "Friction on", "default": False}
                        ]
                    }),
                    cast_block({
                        "type": "meter_panel",
                        "meters": [
                            {"id": "a", "label": "Acceleration", "unit": "m/s²", "expr": "friction ? Math.max((F-2)/m,0) : F/m"}
                        ]
                    }),
                    cast_block({"type": "scene_motion_1d", "u": 2, "a": 0, "t_max": 2, "style": "ball"})
                ]
            }
        ]
    }


def _newton_third_law_practical() -> TeachingVisual:
    return {
        "visual_id": "tpl_newton_third_practical",
        "type": "teaching_visual",
        "total_duration_ms": 6800,
        "metadata": {"topic": "Newton — Third Law (Action = Reaction)", "subject": "physics", "concept_type": "law"},
        "stages": [
            {
                "narration": "Equal & opposite forces appear together (pair).",
                "emphasis": None,
                "duration_ms": 1600,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Action–Reaction", "subtitle": "Definition"})
                ]
            },
            {
                "narration": "Slide Action force; Reaction becomes equal, opposite.",
                "emphasis": None,
                "duration_ms": 2800,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "If Action = 12 N, Reaction becomes?", "expected": "12 N opposite direction."}),
                    cast_block({"type": "control_panel", "sliders": [
                        {"id": "F", "label": "Action (N)", "min": 0, "max": 20, "step": 1, "default": 12}
                    ]}),
                    cast_block({"type": "meter_panel", "meters": [
                        {"id": "R", "label": "Reaction", "unit": "N", "expr": "F"}
                    ]}),
                    cast_block({"type": "flow_map", "nodes": [{"id":"A","label":"Action"},{"id":"R","label":"Reaction"}], "edges": [{"from_":"A","to":"R","label":"equal & opposite"}]})
                ]
            }
        ]
    }


def _newton_law_minimal(which: str) -> TeachingVisual:
    title = {
        'first': "Newton — First Law (Inertia)",
        'second': "Newton — Second Law (F = m a)",
        'third': "Newton — Third Law (Action = Reaction)",
        'all': "Newton's Laws (Definitions)"
    }.get(which, "Newton's Laws")
    laws = []
    if which in ('first','all'):
        laws.append({"name": "1. Inertia", "summary": "State remains until net force acts."})
    if which in ('second','all'):
        laws.append({"name": "2. Dynamics", "summary": "F = m a defines change in motion."})
    if which in ('third','all'):
        laws.append({"name": "3. Action–Reaction", "summary": "Equal & opposite forces pair."})
    return {
        "visual_id": f"tpl_newton_min_{which}",
        "type": "teaching_visual",
        "total_duration_ms": 7200,
        "metadata": {"topic": title, "subject": "physics", "concept_type": "law"},
        "stages": [
            {
                "narration": "Definitions only — tight for marks.",
                "emphasis": None,
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "title_card", "title": title, "subtitle": "Definition"}),
                    cast_block({"type": "law_list", "laws": laws})
                ],
            },
            # Micro‑practical snapshot depending on the asked law
            (
                {
                    "narration": "Slide F to zero — motion stays steady (no acceleration).",
                    "emphasis": None,
                    "duration_ms": 2600,
                    "blocks": [
                        cast_block({
                            "type": "control_panel",
                            "sliders": [
                                {"id": "F", "label": "Net Force (N)", "min": 0, "max": 15, "step": 1, "default": 0},
                                {"id": "m", "label": "Mass (kg)", "min": 0.5, "max": 5, "step": 0.5, "default": 1.0},
                                {"id": "u", "label": "Initial v (m/s)", "min": 0, "max": 6, "step": 1, "default": 2}
                            ]
                        }),
                        cast_block({
                            "type": "meter_panel",
                            "meters": [
                                {"id": "a", "label": "Acceleration", "unit": "m/s²", "expr": "F/m"}
                            ]
                        }),
                        cast_block({"type": "scene_motion_1d", "u": 2, "a": 0, "t_max": 2, "style": "ball"})
                    ]
                }
                if which == 'first' else
                {
                    "narration": "Tiny snapshot to visualize.",
                    "emphasis": None,
                    "duration_ms": 1800,
                    "blocks": [
                        cast_block({"type": "flow_map", "nodes": [{"id": "f","label": "Force"},{"id":"a","label":"Accel"}], "edges": [{"from_":"f","to":"a","label":"→"}]}),
                        cast_block({"type": "equation", "tex": "F = m a"}) if which in ('second','all') else cast_block({"type":"tip_card","tip_type":"exam","text":"Name + 1 line + eg."})
                    ]
                }
            )
        ]
    }


def _ohms_minimal(mode: str) -> TeachingVisual:
    blocks = [cast_block({"type": "title_card", "title": "Ohm's Law", "subtitle": "Core"})]
    if mode == 'derive':
        blocks.append(cast_block({"type": "derivation_steps", "steps": [{"text":"Ohmic conductor → V ∝ I"},{"text":"Introduce constant R","highlight":"V = I R"}] }))
    else:  # define
        blocks.append(cast_block({"type": "definition_card", "term": "Ohm's Law", "definition": "At constant temperature, V is proportional to I (V = IR)."}))
    return {
        "visual_id": f"tpl_ohm_min_{mode}",
        "type": "teaching_visual",
        "total_duration_ms": 4200,
        "metadata": {"topic": "Ohm's Law", "subject": "physics", "concept_type": "law"},
        "stages": [{"narration":"Keep it crisp.","emphasis":None,"duration_ms":2000,"blocks": blocks}]
    }


def _kinematics_minimal() -> TeachingVisual:
    return {
        "visual_id": "tpl_kin_min",
        "type": "teaching_visual",
        "total_duration_ms": 4600,
        "metadata": {"topic": "Kinematics (1D)", "subject": "physics", "concept_type": "definition"},
        "stages": [
            {
                "narration": "Definitions only.",
                "emphasis": None,
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "definition_card", "term": "Velocity (v)", "definition": "Rate of change of displacement."}),
                    cast_block({"type": "definition_card", "term": "Acceleration (a)", "definition": "Rate of change of velocity."})
                ]
            },
            {
                "narration": "Snapshot equation.",
                "emphasis": None,
                "duration_ms": 1600,
                "blocks": [
                    cast_block({"type": "equation", "tex": "v = u + a t"})
                ]
            }
        ]
    }


def _ohms_practical() -> TeachingVisual:
    return {
        "visual_id": "tpl_ohm_practical",
        "type": "teaching_visual",
        "total_duration_ms": 7800,
        "metadata": {"topic": "Ohm's Law", "subject": "physics", "concept_type": "law"},
        "stages": [
            {
                "narration": "Predict and then try values.",
                "emphasis": None,
                "duration_ms": 3600,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "If R increases while V fixed, what happens to I?", "expected": "I decreases (I = V/R)."}),
                    cast_block({"type": "control_panel", "sliders": [
                        {"id": "V", "label": "Voltage (V)", "min": 0, "max": 20, "step": 1, "default": 10},
                        {"id": "R", "label": "Resistance (Ω)", "min": 1, "max": 10, "step": 1, "default": 5}
                    ]}),
                    cast_block({"type": "meter_panel", "meters": [
                        {"id": "I", "label": "Current", "unit": "A", "expr": "V/R"}
                    ]}),
                    cast_block({"type": "scene_circuit_ohm", "V": 10, "R": 5})
                ]
            },
            {
                "narration": "Equation snapshot and quick line.",
                "emphasis": None,
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "equation", "tex": "V = I R"})
                ]
            }
        ]
    }


def _kinematics_practical() -> TeachingVisual:
    return {
        "visual_id": "tpl_kin_practical",
        "type": "teaching_visual",
        "total_duration_ms": 8200,
        "metadata": {"topic": "Kinematics (1D Motion)", "subject": "physics", "concept_type": "laws"},
        "stages": [
            {
                "narration": "Predict and then try u and a.",
                "emphasis": None,
                "duration_ms": 3600,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "If a increases (same u), what happens to v@2s?", "expected": "v increases since v = u + a t."}),
                    cast_block({"type": "control_panel", "sliders": [
                        {"id": "u", "label": "u (m/s)", "min": 0, "max": 10, "step": 1, "default": 2},
                        {"id": "a", "label": "a (m/s²)", "min": 0, "max": 5, "step": 0.5, "default": 1}
                    ]}),
                    cast_block({"type": "meter_panel", "meters": [
                        {"id": "v2s", "label": "v @2s", "unit": "m/s", "expr": "u + a*2"},
                        {"id": "s2s", "label": "s @2s", "unit": "m", "expr": "u*2 + 0.5*a*4"}
                    ]}),
                    cast_block({"type": "scene_motion_1d", "u": 2, "a": 1, "t_max": 2})
                ]
            },
            {
                "narration": "Equation snapshot.",
                "emphasis": None,
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "equation", "tex": "v = u + a t"})
                ]
            }
        ]
    }


def _ionic_bonding() -> TeachingVisual:
    return {
        "visual_id": "tpl_ionic",
        "type": "teaching_visual",
        "total_duration_ms": 7600,
        "metadata": {"topic": "Ionic Bonding", "subject": "chemistry", "concept_type": "bonding"},
        "stages": [
            {
                "narration": "Transfer of electrons forms ions.",
                "emphasis": "Metal → loses; Non‑metal → gains.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Ionic Bonding", "subtitle": "Overview"}),
                    cast_block({
                        "type": "concept_nodes",
                        "layout": "row",
                        "nodes": [
                            {"id": "na", "label": "Na"},
                            {"id": "cl", "label": "Cl"},
                            {"id": "na+cl-", "label": "Na⁺ & Cl⁻"},
                        ],
                    }),
                ],
            },
            {
                "narration": "Electron moves from Na to Cl.",
                "emphasis": "Strong electrostatic attraction.",
                "duration_ms": 2000,
                "blocks": [
                    cast_block({
                        "type": "relation_arrows",
                        "relations": [
                            {"from_": "na", "to": "na+cl-", "label": "e⁻ out"},
                            {"from_": "cl", "to": "na+cl-", "label": "e⁻ in"},
                        ],
                    }),
                    cast_block({"type": "tip_card", "tip_type": "mistake", "text": "Don’t show sharing — it’s transfer."}),
                ],
            },
            {
                "narration": "Properties.",
                "emphasis": "High mp/bp; conducts when molten/aqueous.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({
                        "type": "compare_grid",
                        "left": {"title": "Structure", "points": ["Lattice", "Strong attraction"]},
                        "right": {"title": "Conductivity", "points": ["Molten", "Aqueous"]},
                    }),
                ],
            },
            {
                "narration": "Exam line.",
                "emphasis": "Metal transfers → ions → lattice.",
                "duration_ms": 1600,
                "blocks": [
                    cast_block({"type": "tip_card", "tip_type": "exam", "text": "Define + example: NaCl."}),
                ],
            },
        ],
    }


def _covalent_bonding() -> TeachingVisual:
    return {
        "visual_id": "tpl_covalent",
        "type": "teaching_visual",
        "total_duration_ms": 7600,
        "metadata": {"topic": "Covalent Bonding", "subject": "chemistry", "concept_type": "bonding"},
        "stages": [
            {
                "narration": "Sharing of electron pairs.",
                "emphasis": "Between non‑metals.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Covalent Bonding", "subtitle": "Overview"}),
                    cast_block({
                        "type": "concept_nodes",
                        "layout": "row",
                        "nodes": [
                            {"id": "h", "label": "H"},
                            {"id": "cl", "label": "Cl"},
                            {"id": "hcl", "label": "H—Cl"},
                        ],
                    }),
                ],
            },
            {
                "narration": "Shared pair holds atoms together.",
                "emphasis": "Directional bonding.",
                "duration_ms": 2000,
                "blocks": [
                    cast_block({
                        "type": "relation_arrows",
                        "relations": [
                            {"from_": "h", "to": "hcl", "label": "share"},
                            {"from_": "cl", "to": "hcl", "label": "share"},
                        ],
                    }),
                    cast_block({"type": "tip_card", "tip_type": "mistake", "text": "Don’t show charge transfer here."}),
                ],
            },
            {
                "narration": "Properties.",
                "emphasis": "Low mp/bp (many), poor conductors.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({
                        "type": "compare_grid",
                        "left": {"title": "Simple", "points": ["H2, Cl2", "low mp/bp"]},
                        "right": {"title": "Network", "points": ["Diamond", "hard & high mp"]},
                    }),
                ],
            },
            {
                "narration": "Exam line.",
                "emphasis": "Sharing → molecule(s).",
                "duration_ms": 1600,
                "blocks": [
                    cast_block({"type": "tip_card", "tip_type": "exam", "text": "Define + example: HCl."}),
                ],
            },
        ],
    }


def _cell_division() -> TeachingVisual:
    return {
        "visual_id": "tpl_cell_division",
        "type": "teaching_visual",
        "total_duration_ms": 8200,
        "metadata": {"topic": "Cell Division", "subject": "biology", "concept_type": "process"},
        "stages": [
            {
                "narration": "Two pathways to make new cells.",
                "emphasis": "Mitosis vs Meiosis.",
                "duration_ms": 1800,
                "blocks": [
                    cast_block({"type": "title_card", "title": "Cell Division", "subtitle": "Overview"}),
                    cast_block({
                        "type": "concept_nodes",
                        "layout": "row",
                        "nodes": [
                            {"id": "mito", "label": "Mitosis"},
                            {"id": "meio", "label": "Meiosis"},
                            {"id": "cells", "label": "Daughter cells"},
                        ],
                    }),
                ],
            },
            {
                "narration": "Compare outcomes.",
                "emphasis": "2 identical vs 4 diverse.",
                "duration_ms": 2200,
                "blocks": [
                    cast_block({
                        "type": "compare_grid",
                        "left": {"title": "Mitosis", "points": ["2 cells", "same ploidy"]},
                        "right": {"title": "Meiosis", "points": ["4 cells", "half ploidy"]},
                    }),
                ],
            },
            {
                "narration": "Simple example.",
                "emphasis": "Somatic vs gametes.",
                "duration_ms": 2200,
                "blocks": [
                    cast_block({
                        "type": "worked_example",
                        "steps": [
                            {"label": "Mitosis", "detail": "Skin cell repair"},
                            {"label": "Meiosis", "detail": "Sperm/egg formation"},
                        ],
                    })
                ],
            },
            {
                "narration": "Exam tip.",
                "emphasis": "State count + ploidy + purpose.",
                "duration_ms": 1600,
                "blocks": [
                    cast_block({"type": "tip_card", "tip_type": "exam", "text": "Write outcome and where it happens."}),
                ],
            },
        ],
    }


def _ionic_covalent_practical() -> TeachingVisual:
    return {
        "visual_id": "tpl_bonding_practical",
        "type": "teaching_visual",
        "total_duration_ms": 7600,
        "metadata": {"topic": "Bonding: Ionic vs Covalent", "subject": "chemistry", "concept_type": "bonding"},
        "stages": [
            {
                "narration": "Toggle to see transfer vs sharing.",
                "emphasis": None,
                "duration_ms": 3600,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "Metal + non‑metal → which bonding?", "expected": "Ionic (transfer)."}),
                    cast_block({"type": "control_panel", "sliders": [], "toggles": [
                        {"id": "ionic", "label": "Ionic (transfer)", "default": True}
                    ]}),
                    cast_block({"type": "compare_grid", "left": {"title": "Ionic", "points": ["Transfer e⁻", "Lattice", "Conducts (molten/aq)"]}, "right": {"title": "Covalent", "points": ["Share e⁻", "Molecules", "Low mp/bp (many)"]}})
                ]
            }
        ]
    }


def _wep_practical() -> TeachingVisual:
    return {
        "visual_id": "tpl_wep_practical",
        "type": "teaching_visual",
        "total_duration_ms": 8200,
        "metadata": {"topic": "Work–Energy–Power", "subject": "physics", "concept_type": "law"},
        "stages": [
            {
                "narration": "Predict, then try mass and speed.",
                "emphasis": None,
                "duration_ms": 3600,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "If v doubles, KE becomes?", "expected": "Quadruples (KE ∝ v²)."}),
                    cast_block({"type": "control_panel", "sliders": [
                        {"id": "m", "label": "Mass (kg)", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
                        {"id": "v", "label": "Speed (m/s)", "min": 0, "max": 12, "step": 1, "default": 3},
                        {"id": "F", "label": "Force (N)", "min": 0, "max": 50, "step": 2, "default": 10}
                    ], "toggles": [
                        {"id": "incline", "label": "Incline on", "default": False}
                    ]}),
                    cast_block({"type": "meter_panel", "meters": [
                        {"id": "KE", "label": "KE", "unit": "J", "expr": "0.5*m*v*v"},
                        {"id": "P", "label": "Power (approx)", "unit": "W", "expr": "F*v"}
                    ]}),
                    cast_block({"type": "scene_motion_1d", "u": 0, "a": 0, "t_max": 2})
                ]
            }
        ]
    }


def _projectile_practical() -> TeachingVisual:
    return {
        "visual_id": "tpl_projectile_practical",
        "type": "teaching_visual",
        "total_duration_ms": 8200,
        "metadata": {"topic": "Projectile Basics", "subject": "physics", "concept_type": "law"},
        "stages": [
            {
                "narration": "Predict range with angle.",
                "emphasis": None,
                "duration_ms": 3600,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "Angle increases from 30° to 45° (u same). Range?", "expected": "Increases; 45° gives max range."}),
                    cast_block({"type": "control_panel", "sliders": [
                        {"id": "u", "label": "u (m/s)", "min": 5, "max": 30, "step": 1, "default": 15},
                        {"id": "ang", "label": "angle (deg)", "min": 10, "max": 80, "step": 1, "default": 30}
                    ]}),
                    cast_block({"type": "meter_panel", "meters": [
                        {"id": "T", "label": "Time", "unit": "s", "expr": "(2*u*Math.sin(ang*Math.PI/180))/9.8"},
                        {"id": "R", "label": "Range", "unit": "m", "expr": "(u*u*Math.sin(2*ang*Math.PI/180))/9.8"}
                    ]})
                ]
            }
        ]
    }


def _acids_practical() -> TeachingVisual:
    return {
        "visual_id": "tpl_acids_practical",
        "type": "teaching_visual",
        "total_duration_ms": 7800,
        "metadata": {"topic": "Strong vs Weak Acids", "subject": "chemistry", "concept_type": "concept"},
        "stages": [
            {
                "narration": "Predict pH with concentration and strength.",
                "emphasis": None,
                "duration_ms": 3600,
                "blocks": [
                    cast_block({"type": "predict_card", "question": "If conc ↑ for strong acid, pH becomes?", "expected": "pH decreases (more H⁺)."}),
                    cast_block({"type": "control_panel", "sliders": [
                        {"id": "C", "label": "Conc (M)", "min": 0.001, "max": 1, "step": 0.001, "default": 0.1}
                    ], "toggles": [
                        {"id": "strong", "label": "Strong acid", "default": True}
                    ]}),
                    cast_block({"type": "meter_panel", "meters": [
                        {"id": "pH", "label": "pH (approx)", "unit": "", "expr": "strong ? (-(Math.log10(C))) : (-(Math.log10(Math.sqrt(C))))"}
                    ]}),
                    cast_block({"type": "compare_grid", "left": {"title": "Strong", "points": ["Fully ionizes", "Low pH"]}, "right": {"title": "Weak", "points": ["Partially ionizes", "Higher pH (same conc)"]}})
                ]
            }
        ]
    }
