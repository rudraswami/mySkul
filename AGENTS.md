# Repository Guidelines

## Project Structure & Module Organization
- `backend/` — FastAPI service; entry `backend/main.py`, deps `backend/requirements.txt`, tests `backend/tests/`.
- `frontend/` — React (CRACO); sources `frontend/src/`, static `frontend/public/`.
- `tests/` — cross‑cutting or integration tests.
- `docs/` — documentation; `screenshot/` — reference assets.

## Build, Test, and Development Commands
Backend (Python 3.10+)
- Setup: `python -m venv .venv && .venv\\Scripts\\activate && pip install -r backend/requirements.txt`
- Run API: `uvicorn backend.main:app --host 0.0.0.0 --port 8001`
- Lint/format: `flake8 backend && black backend && isort backend && mypy backend`
- Tests: `pytest backend/tests -q`

Frontend (Yarn)
- Install: `cd frontend && yarn install`
- Dev server: `yarn start`
- Build: `yarn build`
- Tests: `yarn test`

## Coding Style & Naming Conventions
- Python: 4‑space indent; type hints in new/changed code. Names: `snake_case` (vars/functions), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants).
- JS/TS/React: 2‑space indent; components in `PascalCase` (e.g., `src/components/UserCard.tsx`). Prefer functional components and hooks.
- Tools: Python (`black`, `isort`, `flake8`, `mypy`); Frontend (`eslint`). Fix issues before committing.

## Testing Guidelines
- Python: tests in `backend/tests/` as `test_*.py`. Use fixtures; mark slow/integration appropriately.
- Frontend: tests next to components as `*.test.tsx` or under `src/__tests__/`.
- Aim for meaningful coverage on core modules; add reproduction tests for bug fixes.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`). Imperative mood, concise scope; reference issues when applicable.
- PRs: include description, rationale, and test plan (commands + results). Add screenshots for UI changes; link related issues; update docs when behavior/config changes.

## Security & Configuration
- Do not commit secrets. Use env files: `backend/.env` (e.g., `MONGO_URL`, `DB_NAME`, `JWT_SECRET`, `BACKEND_URL`, `FRONTEND_URL`) and `frontend/.env` for UI configs.
- Keep local tokens least‑privilege; rotate if leaked.

---

## Visual Sketch Engine (Druv-AI)

### Overview
The **Druv-AI-Visual-Sketch-Engine** converts educational questions into hand-drawn SVG sketches that feel like a friend explaining concepts at 2 AM before an exam. The system uses a 3-layer architecture with dynamic metaphor selection to create culturally relevant, exam-focused visuals.

### Core Philosophy
**Emotional Mandate:** Students aren't asking for diagrams—they're asking: "Bhai, yeh samjha de. Kal exam hai, dar lag raha hai."
- Visuals must emotionally connect, not just educate
- Should feel personal, imperfect, rushed (like a friend scribbled it)
- Must be screenshot-worthy (students will WhatsApp it to 5 friends)
- Should acknowledge exam fear and use student language (Hinglish/regional slang)

### Architecture Components

#### 1. Metaphor Engine (`backend/services/metaphor_engine.py`)
**Step 1: Concept Deconstruction**
- Extracts core actions, entities, constraints from questions
- Maps verbs to action taxonomy (transfer, accumulate, compare, transform, search, optimize, prove, construct, predict)
- Detects marks distribution from question text
- Returns `ConceptBundle` with question analysis

**Step 2: 5-Muse Candidate Generation**
- Five universal metaphor categories: Family, Food, Cricket, Bollywood, Gaming
- Always includes Family + Food (most universal)
- Conditionally includes Cricket/Bollywood/Gaming based on student DNA
- Generates 3-5 `MetaphorCandidate` objects with hooks, mappings, boundaries

**Step 3: Scoring & Selection**
- Scores candidates on 4 dimensions:
  - **Intuitiveness** (35%): How naturally the metaphor maps to concept
  - **Exam Relevance** (30%): Alignment with marks structure
  - **Cultural Fit** (25%): Match with student profile/interests
  - **Freshness** (10%): Prevents overuse of same metaphors
- Returns top 3 distinct metaphors

#### 2. Visual Sketch Generators
**Hand-Drawn Sketch Engine** (`backend/services/handdrawn_sketch.py`)
- Creates compact SVG (<10KB) with "Professor Chalkboard" feel
- Uses only `<path>` and `<text>` elements (no circles/rects/lines)
- Indian color palette: Saffron (#FF9933), Green (#138808), Navy (#000080)
- Applies jitter effect for hand-drawn appearance
- Deterministic random seed for caching

**Dynamic Visual Sketch** (`backend/services/dynamic_visual_sketch.py`)
- Unified facade `create_visual_sketch(question, student_profile)`
- Integrates metaphor selection with SVG generation
- Returns dict with SVG, metaphors_used, estimated_marks

#### 3. Three-Layer Visual Architecture
**Layer 1: Scientific Skeleton (The "Marks Bone")**
- Goal: Show only what's needed to score marks
- Style: Imperfect hand-drawn but scientifically accurate
- Animation: Draws first (auto after 0.5s) to hook attention
- Content: Core concept diagram (nodes, arrows, labels)

**Layer 2: Exam Warfare Sticky Notes (The "Topper's Cheat Sheet")**
- Goal: Make student feel they have insider info
- Content:
  - Mark breakdown per element
  - Common mistakes (90% students lose marks here)
  - Topper hacks (with specific techniques)
  - PYQ references (past year question patterns)
- Visual: Yellow sticky notes with navy text

**Layer 3: Cultural Soul Blend (The "Memory Hook")**
- Goal: Trigger "Mere life mein bhi yahi hota hai!" moment
- Style: 10-12% opacity background layer
- Content: Blended metaphor motifs from top 3 selected muses
- Layout: Subtle waves/lanes with metaphor labels

#### 4. Progressive Animation System
**5-Step Tap-to-Advance Animation:**
1. **Auto-draw** (0.5s): L1 skeleton appears automatically
2. **Click/Tap**: L1 connections (arrows) reveal
3. **Click/Tap**: L1 complete with all nodes
4. **Click/Tap**: L2 exam annotations overlay
5. **Click/Tap**: L3 cultural metaphors fade in

Uses SMIL `<animate>` with `begin` triggers (no JavaScript dependency)

#### 5. Validation System (`backend/services/visual_validation.py`)
**Quality Tests:**
- File size <10KB
- No gradients (linearGradient/radialGradient)
- Minimum 5 `<path>` elements (hand-drawn feel)
- Exam annotations present (Marks/Topper/emojis)
- Indian color palette used
- Progressive animation implemented
- No forbidden shapes (circle/rect/line)
- Jitter detected (>0.5px variance)

Returns `True` only if all 8 tests pass.

### Student DNA System
Optional student profile for personalized metaphor selection:
```python
StudentDNA(
    level="class_12",           # Education level
    interests=["cricket", "gaming"],  # For metaphor selection
    locale_language="hi-IN",    # For regional content
    gender="M",                 # Influences Cricket/Bollywood priority
    board="CBSE",               # For PYQ references
    exam="JEE",                 # Exam-specific patterns
    prior_metaphor_success={}   # Learning from past effectiveness
)
```

### API Endpoints

#### Diagnostic Endpoint
```
POST /diagnostic/blended-sketch
Body: {
  "question": "Explain recursion with base case [3 marks]",
  "student_dna": {...}  # optional
}
Response: {
  "success": true,
  "question": "...",
  "marks": 3,
  "metaphors": [{name, category, score}, ...],
  "svg": "<svg>...</svg>",
  "size_kb": 8.4,
  "validated": true
}
```

### Performance Constraints
- **File Size:** <10KB (aggressive SVGO optimization)
- **Load Time:** <100ms on 4G networks
- **Render Time:** <30ms on Snapdragon 450
- **No JS Dependency:** Pure SVG + CSS animations
- **No External Fonts:** Base64-encode fonts if needed (<8KB)

### File Structure
```
backend/services/
├── metaphor_engine.py          # Concept → Metaphor selection
├── dynamic_visual_sketch.py    # Main facade (create_visual_sketch)
├── handdrawn_sketch.py         # SVG generation with jitter
├── visual_validation.py        # Quality testing
├── muse_generator.py           # Legacy 5-muse generation
├── metaphor_selector.py        # Legacy selector
└── concept_deconstruction.py   # Legacy deconstruction

