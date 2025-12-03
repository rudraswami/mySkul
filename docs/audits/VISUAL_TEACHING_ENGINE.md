# Visual Teaching Engine - Living Lessons System

## Overview

The Visual Teaching Engine transforms static, repetitive diagrams into **living, animated teaching sequences** that feel like a mentor drawing and explaining concepts in real-time.

### The Problem We Solved

**Before**: Static, template-based visuals that look the same across all subjects
- Grammar lesson → Generic flow diagram with cricket metaphor
- Chemistry lesson → Same flow diagram with cricket metaphor
- Math lesson → Same flow diagram with cricket metaphor
- **Result**: Students see repetitive, lifeless diagrams

**After**: Dynamic, story-driven animations tailored to each concept
- Grammar → Split-screen transformation with cooking metaphor
- Chemistry → Orbital animation with festival lights metaphor
- Math → Process timeline with train journey metaphor
- **Result**: Each explanation feels alive and contextually relevant

---

## Key Features

### 1. **Semantic Understanding**
The engine understands WHAT you're teaching, not just WORDS:
- Detects concept types (comparison, transformation, process, cycle, etc.)
- Maps to appropriate visual patterns automatically
- Chooses culturally relevant metaphors

### 2. **Animated Storytelling**
Every concept unfolds as a short teaching sequence:
- Progressive disclosure (7-15 second stages)
- Smooth transitions between ideas
- Emotional guidance through narration
- Emphasis on key "aha!" moments

### 3. **Cultural Context**
Metaphors that Indian students instantly connect with:
- **Cricket**: Processes, teamwork, strategies
- **Cooking**: Transformations, mixing, reactions
- **Trains**: Sequences, timelines, journeys
- **Bollywood**: Drama, heroes/villains, transformations
- **Festivals**: Cycles, celebrations, traditions
- **Gaming**: Levels, progression, challenges

### 4. **Micro-Interactions**
Students stay engaged every 5-7 seconds:
- Tap to continue
- Quiz questions
- Drag-and-drop exercises
- Predictions
- Sliders for exploration

### 5. **Subject-Specific Intelligence**
- **English Grammar**: Split-screen comparisons, transformation morphs
- **Math**: Step-by-step process flows, equation animations
- **Physics**: Force diagrams, motion trajectories
- **Chemistry**: Molecular animations, reaction sequences
- **Biology**: System diagrams, cycle animations

---

## Architecture

### Backend Components

```
backend/
├── services/
│   ├── visual_teaching_engine.py       # Core engine
│   ├── cultural_metaphor_library.py    # Indian context metaphors
│   └── grammar_visual_templates.py     # Pre-built grammar animations
└── api/
    └── visual_teaching.py              # API endpoints
```

### Frontend Components

```
frontend/src/
├── components/
│   ├── TeachingVisualPlayer.js         # Main animation player
│   ├── InteractionLayer.js             # Student interaction handler
│   └── mentor-v2/
│       └── MentorResponseV2.js         # Integrated with mentor
└── engines/
    └── AnimationEngine.js              # D3.js animation primitives
```

---

## API Usage

### 1. Generate Teaching Visual

```javascript
POST /api/visual-teaching/generate

Request:
{
  "question": "Explain active and passive voice",
  "subject": "English",
  "complexity": "medium",
  "student_profile": {
    "grade": "class_10",
    "region": "North"
  }
}

Response:
{
  "success": true,
  "visual_id": "uuid-123",
  "type": "animated_lesson",
  "stages": [
    {
      "stage_id": "stage-1",
      "duration_ms": 3000,
      "narration": "Let's understand active and passive voice using cooking!",
      "animations": [...],
      "interactions": [...],
      "emphasis": "Active voice = WHO does the action!"
    },
    ...
  ],
  "total_duration_ms": 27000,
  "interaction_points": [1, 3, 4],
  "metadata": {
    "subject": "English",
    "topic": "Active and Passive Voice",
    "cultural_metaphor": "cooking",
    "complexity": "medium"
  }
}
```

