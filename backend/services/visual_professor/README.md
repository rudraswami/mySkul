# Visual Professor Engine

Dynamic, intelligent, interactive visual system that generates professor-like animated explanations for ANY student question.

## Architecture

### Components

1. **UnifiedConceptDetector** (`concept_detector.py`)
   - Integrates existing intent, topic, and concept detection systems
   - Returns structured `ConceptMetadata` with subject, topic, concept, intent, etc.

2. **VisualTemplateRegistry** (`template_registry.py`)
   - Centralized mapping of concepts → intents → visual templates
   - Enhances existing template system with concept-based organization
   - Integrates with `backend/visual_library/templates.json`

3. **VisualProfessorGenerator** (`generator.py`)
   - Main generator that orchestrates visual creation
   - Integrates with `VisualTeachingEngine` for animations
   - Adds professor-style narration
   - Adds interactive elements

4. **ProfessorNarrationGenerator** (in `generator.py`)
   - Generates clear, precise, step-by-step narration
   - Style: Like a real professor teaching on board

## Usage

```python
from services.visual_professor import VisualProfessorGenerator

generator = VisualProfessorGenerator()

# Generate visual for any question
visual_data = await generator.generate_visual(
    question="Explain valency in chemistry",
    subject="Chemistry",
    student_profile={"region": "Delhi", "preferred_metaphor": "cricket"}
)

# Returns:
# {
#   "visual_id": "...",
#   "type": "animated_lesson",
#   "visual_type": "animation",
#   "template": "cricket_bonding_match",
#   "stages": [
#     {
#       "stage_id": "intro",
#       "duration_ms": 2000,
#       "narration": "Let's understand valency step by step.",
#       "narration_style": "professor",
#       "animations": [...],
#       "interactions": [...]
#     }
#   ],
#   "metadata": {
#     "concept": "Valency",
#     "subject": "chemistry",
#     "intent": ["concept_explanation"],
#     ...
#   }
# }
```

## Integration with Existing Systems

- **Reuses**: `IntentPlanner`, `TopicClassifier`, `ConceptDeconstruction`, `VisualTeachingEngine`
- **Enhances**: Template registry with concept→intent mapping
- **Compatible**: Works with existing `TeachingVisualPlayer` frontend component

## Features

✅ Dynamic - Generated based on question understanding
✅ Concept-aware - Matches concept and intent
✅ Multi-step - Animated like a real professor teaching
✅ Interactive - Scrubbing, hover labels, step transitions
✅ Reusable templates - Not static or one-off
✅ Professor narration - Clear, precise, step-by-step

## File Structure

```
backend/services/visual_professor/
├── __init__.py
├── concept_detector.py      # Unified concept detection
├── template_registry.py      # Template registry with concept→intent mapping
├── generator.py              # Main visual generator
├── visual_response_model.py # Response models
└── README.md                 # This file
```

