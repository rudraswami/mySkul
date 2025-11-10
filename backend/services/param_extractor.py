from __future__ import annotations

"""
Lightweight parameter extractor for numbers + units from a question.
This is a pragmatic regex approach good enough for dynamic visuals.
"""

import re
from typing import Dict


NUM_RE = re.compile(r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z°Ω/²^\-]+)?")


def extract_params(question: str) -> Dict[str, float]:
    # Keep original for unit-case cues, and lower for general pattern checks
    q_raw = question or ""
    q = q_raw.lower()
    params: Dict[str, float] = {}

    # Projectile common symbols
    m = re.search(r"u\s*=\s*(\d+(?:\.\d+)?)", q)
    if m:
        params["u"] = float(m.group(1))
    # angle in degrees (with ° or 'deg' or explicit 'angle=')
    m = re.search(r"angle\s*=\s*(\d+(?:\.\d+)?)|\b(\d+(?:\.\d+)?)\s*°|\b(\d+(?:\.\d+)?)\s*deg\b", q)
    if m:
        val = m.group(1) or m.group(2) or m.group(3)
        if val:
            params["ang"] = float(val)

    # Ohm's: V, R, I (context-aware: if ohm/volt/resistance present or explicit V unit)
    ohm_ctx = any(k in q for k in ["ohm", "resistance", "volt", "current", "circuit", "v=ir", "ohm's"])
    m = re.search(r"v\s*=\s*(\d+(?:\.\d+)?)\s*v\b", q) or (ohm_ctx and re.search(r"v\s*=\s*(\d+(?:\.\d+)?)\b", q))
    if m:
        params["V"] = float(m.group(1))
    m = re.search(r"r\s*=\s*(\d+(?:\.\d+)?)\s*Ω?\b", q)
    if m:
        params["R"] = float(m.group(1))
    m = re.search(r"i\s*=\s*(\d+(?:\.\d+)?)\s*a?\b", q)
    if m:
        params["I"] = float(m.group(1))

    # Kinematics: a, u, t (generic)
    m = re.search(r"a\s*=\s*(\d+(?:\.\d+)?)", q)
    if m:
        params["a"] = float(m.group(1))
    m = re.search(r"t\s*=\s*(\d+(?:\.\d+)?)", q)
    if m:
        params["t"] = float(m.group(1))

    # Momentum: mass m (kg), velocity v (m/s), force F (N), delta t (s)
    if any(k in q for k in ["momentum", "impulse", "collision"]) or not ohm_ctx:
        mkg = re.search(r"\bm\s*=\s*(\d+(?:\.\d+)?)\s*kg\b", q)
        if mkg:
            params["m"] = float(mkg.group(1))
        vms = re.search(r"\bv\s*=\s*(\d+(?:\.\d+)?)\s*m\s*\/\s*s\b", q)
        if vms:
            params["v"] = float(vms.group(1))
        fnewt = re.search(r"\bf\s*=\s*(\d+(?:\.\d+)?)\s*n\b", q)
        if fnewt:
            params["F"] = float(fnewt.group(1))
        dtt = re.search(r"(delta\s*t|Δt|dt)\s*=\s*(\d+(?:\.\d+)?)\b", q_raw, re.IGNORECASE)
        if dtt:
            params["dt"] = float(dtt.group(2))

    # Acids: concentration (require acid context to avoid meters)
    if any(k in q for k in ["acid", "hcl", "h2so4", "naoh", "ph"]):
        # Match e.g., 0.1 M, 0.01 mol/L, 1e-2 M
        m = re.search(r"(\d+(?:\.\d+)?(?:e-?\d+)?)\s*(m|mol\/l|mol\s*per\s*l)\b", q)
        if m:
            try:
                params["C"] = float(m.group(1))
            except Exception:
                pass

    # Gas law (PV=nRT) context: pressure/volume/temperature
    gas_ctx = any(k in q for k in ["gas", "pv", "boyle", "charles", "pressure", "volume", "temperature", "atm", "kpa", "kelvin"])
    if gas_ctx:
        # P in atm/kPa/Pa
        mp = re.search(r"\bp\s*=\s*(\d+(?:\.\d+)?)\s*(atm|kpa|pa)?\b", q)
        if mp:
            val = float(mp.group(1))
            unit = (mp.group(2) or 'atm').lower()
            if unit == 'kpa':
                val = val / 101.325
            elif unit == 'pa':
                val = val / 101325.0
            params["P"] = val  # atm
        # V in L or m^3
        mv = re.search(r"\bv\s*=\s*(\d+(?:\.\d+)?)\s*(l|liter|litre|m\^?3|m3)?\b", q)
        if mv and not ohm_ctx:  # avoid voltage confusion
            vv = float(mv.group(1))
            unit = (mv.group(2) or 'l').lower()
            if unit in ['m^3', 'm3']:
                vv = vv * 1000.0  # m^3 → L
            params["V"] = vv  # liters
        # T in K or C
        mt = re.search(r"\bt\s*=\s*(\d+(?:\.\d+)?)\s*(k|c|°c)?\b", q)
        if mt:
            tt = float(mt.group(1))
            unit = (mt.group(2) or 'k').lower()
            if unit in ['c', '°c']:
                tt = tt + 273.15
            params["T"] = tt

    # Optics (lens): focal length f (cm), object distance u (cm)
    if any(k in q for k in ["lens", "focal", "ray", "convex", "concave", "optics"]):
        ff = re.search(r"\bf\s*=\s*(\d+(?:\.\d+)?)\s*cm\b", q)
        if ff:
            params["f"] = float(ff.group(1))
        uu = re.search(r"\bu\s*=\s*(\d+(?:\.\d+)?)\s*cm\b", q)
        if uu:
            params["u"] = float(uu.group(1))

    # Snell: n1, n2, i (deg)
    if any(k in q for k in ["snell", "refraction", "refract", "critical angle"]):
        n1 = re.search(r"n1\s*=\s*(\d+(?:\.\d+)?)", q)
        if n1:
            params["n1"] = float(n1.group(1))
        n2 = re.search(r"n2\s*=\s*(\d+(?:\.\d+)?)", q)
        if n2:
            params["n2"] = float(n2.group(1))
        ai = re.search(r"i\s*=\s*(\d+(?:\.\d+)?)\s*(deg|°)?\b", q)
        if ai:
            params["i"] = float(ai.group(1))

    # Fluids: rho (kg/m^3), h (m), g (m/s^2)
    if any(k in q for k in ["fluid", "rho gh", "hydrostatic", "depth", "pressure in water"]):
        rr = re.search(r"rho\s*=\s*(\d+(?:\.\d+)?)\s*kg\s*\/\s*m\^?3\b", q)
        if rr:
            params["rho"] = float(rr.group(1))
        hh = re.search(r"h\s*=\s*(\d+(?:\.\d+)?)\s*m\b", q)
        if hh:
            params["h"] = float(hh.group(1))
        gg = re.search(r"g\s*=\s*(\d+(?:\.\d+)?)\s*m\s*\/\s*s\^?2\b", q)
        if gg:
            params["g"] = float(gg.group(1))

    # Circuits: R1, R2
    if any(k in q for k in ["series", "parallel", "equivalent resistance", "circuit"]):
        r1 = re.search(r"r1\s*=\s*(\d+(?:\.\d+)?)\s*Ω?\b", q)
        if r1:
            params["R1"] = float(r1.group(1))
        r2 = re.search(r"r2\s*=\s*(\d+(?:\.\d+)?)\s*Ω?\b", q)
        if r2:
            params["R2"] = float(r2.group(1))
        r3 = re.search(r"r3\s*=\s*(\d+(?:\.\d+)?)\s*Ω?\b", q)
        if r3:
            params["R3"] = float(r3.group(1))

    # Math: quadratic coefficients
    if any(k in q for k in ["quadratic", "parabola", "roots", "discriminant", "ax^2"]):
        aa = re.search(r"\ba\s*=\s*(-?\d+(?:\.\d+)?)\b", q)
        if aa:
            params["a"] = float(aa.group(1))
        bb = re.search(r"\bb\s*=\s*(-?\d+(?:\.\d+)?)\b", q)
        if bb:
            params["b"] = float(bb.group(1))
        cc = re.search(r"\bc\s*=\s*(-?\d+(?:\.\d+)?)\b", q)
        if cc:
            params["c"] = float(cc.group(1))

    # Math: linear m,b
    if any(k in q for k in ["linear", "slope", "intercept"]):
        mm = re.search(r"\bm\s*=\s*(-?\d+(?:\.\d+)?)\b", q)
        if mm:
            params["m"] = float(mm.group(1))
        bb2 = re.search(r"\bb\s*=\s*(-?\d+(?:\.\d+)?)\b", q)
        if bb2:
            params["b"] = float(bb2.group(1))

    # Biology: enzyme T and pH
    if any(k in q for k in ["enzyme", "activity"]):
        tC = re.search(r"\b(?:temp|t)\s*=\s*(\d+(?:\.\d+)?)\s*(?:c|°c)?\b", q)
        if tC:
            params["T"] = float(tC.group(1))
        pH = re.search(r"\bpH\s*=\s*(\d+(?:\.\d+)?)\b", q)
        if pH:
            params["pH"] = float(pH.group(1))

    # Equilibrium PV: delta n
    if any(k in q for k in ["delta n", "Δn", "equilibrium", "le chatelier"]):
        dn = re.search(r"(delta\s*n|Δn)\s*=\s*(-?\d+(?:\.\d+)?)", q_raw, re.IGNORECASE)
        if dn:
            try:
                params["dn"] = float(dn.group(2))
            except Exception:
                pass

    return params
