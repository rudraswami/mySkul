# Mentor Micro-Sections Specification

**Version**: 2.4  
**Last Updated**: October 2025  
**Purpose**: Define UX rules, word caps, collapse states, and analytics for Mentor AI interactions

---

## Overview

The **Mentor Panel** provides emotional support, strategic study guidance, and confidence building through **structured micro-sections**. This document specifies the UX design, interaction patterns, word limits, and analytics tracking for optimal student engagement.

---

## Design Philosophy

### Student-First Principles

1. **Collapsed by Default**: Mentor content is optional emotional support, not blocking the main learning flow
2. **Bite-Sized Sections**: Each section ≤ 3 sentences to prevent cognitive overload
3. **Visual Hierarchy**: Icons, gradients, and badges create emotional anchors
4. **Progressive Disclosure**: Users expand sections only when they need support
5. **Warm, Encouraging Tone**: All text written in first-person, supportive voice

---

## Micro-Section Structure

### 1. Motivation Spark

**Purpose**: Opening emotional hook to build confidence and relevance

**Location**: Always visible when Mentor panel expanded

**Icon**: 💙 (blue heart)

**Word Cap**: 1-2 sentences, **≤ 200 characters**

**Tone**: Warm, motivational, forward-looking

**Examples**:
- ✅ "You're tackling one of the most powerful tools in mathematics! These identities will serve you in calculus, physics, and engineering."
- ✅ "Great question! Understanding this concept will make so many future topics click into place for you."
- ❌ "Trigonometric identities are important. They are used in many fields. You should study them carefully." *(too dry, not motivational)*

**Styling**:
```css
.motivation-spark {
  padding: 16px;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border-left: 4px solid #f59e0b;
  font-size: 16px;
  line-height: 1.6;
}
```

---

### 2. Simplified Recap

**Purpose**: Bullet-point summary of key takeaways in simple language

**Location**: Collapsible section (collapsed by default)

**Icon**: 💬 (speech bubble)

**Word Cap**: 3-5 bullet points, **≤ 300 characters total**

**Tone**: Clear, concise, jargon-free

**Format**: Newline-separated bullets with `•` prefix

**Examples**:
- ✅
  ```
  • Pythagorean identities come from the unit circle
  • Reciprocal identities help simplify expressions
  • Co-function identities relate complementary angles
  • Even-odd identities help with symmetry
  ```
- ❌
  ```
  • Trigonometric identities are equations involving trig functions
  • They are derived from the unit circle and Pythagorean theorem
  • There are multiple types including Pythagorean, reciprocal, quotient, co-function, and even-odd identities
  ```
  *(too verbose, exceeds character limit)*

**Styling**:
```css
.simplified-recap {
  padding: 12px 16px 12px 28px;
  background: #f3f4f6;
  font-size: 14px;
  line-height: 1.8;
}

.simplified-recap ul {
  list-style-type: disc;
  padding-left: 16px;
}
```

---

### 3. Confidence Tips

**Purpose**: Actionable study strategies to build confidence and mastery

**Location**: Collapsible section (collapsed by default)

**Icon**: 🌟 (star)

**Word Cap**: 2-3 tips, **≤ 200 characters total**

**Tone**: Actionable, practical, encouraging

**Action Verbs**: "Start by...", "Try...", "Practice...", "Focus on...", "Use..."

**Examples**:
- ✅ "Start by memorizing the three Pythagorean identities. Practice deriving the others from these base forms. Use flashcards and apply them to 5 problems daily."
- ✅ "Try solving problems without looking at your notes. This active recall strengthens memory and builds exam confidence."
- ❌ "You should study these identities carefully and make sure you understand them well." *(too vague, not actionable)*

**Styling**:
```css
.confidence-tips {
  padding: 12px 16px;
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}
```

---

### 4. Encouragement

**Purpose**: Closing motivational quote to leave user feeling positive

**Location**: Always visible when Mentor panel expanded (below collapsible sections)

**Icon**: 🧭 (compass)

**Word Cap**: 1 sentence, **≤ 150 characters**

**Tone**: Inspiring, growth-mindset focused, emotionally uplifting

**Examples**:
- ✅ "Remember, every expert was once a beginner. You're building skills that will unlock advanced mathematics! 🌟"
- ✅ "You've got this! Keep up the great work—each step forward is progress toward mastery. 💪"
- ❌ "Good luck with your studies." *(too generic, lacks emotional impact)*