backend/api/
└── diagnostic.py               # Testing endpoints

backend/tests/
└── test_visual_pipeline.py     # Integration tests
```

### Usage Example
```python
from services.dynamic_visual_sketch import create_visual_sketch

# Basic usage
result = create_visual_sketch(
    question="Explain recursion with base case [5 marks]"
)
# Returns: {svg, metaphors_used, estimated_marks}

# With student profile
student = {
    "interests": ["cricket", "gaming"],
    "gender": "M",
    "board": "CBSE"
}
result = create_visual_sketch(
    question="Compare iterative vs recursive approaches [4+4 marks]",
    student_profile=student
)
```

### Known Limitations & Roadmap
**✅ Implemented:**
- 3-layer architecture
- 5-Muse system with scoring
- Hand-drawn SVG generation
- Progressive animation (basic)
- Visual validation

**🚧 Partially Implemented:**
- Dynamic metaphor blending (sequential, not overlaid)
- Student DNA personalization (basic filtering only)
- Topper hacks (placeholders, not specific examples)

**❌ Not Yet Implemented:**
- Codebase-first visual library analysis
- True tap-to-advance click handling
- Hinglish/regional slang annotations
- PYQ-specific references (CBSE 2023 Q12 patterns)
- Named topper hacks (AIR 124 trick)
- Base64 Kalam font embedding
- Student Council Tests (marks conversion tracking)
- "Friend Test" 8-point checklist validation
- Multi-metaphor opacity blending in single visual

### Testing
```bash
# Run visual pipeline tests
pytest backend/tests/test_visual_pipeline.py -v

# Test via API
curl -X POST http://localhost:8001/diagnostic/blended-sketch \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain binary search [3 marks]"}'

# Visual render test (browser)
open http://localhost:8001/diagnostic/visual-render-test
```

