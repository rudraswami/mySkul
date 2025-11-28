# Legacy Archive

This folder contains legacy/deprecated files that have been replaced by the new unified AI Tutor pipeline.

## Why These Files Were Archived

### Prompts
- `neuro_symbolic_mentor_v2.py` - 500+ line rigid JSON template that forced same structure for all questions
- `neuro_symbolic_tutor.py` - Legacy 8-section response format
- `metaphor_visual_library.py` - Static CDN URLs that often returned placeholders

### Services
- `universal_visual_planner.py` - Generic fallback visual generator (rarely useful)
- `dynamic_visual_builder.py` - Duplicate visual generation logic
- `muse_generator.py` - Legacy metaphor system
- `metaphor_selector.py` - Replaced by intelligent_response_engine

## New Architecture

The new unified pipeline uses:
1. `response_composer.py` - Single entry point for all AI responses
2. `conversation_state.py` - Context tracking across messages
3. `intelligent_response_engine.py` - Adaptive intent detection and block selection
4. `visual_concept_detector.py` + `visual_template_selector.py` - Visual Engine V2

## Do Not Use These Files

These files are kept for reference only. Do not import or use them in new code.