**Styling**:
```css
.encouragement {
  padding: 16px;
  background: linear-gradient(135deg, #fce7f3, #fbcfe8);
  border-left: 4px solid #ec4899;
  font-style: italic;
  font-size: 14px;
  color: #831843;
}
```

---

## Collapse/Expand States

### Default State (Collapsed)

**Visual**:
```
┌─────────────────────────────────────────────────────────────┐
│  💬 Show Mentor's Motivation                    [Chevron ▼] │
│  Get emotional support and study strategies                 │
└─────────────────────────────────────────────────────────────┘
```

**Behavior**:
- Background: Soft pink-purple gradient
- Hover: Slightly darker gradient
- Click: Smooth expand animation (300ms ease-in-out)

**Analytics Event**: *(none - collapsed is default state)*

---

### Expanded State

**Visual**:
```
┌─────────────────────────────────────────────────────────────┐
│  💬 Mentor's Guidance                           [Chevron ▲] │
│  Warm support and confidence-building tips                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  💙 Motivation Spark                                        │
│  You're tackling one of the most powerful tools in         │
│  mathematics! These identities will serve you in calculus,  │
│  physics, and engineering.                                  │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  💬 Quick Recap                                   [▼]       │
│  (collapsed - click to expand)                             │
│                                                             │
│  🌟 Confidence Boost                              [▼]       │
│  (collapsed - click to expand)                             │
│                                                             │
│  🧭 Keep Going!                                             │
│  "Remember, every expert was once a beginner. You're       │
│  building skills that will unlock advanced mathematics! 🌟" │
│                                                             │
│  [50% Emotional Support badge]                             │
└─────────────────────────────────────────────────────────────┘
```

**Behavior**:
- Smooth height animation
- Sub-sections collapsible independently
- Hover effects on all interactive elements

**Analytics Event**: `mentor_expanded`

---

## Visual Rhythm & Spacing

### Spacing Standards

```css
/* Component spacing */
.mentor-panel {
  margin-bottom: 32px;  /* Space before next component */
}

/* Section spacing */
.mentor-section {
  margin-bottom: 16px;  /* Between sections */
  padding: 16px;        /* Internal padding */
}

/* Separator lines */
.section-divider {
  height: 2px;
  background: linear-gradient(90deg, transparent, #ec4899, transparent);
  margin: 16px 0;
}
```

### Icon System

| Section | Icon | Color | Purpose |
|---------|------|-------|---------|
| Motivation Spark | 💙 | Blue | Warm emotional connection |
| Quick Recap | 💬 | Purple | Communication/summary |
| Confidence Boost | 🌟 | Yellow | Achievement/positivity |
| Keep Going | 🧭 | Pink | Direction/guidance |

---

## Typography

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Size & Weight

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| Section Header | 16px | 700 (bold) | 1.4 |
| Motivation Spark | 16px | 400 (regular) | 1.6 |
| Recap Bullets | 14px | 400 | 1.8 |
| Confidence Tips | 14px | 500 (medium) | 1.6 |
| Encouragement | 14px | 400 (italic) | 1.6 |

---

## Color Palette

### Gradients

```css
/* Main panel gradient */
background: linear-gradient(135deg, #fce7f3, #fbcfe8, #fce7f3);

/* Motivation Spark */
background: linear-gradient(135deg, #fef3c7, #fde68a);

/* Confidence Tips */
background: linear-gradient(135deg, #dbeafe, #bfdbfe);

/* Encouragement */
background: linear-gradient(135deg, #fce7f3, #fbcfe8);
```

### Border & Accent Colors

- **Primary Pink**: `#ec4899`
- **Hover Pink**: `#db2777`
- **Text Pink**: `#831843`
- **Yellow Accent**: `#f59e0b`
- **Blue Accent**: `#3b82f6`

---

## Animation & Transitions

### Expand/Collapse

```css
.mentor-panel-content {
  transition: height 400ms cubic-bezier(0.4, 0, 0.2, 1),
              opacity 300ms ease-in-out;
}
```

### Chevron Rotation

```css
.chevron-icon {
  transition: transform 300ms ease-in-out;
}

.expanded .chevron-icon {
  transform: rotate(180deg);
}
```

### Hover Effects

```css
.mentor-button:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 25px rgba(236, 72, 153, 0.2);
  transition: all 200ms ease;
}
```

---

## Analytics Events

### Event 1: mentor_expanded

**Triggered**: When user clicks to expand Mentor panel

**Payload**:
```javascript
{
  event: 'mentor_expanded',
  session_id: 'uuid',
  message_id: 'uuid',
  timestamp: 1697000000000
}
```

