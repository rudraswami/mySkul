# 🛡️ Validators - Intelligent Feedback System

Subject-specific validation engines that catch conceptual errors in real-time.

## Overview

The validator system provides:
- ✅ **Real-time validation** of user interactions
- ✅ **Visual feedback** (shake, glow, scribble, etc.)
- ✅ **Educational messages** via Ghost Mentor
- ✅ **Subject-specific rules** (Physics, Chemistry, Math, Biology)
- ✅ **Extensible architecture** for adding new validators

---

## Available Validators

### 1. **PhysicsValidator** (`PhysicsValidator.js`)

Validates physics concepts:
- ✅ Mass must be positive
- ✅ Friction coefficient (0-1)
- ✅ Velocity cannot exceed speed of light
- ✅ Friction opposes motion
- ✅ Energy conservation
- ✅ F = ma validation

**Example:**
```javascript
import { PhysicsValidator } from './validators';

const validator = new PhysicsValidator();

// Validate mass
const result = validator.validate(5, { property: 'mass' });
if (!result.valid) {
  console.log(result.results[0].message); // Error message
}

// Validate Newton's 2nd law
const check = validator.validateNewtonSecondLaw(10, 2, 5);
// F=10N, m=2kg, a=5m/s² → Valid! ✓
```

### 2. **ChemistryValidator** (`ChemistryValidator.js`)

Validates chemistry concepts:
- ✅ Valency rules (H=1, C=4, O=2, etc.)
- ✅ Charge balance in ionic compounds
- ✅ pH range (0-14)
- ✅ Electronegativity and bond types
- ✅ Noble gases don't bond

**Example:**
```javascript
import { ChemistryValidator } from './validators';

const validator = new ChemistryValidator();

// Validate valency
const result = validator.validate(4, {
  property: 'bonds',
  element: 'C',
});
// Carbon with 4 bonds → Valid! ✓

// Validate pH
const phResult = validator.validate(7.4, {
  property: 'pH',
  fluid: 'blood',
});
// Blood pH 7.4 → Valid! ✓
```

### 3. **MathValidator** (`MathValidator.js`)

Validates math operations:
- ✅ No division by zero
- ✅ Square root domain (≥0)
- ✅ Logarithm domain (>0)
- ✅ Tan asymptotes
- ✅ Probability range (0-1)
- ✅ Factorial domain (non-negative integers)

**Example:**
```javascript
import { MathValidator } from './validators';

const validator = new MathValidator();

// Safe evaluation
const result = validator.safeEvaluate('sqrt', 16);
// result.success = true, result.result = 4

const badResult = validator.safeEvaluate('sqrt', -4);
// badResult.success = false, validation error
```

### 4. **BiologyValidator** (`BiologyValidator.js`)

Validates biology concepts:
- ✅ Blood flow direction (heart → lungs → body)
- ✅ Cell organelles (chloroplast only in plant cells)
- ✅ Blood pH (7.35-7.45)
- ✅ Body temperature (36-38°C)
- ✅ Photosynthesis equation
- ✅ DNA base pairing (A-T, G-C)

**Example:**
```javascript
import { BiologyValidator } from './validators';

const validator = new BiologyValidator();

// Validate blood pH
const result = validator.validate(7.4, {
  property: 'pH',
  fluid: 'blood',
});
// pH 7.4 → Valid! ✓

// Validate DNA base pairing
const dnaResult = validator.validate('T', {
  property: 'basePair',
  base1: 'A',
});
// A-T pairing → Valid! ✓
```

---

## Usage Patterns

### Pattern 1: Direct Validation

```javascript
import { getValidator } from './validators';

const validator = getValidator('physics');
const result = validator.validate(10, {
  property: 'mass',
});

if (!result.valid) {
  console.log(result.results[0].message);
  // "Mass cannot be negative! Objects have positive mass! 📦"
}
```

### Pattern 2: React Hook

