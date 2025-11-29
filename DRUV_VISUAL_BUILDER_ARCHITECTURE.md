# Druv AI Visual Builder: Technical Architecture
## Hallucination-Free, Culturally-Rooted Interactive Content System

**Core Philosophy**: "Professor's Blueprint, Not AI's Guess"

The Visual Builder doesn't generate visuals—it assembles them from pre-verified, culturally-tuned components using a rule-based grammar. The AI's role is copilot, not creator.

---

## System Architecture: The "Panchayat Model"

Five modular layers, each with a distinct technical owner and hallucination guardrail.

---

## 1. BHARAT ASSET LIBRARY (BAL) - The Raw Materials

**Purpose**: Version-controlled, culturally-coded 3D/2D object repository

### What it contains:
- ~500 Core Objects: Auto-rickshaw (mass: 450kg, friction: 0.7), cricket ball (dia: 7.2cm), LPG cylinder (pressure: 8bar), sugarcane stalk, Kochi backwater boat, Jaipur fort rampart
- **Metadata Schema**: Each asset has JSON tags: `cultural_region`, `syllabus_topic`, `physics_behaviour`, `real_world_measurement`, `citation_url`
- **LOD (Level of Detail)**: 3 versions per object: High (WebGL), Medium (Canvas 2D), Low (SVG). Auto-switches based on student's device & bandwidth

### Technical Stack:
- **Storage**: AWS S3 + CloudFront with India edge nodes
- **Format**: glTF (3D), Lottie (2D animations), SVG (vectors). All compressed via DRACO
- **Version Control**: Git LFS for asset binaries. Every change requires pull request + teacher approval
- **Access**: GraphQL API for the Builder to query assets by concept

### Hallucination Guardrail:
No asset enters BAL without a SME (IIT professor) + Teacher (CBSE) + Cultural Reviewer approval. Each asset is signed with a digital certificate.

---

## 2. VIDYA GRAMMAR ENGINE (VGE) - The Rulebook

**Purpose**: Declarative, open-source DSL (Domain Specific Language) that defines how subjects are visualized. No code generation.

### Grammar Examples (YAML configs):

```yaml
# Physics.ForceBetweenTwoObjects

parameters:
  - object_a: {type: asset, tag: movable}
  - object_b: {type: asset, tag: surface}
  - force_slider: {type: variable, min: 0, max: 1000, unit: N}
  - surface_type: {enum: [dry, wet, oily, muddy]}

output:
  animation: |
    object_a.acceleration = force_slider / object_a.mass
    friction_force = object_a.mass * gravity * surface_friction_coefficient[surface_type]
    if (force_slider > friction_force):
      object_a.velocity += object_a.acceleration * timestep
  annotations:
    - label: "Static Friction Limit"
      position: friction_force
      color: red
      ncert_citation: "Page 102, Fig 5.3"
```

### Technical Stack:
- **Parser**: Python Pydantic models for strict validation
- **Runtime**: WASM (WebAssembly) module compiled from Rust. Executes grammar in <16ms on a ₹8,000 Android phone
- **Registry**: Each grammar is an immutable npm package versioned by subject (e.g., `@druv/grammar-physics@1.2.0`)

### Hallucination Guardrail:
Grammars are unit-tested against 100+ NCERT problems. If output doesn't match NCERT's answer key, CI pipeline fails. No AI touches the grammar logic—only SMEs write it.

---

## 3. DRUV VISUAL BUILDER (DVB) - The Assembly Line

**Purpose**: No-code interface where content team (not engineers) assembles visuals in under 15 minutes

### Workflow:
1. SME selects concept (e.g., "Newton's 2nd Law")
2. Copilot AI suggests: "Use Physics.ForceBetweenTwoObjects. Recommended assets: auto-rickshaw, wet Mumbai road."
3. SME drags assets into canvas. Builder auto-snaps to grammar rules
4. SME binds parameters: Drags a slider onto "Force" variable. Builder auto-generates range (0-500N) based on auto-rickshaw mass
5. SME adds cultural hook: "How many Dabbawalas to push your auto?"
6. Real-time preview: WASM engine renders visual instantly on a simulated ₹5,000 phone inside the builder
7. SME submits for approval: JSON config is generated

### Technical Stack:
- **Frontend**: React + TypeScript + Canvas API (for preview). MobX for state management
- **Copilot AI**: OpenAI GPT-4o-mini, but heavily prompt-engineered to only suggest from BAL/VGE. Context: 10-shot examples + retrieval from knowledge graph. Temperature = 0
- **Config Format**: Protobuf (for size) + JSON schema (for human-readability). Stored in PostgreSQL with Row-Level Security
- **Collaboration**: Yjs for real-time multi-user editing (teacher + SME working together)

### Hallucination Guardrail:
Builder has a "Truth Mode" toggle. When on, AI suggestions are greyed out and must be double-clicked to accept. All AI suggestions are logged and reviewed weekly. Builder UI shows a "Creativity vs. Truth" score: if you accept >30% AI suggestions, your approval rights are revoked.

---

## 4. SATYA RUNTIME (Satya) - The Player

**Purpose**: Student-facing renderer. Takes a config ID and runs the visual without any AI.

### Technical Stack:
- **Core**: WASM module (same as VGE) + Three.js for 3D fallback
- **Performance**:
  - First load: 50KB WASM + 200KB assets via CDN
  - Subsequent loads: Visuals cached in IndexedDB. Works offline after first view
  - 2G optimization: If bandwidth < 50kbps, auto-falls back to SVG + CSS animations (pre-rendered on server using Puppeteer)
