/**
 * 🛡️ VALIDATOR ENGINE (SketchSense V5.0)
 * =======================================
 * 
 * Universal validation system with subject-specific plugins.
 * Prevents students from learning incorrect science through
 * real-time constraint checking and micro-feedback.
 * 
 * Architecture:
 * - ValidatorEngine (generic core)
 * - Subject Plugins: physics, chemistry, biology, mathematics
 * - Future extensibility: any subject can add its own validator
 * 
 * Returns ValidationResult:
 * {
 *   isValid: boolean,
 *   violationType?: string,
 *   mentorMessage?: string,
 *   hindiMessage?: string,
 *   visualEffect?: 'shake' | 'fade' | 'skid' | 'highlight' | 'pulse'
 * }
 */

// ============================================
// VALIDATION RESULT TYPES
// ============================================
export const VALIDATION_STATUS = {
  VALID: 'valid',
  WARNING: 'warning',
  ERROR: 'error',
};

export const VISUAL_EFFECTS = {
  SHAKE: 'shake',      // Object shakes (invalid input)
  FADE: 'fade',        // Object fades (impossible state)
  SKID: 'skid',        // Object skids (friction violation)
  HIGHLIGHT: 'highlight', // Highlight issue area
  PULSE: 'pulse',      // Pulsing warning
  EXPLODE: 'explode',  // Dramatic failure visualization
};

// ============================================
// PHYSICS VALIDATOR PLUGIN
// ============================================
export const physicsValidator = {
  name: 'physics',
  
  validate(state, blueprint) {
    const violations = [];
    
    // Rule 1: Mass cannot be negative or zero
    if (state.mass !== undefined && state.mass <= 0) {
      violations.push({
        type: 'negative_mass',
        message: "Mass can't be zero or negative! All objects have positive mass.",
        hindiMessage: "द्रव्यमान शून्य या ऋणात्मक नहीं हो सकता!",
        effect: VISUAL_EFFECTS.SHAKE,
      });
    }
    
    // Rule 2: Velocity sanity check (speed of light limit)
    if (state.velocity !== undefined && Math.abs(state.velocity) > 3e8) {
      violations.push({
        type: 'superluminal',
        message: "Nothing can travel faster than light (3×10⁸ m/s)!",
        hindiMessage: "कुछ भी प्रकाश की गति से तेज़ नहीं चल सकता!",
        effect: VISUAL_EFFECTS.PULSE,
      });
    }
    
    // Rule 3: Friction cannot be negative
    if (state.friction !== undefined && state.friction < 0) {
      violations.push({
        type: 'negative_friction',
        message: "Friction coefficient can't be negative!",
        hindiMessage: "घर्षण गुणांक ऋणात्मक नहीं हो सकता!",
        effect: VISUAL_EFFECTS.HIGHLIGHT,
      });
    }
    
    // Rule 4: Centripetal force requires friction on curves
    if (state.curvedPath && state.friction === 0) {
      violations.push({
        type: 'no_centripetal',
        message: "Whoops! Without friction, centripetal force fails. The car would skid off!",
        hindiMessage: "अरे! घर्षण के बिना अभिकेंद्रीय बल नहीं लगेगा। गाड़ी फिसल जाएगी!",
        effect: VISUAL_EFFECTS.SKID,
      });
    }
    
    // Rule 5: Force > 0 but no motion (check friction)
    if (state.force > 0 && state.velocity === 0 && state.friction !== undefined) {
      const maxStaticFriction = (state.mass || 1) * 9.8 * (state.frictionCoeff || state.friction);
      if (state.force < maxStaticFriction) {
        // This is actually valid - force not enough to overcome friction
      } else if (state.force > maxStaticFriction && state.velocity === 0) {
        violations.push({
          type: 'impossible_static',
          message: "This force should overcome friction and cause motion!",
          hindiMessage: "यह बल घर्षण को पार करके गति उत्पन्न करना चाहिए!",
          effect: VISUAL_EFFECTS.PULSE,
        });
      }
    }
    
    // Rule 6: Projectile angle must be 0-90 degrees for forward throw
    if (state.angle !== undefined) {
      if (state.angle < 0) {
        violations.push({
          type: 'negative_angle',
          message: "Negative angle means throwing backwards/downward!",
          hindiMessage: "ऋणात्मक कोण का मतलब पीछे/नीचे फेंकना!",
          effect: VISUAL_EFFECTS.HIGHLIGHT,
        });
      }
      if (state.angle > 90) {
        violations.push({
          type: 'backward_throw',
          message: "Angle > 90° throws the projectile backwards!",
          hindiMessage: "90° से अधिक कोण प्रक्षेप्य को पीछे फेंकता है!",
          effect: VISUAL_EFFECTS.HIGHLIGHT,
        });
      }
    }
    
    // Rule 7: Temperature cannot go below absolute zero
    if (state.temperature !== undefined && state.temperature < -273.15) {
      violations.push({
        type: 'below_absolute_zero',
        message: "Temperature can't go below absolute zero (-273.15°C)!",
        hindiMessage: "तापमान परम शून्य से नीचे नहीं जा सकता!",
        effect: VISUAL_EFFECTS.SHAKE,
      });
    }
    
    // Return result
    if (violations.length === 0) {
      return { isValid: true };
    }
    
    const primary = violations[0];
    return {
      isValid: false,
      violationType: primary.type,
      mentorMessage: primary.message,
      hindiMessage: primary.hindiMessage,
      visualEffect: primary.effect,
      allViolations: violations,
    };
  },
};

