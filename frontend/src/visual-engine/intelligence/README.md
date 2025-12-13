# 🧠 Intelligence Layer

**Purpose:** The "brain" that generates visual blueprints from questions

## Components

### `ConceptBreaker.js`
Transforms natural language questions into structured visual blueprints.

**Input:** Question string, subject, difficulty level
**Output:** Blueprint JSON with mode, entities, relations, controls, beats

**Powered by:**
- OpenAI GPT-4-mini (primary)
- Rule-based fallback (reliability)

**Example:**
```javascript
ConceptBreaker.analyze("Explain centripetal force using cricket")
// → { mode: 'SCENE', metaphor: 'cricket', entities: [...], beats: [...] }
```

### `SceneComposer.js`
Positions elements spatially using layout algorithms.

**Input:** Entities and relations from ConceptBreaker
**Output:** Positioned blueprint with x,y coordinates

**Algorithms:**
- Force-directed layout
- Grid layout
- Circular layout
- Tree layout
- Flow layout

### `MetaphorMapper.js`
Applies cultural context (India-first) to blueprints.

**Mappings:**
- Force → Cricket bowler
- Acceleration → Auto-rickshaw
- Gravity → Mango falling
- Heat → Chai cooling
- Circuit → Diwali lights

### `ModeDetector.js`
Determines the best visual mode for a concept.

**Modes:**
- SCENE - Physics simulations
- PROCESS - Step-by-step flows
- CYCLE - Circular loops
- COMPARISON - X vs Y
- STRUCTURE - Labeled diagrams
- GRAPH - Math plots
- TIMELINE - Chronological
- HIERARCHY - Trees

### `prompts/`
LLM prompt templates for each subject.

---

**Status:** 🚧 Phase 6 (After renderer is built)
**Dependencies:** core/, layouts/, metaphors/