- **Interaction**: Hammer.js for touch gestures. Students can pinch, zoom, pan, slow-mo, rewind
- **Telemetry**: Sends interaction heatmaps (where student paused, which slider they moved) to backend. No PII

### Hallucination Guardrail:
Runtime is read-only. It cannot fetch new assets or change logic. If config is malformed, it fails gracefully to a pre-approved static image + text. No dynamic generation = no hallucination.

---

## 5. GURU VALIDATOR (GV) - The Panchayat Seal

**Purpose**: Blockchain-inspired attestation system where teachers cryptographically sign visuals.

### Workflow:
1. Visual config is minted as a draft NFT (on Polygon for low gas fees—not for speculation, for immutability)
2. 3 Teachers must sign:
   - Subject Expert (e.g., Physics teacher with >5 years CBSE)
   - Cultural Expert (e.g., teacher from same state as target student)
   - Pedagogy Expert (e.g., verified JEE coach)
3. Once 3 signatures collected, visual is published and config hash is stored on-chain
4. Student sees: "✅ Approved by Mr. Sharma (IIT-D), Ms. Pillai (Kerala CBSE), Mr. Yadav (JEE Coach)" with QR code linking to validation proof

### Technical Stack:
- **Smart Contracts**: Solidity on Polygon. Stores only config hash + teacher DID (Decentralized Identifier)
- **Teacher Identity**: Verifiable credentials via Ceramic Network. Linked to CBSE teacher ID database (API integration)
- **UI**: Simple React app where teachers see a queue of pending visuals. One-click approve/reject with reason

### Hallucination Guardrail:
This is ultimate truth. If a visual is wrong, you know exactly which teachers approved it. Reputation is on-chain. Teachers are paid ₹500 per approval (micropayment via UPI), creating a curation economy.

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [x] Architecture documentation
- [ ] BAL: Basic asset schema and storage structure
- [ ] VGE: Grammar parser and validator
- [ ] DVB: Basic canvas interface
- [ ] Satya: WASM runtime foundation

### Phase 2: Core Features (Weeks 3-4)
- [ ] BAL: 50 core Indian assets (auto-rickshaw, cricket ball, etc.)
- [ ] VGE: 10 core grammars (Physics: Force, Friction, Motion)
- [ ] DVB: Drag-drop interface with grammar validation
- [ ] Satya: Basic renderer with interaction

### Phase 3: Scale (Weeks 5-6)
- [ ] BAL: 200+ assets across all subjects
- [ ] VGE: 50+ grammars covering CBSE syllabus
- [ ] DVB: AI copilot integration
- [ ] Satya: Performance optimization for low-end devices

### Phase 4: Validation (Weeks 7-8)
- [ ] GV: Teacher approval workflow
- [ ] GV: Blockchain integration (Polygon)
- [ ] GV: Reputation system
- [ ] End-to-end testing with real teachers

---

## File Structure

```
backend/
├── visual_builder/
│   ├── bal/                    # Bharat Asset Library
│   │   ├── __init__.py
│   │   ├── asset_schema.py     # Pydantic models for assets
│   │   ├── asset_storage.py    # S3/CloudFront integration
│   │   ├── asset_validator.py  # SME approval workflow
│   │   └── asset_api.py        # GraphQL API
│   │
│   ├── vge/                    # Vidya Grammar Engine
│   │   ├── __init__.py
│   │   ├── grammar_parser.py   # YAML → Pydantic models
│   │   ├── grammar_validator.py # NCERT test suite
│   │   ├── grammar_runtime.py   # WASM compilation target
│   │   └── grammars/           # Grammar definitions
│   │       ├── physics/
│   │       ├── chemistry/
│   │       └── mathematics/
│   │
│   ├── dvb/                    # Druv Visual Builder
│   │   ├── __init__.py
│   │   ├── builder_api.py      # REST API for builder
│   │   ├── config_generator.py # JSON/Protobuf output
│   │   ├── copilot_ai.py       # GPT-4o-mini integration
│   │   └── collaboration.py    # Yjs real-time editing
│   │
│   ├── satya/                  # Satya Runtime
│   │   ├── __init__.py
│   │   ├── runtime_wasm.py     # WASM module
│   │   ├── renderer.py         # Three.js/Canvas renderer
│   │   ├── interaction.py      # Hammer.js gestures
│   │   └── telemetry.py        # Interaction tracking
│   │
│   └── gv/                     # Guru Validator
│       ├── __init__.py
│       ├── validator_api.py    # Teacher approval API
│       ├── blockchain.py       # Polygon smart contracts
│       ├── teacher_identity.py # Ceramic DID integration
│       └── reputation.py       # On-chain reputation
│
frontend/
├── visual-builder/             # DVB Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Canvas.tsx
│   │   │   ├── AssetPalette.tsx
│   │   │   ├── GrammarPanel.tsx
│   │   │   └── CopilotPanel.tsx
│   │   ├── hooks/
│   │   │   ├── useGrammar.ts
│   │   │   └── useAssets.ts
│   │   └── utils/
│   │       └── wasmLoader.ts
│   │
└── satya-runtime/             # Satya Frontend (React)
    ├── src/
    │   ├── components/
    │   │   ├── VisualRenderer.tsx
    │   │   └── InteractionLayer.tsx
    │   └── wasm/
    │       └── satya.wasm
```

---

## Next Steps

1. **Create foundational directory structure**
2. **Implement BAL asset schema**
3. **Implement VGE grammar parser**
4. **Create basic DVB API endpoints**
5. **Build Satya runtime foundation**

Let's start building! 🚀







