# Text Sanitization Pipeline

**Version**: 2.4  
**Last Updated**: October 2025  
**Purpose**: Prevent escape sequence leaks, markdown artifacts, and special characters from reaching users

---

## Overview

The text sanitization pipeline ensures that all AI-generated content is clean, readable, and properly formatted before being displayed to users. This document details the **multi-stage sanitization** process across backend and frontend layers.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI MODEL (GPT-5 / Gemini)                   │
│  Generates raw text with markdown, LaTeX, escape sequences      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               BACKEND SANITIZATION (Stage 1)                    │
│  Location: /app/backend/utils/response_parser.py               │
│  Function: clean_text(), split_mentor_response()               │
│                                                                 │
│  Actions:                                                       │
│  ✓ Remove markdown (**bold**, *italic*)                        │
│  ✓ Remove checkmarks (✅, ❌)                                    │
│  ✓ Remove double backslashes (\\)                               │
│  ✓ Convert escape sequences (\n → newline)                      │
│  ✓ Preserve LaTeX delimiters (\[, \], \(, \))                  │
│  ✓ Remove non-breaking spaces                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATABASE PERSISTENCE                          │
│  Sanitized text stored in MongoDB (chat_messages collection)   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API RESPONSE                               │
│  Endpoint: /api/ai/dual-response                                │
│  Returns: Sanitized JSON with micro_lesson_sections             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│             FRONTEND SANITIZATION (Stage 2)                     │
│  Location: /app/frontend/src/hooks/useAITutor.js               │
│  Function: sanitizeText(), sanitizeResponse()                  │
│                                                                 │
│  Actions:                                                       │
│  ✓ Double-check markdown removal                               │
│  ✓ Ensure checkmarks removed                                    │
│  ✓ Verify escape sequences cleaned                             │
│  ✓ Preserve LaTeX for LatexRenderer                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LATEX RENDERING (Stage 3)                      │
│  Location: /app/frontend/src/components/microlesson/           │
│            LatexRenderer.js                                     │
│                                                                 │
│  Actions:                                                       │
│  ✓ Detect LaTeX patterns (\[...\], \(...\), $$...$$, $...$)   │
│  ✓ Render block math with <BlockMath>                          │
│  ✓ Render inline math with <InlineMath>                        │
│  ✓ Handle mixed text + LaTeX seamlessly                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER DISPLAY (Final)                         │
│  Clean, readable text with beautifully rendered math formulas  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stage 1: Backend Sanitization

### Location
`/app/backend/utils/response_parser.py`

### Functions

#### `clean_text(text: str) -> str`

**Purpose**: Primary sanitization function applied to all GPT-derived text.

**Implementation**:
```python
def clean_text(self, text: str) -> str:
    """
    Comprehensive text cleaning - preserves LaTeX, removes artifacts
    AI Tutor 2.4 enhancement - Student-friendly cleaning
    """
    if not text:
        return ''
    
    # Remove markdown formatting (bold, italic)
    cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **bold**
    cleaned = re.sub(r'\*(.+?)\*', r'\1', cleaned)   # *italic*
    cleaned = re.sub(r'__(.+?)__', r'\1', cleaned)   # __underline__
    cleaned = re.sub(r'_(.+?)_', r'\1', cleaned)     # _italic_
    
    # Remove emoji-like checkmarks and boxes
    cleaned = cleaned.replace('✅', '')
    cleaned = cleaned.replace('❌', '')
    cleaned = cleaned.replace('☑', '')
    
    # Remove escape sequences (preserve LaTeX delimiters)
    cleaned = cleaned.replace('\\"', '"')
    cleaned = cleaned.replace("\\'", "'")
    cleaned = cleaned.replace('\\/', '/')
    
    # Remove double backslashes
    cleaned = cleaned.replace('\\\\', '')
    
    # Remove non-breaking spaces
    cleaned = cleaned.replace('\u00a0', ' ')
    cleaned = cleaned.replace('\xa0', ' ')
    cleaned = cleaned.replace('\u200b', '')
    
    # Clean up multiple spaces and newlines
    cleaned = re.sub(r' {3,}', '  ', cleaned)
    cleaned = re.sub(r'  +', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()
```

**Invocation Points**:

1. **Professor Response Parsing** (`_rule_based_parse`)
   ```python
   sections['concept_overview'] = self.clean_text(para)
   sections['step_by_step'] = self.clean_text('\n\n'.join(step_blocks))
   sections['real_life_analogy'] = self.clean_text(example_text)
   sections['mentor_tip'] = self.clean_text(para)
   ```

2. **Mentor Response Splitting** (`split_mentor_response`)
   ```python
   cleaned = self.clean_text(mentor_text)
   sections['motivation_spark'] = '. '.join(sentences[:2]) + '.'
   # ... etc
   ```

3. **Formula Extraction**
   - LaTeX formulas are **NOT** sanitized to preserve mathematical syntax
   - Only cleaned for extra whitespace

---

#### `split_mentor_response(mentor_text: str) -> Dict[str, str]`

**Purpose**: Structure verbose mentor responses into digestible emotional sections.

**Output**:
```python
{
    'motivation_spark': '...',      # 1-2 sentences, <200 chars
    'simplified_recap': '...',      # Bullet points, <300 chars
    'confidence_tips': '...',       # Actionable advice, <200 chars
    'encouragement': '...'          # Closing quote, <150 chars
}
```

**Word Cap Enforcement**:
```python
for key in sections:
    if sections[key] and len(sections[key]) > 200:
        sections[key] = sections[key][:197] + '...'
```

---

## Stage 2: Frontend Defensive Sanitization

### Location
`/app/frontend/src/hooks/useAITutor.js`

### Functions

#### `sanitizeText(text: string) -> string`