### 2. Submit Interaction Feedback

```javascript
POST /api/visual-teaching/feedback

Request:
{
  "visual_id": "uuid-123",
  "stage_index": 3,
  "interaction_type": "quiz",
  "user_response": {
    "selected": 0,
    "correct": true,
    "option": "Active Voice"
  },
  "timestamp": 1234567890
}
```

### 3. Get Available Patterns

```javascript
GET /api/visual-teaching/patterns

Response:
{
  "visual_patterns": [
    {
      "name": "flow_diagram",
      "description": "Step-by-step process visualization"
    },
    {
      "name": "split_screen",
      "description": "Side-by-side comparison"
    },
    ...
  ],
  "concept_types": [...]
}
```

### 4. Get Learning Analytics

```javascript
GET /api/visual-teaching/analytics/{user_id}

Response:
{
  "user_id": "user-123",
  "overall_stats": {
    "total_visuals_viewed": 45,
    "total_learning_time_seconds": 1260,
    "subjects_covered": 5
  },
  "subject_breakdown": [...],
  "interaction_performance": [...],
  "learning_patterns": {
    "most_used_subject": "Physics",
    "avg_visual_duration_seconds": 28,
    "interaction_rate": 0.85
  }
}
```

---

## Frontend Integration

### Basic Usage

```jsx
import TeachingVisualPlayer from './components/TeachingVisualPlayer';

function MyComponent() {
  const [visualData, setVisualData] = useState(null);

  useEffect(() => {
    // Fetch visual from API
    fetch('/api/visual-teaching/generate', {
      method: 'POST',
      body: JSON.stringify({
        question: "Explain active and passive voice",
        subject: "English"
      })
    })
    .then(res => res.json())
    .then(data => setVisualData(data));
  }, []);

  return (
    <TeachingVisualPlayer
      visualData={visualData}
      onComplete={(result) => {
        console.log('Completed!', result);
      }}
      onInteraction={(interaction) => {
        console.log('User interaction:', interaction);
      }}
    />
  );
}
```

### Integration with MentorResponseV2

The TeachingVisualPlayer is automatically integrated with `MentorResponseV2.js`. When the backend sends `teaching_visual` data, it will render animated visuals instead of static images:

```jsx
// In your AI response
{
  "default_view": { ... },
  "teaching_visual": {
    "visual_id": "...",
    "stages": [...],
    ...
  }
}
```

---

## Creating Custom Visual Templates

### Example: Custom Grammar Template

```python
from services.visual_teaching_engine import AnimationStage
import uuid

def my_custom_template():
    stages = [
        AnimationStage(
            stage_id=str(uuid.uuid4()),
            duration_ms=3000,
            narration="Your teaching narration here...",
            animations=[
                {
                    "type": "scene_setup",
                    "elements": ["element1", "element2"],
                    "style": "your_style"
                },
                {
                    "type": "fade_in",
                    "target": "element1",
                    "duration": 1000
                }
            ],
            interactions=[
                {
                    "type": "quiz",
                    "question": "Your question?",
                    "options": ["A", "B", "C"],
                    "correct": 0
                }
            ],
            emphasis="Key point to emphasize!"
        ),
        # ... more stages
    ]

    return {
        "visual_id": str(uuid.uuid4()),
        "type": "animated_lesson",
        "stages": stages,
        "total_duration_ms": sum(s.duration_ms for s in stages),
        "interaction_points": [0, 2, 4],
        "metadata": {
            "subject": "Your Subject",
            "topic": "Your Topic",
            "complexity": "medium"
        }
    }
```

---

## Animation Types

### Scene Setup
```python
{
  "type": "scene_setup",
  "elements": ["cricket_pitch", "players"],
  "style": "cricket_theme"
}
```

### Split Screen
```python
{
  "type": "split_screen_enter",
  "side": "left",
  "label": "ACTIVE VOICE"
}
```

