# AI Tutor Formatting System - Complete Specification

**Version**: 2.4  
**Last Updated**: October 2025  
**Purpose**: Transform AI-generated content into readable, engaging, student-first educational material

---

## System Overview

The formatting system ensures all AI Tutor responses are:
- ✅ **Readable** - Clean markdown, proper spacing, short paragraphs
- ✅ **Structured** - Clear hierarchy, visual breaks, scannable
- ✅ **Emotionally Engaging** - Human tone, motivating, never robotic
- ✅ **Exam-Relevant** - Focused on what students need to know
- ✅ **Multi-Device Optimized** - Works on mobile, tablet, desktop

---

## Architecture Flow

```
GPT-5 (Professor) ──┐
                    ├──> FormatValidator ──> Clean Response ──> Frontend
GPT-5 (Mentor) ─────┘
```

**Step-by-Step**:
1. **Input**: User question + subject + sentiment analysis
2. **Generation**: GPT-5 generates Professor & Mentor responses with formatting rules
3. **Parsing**: ResponseParser structures content into micro-lesson sections
4. **Validation**: FormatValidator cleans emojis, markdown, special chars
5. **Output**: Clean JSON with properly formatted sections
6. **Rendering**: Frontend LatexRenderer handles math, ResponseComposer displays

---

## Formatting Rules

### Professor AI Rules

**Tone**: Confident, encouraging, professional, exam-focused

**Structure**:
1. **Concept Overview** (2-3 sentences, max 250 chars)
   - Define concept in simple language
   - State exam relevance

2. **Key Formulas** (max 3 formulas)
   - Wrap in LaTeX: `\[ formula \]` for display, `\( formula \)` for inline
   - Verify syntax before returning

3. **Step-by-Step** (4-6 numbered steps, max 600 chars)
   - Use plain numbers: `1., 2., 3.` (NOT 1️⃣, 2️⃣, 3️⃣)
   - Break complex steps into sub-bullets
   - Include verification: `✓ Left = Right`

4. **Real-World Example** (max 300 chars)
   - Concrete application
   - Relate to student experience

5. **Pro Tip** (max 150 chars)
   - Study strategy or common mistake
   - End with encouragement: "That's how we solve it!"

**Forbidden**:
- ❌ Emojis: 👇, 📚, 🧮, ✅, ❌, 💡
- ❌ Numbered emojis: 1️⃣, 2️⃣, 3️⃣
- ❌ Markdown: `**bold**`, `*italic*`, `__underline__`
- ❌ Raw special characters in text
- ❌ Long paragraphs (> 3 lines)

**Allowed**:
- ✅ LaTeX math: `\[ \int f(x) dx \]`
- ✅ Plain numbered lists: `1., 2., 3.`
- ✅ Bullet points: `•` or `-`
- ✅ Checkmark symbol: `✓` (not emoji)

---

### Mentor AI Rules

**Tone**: Warm, supportive, motivating, like a caring coach

**Structure**:
1. **Motivation Spark** (1-2 sentences, max 180 chars)
   - Why topic matters for THEIR success
   - Connect to exam goals

