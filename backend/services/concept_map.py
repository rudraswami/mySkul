from __future__ import annotations

"""
Concept mapping for dynamic visual synthesis.

Maps question text → (subject, concept_id) with light heuristics and synonyms.
This is intentionally small and explicit; it can grow via a registry later.
"""

from typing import Optional, Tuple


PHYSICS_CONCEPTS = {
    "ohm": "ohm_law",
    "resistance": "ohm_law",
    "v=ir": "ohm_law",
    "ohm's": "ohm_law",
    "newton": "newton_law",
    "first law": "newton_first",
    "second law": "newton_second",
    "third law": "newton_third",
    "kinematics": "kinematics_1d",
    "v=u+at": "kinematics_1d",
    "projectile": "projectile",
    "time of flight": "projectile",
    "range": "projectile",
    "work energy power": "wep",
    "work": "wep",
    "energy": "wep",
    "power": "wep",
    "kinetic energy": "wep",
    "potential energy": "wep",
    "momentum": "momentum_impulse",
    "impulse": "momentum_impulse",
    "ray": "optics_ray",
    "lens": "optics_ray",
    "focal": "optics_ray",
    "convex": "optics_ray",
    "concave": "optics_ray",
    "plane mirror": "optics_plane_mirror",
    "mirror": "optics_mirror",
    "refraction": "snell_refraction",
    "snell": "snell_refraction",
    "critical angle": "snell_critical",
    "tir": "snell_critical",
    "total internal reflection": "snell_critical",
    "fluid": "fluids_rho_gh",
    "rho gh": "fluids_rho_gh",
    "depth": "fluids_rho_gh",
    "series": "circuits_sp",
    "parallel": "circuits_sp",
    "equivalent resistance": "circuits_sp",
    "divider": "circuits_divider",
    "voltage divider": "circuits_divider",
}

CHEM_CONCEPTS = {
    "ionic": "bonding",
    "covalent": "bonding",
    "strong acid": "acids_strength",
    "weak acid": "acids_strength",
    "ph": "acids_strength",
    "gas": "gas_law",
    "boyle": "gas_law",
    "charles": "gas_law",
    "pv": "gas_law",
    "pressure": "gas_law",
    "volume": "gas_law",
    "temperature": "gas_law",
    "charles": "gas_law_charles",
    "equilibrium": "equilibrium_shift",
    "le chatelier": "equilibrium_shift",
    "shift": "equilibrium_shift",
    "pressure effect": "equilibrium_pv",
    "volume effect": "equilibrium_pv",
    "delta n": "equilibrium_pv",
}

BIO_CONCEPTS = {
    "photosynthesis": "photosynthesis",
    "respiration": "cell_respiration",
    "enzyme": "enzyme_activity",
    "enzyme activity": "enzyme_activity",
}

MATH_CONCEPTS = {
    "quadratic": "math_quadratic",
    "parabola": "math_quadratic",
    "roots": "math_quadratic",
    "discriminant": "math_quadratic",
    "ax^2": "math_quadratic",
    "linear": "math_linear",
    "slope": "math_linear",
    "intercept": "math_linear",
}


def detect_concept(question: str, subject_hint: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    q = (question or "").lower()
    subj = (subject_hint or "").lower()

    # Subject-directed mapping first
    if subj == "physics":
        for key, cid in PHYSICS_CONCEPTS.items():
            if key in q:
                return ("physics", cid)
    if subj == "chemistry":
        for key, cid in CHEM_CONCEPTS.items():
            if key in q:
                return ("chemistry", cid)
    if subj == "biology":
        for key, cid in BIO_CONCEPTS.items():
            if key in q:
                return ("biology", cid)
    if subj in ("math", "mathematics"):
        for key, cid in MATH_CONCEPTS.items():
            if key in q:
                return ("mathematics", cid)

    # Fallback: scan all subjects
    for key, cid in PHYSICS_CONCEPTS.items():
        if key in q:
            return ("physics", cid)
    for key, cid in CHEM_CONCEPTS.items():
        if key in q:
            return ("chemistry", cid)
    for key, cid in BIO_CONCEPTS.items():
        if key in q:
            return ("biology", cid)
    for key, cid in MATH_CONCEPTS.items():
        if key in q:
            return ("mathematics", cid)

    return (None, None)
