# 🇮🇳 Cultural Metaphors Engine

India-first metaphor system that makes learning relatable using everyday contexts.

## Overview

The Metaphor Engine automatically substitutes generic educational visuals with culturally relevant Indian contexts:

- 🏏 **Cricket** - for force and motion
- 🛺 **Auto Rickshaw** - for friction and acceleration
- ☕ **Chai** - for heat transfer and evaporation
- 🪔 **Diwali** - for light and energy
- 🌧️ **Monsoon** - for water cycle and weather
- 🎨 **Holi** - for dispersion and projectile motion

---

## Quick Start

### Automatic Detection

```javascript
import { MetaphorMapper } from './visual-engine/metaphors';

const mapper = new MetaphorMapper();

// Auto-detect and apply metaphor
const blueprint = {
  concept: 'centripetal force',
  subject: 'physics',
  items: [{ id: 'ball', label: 'Ball', type: 'circle' }],
};

const enhanced = mapper.apply(blueprint);
// Automatically uses cricket metaphor!
// ball → cricket ball 🏏
```

### Manual Selection

```javascript
// Force specific metaphor
const enhanced = mapper.apply(blueprint, 'auto_rickshaw');
// Now uses auto rickshaw context 🛺
```

---

## Available Metaphors

### 🏏 Sports

#### **Cricket**
- **Concepts:** Force, motion, centripetal force, momentum
- **Best for:** Physics - projectile motion, forces
- **Elements:** Cricket ball, bat, wicket, pitch, bowler

```javascript
{
  force: 'Cricket ball being bowled',
  motion: 'Ball trajectory to batsman',
  momentum: 'Powerful six hit'
}
```

### 🛺 Transport

#### **Auto Rickshaw**
- **Concepts:** Friction, acceleration, mass
- **Best for:** Physics - motion on roads
- **Elements:** Auto, road, driver, passengers

#### **Local Train**
- **Concepts:** Momentum, kinetic energy
- **Best for:** Physics - large mass systems
- **Elements:** Train, tracks, platform

### ☕ Food & Daily Life

#### **Chai (Tea)**
- **Concepts:** Heat transfer, temperature, evaporation
- **Best for:** Thermodynamics, phase changes
- **Elements:** Chai cup, steam, stove

#### **Dosa**
- **Concepts:** Heat conduction, chemical reactions
- **Best for:** Chemistry - reactions, heat
- **Elements:** Dosa, tawa (pan), batter

### 🪔 Festivals

#### **Diwali**
- **Concepts:** Light, energy, combustion
- **Best for:** Optics, energy transformations
- **Elements:** Diya (lamp), firecracker, rangoli

#### **Holi**
- **Concepts:** Projectile motion, dispersion
- **Best for:** Physics - trajectories
- **Elements:** Pichkari (water gun), gulal (powder)

### 🌧️ Nature

#### **Monsoon**
- **Concepts:** Water cycle, evaporation, condensation
- **Best for:** Water cycle, weather
- **Elements:** Rain, clouds, lightning

### 👨‍👩‍👧‍👦 Family & Society

#### **Market (Sabzi Mandi)**
- **Concepts:** Supply-demand, weighing, mass
- **Best for:** Economics, measurement
- **Elements:** Vendor, vegetables, balance

#### **Classroom**
- **Concepts:** Sound, reflection, communication
- **Best for:** Waves, optics
- **Elements:** Teacher, blackboard, students

---

## Integration with Pipeline

### With ConceptBreaker

```javascript
import { ConceptBreaker } from './intelligence';
import { MetaphorMapper } from './metaphors';

// Break concept
const breaker = new ConceptBreaker();
const blueprint = await breaker.break(
  'Explain friction using auto rickshaw',
  { subject: 'physics' }
);

// Blueprint already has metaphor: 'auto_rickshaw'
// Apply it
const mapper = new MetaphorMapper();
const enhanced = mapper.apply(blueprint);

// enhanced.items[0].metaphorLabel = 'Auto'
// enhanced.items[0].metaphorEmoji = '🛺'
```

### With SceneComposer

```javascript
import { composeScene } from './intelligence';
import { applyMetaphor } from './metaphors';

const conceptData = { /* from ConceptBreaker */ };
const positioned = composeScene(conceptData);
const withMetaphor = applyMetaphor(positioned, 'cricket');

// Now render with UniversalSketchRenderer
```

---

## Metaphor Detection

The system automatically detects metaphors in three ways:

### 1. Keyword Detection
```javascript
"Explain force using cricket ball"
→ Detects 'cricket' keyword
→ Applies cricket metaphor 🏏
```

### 2. Concept Mapping
```javascript
concept: 'centripetal force'
→ Searches database for centripetal_force
→ Finds cricket (spin bowling)
→ Applies automatically
```

### 3. Subject Defaults
```javascript
subject: 'physics', concept: 'force'
→ No specific metaphor found
→ Uses default: cricket 🏏
```

---

## SVG Assets

Hand-drawn style SVG assets for each metaphor:

```javascript
import { getAsset, getAssetDataUrl } from './metaphors';

// Get SVG string
const svg = getAsset('cricket_ball');

// Get data URL for <img> src
const url = getAssetDataUrl('cricket_ball');

// Render as React component
import { renderAsset } from './metaphors';
<div>{renderAsset('cricket_ball', { width: 40, height: 40 })}</div>
```

**Available Assets:**
- `cricket_ball`, `cricket_bat`, `wickets`
- `auto_rickshaw`, `local_train`
- `chai_cup`, `dosa`
- `diya` (lamp)
- `rain_drop`, `monsoon_cloud`
- `stick_figure`

---

## Custom Metaphors

Add your own metaphors to `MetaphorDatabase.js`:

```javascript
export const METAPHOR_DATABASE = {
  my_metaphor: {
    id: 'my_metaphor',
    category: METAPHOR_CATEGORIES.SPORTS,
    name: 'My Metaphor',
    description: 'Description here',
    keywords: ['keyword1', 'keyword2'],
    
    concepts: {
      my_concept: {
        label: 'How it maps',
        description: 'Explanation',
      },
    },
    
    substitutions: {
      ball: { emoji: '⚽', svg: 'my_ball', label: 'My Ball' },
    },
    
    background: {
      color: '#FFE5B4',
      pattern: 'my_pattern',
    },
  },
};
```

---

## API Reference

### MetaphorMapper

```javascript
class MetaphorMapper {
  apply(blueprint, metaphorId?) // Apply metaphor to blueprint
  detectMetaphor(concept, subject) // Auto-detect metaphor
  getSuggestedMetaphors(concept, subject) // Get top 5 suggestions
  explainMetaphor(metaphorId, concept) // Get explanation
}
```

### Helper Functions

```javascript
getMetaphor(id) // Get metaphor by ID
findMetaphorByKeyword(keyword) // Search by keyword
searchMetaphorsByConcept(concept) // Find metaphors for concept
getConceptMapping(metaphorId, concept) // Get specific mapping
getSubstitution(metaphorId, element) // Get element substitution
```

---

## Examples

### Example 1: Cricket for Force

```javascript
const blueprint = await breakConcept(
  'Explain Newton\'s second law',
  { subject: 'physics' }
);

const mapper = new MetaphorMapper();
const enhanced = mapper.apply(blueprint, 'cricket');

// Result:
// - Force visualized as cricket ball being bowled
// - Mass as ball weight
// - Acceleration as ball speed change
// - Background: Green cricket pitch
// - Doodle: 🏏 emoji
```

### Example 2: Chai for Heat Transfer

```javascript
const blueprint = {
  concept: 'heat transfer',
  subject: 'physics',
  items: [
    { id: 'hot', label: 'Hot object' },
    { id: 'cold', label: 'Cold object' },
  ],
};

const enhanced = applyMetaphor(blueprint, 'chai');

// Result:
// - Hot object → Hot chai cup ☕
// - Cold object → Air around cup
// - Shows heat flowing from chai to surroundings
```

---

## Cultural Context

The metaphor system is designed to:

1. ✅ **Make concepts relatable** - Uses everyday Indian experiences
2. ✅ **Reduce cognitive load** - Familiar contexts = faster understanding
3. ✅ **Increase engagement** - Students see themselves in examples
4. ✅ **Support multilingual** - Visual metaphors transcend language
5. ✅ **Respect diversity** - Multiple metaphors for different regions

---

## Performance

- ✅ **Lightweight** - No external dependencies
- ✅ **Fast** - Simple keyword matching + lookup
- ✅ **Cached** - ConceptBreaker caches results
- ✅ **Scalable** - Easy to add new metaphors

---

## Future Enhancements

- [ ] Regional variations (North India, South India, etc.)
- [ ] User preference learning (which metaphors work best)
- [ ] Animated SVG assets
- [ ] Sound effects for metaphors
- [ ] Community-contributed metaphors
- [ ] A/B testing different metaphors

---

For more details, see the implementation files in `metaphors/`.
