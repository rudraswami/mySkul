# Here are your Instructions

## Visual Engine (QA + Hints)

- Theme hint (palette only): set `REACT_APP_VISUAL_THEME` to one of `cricket | bollywood | cooking | festival` for demos/QA. This does not affect semantic context selection (still concept-driven), only colors/accents.
- Auto-advance frames globally (QA): set `REACT_APP_FORCE_AUTO_ADVANCE=true`. Optional: `REACT_APP_AUTO_ADVANCE_INTERVAL_MS=1300`.
- Per-response hints from backend (non-breaking): include a `visual_data` object alongside the normal tutor response.

Example backend payload fragment:

```
{
  "practical_explanation": "...",
  "metaphor": "...",
  "visual_data": {
    "theme": "festival",          // optional; overrides palette only
    "subject": "chemistry",       // optional; biases semantic context
    "scene_json": null             // optional; if provided, is used as-is
  }
}
```

Notes:
- Semantic routing is concept-aware (integration → accumulation_process, quadratic → parabolic_motion, newton → motion_dynamics, chemistry → reaction/bonding, history → timeline, probability → bars/slider). Themes only change palette.
- Rangoli is kept only as a rare edge fallback; Chemistry/History/Probability now render dedicated explanatory scenes.