```javascript
import { useValidationFeedback } from '../feedback';

function PhysicsDemo() {
  const { validate, validation, isValid } = useValidationFeedback('physics');
  
  const handleSliderChange = (value) => {
    validate(value, 'friction', { scenario: 'everyday' });
  };
  
  return (
    <div>
      <Slider onChange={handleSliderChange} />
      {!isValid && <div>{validation.results[0].message}</div>}
    </div>
  );
}
```

### Pattern 3: With Visual Feedback

```javascript
import { ValidationFeedback } from '../feedback';

function InteractiveScene() {
  const [validation, setValidation] = useState(null);
  
  return (
    <ValidationFeedback
      validation={validation}
      targetX={200}
      targetY={150}
    >
      <Ball mass={mass} />
    </ValidationFeedback>
  );
}
```

---

## Feedback Types

| Type | Description | Visual Effect |
|------|-------------|---------------|
| `SHAKE` | Shake animation | Element shakes left-right |
| `GLOW` | Success glow | Green glow around element |
| `DIM` | Fade effect | Element fades and returns |
| `SCRIBBLE` | Red X mark | Red scribble overlay |
| `GHOST_MENTOR` | Text bubble | Mentor message appears |
| `HIGHLIGHT` | Yellow highlight | Yellow circle highlight |

---

## Validation Status

| Status | Meaning | Color |
|--------|---------|-------|
| `VALID` | No errors | Green ✓ |
| `WARNING` | Caution | Yellow ⚠ |
| `ERROR` | Invalid | Red ✗ |
| `INFO` | Information | Blue ℹ |

---

## Creating Custom Validators

```javascript
import { BaseValidator, VALIDATION_STATUS, FEEDBACK_TYPE } from './BaseValidator';

export class CustomValidator extends BaseValidator {
  constructor(options = {}) {
    super({ subject: 'custom', ...options });
    this.initializeRules();
  }
  
  initializeRules() {
    this.addRule({
      id: 'my_rule',
      name: 'My Custom Rule',
      description: 'Description of the rule',
      check: (value, context) => {
        return value > 0; // Your validation logic
      },
      message: 'Value must be positive!',
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
      suggestion: () => 'Try a positive number',
    });
  }
}
```

---

## Integration with Controls

Validators integrate seamlessly with sketchy controls:

```javascript
import { SketchSlider } from '../controls';
import { useValidationFeedback } from '../feedback';

function PhysicsSlider() {
  const { validate, validation } = useValidationFeedback('physics');
  
  return (
    <SketchSlider
      value={friction}
      onChange={(val) => {
        const result = validate(val, 'friction');
        if (result.valid) {
          setFriction(val);
        }
      }}
      validation={validation}
    />
  );
}
```

---

## Architecture

```
User Interaction
    ↓
SketchSlider / SketchToggle
    ↓
useValidationFeedback hook
    ↓
PhysicsValidator / ChemistryValidator / etc.
    ↓
ValidationResult { valid, status, results }
    ↓
ValidationFeedback component
    ↓
Visual Effects (shake, glow, scribble, etc.)
```

---

## Best Practices

1. **Always validate user input** in interactive controls
2. **Use appropriate feedback types** for different errors
3. **Provide helpful suggestions** in validation messages
4. **Cache validators** for performance (reuse instances)
5. **Test edge cases** (zero, negative, infinity, etc.)
6. **Use warnings for unusual** but valid values
7. **Keep error messages educational** and friendly

---

## Performance

- ✅ Validators are lightweight (no external dependencies)
- ✅ Rules are evaluated synchronously (fast)
- ✅ Feedback animations use GPU-accelerated transforms
- ✅ Validation results can be cached if needed

---

## Future Enhancements

- [ ] Async validation for complex rules
- [ ] Rule composition (combine multiple rules)
- [ ] Validation context history
- [ ] Machine learning-based validation
- [ ] Multi-language error messages

---

For more details, see the implementation files in `validators/`.