---

### Event 2: mentor_collapsed

**Triggered**: When user clicks to collapse Mentor panel

**Payload**:
```javascript
{
  event: 'mentor_collapsed',
  session_id: 'uuid',
  message_id: 'uuid',
  time_expanded_seconds: 45,
  timestamp: 1697000000000
}
```

---

### Event 3: mentor_section_viewed

**Triggered**: When user expands a sub-section (Recap or Tips)

**Payload**:
```javascript
{
  event: 'mentor_section_viewed',
  session_id: 'uuid',
  section: 'simplified_recap' | 'confidence_tips',
  timestamp: 1697000000000
}
```

---

### Event 4: mentor_interaction_time

**Triggered**: When Mentor panel collapses, summarizing interaction

**Payload**:
```javascript
{
  event: 'mentor_interaction_time',
  session_id: 'uuid',
  total_time_seconds: 120,
  sections_viewed: ['motivation_spark', 'confidence_tips'],
  expanded_count: 2,
  timestamp: 1697000000000
}
```

---

## Accessibility

### ARIA Labels

```jsx
<button
  onClick={handleExpand}
  aria-expanded={expanded}
  aria-controls="mentor-content"
  aria-label="Show mentor's motivational guidance"
>
  💬 Show Mentor's Motivation
</button>

<div
  id="mentor-content"
  role="region"
  aria-labelledby="mentor-header"
  hidden={!expanded}
>
  {/* Content */}
</div>
```

### Keyboard Navigation

- **Enter/Space**: Toggle expand/collapse
- **Tab**: Navigate between collapsible sub-sections
- **Escape**: Collapse Mentor panel if expanded

---

## Error Handling

### Missing Mentor Sections

If `mentor_sections` is null or incomplete:

1. **Fallback to legacy**: Display `secondary.response` as plain text
2. **Log warning**: Track missing sections for debugging
3. **Show generic message**: "Your mentor is here to support you! 💜"

---

## Word Cap Enforcement (Backend)

```python
def split_mentor_response(self, mentor_text: str) -> Dict[str, str]:
    # ... parsing logic ...
    
    # Trim each section to reasonable length
    for key in sections:
        if sections[key] and len(sections[key]) > 200:
            sections[key] = sections[key][:197] + '...'
    
    return sections
```

---

## Component Implementation

### File Location
`/app/frontend/src/components/microlesson/MentorCard.js`

### Key Props

```javascript
<MentorCard 
  mentorData={secondary}  // Contains mentor_sections
  weight={0.3}            // Mentor persona weight (0-0.5)
/>
```

### State Management

```javascript
const [expanded, setExpanded] = useState(false);         // Main panel
const [showRecap, setShowRecap] = useState(false);       // Recap section
const [showTips, setShowTips] = useState(false);         // Tips section
const [interactionStartTime, setInteractionStartTime] = useState(null);
```

---

## Testing Checklist

### Visual Tests

- [ ] Mentor panel collapsed by default
- [ ] Smooth expand animation (300-400ms)
- [ ] Chevron rotates 180° on expand
- [ ] Sub-sections collapsed when parent expands
- [ ] Icon colors match spec
- [ ] Gradients render correctly
- [ ] Text doesn't overflow containers

### Functional Tests

- [ ] Click to expand/collapse works
- [ ] Sub-section expand/collapse independent
- [ ] Analytics events fire correctly
- [ ] Keyboard navigation functional
- [ ] Screen reader announces state changes

### Content Tests

- [ ] Motivation Spark ≤ 200 chars
- [ ] Simplified Recap ≤ 300 chars
- [ ] Confidence Tips ≤ 200 chars
- [ ] Encouragement ≤ 150 chars
- [ ] No markdown artifacts visible
- [ ] No escape sequences visible

---

## Performance Targets

| Metric | Target | Max |
|--------|--------|-----|
| Expand animation | 300ms | 500ms |
| Collapse animation | 300ms | 500ms |
| First paint (collapsed) | <50ms | 100ms |
| First paint (expanded) | <100ms | 200ms |
| Analytics event latency | <10ms | 50ms |

---

## See Also

- [AI Tutor Response Schema](./ai_tutor_response_schema.md)
- [Text Sanitization Pipeline](./text_sanitization_pipeline.md)
- Backend: `/app/backend/utils/response_parser.py`
- Frontend: `/app/frontend/src/components/microlesson/MentorCard.js`
- Analytics: `/app/frontend/src/hooks/useAITutor.js`
