# Visual Sketch Engine: Implementation Plan

## 🎯 Goal
Transform the Visual Sketch Engine from a technical diagram generator into an emotionally resonant "friend explaining at 2 AM" experience.

---

## Phase 1: Emotional Connection (PRIORITY 1)

### Task 1.1: Hinglish Annotation System
**File:** `backend/services/hinglish_annotations.py` (NEW)

```python
"""
Hinglish Annotation Generator
Generates emotionally resonant exam annotations in Hinglish
"""

REGIONAL_SLANG = {
    "North": {
        "attention": ["Dhyan se dekho", "Yeh important hai", "Arre bhai"],
        "warning": ["Sharma sir yaha cut maarte hain", "Yaha galti mat karna"],
        "encouragement": ["Simple hai yaar", "Bas yeh samajh le"],
        "teachers": ["Sharma sir", "Khan ma'am", "Gupta sir"]
    },
    "South": {
        "attention": ["See this carefully da", "This is important pa"],
        "warning": ["Sir will deduct marks here", "Don't skip this step da"],
        "encouragement": ["Simple only", "Just understand this"],
        "teachers": ["Kumar sir", "Lakshmi ma'am", "Reddy sir"]
    },
    "West": {
        "attention": ["Aata, yeh dekh", "Focus kar yaha"],
        "warning": ["Madam points kaapti hai", "Aamcha galti yaha"],
        "encouragement": ["Simple aahe", "Samjun ghya"],
        "teachers": ["Patil sir", "Desai ma'am", "Joshi sir"]
    },
    "East": {
        "attention": ["Ektu dekho", "Important hoiche"],
        "warning": ["Sir ekhane number katbe", "Mistake korbe na"],
        "encouragement": ["Simple", "Bujhe nao"],
        "teachers": ["Das sir", "Sen ma'am", "Chatterjee sir"]
    }
}

EXAM_FEAR_TEMPLATES = [
    "Kal exam hai, yeh yaad rakhna! 📝",
    "90% yaha marks lose karte hain ⚠️",
    "Yeh step skip kiya toh {marks} marks gaye 💔",
    "Examiner yaha pakka check karega 👀",
    "{teacher} specifically iske baare mein bole the 🎓"
]

def generate_annotation(
    concept: str,
    annotation_type: str,  # "attention", "warning", "encouragement"
    region: str = "North",
    marks: int = 2,
    teacher_name: str = None
) -> str:
    """Generate context-aware Hinglish annotation"""
    templates = REGIONAL_SLANG.get(region, REGIONAL_SLANG["North"])

    if annotation_type == "warning":
        base = random.choice(templates["warning"])
        return f"{base} ⚠️ ({marks} marks risk)"

    elif annotation_type == "teacher_tip":
        teacher = teacher_name or random.choice(templates["teachers"])
        return f"{teacher} ne bola: '{concept}' - yeh exam mein zaroori hai"

    elif annotation_type == "exam_fear":
        return random.choice(EXAM_FEAR_TEMPLATES).format(
            marks=marks,
            teacher=teacher_name or random.choice(templates["teachers"])
        )

    return random.choice(templates.get(annotation_type, templates["attention"]))
```

**Integration:**
- Modify `handdrawn_sketch.py` to use `generate_annotation()` instead of hardcoded strings
- Add `region` parameter to `build_handdrawn_svg()`

---

### Task 1.2: Topper Hacks Database
**File:** `backend/data/topper_hacks.json` (NEW)

```json
{
  "recursion": {
    "concept": "Recursion with base case",
    "hacks": [
      {
        "rank": "AIR 124 (JEE 2023)",
        "hack": "Pehle base case likhna, phir recursive call - examiner sequence dekhta hai",
        "marks_saved": 2,
        "board": "CBSE",
        "subject": "Computer Science"
      }
    ]
  },
  "binary_search": {
    "concept": "Binary search algorithm",
    "hacks": [
      {
        "rank": "State Topper (Maharashtra)",
        "hack": "Mid calculation (left + right) / 2 ko bold/underline karo",
        "marks_saved": 1,
        "board": "HSC",
        "subject": "Computer Science"
      }
    ]
  }
}
```