// ============================================
// CHEMISTRY VALIDATOR PLUGIN
// ============================================
export const chemistryValidator = {
  name: 'chemistry',
  
  validate(state, blueprint) {
    const violations = [];
    
    // Rule 1: Carbon cannot form more than 4 bonds
    if (state.carbonBonds !== undefined && state.carbonBonds > 4) {
      violations.push({
        type: 'carbon_valence',
        message: "Carbon can only form 4 bonds! Its valence is 4.",
        hindiMessage: "कार्बन केवल 4 बंध बना सकता है! इसकी संयोजकता 4 है।",
        effect: VISUAL_EFFECTS.SHAKE,
      });
    }
    
    // Rule 2: pH must be between 0 and 14
    if (state.pH !== undefined && (state.pH < 0 || state.pH > 14)) {
      violations.push({
        type: 'invalid_ph',
        message: "pH scale goes from 0 to 14 only!",
        hindiMessage: "pH स्केल केवल 0 से 14 तक जाता है!",
        effect: VISUAL_EFFECTS.HIGHLIGHT,
      });
    }
    
    // Rule 3: Concentration cannot be negative
    if (state.concentration !== undefined && state.concentration < 0) {
      violations.push({
        type: 'negative_concentration',
        message: "Concentration can't be negative!",
        hindiMessage: "सांद्रता ऋणात्मक नहीं हो सकती!",
        effect: VISUAL_EFFECTS.FADE,
      });
    }
    
    // Rule 4: Electron count in shells (2n² rule)
    if (state.electronShell && state.electronCount) {
      const maxElectrons = 2 * Math.pow(state.electronShell, 2);
      if (state.electronCount > maxElectrons) {
        violations.push({
          type: 'electron_overflow',
          message: `Shell ${state.electronShell} can hold maximum ${maxElectrons} electrons (2n² rule)!`,
          hindiMessage: `कोश ${state.electronShell} अधिकतम ${maxElectrons} इलेक्ट्रॉन रख सकता है!`,
          effect: VISUAL_EFFECTS.PULSE,
        });
      }
    }
    
    // Rule 5: Oxidation state constraints
    if (state.oxidationState !== undefined) {
      // Generic check - can be element-specific
      if (state.element === 'oxygen' && state.oxidationState !== -2 && state.oxidationState !== -1) {
        // Allow -2 (normal) and -1 (peroxides)
        if (state.oxidationState > 0) {
          violations.push({
            type: 'unusual_oxidation',
            message: "Oxygen usually has negative oxidation state (-2 or -1)!",
            hindiMessage: "ऑक्सीजन आमतौर पर ऋणात्मक ऑक्सीकरण अवस्था रखता है!",
            effect: VISUAL_EFFECTS.HIGHLIGHT,
          });
        }
      }
    }
    
    if (violations.length === 0) {
      return { isValid: true };
    }
    
    const primary = violations[0];
    return {
      isValid: false,
      violationType: primary.type,
      mentorMessage: primary.message,
      hindiMessage: primary.hindiMessage,
      visualEffect: primary.effect,
      allViolations: violations,
    };
  },
};