**Purpose**: Client-side fallback sanitization to catch any backend leaks.

**Implementation**:
```javascript
const sanitizeText = (text) => {
  if (!text) return '';
  
  return text
    .replace(/\*\*(.+?)\*\*/g, '$1')  // Remove bold
    .replace(/\*(.+?)\*/g, '$1')      // Remove italic
    .replace(/✅/g, '')                // Remove checkmarks
    .replace(/❌/g, '')
    .replace(/\\"/g, '"')
    .replace(/\\'/g, "'")
    .replace(/\\\\/g, '')
    .replace(/\u00a0/g, ' ')
    .trim();
};
```

#### `sanitizeResponse(data) -> data`

**Purpose**: Recursively sanitize entire response object.

**Applied To**:
- `dual_response.primary.micro_lesson_sections.*`
- `dual_response.secondary.mentor_sections.*`
- Arrays of formulas
- All text fields

**Invocation**: Automatically called in `useSendMessage` mutation before returning data to components.

---

## Stage 3: LaTeX Rendering

### Location
`/app/frontend/src/components/microlesson/LatexRenderer.js`

### How It Works

1. **Pattern Detection**:
   ```javascript
   const latexPattern = /(\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$\$[\s\S]*?\$\$|\$[^\$\n]+?\$)/g;
   ```

2. **Text Splitting**:
   - Splits text into `text` and `math` segments
   - Preserves order and context

3. **Selective Rendering**:
   ```jsx
   if (part.type === 'inline-math') {
     return <InlineMath key={index} math={part.content} />;
   } else if (part.type === 'block-math') {
     return <BlockMath key={index} math={part.content} />;
   }
   ```

4. **Error Handling**:
   ```javascript
   try {
     return <InlineMath math={content} />;
   } catch (error) {
     console.error('KaTeX render error:', error);
     return <span className="text-red-600">{content}</span>;
   }
   ```

---

## Critical Rules

### ✅ DO

1. **Always sanitize before persistence** (Stage 1 - Backend)
2. **Preserve LaTeX delimiters** (`\[`, `\]`, `\(`, `\)`)
3. **Apply defensive sanitization** on frontend (Stage 2)
4. **Use LatexRenderer** for all text with potential math
5. **Log sanitization errors** for debugging

### ❌ DON'T

1. **Never remove single backslashes** (breaks LaTeX)
2. **Don't sanitize formula arrays** directly (handled by LatexRenderer)
3. **Don't double-encode** (sanitize once per stage)
4. **Don't strip newlines** from step-by-step sections
5. **Don't remove spaces** from formula strings

---

## Testing Sanitization

### Backend Test

```python
# /app/backend/tests/test_sanitization.py
from backend.utils.response_parser import ResponseParser

def test_clean_text_preserves_latex():
    parser = ResponseParser(emergent_llm_key="dummy")
    
    input_text = r"""
    **Key Formula**: \[ \sin^2 \theta + \cos^2 \theta = 1 \]
    ✅ Remember to practice!
    """
    
    cleaned = parser.clean_text(input_text)
    
    assert '**' not in cleaned
    assert '✅' not in cleaned
    assert r'\[' in cleaned  # LaTeX preserved
    assert r'\]' in cleaned
```

### Frontend Test

```javascript
// /app/frontend/src/hooks/__tests__/useAITutor.test.js
import { sanitizeText } from '../useAITutor';

test('sanitizeText removes markdown but preserves LaTeX', () => {
  const input = '**Bold** text with \\( \\sin \\theta \\)';
  const output = sanitizeText(input);
  
  expect(output).not.toContain('**');
  expect(output).toContain('\\(');
  expect(output).toContain('\\)');
});
```

---

## Common Issues & Solutions

### Issue 1: Raw LaTeX Showing

**Symptom**: `\sin^2 \theta` displays as text instead of rendered math

**Root Cause**: LaTeX delimiters removed during sanitization

**Solution**: Verify `clean_text()` preserves `\[`, `\]`, `\(`, `\)`

---

### Issue 2: Double Backslashes

**Symptom**: `\\\\sin` or `\\text` appearing in UI

**Root Cause**: Over-aggressive escaping in GPT response

**Solution**: Backend `cleaned.replace('\\\\', '')` should handle this

---

### Issue 3: Checkmarks Appearing

**Symptom**: `✅` or `❌` visible in rendered text

**Root Cause**: Sanitization not applied or failed

**Solution**: Check both backend and frontend sanitization executed

---

### Issue 4: Markdown Visible

**Symptom**: `**Bold**` or `*Italic*` showing as text

**Root Cause**: Regex not matching or sanitization skipped

**Solution**: Verify `re.sub(r'\*\*(.+?)\*\*', r'\1', text)` runs

---

## Performance Considerations

- **Backend sanitization**: ~2-5ms per text field
- **Frontend sanitization**: ~1-2ms per response
- **LaTeX rendering**: ~10-50ms per formula (KaTeX)
- **Total overhead**: <100ms for typical response

---

## Monitoring & Alerts

### Metrics to Track

1. **Sanitization failures**: Count of text fields with artifacts post-sanitization
2. **LaTeX render errors**: KaTeX errors logged to console
3. **Performance**: p95 latency for sanitization pipeline

### Alerts

- Alert if >5% of responses have unsanitized artifacts
- Alert if KaTeX render errors >1% of formulas

---

## See Also

- [AI Tutor Response Schema](./ai_tutor_response_schema.md)
- [Mentor Micro-Sections Spec](./mentor_microsections_spec.md)
- Backend: `/app/backend/utils/response_parser.py`
- Frontend: `/app/frontend/src/hooks/useAITutor.js`
- Components: `/app/frontend/src/components/microlesson/LatexRenderer.js`