**File:** `backend/services/topper_hack_selector.py` (NEW)

```python
"""
Topper Hack Selector
Maps concepts to verified topper tricks
"""
import json
from pathlib import Path
from typing import Optional, Dict, List

class TopperHackSelector:
    def __init__(self, data_path="backend/data/topper_hacks.json"):
        self.hacks = self._load_hacks(data_path)

    def _load_hacks(self, path: str) -> Dict:
        with open(path) as f:
            return json.load(f)

    def get_hack(
        self,
        concept_keywords: List[str],
        board: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Optional[Dict]:
        """Find most relevant topper hack for given concept"""
        # Fuzzy match concept keywords
        for key, data in self.hacks.items():
            if any(kw.lower() in key.lower() for kw in concept_keywords):
                # Filter by board if specified
                matching_hacks = data["hacks"]
                if board:
                    matching_hacks = [
                        h for h in matching_hacks
                        if h["board"] == board
                    ]

                if matching_hacks:
                    return {
                        "concept": data["concept"],
                        **matching_hacks[0]  # Return best match
                    }

        return None

    def format_hack_annotation(self, hack: Dict) -> str:
        """Format hack for SVG display"""
        return (
            f"🏆 {hack['rank']} trick:\n"
            f"{hack['hack']}\n"
            f"💡 Saves {hack['marks_saved']} marks"
        )
```

**Integration:**
- Import in `dynamic_visual_sketch.py`
- Add hack lookup in `_layer_exam()` function

---

### Task 1.3: PYQ Integration System
**File:** `backend/data/pyq_patterns.json` (NEW)

```json
{
  "recursion_base_case": {
    "pattern_id": "REC_BC_001",
    "keywords": ["recursion", "base case", "recursive"],
    "references": [
      {
        "board": "CBSE",
        "year": 2023,
        "question_number": "Q12(b)",
        "marks": 3,
        "similarity": 0.95
      },
      {
        "board": "CBSE",
        "year": 2022,
        "question_number": "Q8",
        "marks": 5,
        "similarity": 0.87
      }
    ]
  }
}
```

**File:** `backend/services/pyq_matcher.py` (NEW)

```python
"""
PYQ Pattern Matcher
Identifies similar past year questions
"""
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class PYQReference:
    board: str
    year: int
    question_number: str
    marks: int
    similarity: float

class PYQMatcher:
    def __init__(self, data_path="backend/data/pyq_patterns.json"):
        self.patterns = self._load_patterns(data_path)

    def _load_patterns(self, path: str) -> Dict:
        with open(path) as f:
            return json.load(f)

    def find_similar_pyqs(
        self,
        question: str,
        board: Optional[str] = None,
        min_similarity: float = 0.7
    ) -> List[PYQReference]:
        """Find PYQs with similar patterns"""
        results = []
        q_lower = question.lower()

        for pattern_id, pattern_data in self.patterns.items():
            # Check keyword overlap
            keyword_matches = sum(
                1 for kw in pattern_data["keywords"]
                if kw.lower() in q_lower
            )

            if keyword_matches >= 2:  # At least 2 keywords match
                for ref in pattern_data["references"]:
                    if ref["similarity"] >= min_similarity:
                        if board is None or ref["board"] == board:
                            results.append(PYQReference(**ref))

        # Sort by similarity
        return sorted(results, key=lambda x: x.similarity, reverse=True)[:3]

    def format_pyq_annotation(self, pyq: PYQReference) -> str:
        """Format for SVG display"""
        return (
            f"📌 {pyq.board} {pyq.year} {pyq.question_number}\n"
            f"Same pattern! ({pyq.marks} marks)\n"
            f"✓ {int(pyq.similarity * 100)}% similar"
        )
```

---

## Phase 2: Enhanced SVG Generation

### Task 2.1: Improved Layer 2 with Real Data
**File:** `backend/services/dynamic_visual_sketch.py` (MODIFY)