// ============================================
// BIOLOGY VALIDATOR PLUGIN
// ============================================
export const biologyValidator = {
  name: 'biology',
  
  validate(state, blueprint) {
    const violations = [];
    
    // Rule 1: Blood cannot flow backward through heart valves
    if (state.bloodFlow && state.valveOpen === false && state.flowDirection === 'backward') {
      violations.push({
        type: 'backward_blood_flow',
        message: "Heart valves prevent blood from flowing backward!",
        hindiMessage: "हृदय के वाल्व रक्त को पीछे बहने से रोकते हैं!",
        effect: VISUAL_EFFECTS.SHAKE,
      });
    }
    
    // Rule 2: Photosynthesis requires light
    if (state.process === 'photosynthesis' && state.lightIntensity === 0) {
      violations.push({
        type: 'no_light_photosynthesis',
        message: "Photosynthesis needs light! It can't happen in complete darkness.",
        hindiMessage: "प्रकाश संश्लेषण के लिए प्रकाश चाहिए! अंधेरे में नहीं हो सकता।",
        effect: VISUAL_EFFECTS.FADE,
      });
    }
    
    // Rule 3: ATP production rates
    if (state.atpCount !== undefined) {
      if (state.process === 'glycolysis' && state.atpCount > 4) {
        violations.push({
          type: 'excess_atp_glycolysis',
          message: "Glycolysis produces only 2 net ATP (4 total, 2 used)!",
          hindiMessage: "ग्लाइकोलिसिस केवल 2 शुद्ध ATP बनाता है!",
          effect: VISUAL_EFFECTS.HIGHLIGHT,
        });
      }
      if (state.process === 'krebs_cycle' && state.atpCount > 2) {
        violations.push({
          type: 'excess_atp_krebs',
          message: "Krebs cycle produces only 2 ATP per glucose!",
          hindiMessage: "क्रेब्स चक्र प्रति ग्लूकोज केवल 2 ATP बनाता है!",
          effect: VISUAL_EFFECTS.HIGHLIGHT,
        });
      }
    }
    
    // Rule 4: Cell division phases
    if (state.cellPhase && state.chromosomeCount) {
      if (state.cellPhase === 'metaphase' && !state.chromosomesAligned) {
        violations.push({
          type: 'metaphase_alignment',
          message: "In metaphase, chromosomes must align at the cell equator!",
          hindiMessage: "मेटाफेज में गुणसूत्र कोशिका के मध्य में पंक्तिबद्ध होने चाहिए!",
          effect: VISUAL_EFFECTS.PULSE,
        });
      }
    }
    
    // Rule 5: DNA base pairing (A-T, G-C)
    if (state.dnaBasePair) {
      const validPairs = { 'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G' };
      if (validPairs[state.dnaBasePair.base1] !== state.dnaBasePair.base2) {
        violations.push({
          type: 'invalid_base_pair',
          message: "DNA base pairing: A pairs with T, G pairs with C!",
          hindiMessage: "DNA क्षार युग्मन: A-T और G-C!",
          effect: VISUAL_EFFECTS.SHAKE,
        });
      }
    }
    
    if (violations.length === 0) {
      return { isValid: true };
    }
    
    const primary = violations[0];
    return {
      isValid: false,
      violationType: primary.type,
      mentorMessage: primary.message,
      hindiMessage: primary.hindiMessage,
      visualEffect: primary.effect,
      allViolations: violations,
    };
  },
};

