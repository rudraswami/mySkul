from __future__ import annotations

"""
Dynamic Visual Builder

Builds a TeachingVisual based on (question → scope → concept → params).
Uses the existing practical patterns for a handful of concepts, and
prefills sliders/expressions when numbers are present in the question.
"""

from typing import Dict, Optional

from .visual_contract import TeachingVisual
from .question_scope import build_scope
from .concept_map import detect_concept
from .param_extractor import extract_params


def _merge(defaults: Dict[str, float], params: Dict[str, float]) -> Dict[str, float]:
    out = dict(defaults)
    out.update({k: v for k, v in params.items() if isinstance(v, (int, float))})
    return out


def build_dynamic_visual(question: str, subject_hint: Optional[str] = None) -> Optional[TeachingVisual]:
    scope = build_scope(question)
    subject, concept = detect_concept(question, subject_hint)
    if not concept:
        return None
    params = extract_params(question)

    # Dispatch: concept → practical pattern with merged defaults
    if concept == "projectile":
        defaults = {"u": 15.0, "ang": 30.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_projectile",
            "type": "teaching_visual",
            "total_duration_ms": 7000,
            "metadata": {"topic": "Projectile Basics", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Predict and try angle & speed.",
                    "emphasis": None,
                    "duration_ms": 3400,
                    "blocks": [
                        {"type": "predict_card", "question": "Angle ↑ (same u) → Range?", "expected": "Max near 45°."},
                        {"type": "control_panel", "sliders": [
                            {"id": "u", "label": "u (m/s)", "min": 5, "max": 30, "step": 1, "default": p["u"]},
                            {"id": "ang", "label": "angle (deg)", "min": 10, "max": 80, "step": 1, "default": p["ang"]}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "T", "label": "Time", "unit": "s", "expr": "(2*u*Math.sin(ang*Math.PI/180))/9.8"},
                            {"id": "R", "label": "Range", "unit": "m", "expr": "(u*u*Math.sin(2*ang*Math.PI/180))/9.8"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "ohm_law":
        defaults = {"V": 10.0, "R": 5.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_ohm",
            "type": "teaching_visual",
            "total_duration_ms": 6400,
            "metadata": {"topic": "Ohm's Law", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Predict current with V and R.",
                    "emphasis": None,
                    "duration_ms": 3200,
                    "blocks": [
                        {"type": "predict_card", "question": "R ↑ at fixed V → I?", "expected": "I decreases (I=V/R)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "V", "label": "Voltage (V)", "min": 0, "max": 20, "step": 1, "default": p["V"]},
                            {"id": "R", "label": "Resistance (Ω)", "min": 1, "max": 10, "step": 1, "default": p["R"]}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "I", "label": "Current", "unit": "A", "expr": "V/R"}
                        ]},
                        {"type": "scene_circuit_ohm", "V": p["V"], "R": p["R"]}
                    ]
                }
            ]
        }

    if concept == "wep":
        # Work–Energy–Power (simple KE focus)
        defaults = {"m": 1.0, "v": 2.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_wep",
            "type": "teaching_visual",
            "total_duration_ms": 6200,
            "metadata": {"topic": "Work–Energy–Power (KE)", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Speed badhao? KE kitna badhega?",
                    "emphasis": None,
                    "duration_ms": 3100,
                    "blocks": [
                        {"type": "predict_card", "question": "v double → KE?", "expected": "4x (½mv²)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "m", "label": "Mass (kg)", "min": 0.5, "max": 5, "step": 0.5, "default": p.get("m", 1.0)},
                            {"id": "v", "label": "Speed (m/s)", "min": 1, "max": 10, "step": 1, "default": p.get("v", 2.0)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "KE", "label": "Kinetic Energy", "unit": "J", "expr": "0.5*m*v*v"},
                            {"id": "P3s", "label": "Avg Power @3s", "unit": "W", "expr": "(0.5*m*v*v)/3"}
                        ]},
                        {"type": "live_plot", "series": [
                            {"label": "KE vs v", "expr": "0.5*m*x*x", "x_min": 0, "x_max": 10, "step": 1}
                        ]}
                    ]
                }
            ]
        }

    if concept == "kinematics_1d":
        defaults = {"u": 2.0, "a": 1.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_kinematics",
            "type": "teaching_visual",
            "total_duration_ms": 6400,
            "metadata": {"topic": "Kinematics (1D)", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Try u and a; see values.",
                    "emphasis": None,
                    "duration_ms": 3200,
                    "blocks": [
                        {"type": "predict_card", "question": "a ↑ (same u) → v@2s?", "expected": "v increases (v=u+at)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "u", "label": "u (m/s)", "min": 0, "max": 10, "step": 1, "default": p["u"]},
                            {"id": "a", "label": "a (m/s²)", "min": 0, "max": 5, "step": 0.5, "default": p["a"]}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "v2s", "label": "v @2s", "unit": "m/s", "expr": "u + a*2"},
                            {"id": "s2s", "label": "s @2s", "unit": "m", "expr": "u*2 + 0.5*a*4"}
                        ]},
                        {"type": "scene_motion_1d", "u": p["u"], "a": p["a"], "t_max": 2}
                    ]
                }
            ]
        }

    if concept == "acids_strength":
        defaults = {"C": 0.1}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_acids",
            "type": "teaching_visual",
            "total_duration_ms": 6000,
            "metadata": {"topic": "Strong vs Weak Acids", "subject": subject or "chemistry", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Predict pH with concentration.",
                    "emphasis": None,
                    "duration_ms": 3000,
                    "blocks": [
                        {"type": "predict_card", "question": "Conc ↑ for strong acid → pH?", "expected": "pH decreases."},
                        {"type": "control_panel", "sliders": [
                            {"id": "C", "label": "Conc (M)", "min": 0.001, "max": 1, "step": 0.001, "default": p["C"]}
                        ], "toggles": [
                            {"id": "strong", "label": "Strong acid", "default": True}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "pH", "label": "pH (approx)", "unit": "", "expr": "strong ? (-(Math.log10(C))) : (-(Math.log10(Math.sqrt(C))))"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "newton_first":
        defaults = {"F": 0.0, "m": 1.0, "u": 2.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_newton_first",
            "type": "teaching_visual",
            "total_duration_ms": 6800,
            "metadata": {"topic": "Newton — First Law (Inertia)", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Force zero? Motion stays steady.",
                    "emphasis": None,
                    "duration_ms": 3400,
                    "blocks": [
                        {"type": "predict_card", "question": "If F=0, a becomes?", "expected": "Zero; motion remains."},
                        {"type": "control_panel", "sliders": [
                            {"id": "F", "label": "Net Force (N)", "min": 0, "max": 15, "step": 1, "default": p["F"]},
                            {"id": "m", "label": "Mass (kg)", "min": 0.5, "max": 5, "step": 0.5, "default": p["m"]},
                            {"id": "u", "label": "Initial v (m/s)", "min": 0, "max": 6, "step": 1, "default": p["u"]}
                        ], "toggles": [
                            {"id": "friction", "label": "Friction on", "default": False}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "a", "label": "Acceleration", "unit": "m/s²", "expr": "friction ? Math.max((F-2)/m,0) : F/m"}
                        ]},
                        {"type": "scene_motion_1d", "u": p["u"], "a": 0, "t_max": 2, "style": "ball"}
                    ]
                }
            ]
        }

    if concept == "newton_second":
        # F = m a → a = F/m; simple motion intuition
        defaults = {"F": 10.0, "m": 2.0, "u": 0.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_newton_second",
            "type": "teaching_visual",
            "total_duration_ms": 6000,
            "metadata": {"topic": "Newton — Second Law (F=ma)", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Force aur mass set karo — acceleration dekho.",
                    "emphasis": None,
                    "duration_ms": 3000,
                    "blocks": [
                        {"type": "predict_card", "question": "m double (F same) → a?", "expected": "a halves."},
                        {"type": "control_panel", "sliders": [
                            {"id": "F", "label": "Force (N)", "min": 0, "max": 30, "step": 1, "default": p.get("F", 10)},
                            {"id": "m", "label": "Mass (kg)", "min": 0.5, "max": 10, "step": 0.5, "default": p.get("m", 2)},
                            {"id": "u", "label": "Initial v (m/s)", "min": 0, "max": 5, "step": 0.5, "default": p.get("u", 0)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "a", "label": "Acceleration", "unit": "m/s²", "expr": "F/m"}
                        ]},
                        {"type": "scene_motion_1d", "u": p.get("u", 0), "a": None, "t_max": 2}
                    ]
                }
            ]
        }

    if concept == "newton_third":
        # Action–reaction pairs with equal magnitude, opposite direction
        defaults = {"F": 5.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_newton_third",
            "type": "teaching_visual",
            "total_duration_ms": 6000,
            "metadata": {"topic": "Newton — Third Law", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Action = Reaction (equal & opposite)",
                    "emphasis": None,
                    "duration_ms": 3000,
                    "blocks": [
                        {"type": "predict_card", "question": "Push harder → reaction?", "expected": "Same magnitude, opposite."},
                        {"type": "control_panel", "sliders": [
                            {"id": "F", "label": "Action Force (N)", "min": 0, "max": 20, "step": 1, "default": p.get("F", 5.0)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "Fa", "label": "Action", "unit": "N", "expr": "F"},
                            {"id": "Fr", "label": "Reaction", "unit": "N", "expr": "-F"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "A", "label": "Hand"}, {"id": "B", "label": "Wall"}
                        ], "arrows": [
                            {"from": "A", "to": "B", "label": "+F"}, {"from": "B", "to": "A", "label": "-F"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "momentum_impulse":
        # Momentum p = m v; Impulse J = F Δt; simple sliders
        defaults = {"m": 1.0, "v": 2.0, "F": 5.0, "dt": 1.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_momentum_impulse",
            "type": "teaching_visual",
            "total_duration_ms": 6000,
            "metadata": {"topic": "Momentum & Impulse", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Speed badhao to momentum kaisa badhega?",
                    "emphasis": None,
                    "duration_ms": 3000,
                    "blocks": [
                        {"type": "predict_card", "question": "v double → p?", "expected": "p doubles (p=mv)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "m", "label": "Mass (kg)", "min": 0.5, "max": 5, "step": 0.5, "default": p["m"]},
                            {"id": "v", "label": "Velocity (m/s)", "min": 0, "max": 10, "step": 1, "default": p["v"]},
                            {"id": "F", "label": "Force (N)", "min": 0, "max": 20, "step": 1, "default": p["F"]},
                            {"id": "dt", "label": "Δt (s)", "min": 0.2, "max": 5, "step": 0.2, "default": p["dt"]}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "p", "label": "Momentum p", "unit": "kg·m/s", "expr": "m*v"},
                            {"id": "J", "label": "Impulse J", "unit": "N·s", "expr": "F*dt"}
                        ]},
                        {"type": "live_plot", "series": [
                            {"label": "p vs v", "expr": "m*x", "x_min": 0, "x_max": 10, "step": 1}
                        ]}
                    ]
                }
            ]
        }

    if concept == "optics_ray":
        # Thin lens: v = (f*u)/(u - f), magnification m = -v/u (sign ignored visually)
        defaults = {"f": 10.0, "u": 30.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_optics_ray",
            "type": "teaching_visual",
            "total_duration_ms": 6200,
            "metadata": {"topic": "Lens Ray Basics", "subject": subject or "physics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Lens f set karo, object distance badhao aur dekho image.",
                    "emphasis": None,
                    "duration_ms": 3100,
                    "blocks": [
                        {"type": "predict_card", "question": "u → f ke paas?", "expected": "Image door/nazdeek shift."},
                        {"type": "control_panel", "sliders": [
                            {"id": "f", "label": "Focal (cm)", "min": 5, "max": 30, "step": 1, "default": p["f"]},
                            {"id": "u", "label": "Object u (cm)", "min": 8, "max": 100, "step": 1, "default": p["u"]}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "v", "label": "Image v (cm)", "unit": "cm", "expr": "(u==f)? Infinity : (f*u)/(u-f)"},
                            {"id": "mag", "label": "Magnification", "unit": "", "expr": "-( (u==f)? 0 : ((f*u)/(u-f))/u )"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "obj", "label": "Object (u)"}, {"id": "lens", "label": "Lens (f)"}, {"id": "img", "label": "Image (v)"}
                        ], "arrows": [
                            {"from": "obj", "to": "lens", "label": "rays"}, {"from": "lens", "to": "img", "label": "refracted"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "optics_mirror":
        # Mirror ray basics (uses lens-like thin formula for intuition)
        defaults = {"f": 15.0, "u": 40.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_optics_mirror",
            "type": "teaching_visual",
            "total_duration_ms": 6200,
            "metadata": {"topic": "Mirror Ray Basics", "subject": subject or "physics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Concave/convex mirror ka feel — u aur f set karo.",
                    "emphasis": None,
                    "duration_ms": 3100,
                    "blocks": [
                        {"type": "predict_card", "question": "u change → image kahan?", "expected": "v shifts per 1/f = 1/u + 1/v"},
                        {"type": "control_panel", "sliders": [
                            {"id": "f", "label": "Focal (cm)", "min": 5, "max": 50, "step": 1, "default": p["f"]},
                            {"id": "u", "label": "Object u (cm)", "min": 8, "max": 120, "step": 1, "default": p["u"]}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "v", "label": "Image v (cm)", "unit": "cm", "expr": "(u==f)? Infinity : (f*u)/(u-f)"},
                            {"id": "m", "label": "Magnification", "unit": "", "expr": "-( (u==f)? 0 : ((f*u)/(u-f))/u )"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "obj", "label": "Object"}, {"id": "mirror", "label": "Mirror (f)"}, {"id": "img", "label": "Image"}
                        ], "arrows": [
                            {"from": "obj", "to": "mirror", "label": "rays"}, {"from": "mirror", "to": "img", "label": "reflected"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "gas_law":
        # Ideal Gas quick demo with n=1 mol, R=0.082057 L·atm/(mol·K)
        defaults = {"V": 5.0, "T": 300.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_gas_law",
            "type": "teaching_visual",
            "total_duration_ms": 6000,
            "metadata": {"topic": "Gas Law (PV=nRT)", "subject": subject or "chemistry", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Boyle/Charles ka feel — V aur T set karo, P dekho.",
                    "emphasis": None,
                    "duration_ms": 3000,
                    "blocks": [
                        {"type": "predict_card", "question": "T↑ (V same) → P?", "expected": "P increases (PV=nRT)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "V", "label": "Volume (L)", "min": 1, "max": 20, "step": 1, "default": p.get("V", 5.0)},
                            {"id": "T", "label": "Temp (K)", "min": 250, "max": 400, "step": 5, "default": p.get("T", 300.0)}
                        ], "toggles": [
                            {"id": "boyle", "label": "Boyle focus", "default": false}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "P", "label": "Pressure", "unit": "atm", "expr": "(0.082057*T)/V"}
                        ]},
                        {"type": "live_plot", "series": [
                            {"label": "P vs V (T const)", "expr": "(0.082057*T)/x", "x_min": 1, "x_max": 20, "step": 1}
                        ]}
                    ]
                }
            ]
        }

    if concept == "snell_refraction":
        # Snell's law: n1*sin(i) = n2*sin(r); handle TIR when n1*sin(i) > n2
        defaults = {"n1": 1.00, "n2": 1.50, "i": 30.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_snell",
            "type": "teaching_visual",
            "total_duration_ms": 6200,
            "metadata": {"topic": "Snell’s Law (Refraction)", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "n1, n2 aur angle set karo — refraction dekho.",
                    "emphasis": None,
                    "duration_ms": 3100,
                    "blocks": [
                        {"type": "predict_card", "question": "n2↑ (denser) → r?", "expected": "r decreases (bends towards normal)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "n1", "label": "n1", "min": 1.0, "max": 1.6, "step": 0.01, "default": p.get("n1", 1.0)},
                            {"id": "n2", "label": "n2", "min": 1.0, "max": 1.8, "step": 0.01, "default": p.get("n2", 1.5)},
                            {"id": "i", "label": "i (deg)", "min": 0, "max": 80, "step": 1, "default": p.get("i", 30.0)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "r", "label": "r (deg)", "unit": "°", "expr": "( (n1*Math.sin(i*Math.PI/180))<=n2 ? (180/Math.PI)*Math.asin((n1*Math.sin(i*Math.PI/180))/n2) : NaN )"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "med1", "label": "Medium n1"}, {"id": "interface", "label": "Boundary"}, {"id": "med2", "label": "Medium n2"}
                        ], "arrows": [
                            {"from": "med1", "to": "interface", "label": "incidence i"}, {"from": "interface", "to": "med2", "label": "refraction r"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "fluids_rho_gh":
        # Hydrostatic pressure: P = ρ g h → kPa for readability
        defaults = {"rho": 1000.0, "h": 2.0, "g": 9.8}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_fluids",
            "type": "teaching_visual",
            "total_duration_ms": 5600,
            "metadata": {"topic": "Fluids: P=ρgh", "subject": subject or "physics", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Depth badhao → pressure kaise badhega?",
                    "emphasis": None,
                    "duration_ms": 2800,
                    "blocks": [
                        {"type": "predict_card", "question": "h double → P?", "expected": "P doubles (linear)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "rho", "label": "ρ (kg/m³)", "min": 500, "max": 1500, "step": 50, "default": p.get("rho", 1000)},
                            {"id": "h", "label": "h (m)", "min": 0.5, "max": 10, "step": 0.5, "default": p.get("h", 2)},
                            {"id": "g", "label": "g (m/s²)", "min": 1.6, "max": 9.8, "step": 0.1, "default": p.get("g", 9.8)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "P", "label": "Pressure", "unit": "kPa", "expr": "(rho*g*h)/1000"}
                        ]},
                        {"type": "live_plot", "series": [
                            {"label": "P vs h", "expr": "(rho*9.8*x)/1000", "x_min": 0, "x_max": 10, "step": 1}
                        ]}
                    ]
                }
            ]
        }

    if concept == "circuits_sp":
        # Two resistors: series vs parallel toggle; total current at voltage V
        defaults = {"R1": 4.0, "R2": 6.0, "V": 10.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_circuits_sp",
            "type": "teaching_visual",
            "total_duration_ms": 5800,
            "metadata": {"topic": "Circuits: Series vs Parallel", "subject": subject or "physics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Series me add hota, parallel me reduce hota — check karo.",
                    "emphasis": None,
                    "duration_ms": 2900,
                    "blocks": [
                        {"type": "predict_card", "question": "Parallel pe Req?", "expected": "Smaller than each."},
                        {"type": "control_panel", "sliders": [
                            {"id": "R1", "label": "R1 (Ω)", "min": 1, "max": 20, "step": 1, "default": p.get("R1", 4)},
                            {"id": "R2", "label": "R2 (Ω)", "min": 1, "max": 20, "step": 1, "default": p.get("R2", 6)},
                            {"id": "V", "label": "V (V)", "min": 0, "max": 20, "step": 1, "default": p.get("V", 10)}
                        ], "toggles": [
                            {"id": "parallel", "label": "Parallel mode", "default": True}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "Req", "label": "R_eq", "unit": "Ω", "expr": "parallel ? ((R1*R2)/(R1+R2)) : (R1+R2)"},
                            {"id": "I", "label": "Current", "unit": "A", "expr": "V / ( parallel ? ((R1*R2)/(R1+R2)) : (R1+R2) )"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "src", "label": "Source V"}, {"id": "n1", "label": "R1"}, {"id": "n2", "label": "R2"}, {"id": "out", "label": "Load"}
                        ], "arrows": [
                            {"from": "src", "to": "n1", "label": "path 1"}, {"from": "src", "to": "n2", "label": "path 2"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "equilibrium_shift":
        # Le Chatelier: simple shift score using Δn and temperature effect (exothermic toggle)
        defaults = {"conc": 1.0, "T": 300.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_equilibrium",
            "type": "teaching_visual",
            "total_duration_ms": 5600,
            "metadata": {"topic": "Equilibrium Shift (Le Chatelier)", "subject": subject or "chemistry", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Concentration/temperature badlo — kidhar shift hota?",
                    "emphasis": None,
                    "duration_ms": 2800,
                    "blocks": [
                        {"type": "predict_card", "question": "Temp↑ (exo)?", "expected": "Left (reactants)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "conc", "label": "Reactant conc (M)", "min": 0.1, "max": 2, "step": 0.1, "default": p.get("conc", 1.0)},
                            {"id": "T", "label": "Temp (K)", "min": 280, "max": 360, "step": 2, "default": p.get("T", 300.0)}
                        ], "toggles": [
                            {"id": "exo", "label": "Exothermic", "default": True}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "shift", "label": "Shift score", "unit": "(L=−, R=+)", "expr": "(exo ? (300-T) : (T-300)) / 50 + (conc-1)"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "R", "label": "Reactants"}, {"id": "P", "label": "Products"}
                        ], "arrows": [
                            {"from": "R", "to": "P", "label": "→"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "snell_critical":
        # Critical angle c = asin(n2/n1) when n1 > n2; else no TIR
        defaults = {"n1": 1.50, "n2": 1.33}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_snell_critical",
            "type": "teaching_visual",
            "total_duration_ms": 5200,
            "metadata": {"topic": "Critical Angle (TIR)", "subject": subject or "physics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "n1>n2 ho to critical angle define hota hai.",
                    "emphasis": None,
                    "duration_ms": 2600,
                    "blocks": [
                        {"type": "predict_card", "question": "n1↑ (denser) → c?", "expected": "c decreases."},
                        {"type": "control_panel", "sliders": [
                            {"id": "n1", "label": "n1", "min": 1.0, "max": 1.8, "step": 0.01, "default": p.get("n1", 1.5)},
                            {"id": "n2", "label": "n2", "min": 1.0, "max": 1.6, "step": 0.01, "default": p.get("n2", 1.33)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "c", "label": "Critical angle c", "unit": "°", "expr": "(n1>n2 ? (180/Math.PI)*Math.asin(n2/n1) : NaN)"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "dense", "label": "n1 (denser)"}, {"id": "rarer", "label": "n2 (rarer)"}
                        ], "arrows": [
                            {"from": "dense", "to": "rarer", "label": "at c ⇒ 90°"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "circuits_divider":
        # Voltage divider with optional load R3
        defaults = {"R1": 1000.0, "R2": 1000.0, "R3": 0.0, "V": 9.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_circuits_divider",
            "type": "teaching_visual",
            "total_duration_ms": 5600,
            "metadata": {"topic": "Voltage Divider (loaded)", "subject": subject or "physics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Load lagane par Vout girta hai — check karo.",
                    "emphasis": None,
                    "duration_ms": 2800,
                    "blocks": [
                        {"type": "predict_card", "question": "R3 ↓ → Vout?", "expected": "Decreases (loading)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "R1", "label": "R1 (Ω)", "min": 100, "max": 10000, "step": 100, "default": p.get("R1", 1000)},
                            {"id": "R2", "label": "R2 (Ω)", "min": 100, "max": 10000, "step": 100, "default": p.get("R2", 1000)},
                            {"id": "R3", "label": "Load R3 (Ω)", "min": 0, "max": 10000, "step": 100, "default": p.get("R3", 0)},
                            {"id": "V", "label": "V_in (V)", "min": 1, "max": 20, "step": 1, "default": p.get("V", 9)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "Vout", "label": "V_out", "unit": "V", "expr": "( (R3>0 ? 1/(1/R2 + 1/R3) : R2) / ( R1 + (R3>0 ? 1/(1/R2 + 1/R3) : R2) ) ) * V"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "Vin", "label": "Vin"}, {"id": "Tap", "label": "Tap"}, {"id": "Gnd", "label": "GND"}
                        ], "arrows": [
                            {"from": "Vin", "to": "Tap", "label": "R1"}, {"from": "Tap", "to": "Gnd", "label": "R2 || R3"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "fluids_utube":
        # U-tube two-fluid columns: ratio h2/h1 = rho1/rho2 (illustrative)
        defaults = {"rho1": 1000.0, "rho2": 800.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_fluids_utube",
            "type": "teaching_visual",
            "total_duration_ms": 5200,
            "metadata": {"topic": "U‑Tube Balance", "subject": subject or "physics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Dense fluid ka column chhota hota — ratio dekho.",
                    "emphasis": None,
                    "duration_ms": 2600,
                    "blocks": [
                        {"type": "predict_card", "question": "ρ2 > ρ1 → h2?", "expected": "h2 smaller."},
                        {"type": "control_panel", "sliders": [
                            {"id": "rho1", "label": "ρ1 (kg/m³)", "min": 500, "max": 2000, "step": 50, "default": p.get("rho1", 1000)},
                            {"id": "rho2", "label": "ρ2 (kg/m³)", "min": 500, "max": 2000, "step": 50, "default": p.get("rho2", 800)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "ratio", "label": "h2/h1", "unit": "", "expr": "rho1/rho2"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "col1", "label": "Fluid 1"}, {"id": "col2", "label": "Fluid 2"}
                        ], "arrows": [
                            {"from": "col1", "to": "col2", "label": "balance"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "equilibrium_pv":
        # Pressure/volume effect via Δn (gas moles change)
        defaults = {"dn": -1.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_equilibrium_pv",
            "type": "teaching_visual",
            "total_duration_ms": 5200,
            "metadata": {"topic": "Equilibrium: Pressure/Volume", "subject": subject or "chemistry", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Δn<0 → pressure badhane par right shift.",
                    "emphasis": None,
                    "duration_ms": 2600,
                    "blocks": [
                        {"type": "predict_card", "question": "incP on & Δn<0 →?", "expected": "Right (products)."},
                        {"type": "control_panel", "sliders": [
                            {"id": "dn", "label": "Δn (prod−react)", "min": -3, "max": 3, "step": 1, "default": p.get("dn", -1)}
                        ], "toggles": [
                            {"id": "incP", "label": "Increase Pressure", "default": True}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "shift", "label": "Shift score", "unit": "(L=−, R=+)", "expr": "incP ? ( -dn ) : dn"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "R", "label": "Reactants"}, {"id": "P", "label": "Products"}
                        ], "arrows": [
                            {"from": "R", "to": "P", "label": "⇄"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "enzyme_activity":
        # Enzyme activity vs Temperature and pH (product of two Gaussians around optima)
        defaults = {"T": 37.0, "pH": 7.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_enzyme_activity",
            "type": "teaching_visual",
            "total_duration_ms": 5600,
            "metadata": {"topic": "Enzyme Activity", "subject": subject or "biology", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Temp/pH badlo — activity peak dekhna.",
                    "emphasis": None,
                    "duration_ms": 2800,
                    "blocks": [
                        {"type": "predict_card", "question": "pH दूर from 7 → activity?", "expected": "Drops."},
                        {"type": "control_panel", "sliders": [
                            {"id": "T", "label": "Temp (°C)", "min": 0, "max": 60, "step": 1, "default": p.get("T", 37)},
                            {"id": "pH", "label": "pH", "min": 1, "max": 14, "step": 0.5, "default": p.get("pH", 7)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "A", "label": "Activity (norm)", "unit": "", "expr": "Math.exp(-Math.pow((T-37)/10,2)) * Math.exp(-Math.pow((pH-7)/2,2))"}
                        ]},
                        {"type": "live_plot", "series": [
                            {"label": "Activity vs T (pH fixed)", "expr": "Math.exp(-Math.pow((x-37)/10,2)) * Math.exp(-Math.pow((pH-7)/2,2))", "x_min": 0, "x_max": 60, "step": 2}
                        ]}
                    ]
                }
            ]
        }

    if concept == "cell_respiration":
        # Simple flow with oxygen/glucose toggles affecting a notional rate
        defaults = {"O2": 1.0, "Glc": 1.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_cell_respiration",
            "type": "teaching_visual",
            "total_duration_ms": 5200,
            "metadata": {"topic": "Cellular Respiration", "subject": subject or "biology", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Glucose+O2 → Energy + CO2 + H2O (rate intuition).",
                    "emphasis": None,
                    "duration_ms": 2600,
                    "blocks": [
                        {"type": "predict_card", "question": "O2 कम → rate?", "expected": "Drops."},
                        {"type": "control_panel", "sliders": [
                            {"id": "O2", "label": "Oxygen level", "min": 0, "max": 1, "step": 0.1, "default": p.get("O2", 1)},
                            {"id": "Glc", "label": "Glucose level", "min": 0, "max": 1, "step": 0.1, "default": p.get("Glc", 1)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "rate", "label": "Rate (norm)", "unit": "", "expr": "O2*Glc"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "glc", "label": "Glucose"}, {"id": "o2", "label": "Oxygen"}, {"id": "mito", "label": "Mitochondria"}, {"id": "atp", "label": "Energy"}
                        ], "arrows": [
                            {"from": "glc", "to": "mito", "label": "input"}, {"from": "o2", "to": "mito", "label": "input"}, {"from": "mito", "to": "atp", "label": "output"}
                        ]}
                    ]
                }
            ]
        }

    if concept == "math_quadratic":
        # y = a x^2 + b x + c; discriminant and roots
        defaults = {"a": 1.0, "b": 0.0, "c": 0.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_math_quadratic",
            "type": "teaching_visual",
            "total_duration_ms": 5800,
            "metadata": {"topic": "Quadratic (Graph & Roots)", "subject": subject or "mathematics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "a,b,c ghumao — shape aur roots dekho.",
                    "emphasis": None,
                    "duration_ms": 2900,
                    "blocks": [
                        {"type": "predict_card", "question": "a<0 → shape?", "expected": "Opens down."},
                        {"type": "control_panel", "sliders": [
                            {"id": "a", "label": "a", "min": -3, "max": 3, "step": 0.5, "default": p.get("a", 1)},
                            {"id": "b", "label": "b", "min": -5, "max": 5, "step": 0.5, "default": p.get("b", 0)},
                            {"id": "c", "label": "c", "min": -5, "max": 5, "step": 0.5, "default": p.get("c", 0)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "D", "label": "Discriminant", "unit": "", "expr": "b*b - 4*a*c"},
                            {"id": "x1", "label": "x1", "unit": "", "expr": "(b*b-4*a*c)>=0 ? (-b + Math.sqrt(b*b-4*a*c))/(2*a) : NaN"},
                            {"id": "x2", "label": "x2", "unit": "", "expr": "(b*b-4*a*c)>=0 ? (-b - Math.sqrt(b*b-4*a*c))/(2*a) : NaN"}
                        ]},
                        {"type": "live_plot", "series": [
                            {"label": "y = ax²+bx+c", "expr": "a*x*x + b*x + c", "x_min": -10, "x_max": 10, "step": 1}
                        ]}
                    ]
                }
            ]
        }

    if concept == "math_linear":
        # y = m x + b; slope/intercept intuition
        defaults = {"m": 1.0, "b": 0.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_math_linear",
            "type": "teaching_visual",
            "total_duration_ms": 5200,
            "metadata": {"topic": "Linear (Slope & Intercept)", "subject": subject or "mathematics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "m aur b badlo — line ka tilt/shift dekho.",
                    "emphasis": None,
                    "duration_ms": 2600,
                    "blocks": [
                        {"type": "predict_card", "question": "b↑ → line?", "expected": "Shifts up."},
                        {"type": "control_panel", "sliders": [
                            {"id": "m", "label": "m", "min": -5, "max": 5, "step": 0.5, "default": p.get("m", 1)},
                            {"id": "b", "label": "b", "min": -5, "max": 5, "step": 0.5, "default": p.get("b", 0)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "slope", "label": "Slope", "unit": "", "expr": "m"}
                        ]},
                        {"type": "live_plot", "series": [
                            {"label": "y = mx + b", "expr": "m*x + b", "x_min": -10, "x_max": 10, "step": 1}
                        ]}
                    ]
                }
            ]
        }

    if concept == "gas_law_charles":
        # Charles’ Law focus: V ∝ T at constant P (assume P=1 atm, n=1 mol)
        defaults = {"T": 300.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_gas_law_charles",
            "type": "teaching_visual",
            "total_duration_ms": 5800,
            "metadata": {"topic": "Charles’ Law (V ∝ T)", "subject": subject or "chemistry", "concept_type": "law"},
            "stages": [
                {
                    "narration": "Temp badhao (P same) to volume kaise badlega?",
                    "emphasis": None,
                    "duration_ms": 2900,
                    "blocks": [
                        {"type": "predict_card", "question": "T↑ (P same) → V?", "expected": "V increases linearly."},
                        {"type": "control_panel", "sliders": [
                            {"id": "T", "label": "Temp (K)", "min": 250, "max": 400, "step": 5, "default": p.get("T", 300.0)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "V", "label": "Volume", "unit": "L", "expr": "0.082057*T"}
                        ]},
                        {"type": "live_plot", "series": [
                            {"label": "V vs T (P=1 atm)", "expr": "0.082057*x", "x_min": 250, "x_max": 400, "step": 5}
                        ]}
                    ]
                }
            ]
        }

    if concept == "optics_plane_mirror":
        # Plane mirror: |m| ≈ 1, image distance ≈ -u (virtual)
        defaults = {"u": 30.0}
        p = _merge(defaults, params)
        return {
            "visual_id": "dyn_optics_plane_mirror",
            "type": "teaching_visual",
            "total_duration_ms": 5200,
            "metadata": {"topic": "Plane Mirror Basics", "subject": subject or "physics", "concept_type": "concept"},
            "stages": [
                {
                    "narration": "Plane mirror: size same, peeche virtual image.",
                    "emphasis": None,
                    "duration_ms": 2600,
                    "blocks": [
                        {"type": "predict_card", "question": "u badla to image kahan?", "expected": "v ≈ -u (virtual)"},
                        {"type": "control_panel", "sliders": [
                            {"id": "u", "label": "Object u (cm)", "min": 10, "max": 100, "step": 2, "default": p.get("u", 30.0)}
                        ]},
                        {"type": "meter_panel", "meters": [
                            {"id": "v", "label": "Image v (cm)", "unit": "cm", "expr": "-u"},
                            {"id": "mag", "label": "|Magnification|", "unit": "", "expr": "1"}
                        ]},
                        {"type": "flow_map", "nodes": [
                            {"id": "obj", "label": "Object"}, {"id": "mirror", "label": "Plane Mirror"}, {"id": "img", "label": "Image (virtual)"}
                        ], "arrows": [
                            {"from": "obj", "to": "mirror", "label": "rays"}, {"from": "mirror", "to": "img", "label": "reflected (virtual)"}
                        ]}
                    ]
                }
            ]
        }

    return None