**Changes:**
```python
from .hinglish_annotations import generate_annotation
from .topper_hack_selector import TopperHackSelector
from .pyq_matcher import PYQMatcher

topper_selector = TopperHackSelector()
pyq_matcher = PYQMatcher()

def _layer_exam(bundle: ConceptBundle, student_dna: Optional[StudentDNA] = None) -> str:
    """Enhanced Layer 2 with Hinglish, topper hacks, and PYQs"""
    region = (student_dna.locale_language[:2] if student_dna else "North")

    # Get topper hack
    hack = topper_selector.get_hack(
        concept_keywords=bundle.entities,
        board=student_dna.board if student_dna else None
    )

    # Get PYQ references
    pyqs = pyq_matcher.find_similar_pyqs(
        bundle.question,
        board=student_dna.board if student_dna else None
    )

    # Generate Hinglish annotations
    warning = generate_annotation(
        concept=bundle.entities[0] if bundle.entities else "concept",
        annotation_type="warning",
        region=region,
        marks=bundle.marks_distribution["total"]
    )

    # Build SVG with real data
    stroke = PALETTE["navy"]
    note = _path_from_points(_jitter_points([...]))  # Same as before

    y_offset = 110
    title = _text(440, y_offset, f"Marks: {bundle.marks_distribution['total']}", stroke, 12)
    y_offset += 20

    warning_text = _text(440, y_offset, warning, stroke, 10)
    y_offset += 20

    if hack:
        hack_text = _text(440, y_offset, topper_selector.format_hack_annotation(hack), stroke, 10)
        y_offset += 30
    else:
        hack_text = ""

    if pyqs:
        pyq_text = _text(440, y_offset, pyq_matcher.format_pyq_annotation(pyqs[0]), stroke, 9)
    else:
        pyq_text = ""

    return f'<path id="l2_note" d="{note}" stroke="{stroke}" ... />{title}{warning_text}{hack_text}{pyq_text}'
```

---

### Task 2.2: Multi-Metaphor Blending in Layer 3
**File:** `backend/services/dynamic_visual_sketch.py` (MODIFY)

**Current Issue:** Metaphors shown sequentially
**Fix:** Overlay all 3 at 10% opacity with visual blend

```python
def _layer_culture_blended(
    primary: MetaphorCandidate,
    secondary: MetaphorCandidate,
    tertiary: MetaphorCandidate
) -> str:
    """Enhanced Layer 3: All metaphors blended at low opacity"""

    # Create 3 overlapping organic shapes
    metaphors = [primary, secondary, tertiary]
    colors = [PALETTE["saffron"], PALETTE["green"], PALETTE["navy"]]

    svg_parts = ['<g id="l3_meta" opacity="0.10">']

    for i, (metaphor, color) in enumerate(zip(metaphors, colors)):
        # Create organic blob shape for each metaphor
        x_offset = 80 + (i * 180)
        y_base = 220 + (i * 10)  # Slight vertical offset

        # Wavy blob path
        blob_points = [
            (x_offset, y_base),
            (x_offset + 90, y_base - 10),
            (x_offset + 110, y_base + 30),
            (x_offset + 80, y_base + 50),
            (x_offset + 20, y_base + 40),
            (x_offset, y_base)
        ]

        jittered = _jitter_points(blob_points, 3.0)
        path = _path_from_points(jittered)

        # Add metaphor-specific icon/text
        icon_map = {
            "family": "👨‍👩‍👦",
            "food": "🍲",
            "cricket": "🏏",
            "bollywood": "🎬",
            "gaming": "🎮"
        }

        icon = icon_map.get(metaphor.muse, "•")
        label = f"{icon} {metaphor.muse.title()}"

        svg_parts.append(
            f'<path d="{path}" stroke="{color}" stroke-width="1.5" '
            f'fill="{color}" fill-opacity="0.3" />'
        )
        svg_parts.append(
            _text(x_offset + 40, y_base + 25, label, color, 10)
        )

    # Add blend explanation
    blend_text = f"Memory Hook: {primary.muse} + {secondary.muse} + {tertiary.muse}"
    svg_parts.append(_text(320, 290, blend_text, PALETTE["navy"], 8))

    svg_parts.append('</g>')
    return ''.join(svg_parts)
```