// ============================================
// MATHEMATICS VALIDATOR PLUGIN
// ============================================
export const mathematicsValidator = {
  name: 'mathematics',
  
  validate(state, blueprint) {
    const violations = [];
    
    // Rule 1: Division by zero
    if (state.divisor !== undefined && state.divisor === 0) {
      violations.push({
        type: 'division_by_zero',
        message: "Can't divide by zero! It's undefined.",
        hindiMessage: "शून्य से भाग नहीं कर सकते! यह अपरिभाषित है।",
        effect: VISUAL_EFFECTS.EXPLODE,
      });
    }
    
    // Rule 2: Square root of negative (real numbers)
    if (state.sqrtInput !== undefined && state.sqrtInput < 0 && !state.allowComplex) {
      violations.push({
        type: 'negative_sqrt',
        message: "Square root of negative number is not real (unless using complex numbers)!",
        hindiMessage: "ऋणात्मक संख्या का वर्गमूल वास्तविक नहीं है!",
        effect: VISUAL_EFFECTS.SHAKE,
      });
    }
    
    // Rule 3: Logarithm of non-positive
    if (state.logInput !== undefined && state.logInput <= 0) {
      violations.push({
        type: 'invalid_log',
        message: "Logarithm is only defined for positive numbers!",
        hindiMessage: "लघुगणक केवल धनात्मक संख्याओं के लिए परिभाषित है!",
        effect: VISUAL_EFFECTS.FADE,
      });
    }
    
    // Rule 4: Probability must be between 0 and 1
    if (state.probability !== undefined && (state.probability < 0 || state.probability > 1)) {
      violations.push({
        type: 'invalid_probability',
        message: "Probability must be between 0 and 1!",
        hindiMessage: "प्रायिकता 0 और 1 के बीच होनी चाहिए!",
        effect: VISUAL_EFFECTS.HIGHLIGHT,
      });
    }
    
    // Rule 5: Factorial of negative
    if (state.factorialInput !== undefined && state.factorialInput < 0) {
      violations.push({
        type: 'negative_factorial',
        message: "Factorial is not defined for negative integers!",
        hindiMessage: "ऋणात्मक पूर्णांकों के लिए क्रमगुणित परिभाषित नहीं है!",
        effect: VISUAL_EFFECTS.SHAKE,
      });
    }
    
    if (violations.length === 0) {
      return { isValid: true };
    }
    
    const primary = violations[0];
    return {
      isValid: false,
      violationType: primary.type,
      mentorMessage: primary.message,
      hindiMessage: primary.hindiMessage,
      visualEffect: primary.effect,
      allViolations: violations,
    };
  },
};

// ============================================
// VALIDATOR REGISTRY
// ============================================
const validatorRegistry = {
  physics: physicsValidator,
  chemistry: chemistryValidator,
  biology: biologyValidator,
  mathematics: mathematicsValidator,
  math: mathematicsValidator, // Alias
  general: physicsValidator, // Default fallback
};

// ============================================
// VALIDATOR ENGINE (Core)
// ============================================
export class ValidatorEngine {
  constructor() {
    this.validators = { ...validatorRegistry };
  }
  
  /**
   * Register a new validator plugin
   */
  registerValidator(subject, validator) {
    if (validator && typeof validator.validate === 'function') {
      this.validators[subject.toLowerCase()] = validator;
    }
  }
  
  /**
   * Get validator for a subject
   */
  getValidator(subject) {
    return this.validators[subject?.toLowerCase()] || this.validators.general;
  }
  
  /**
   * Validate state with appropriate subject validator
   */
  validate(subject, state, blueprint) {
    const validator = this.getValidator(subject);
    return validator.validate(state, blueprint);
  }
  
  /**
   * Cross-validate multiple parameters
   */
  crossValidate(subject, params, blueprint) {
    const validator = this.getValidator(subject);
    const results = [];
    
    // Validate each parameter
    for (const [key, value] of Object.entries(params)) {
      const result = validator.validate({ [key]: value }, blueprint);
      if (!result.isValid) {
        results.push({ parameter: key, ...result });
      }
    }
    
    return results.length === 0 
      ? { isValid: true } 
      : { isValid: false, violations: results };
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================
export function getValidatorForSubject(subject) {
  return validatorRegistry[subject?.toLowerCase()] || validatorRegistry.general;
}

export function validateParameter(subject, paramName, value, blueprint = {}) {
  const validator = getValidatorForSubject(subject);
  return validator.validate({ [paramName]: value }, blueprint);
}

// Default export
export default new ValidatorEngine();