### Sentence Building
```python
{
  "type": "sentence_build",
  "words": ["Ravi", "makes", "chai"],
  "highlights": {
    "Ravi": "subject",
    "makes": "verb",
    "chai": "object"
  },
  "colors": {
    "subject": "#10b981",
    "verb": "#f59e0b",
    "object": "#6366f1"
  }
}
```

### Transformation Morph
```python
{
  "type": "transformation_morph",
  "from": "Ravi makes chai",
  "to": "Chai is made by Ravi",
  "duration": 2000,
  "style": "smooth_flow"
}
```

### Spotlight
```python
{
  "type": "character_spotlight",
  "character": "Ravi",
  "highlight": true,
  "duration": 1500
}
```

---

## Interaction Types

### Tap to Continue
```python
{
  "type": "tap_to_continue",
  "prompt": "Tap when you're ready!"
}
```

### Quiz
```python
{
  "type": "quiz",
  "question": "Which voice puts the DOER first?",
  "options": ["Active", "Passive", "Both"],
  "correct": 0,
  "hint": "Think about the sentence structure!",
  "successMessage": "Perfect!",
  "errorMessage": "Not quite - try again!"
}
```

### Drag and Drop
```python
{
  "type": "drag",
  "items": [
    {"id": "item1", "label": "Subject"},
    {"id": "item2", "label": "Verb"}
  ],
  "targets": [
    {"id": "pos1", "label": "Position 1"}
  ],
  "correctMapping": {"item1": "pos1"}
}
```

### Slider
```python
{
  "type": "slider",
  "min": 0,
  "max": 100,
  "step": 1,
  "label": "Adjust the temperature"
}
```

### Prediction
```python
{
  "type": "predict",
  "prompt": "What will happen next?",
  "options": ["Option A", "Option B"],
  "actual": "Option A - Here's why..."
}
```

---

## Cultural Metaphor Library

### Available Metaphors

| Category | Best For | Visual Elements | Example |
|----------|----------|-----------------|---------|
| **Cricket** | Processes, teamwork, strategies | Pitch, players, ball, wickets | "Photosynthesis is like a cricket match" |
| **Cooking** | Transformations, mixing | Kadhai, spices, flame | "Chemical reactions are like cooking chai" |
| **Trains** | Sequences, timelines | Train, stations, tracks | "Digestion is a journey through stations" |
| **Bollywood** | Drama, conflicts, resolution | Hero, villain, stage | "Immune system is heroes vs villains" |
| **Festivals** | Cycles, celebrations | Diya, rangoli, fireworks | "Seasons are like festival cycles" |
| **Gaming** | Levels, progression | Avatar, health bar, power-ups | "Energy levels are like game levels" |
| **Traffic** | Flow, congestion | Auto, signals, flyover | "Blood flow is like Mumbai traffic" |
| **Family** | Hierarchy, relationships | Family tree, elders | "Taxonomy is like a joint family" |
| **Street Food** | Combinations, proportions | Pani puri, chutneys | "H₂O is like perfect pani puri ratio" |

### Using Metaphors

```python
from services.cultural_metaphor_library import get_culturally_relevant_metaphor

# Get metaphor for a concept
metaphor = get_culturally_relevant_metaphor(
    concept="chemical reaction",
    subject="chemistry",
    preferred_category="cooking"
)

# Returns complete metaphor with:
# - Visual elements
# - Animation sequences
# - Micro-interactions
# - Subject-specific adaptations
```

---

## Pre-built Templates

### Grammar Templates

1. **Active vs Passive Voice** ✓
   - 7 animated stages
   - Cooking + cricket metaphors
   - 4 interaction points
   - Duration: ~27 seconds

2. **Subject-Verb Agreement** ✓
   - Cricket team metaphor
   - Singular vs plural comparison
   - Duration: ~7 seconds

3. **Verb Tenses** ✓
   - Train timeline metaphor
   - Past → Present → Future journey
   - Duration: ~15 seconds

### Coming Soon