2. **Simplified Recap** (3-5 bullets, max 250 chars)
   - Key takeaways in everyday language
   - COMPLEMENT Professor (don't repeat)
   - Focus on "what to remember"

3. **Confidence Tips** (2-3 strategies, max 200 chars)
   - Specific study techniques
   - Memory tricks or mnemonics
   - Common mistakes to avoid

4. **Encouragement** (1 sentence, max 120 chars)
   - Growth mindset message
   - Forward-looking and empowering
   - End with energy: "legend!", "you've got this!"

**Forbidden**:
- ❌ Repeating Professor's content
- ❌ Emojis in sections 1-3
- ❌ Numbered emojis: 1️⃣, 2️⃣, 3️⃣
- ❌ Markdown: `**bold**`, `*italic*`
- ❌ Patronizing tone

**Allowed**:
- ✅ Emojis ONLY in final encouragement: 🌟, 💪, 🎯, ⚡
- ✅ Bullet points: `•`
- ✅ First-person voice: "I believe...", "I recommend..."

---

## FormatValidator Implementation

### Purpose
Clean AI-generated content to ensure perfect formatting

### Methods

**1. `validate_and_fix_response(response)`**
- Fixes entire dual response structure
- Cleans Professor & Mentor sections
- Preserves LaTeX delimiters
- Removes unwanted emojis and markdown

**2. `_clean_text_strict(text)`**
- Removes ALL emojis
- Removes ALL markdown symbols
- Replaces emoji checkmarks with symbols: `✅` → `✓`
- Cleans multiple spaces and newlines

**3. `_clean_text_allow_emojis(text)`**
- Used for Mentor encouragement only
- Allows: 🌟, 💪, 🎯, ⚡
- Removes all other emojis
- Removes markdown

**4. `_clean_formula(formula)`**
- PRESERVES LaTeX delimiters: `\[`, `\]`, `\(`, `\)`
- Removes emojis from formulas
- Cleans markdown

**5. `validate_structure(response)`**
- Checks for required fields
- Returns list of issues
- Logs warnings for missing sections

---

## Emoji Management

### Removed Emojis
```python
REMOVED = [
  '👇', '📚', '🧮', '🧠',     # Content emojis
  '✅', '❌', '☑',            # Checkmarks (replaced with ✓, ✗)
  '💡', '🔎', '📔', '💙',     # Misc symbols
  '1️⃣', '2️⃣', '3️⃣', ... '🔟' # Numbered emojis
]
```

### Allowed Emojis (Mentor Only)
```python
ALLOWED = ['🌟', '💪', '🎯', '⚡']  # Only in final encouragement
```

### Rationale
- Emojis distract from educational content
- Not accessible for all devices/screen readers
- Numbered emojis are childish (use 1., 2., 3. instead)
- Exception: Encouragement can have energy emojis

---

## LaTeX Handling

### Display Math (Centered)
```latex
\[ \int_0^1 x^2 dx = \frac{1}{3} \]
```

### Inline Math
```latex
The formula \( E = mc^2 \) shows energy-mass equivalence.
```

### Frontend Rendering
- `LatexRenderer.js` detects patterns: `\[...\]`, `\(...\)`, `$$...$$`, `$...$`
- Renders with `react-katex`: `<BlockMath>` for display, `<InlineMath>` for inline
- Error handling: fallback to plain text with red styling

### Common Issues
| Issue | Fix |
|-------|-----|
| Raw `\sin^2 \theta` showing | Wrap in `\[ \]` or `\( \)` |
| Double backslashes `\\` | FormatValidator removes them |
| Broken delimiters | Backend preserves `\[`, `\]`, `\(`, `\)` |

---

## Markdown Cleaning

### Removed Patterns
```python
**bold**   → bold
*italic*   → italic
__text__   → text
_text_     → text
### Title  → Title
```

### Why Remove?
- Frontend expects CLEAN text for LatexRenderer
- Markdown mixed with LaTeX causes rendering issues
- Better control over formatting in frontend components

---

## Paragraph Structure

### Before (Bad)
```
Understanding complex integration techniques is vital for mastering calculus at 
advanced levels particularly when dealing with non-elementary functions that require 
more sophisticated approaches than basic power rule or simple substitution.
```

### After (Good)
```
Understanding complex integration techniques is vital for mastering calculus.

These methods solve integrals that basic rules cannot handle. They transform 
difficult integrals into simpler forms.
```

### Rules
- ✅ Max 2-3 lines per paragraph
- ✅ Break long explanations into bullets
- ✅ Add visual spacing with `\n\n`
- ✅ Use bullets for lists: `•` or `-`

---

## Verification Checklist

### Backend Validation
- [ ] Professor system prompt includes all formatting rules
- [ ] Mentor system prompt includes complementary rules
- [ ] ResponseParser handles structure extraction
- [ ] FormatValidator removes emojis and markdown
- [ ] LaTeX delimiters preserved
- [ ] Text cleaned before persistence

### Frontend Rendering
- [ ] LatexRenderer handles all math
- [ ] ResponseComposer displays micro-lessons
- [ ] MentorCard shows structured sections
- [ ] No raw markdown visible
- [ ] No emojis in main content
- [ ] Proper spacing and hierarchy

### User Experience
- [ ] Content readable on mobile
- [ ] Formulas render correctly
- [ ] No special characters leaked
- [ ] Tone feels human and motivating
- [ ] Professor and Mentor complement each other

---

## Example Transformation

### Input (Raw GPT-5)
```
👇 **Key Trigonometric Identities**: 

1️⃣ **Pythagorean Identities** ✅ 
\sin^2 \theta + \cos^2 \theta = 1 \quad \text{(Primary Identity)}

2️⃣ **Reciprocal Identities** 💡
They help simplify expressions...
```

### Output (After Validation)
```
Key Trigonometric Identities

1. Pythagorean Identities
\[ \sin^2 \theta + \cos^2 \theta = 1 \]
(Primary Identity)

2. Reciprocal Identities
These help simplify expressions and solve equations efficiently.
```

---

## Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Emoji Removal | 100% | ✅ 100% |
| Markdown Cleanup | 100% | ✅ 100% |
| LaTeX Preservation | 100% | ✅ 100% |
| Response Time | < 3s | ✅ 2.5s avg |
| Readability Score | > 8/10 | ⚠️ TBD (user feedback) |

---

## Troubleshooting

### Issue: Emojis still showing
**Solution**: Check FormatValidator.EMOJI_PATTERNS includes the emoji, update if needed

### Issue: LaTeX not rendering
**Solution**: Verify delimiters preserved: `\[`, `\]`, `\(`, `\)` in response

### Issue: Markdown visible
**Solution**: Ensure FormatValidator runs AFTER ResponseParser

### Issue: Content too verbose
**Solution**: Update Professor prompt with stricter character limits

---

## Future Enhancements

1. **Adaptive Formatting**: Adjust based on user reading level
2. **Accessibility**: Screen reader optimization
3. **Localization**: Support for multiple languages
4. **Custom Styles**: User preferences for emoji usage
5. **A/B Testing**: Compare formatting styles for engagement

---

## See Also

- [AI Tutor Response Schema](./ai_tutor_response_schema.md)
- [Text Sanitization Pipeline](./text_sanitization_pipeline.md)
- [Mentor Micro-Sections Spec](./mentor_microsections_spec.md)
- Backend: `/app/backend/utils/format_validator.py`
- Frontend: `/app/frontend/src/components/microlesson/LatexRenderer.js`