---

### Task 2.3: True Tap-to-Advance Animation
**File:** `backend/services/dynamic_visual_sketch.py` (MODIFY)

```python
def _animation_block_interactive() -> str:
    """True tap-to-advance with invisible click zones"""
    return '''
    <style><![CDATA[
        text{pointer-events:none}
        .tap-zone{fill:transparent;cursor:pointer;opacity:0}
        .tap-zone:hover{opacity:0.05;fill:#FFD700}
    ]]></style>

    <!-- Step 1: Auto-draw skeleton -->
    <set xlink:href="#layer1" attributeName="visibility" to="visible" begin="0.5s" />

    <!-- Tap zone 1: Click anywhere to show arrows -->
    <rect id="tap1" class="tap-zone" width="640" height="360" />
    <set xlink:href="#l1_arrow" attributeName="visibility" to="visible" begin="tap1.click" />
    <set xlink:href="#tap1" attributeName="display" to="none" begin="tap1.click" />

    <!-- Tap zone 2: Show second box -->
    <rect id="tap2" class="tap-zone" width="640" height="360" display="none" />
    <set xlink:href="#tap2" attributeName="display" to="block" begin="tap1.click" />
    <set xlink:href="#l1_box2" attributeName="visibility" to="visible" begin="tap2.click" />
    <set xlink:href="#tap2" attributeName="display" to="none" begin="tap2.click" />

    <!-- Tap zone 3: Show exam layer -->
    <rect id="tap3" class="tap-zone" width="640" height="360" display="none" />
    <set xlink:href="#tap3" attributeName="display" to="block" begin="tap2.click" />
    <set xlink:href="#layer2" attributeName="visibility" to="visible" begin="tap3.click" />
    <set xlink:href="#tap3" attributeName="display" to="none" begin="tap3.click" />

    <!-- Tap zone 4: Show metaphor layer -->
    <rect id="tap4" class="tap-zone" width="640" height="360" display="none" />
    <set xlink:href="#tap4" attributeName="display" to="block" begin="tap3.click" />
    <set xlink:href="#layer3" attributeName="visibility" to="visible" begin="tap4.click" />

    <!-- Progress indicator -->
    <text x="10" y="20" font-size="10" fill="#666">Tap to continue →</text>
    '''
```

---

## Phase 3: Friend Test Validation

### Task 3.1: Friend Test Validator
**File:** `backend/services/friend_test.py` (NEW)

```python
"""
Friend Test - The Real Validation
8-point checklist for emotional connection
"""
from typing import Dict, List
import re

def friend_test_validation(
    svg: str,
    metadata: Dict,
    concept: str
) -> Dict[str, bool]:
    """
    Would a student screenshot this within 30 seconds?
    Would they WhatsApp it to 5 friends?
    """

    tests = {
        "screenshot_worthy": _check_visual_appeal(svg, metadata),
        "whatsapp_ready": _check_shareability(svg),
        "hand_drawn_feel": _check_imperfection(svg),
        "topper_hack_present": _check_specific_hack(metadata),
        "marks_breakdown_visible": _check_marks_clarity(svg),
        "multi_metaphor_blend": _check_metaphor_count(metadata),
        "common_mistake_shown": _check_mistake_warning(svg),
        "instant_load": _check_performance(svg)
    }

    return {
        "tests": tests,
        "score": f"{sum(tests.values())}/8",
        "passed": sum(tests.values()) >= 6,
        "feedback": _generate_feedback(tests)
    }

def _check_visual_appeal(svg: str, metadata: Dict) -> bool:
    """Has colors, emojis, Hinglish text?"""
    has_emojis = any(emoji in svg for emoji in ["⚠️", "📌", "🏆", "💡"])
    has_hinglish = any(word in svg for word in ["yaar", "bhai", "sir", "madam"])
    has_colors = all(color in svg for color in ["#FF9933", "#138808"])
    return has_emojis and (has_hinglish or has_colors)

def _check_specific_hack(metadata: Dict) -> bool:
    """Has topper hack with rank attribution?"""
    return "topper_hack" in metadata and "AIR" in str(metadata.get("topper_hack", ""))

def _check_metaphor_count(metadata: Dict) -> bool:
    """Uses 2-3 metaphors, not just one?"""
    metaphor_count = len(metadata.get("metaphors_used", []))
    return 2 <= metaphor_count <= 3

def _check_mistake_warning(svg: str) -> bool:
    """Mentions specific common mistake?"""
    warning_keywords = ["90%", "cut", "forget", "galti", "mistake"]
    return any(kw in svg.lower() for kw in warning_keywords)

def _generate_feedback(tests: Dict[str, bool]) -> List[str]:
    """Generate actionable feedback"""
    feedback = []

    if not tests["screenshot_worthy"]:
        feedback.append("Add more emojis and Hinglish phrases")

    if not tests["topper_hack_present"]:
        feedback.append("Include topper hack with rank (e.g., 'AIR 124 trick')")

    if not tests["multi_metaphor_blend"]:
        feedback.append("Blend 2-3 metaphors in Layer 3")

    if not tests["common_mistake_shown"]:
        feedback.append("Add specific mistake warning (e.g., '90% yaha base case bhoolte hain')")

    return feedback
```