- **Math**: Equation solving, fractions, percentages
- **Physics**: Forces, motion, energy
- **Chemistry**: Atomic structure, bonding, reactions
- **Biology**: Cell structure, digestion, circulation

---

## Performance Metrics

### Target Metrics
- **Engagement**: 5-7 second micro-interactions
- **Duration**: 15-45 seconds per lesson
- **Completion**: >80% watch to end
- **Retention**: >60% can explain after 1 week
- **Cultural Fit**: >90% understand metaphor instantly

### Analytics Tracked
- Visual views per user
- Interaction completion rates
- Quiz accuracy
- Time spent per stage
- Drop-off points
- Preferred metaphor categories

---

## Development Roadmap

### Phase 1: Core Engine ✓
- [x] Semantic parser
- [x] Animation engine
- [x] Cultural metaphor library
- [x] Basic interaction types
- [x] API endpoints

### Phase 2: Templates & Integration ✓
- [x] Grammar visual templates
- [x] Frontend player component
- [x] MentorResponseV2 integration
- [ ] Math visual templates
- [ ] Physics visual templates

### Phase 3: Advanced Features
- [ ] Voice narration synthesis
- [ ] Real-time adaptation based on confusion
- [ ] Peer interaction (students see each other's responses)
- [ ] Teacher dashboard for custom visuals
- [ ] A/B testing framework

### Phase 4: Scale & Polish
- [ ] Performance optimization (WebGL rendering)
- [ ] Offline support
- [ ] Multi-language support
- [ ] Accessibility features
- [ ] Mobile app integration

---

## Testing

### Backend Testing

```bash
# Test visual generation
python -m pytest backend/tests/test_visual_pipeline.py

# Test cultural metaphor library
python -m pytest backend/tests/test_cultural_metaphors.py
```

### Frontend Testing

```bash
# Run Storybook to preview components
cd frontend
npm run storybook

# Test specific visual
npm run test:visual -- --visual=active_passive
```

### Manual Testing

1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm start`
3. Navigate to: `http://localhost:3000/test-visual`
4. Try question: "Explain active and passive voice"

---

## Troubleshooting

### Visual Not Loading
- Check network tab for API errors
- Verify `visual_teaching` router is registered in `main.py`
- Check console for JavaScript errors

### Animations Not Smooth
- Reduce `fps` in AnimationEngine config
- Use `renderer: 'canvas'` instead of `'svg'` for complex animations
- Check browser performance

### Interactions Not Working
- Verify interaction event handlers in InteractionLayer
- Check that interaction data structure matches expected format
- Test on different devices (touch vs mouse)

### Cultural Metaphor Not Relevant
- Update metaphor mapping in `cultural_metaphor_library.py`
- Add region-specific variations
- Provide fallback metaphors

---

## Contributing

### Adding a New Visual Template

1. Create template function in appropriate file
2. Register in API endpoint keyword detection
3. Test with multiple questions
4. Document in this README

### Adding a New Metaphor Category

1. Add to `MetaphorCategory` enum
2. Create visual elements in `_load_visual_elements()`
3. Add animation sequences
4. Test with students from target region

### Adding a New Animation Type

1. Implement in `AnimationEngine.js`
2. Add to animation primitives
3. Document parameters and usage
4. Create example in Storybook

---

## Credits

Built with ❤️ for Indian students by the DruvAI team.

**Core Technologies:**
- FastAPI (Backend)
- React + Framer Motion (Frontend)
- D3.js (Animations)
- MongoDB (Analytics)

**Inspired by:**
- Khan Academy's interactive lessons
- Brilliant.org's visual explanations
- Traditional Indian teaching methods (guru-shishya)

---

## License

Proprietary - DruvAI © 2024

---

## Support

- **Issues**: Report at GitHub issues
- **Questions**: Contact dev@druvai.com
- **Feature Requests**: Create a GitHub discussion

---

**Last Updated**: 2024-01-09
**Version**: 1.0.0