---

## Phase 4: Visual Library System

### Task 4.1: Visual Fingerprinting
**File:** `backend/services/visual_library.py` (NEW)

```python
"""
Visual Library - Codebase-First Approach
Check existing visuals before generating new ones
"""
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

class VisualLibrary:
    def __init__(self, base_path="visual_library/"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.index = self._load_index()

    def _create_fingerprint(self, question: str, marks: int) -> str:
        """Create content-based fingerprint"""
        # Normalize question
        normalized = re.sub(r'\W+', '', question.lower())
        key = f"{normalized}_{marks}"
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def find_existing(
        self,
        question: str,
        marks: int,
        subject: str = "cs"
    ) -> Optional[Dict]:
        """Search for existing visual by concept fingerprint"""
        fingerprint = self._create_fingerprint(question, marks)
        subject_path = self.base_path / subject
        visual_file = subject_path / f"{fingerprint}.json"

        if visual_file.exists():
            with open(visual_file) as f:
                visual_data = json.load(f)

            # Check if needs regeneration
            if self._should_regenerate(visual_data):
                return None  # Force regeneration

            return visual_data

        return None

    def _should_regenerate(self, visual_metadata: Dict) -> bool:
        """Student Council Tests - did visual perform well?"""
        marks_conversion = visual_metadata.get("analytics", {}).get("marks_conversion", 0)
        screenshot_count = visual_metadata.get("analytics", {}).get("screenshots", 0)
        age_days = (datetime.now() - datetime.fromisoformat(
            visual_metadata.get("created_at", datetime.now().isoformat())
        )).days

        # Regenerate if:
        # - Low marks conversion (<70%)
        # - Not popular (<10 screenshots)
        # - Very old (>180 days) and we have better techniques now

        if marks_conversion < 0.7:
            return True
        if screenshot_count < 10 and age_days > 30:
            return True
        if age_days > 180:
            return True

        return False

    def save_visual(
        self,
        question: str,
        marks: int,
        svg: str,
        metadata: Dict,
        subject: str = "cs"
    ) -> str:
        """Cache generated visual"""
        fingerprint = self._create_fingerprint(question, marks)
        subject_path = self.base_path / subject
        subject_path.mkdir(exist_ok=True)

        visual_data = {
            "fingerprint": fingerprint,
            "question": question,
            "marks": marks,
            "svg": svg,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "analytics": {
                "screenshots": 0,
                "marks_conversion": 0.0,
                "views": 0
            }
        }

        visual_file = subject_path / f"{fingerprint}.json"
        with open(visual_file, 'w') as f:
            json.dump(visual_data, f, indent=2)

        return fingerprint
```

**Integration:**
```python
# In dynamic_visual_sketch.py
library = VisualLibrary()

def create_visual_sketch(
    question: str,
    student_profile: Optional[Dict] = None
) -> Dict[str, Any]:
    """Enhanced with library check"""

    # Step 0: Check library first
    marks = _estimate_marks(question)
    existing = library.find_existing(question, marks)

    if existing:
        return {
            "svg": existing["svg"],
            "metaphors_used": existing["metadata"]["metaphors_used"],
            "estimated_marks": marks,
            "source": "cached"
        }

    # Generate new if not found
    result = _generate_new_visual(question, student_profile)

    # Cache for future use
    library.save_visual(
        question=question,
        marks=marks,
        svg=result["svg"],
        metadata=result
    )

    result["source"] = "generated"
    return result
```

---

## File Structure After Implementation

```
backend/
├── services/
│   ├── metaphor_engine.py          (existing)
│   ├── dynamic_visual_sketch.py    (ENHANCED)
│   ├── handdrawn_sketch.py         (ENHANCED)
│   ├── hinglish_annotations.py     (NEW)
│   ├── topper_hack_selector.py     (NEW)
│   ├── pyq_matcher.py              (NEW)
│   ├── friend_test.py              (NEW)
│   └── visual_library.py           (NEW)
├── data/
│   ├── topper_hacks.json           (NEW)
│   └── pyq_patterns.json           (NEW)
├── api/
│   └── diagnostic.py               (ENHANCE with friend test)
└── tests/
    ├── test_hinglish.py            (NEW)
    ├── test_topper_hacks.py        (NEW)
    └── test_friend_validation.py   (NEW)

visual_library/
├── cs/                             (NEW directory structure)
│   ├── a3c4f1b2.json
│   └── b9e2d8f1.json
├── physics/
└── math/
```

---

## Testing Strategy

### Unit Tests
```bash
pytest backend/tests/test_hinglish.py -v
pytest backend/tests/test_topper_hacks.py -v
pytest backend/tests/test_friend_validation.py -v
```

### Integration Tests
```python
# Test end-to-end with Friend Test
def test_visual_passes_friend_test():
    result = create_visual_sketch(
        question="Explain recursion with base case [3 marks]",
        student_profile={"region": "North", "board": "CBSE"}
    )

    friend_result = friend_test_validation(
        svg=result["svg"],
        metadata=result,
        concept="recursion"
    )

    assert friend_result["passed"] == True
    assert friend_result["score"] >= "6/8"
```

---

## Success Criteria

### Before (Current State)
- ❌ Friend Test Score: 3/8
- ❌ Generic annotations
- ❌ No topper hacks
- ❌ No PYQ references
- ✅ Technical validation passes

### After (Target State)
- ✅ Friend Test Score: 7-8/8
- ✅ Hinglish annotations with regional flavor
- ✅ Specific topper hacks with ranks
- ✅ PYQ pattern references
- ✅ Multi-metaphor blending
- ✅ True tap-to-advance
- ✅ Visual library with reuse

---

## Timeline Estimate

| Phase | Tasks | Time | Priority |
|-------|-------|------|----------|
| Phase 1.1 | Hinglish Annotations | 4-6 hours | 🔴 Critical |
| Phase 1.2 | Topper Hacks | 3-4 hours | 🔴 Critical |
| Phase 1.3 | PYQ Integration | 4-6 hours | 🟠 High |
| Phase 2.1 | Enhanced Layer 2 | 2-3 hours | 🟠 High |
| Phase 2.2 | Multi-Metaphor Blend | 3-4 hours | 🟡 Medium |
| Phase 2.3 | Tap-to-Advance | 2-3 hours | 🟡 Medium |
| Phase 3.1 | Friend Test | 2-3 hours | 🟠 High |
| Phase 4.1 | Visual Library | 6-8 hours | 🟡 Medium |

**Total: ~30-40 hours (~1 week full-time)**

---

## Next Steps

### Option A: Quick Wins First (Recommended)
Start with Phase 1.1 & 1.2 (Hinglish + Topper Hacks) to get immediate emotional impact

### Option B: Complete System
Implement all phases sequentially for full system upgrade

### Option C: Prototype & Test
Build Phase 1 only, test with real students, then iterate

**Choose your path and let's start coding! 🚀**
