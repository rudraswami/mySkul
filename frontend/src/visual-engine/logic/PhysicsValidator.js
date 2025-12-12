/**
 * 🧠 PHYSICS VALIDATOR - Intelligence Layer for SketchSense
 * =========================================================
 * 
 * PURPOSE:
 * Monitor state changes in interactive controls and validate
 * against physical laws and constraints.
 * 
 * FEATURES:
 * - Misconception Detection: Catches physically impossible states
 * - Friendly Feedback: Returns toast messages with explanations
 * - Hint System: Provides educational hints for edge cases
 * - Ghost Mentor Integration: Triggers visual feedback animations
 * 
 * ARCHITECTURE:
 * InteractiveControls → PhysicsValidator → FeedbackToast
 *                                       → GhostMentorEvent
 *                                       → VisualOverride
 */

// ============================================
// VALIDATION RESULT TYPES
// ============================================
export const VALIDATION_STATUS = {
  VALID: 'valid',
  WARNING: 'warning',
  ERROR: 'error',
  HINT: 'hint',
};

export const FEEDBACK_TYPE = {
  TOAST: 'toast',
  MENTOR: 'mentor',
  VISUAL: 'visual',
  SOUND: 'sound',
};

// ============================================
// CONSTRAINT DEFINITIONS BY TEMPLATE
// ============================================
const PHYSICS_CONSTRAINTS = {
  // Projectile Motion Constraints
  projectile: {
    angle: {
      min: 0,
      max: 90,
      errorBelow: {
        message: "🎯 Angle can't be negative! You can't throw backwards through the ground.",
        hindiMessage: "कोण नकारात्मक नहीं हो सकता!",
        type: VALIDATION_STATUS.ERROR,
      },
      errorAbove: {
        message: "🔄 Angle > 90° means throwing backwards! The ball would go behind you.",
        hindiMessage: "90° से अधिक कोण = पीछे की ओर फेंकना!",
        type: VALIDATION_STATUS.ERROR,
        visualOverride: { animation: 'backwards_throw' },
      },
      warningAt45: {
        message: "🎯 45° is the sweet spot for maximum range! (ignoring air resistance)",
        hindiMessage: "45° अधिकतम दूरी के लिए सबसे अच्छा कोण है!",
        type: VALIDATION_STATUS.HINT,
      },
    },
    velocity: {
      min: 0,
      max: 200,
      errorBelow: {
        message: "🛑 Velocity can't be negative. That would mean time travel!",
        hindiMessage: "वेग नकारात्मक नहीं हो सकता!",
        type: VALIDATION_STATUS.ERROR,
      },
      warningHigh: {
        threshold: 150,
        message: "🚀 That's faster than most cricket balls! Professional bowlers reach ~160 km/h.",
        hindiMessage: "यह ज्यादातर क्रिकेट गेंदों से तेज है!",
        type: VALIDATION_STATUS.HINT,
      },
    },
    gravity: {
      min: 0.1,
      max: 30,
      errorBelow: {
        message: "🌙 Zero gravity? You'd need to be in space! Try g = 1.6 for Moon.",
        hindiMessage: "शून्य गुरुत्वाकर्षण? आपको अंतरिक्ष में होना चाहिए!",
        type: VALIDATION_STATUS.WARNING,
        visualOverride: { background: 'space_scene' },
      },
      hintMoon: {
        threshold: 1.6,
        tolerance: 0.2,
        message: "🌙 That's Moon gravity! Objects fall 6x slower there.",
        hindiMessage: "यह चंद्रमा का गुरुत्वाकर्षण है!",
        type: VALIDATION_STATUS.HINT,
      },
      hintEarth: {
        threshold: 9.8,
        tolerance: 0.5,
        message: "🌍 Earth's gravity! g = 9.8 m/s²",
        hindiMessage: "पृथ्वी का गुरुत्वाकर्षण! g = 9.8 m/s²",
        type: VALIDATION_STATUS.HINT,
      },
    },
  },

  // Race/Velocity Comparison Constraints
  race_comparison: {
    velocity: {
      min: 0,
      max: 500,
      errorBelow: {
        message: "🛑 Negative velocity? The car would move backwards!",
        hindiMessage: "नकारात्मक वेग? गाड़ी पीछे चलेगी!",
        type: VALIDATION_STATUS.ERROR,
        visualOverride: { animation: 'reverse_car' },
      },
    },
    friction: {
      min: 0,
      max: 1,
      warningZero: {
        message: "⚠️ Whoops! Without friction, centripetal force fails. The car skids!",
        hindiMessage: "घर्षण के बिना, कार फिसल जाएगी!",
        type: VALIDATION_STATUS.WARNING,
        visualOverride: { animation: 'car_spin_out' },
        mentorMessage: "No grip means no turns! Even on curves, friction keeps you on track.",
      },
      warningLow: {
        threshold: 0.2,
        message: "🧊 Very low friction - like driving on ice! Be careful on turns.",
        hindiMessage: "बहुत कम घर्षण - बर्फ पर गाड़ी चलाने जैसा!",
        type: VALIDATION_STATUS.WARNING,
      },
    },
    mass: {
      min: 0.1,
      max: 10000,
      errorBelow: {
        message: "🤔 Zero mass? That's not physically possible - everything has mass!",
        hindiMessage: "शून्य द्रव्यमान? यह संभव नहीं है!",
        type: VALIDATION_STATUS.ERROR,
      },
      hintLightVsHeavy: {
        message: "💡 F = ma: Same force on lighter object = more acceleration!",
        hindiMessage: "F = ma: हल्की वस्तु पर समान बल = अधिक त्वरण!",
        type: VALIDATION_STATUS.HINT,
      },
    },
  },

  // Circular Motion Constraints
  circular_motion: {
    radius: {
      min: 0.1,
      max: 1000,
      errorBelow: {
        message: "🔴 Radius can't be zero - there's no circle without a radius!",
        hindiMessage: "त्रिज्या शून्य नहीं हो सकती!",
        type: VALIDATION_STATUS.ERROR,
      },
    },
    angular_velocity: {
      min: 0,
      max: 100,
      warningHigh: {
        threshold: 50,
        message: "🌀 That's spinning faster than a washing machine!",
        hindiMessage: "यह वॉशिंग मशीन से भी तेज घूम रहा है!",
        type: VALIDATION_STATUS.WARNING,
      },
    },
  },

  // Wave Motion Constraints
  wave: {
    frequency: {
      min: 0.1,
      max: 1000,
      errorBelow: {
        message: "📻 Frequency must be positive - waves need oscillation!",
        hindiMessage: "आवृत्ति सकारात्मक होनी चाहिए!",
        type: VALIDATION_STATUS.ERROR,
      },
      hintAudible: {
        range: [20, 20000],
        message: "👂 Human hearing range: 20 Hz - 20,000 Hz",
        hindiMessage: "मानव श्रवण सीमा: 20 Hz - 20,000 Hz",
        type: VALIDATION_STATUS.HINT,
      },
    },
    wavelength: {
      min: 0.001,
      max: 10000,
      errorBelow: {
        message: "🌊 Wavelength must be positive!",
        hindiMessage: "तरंगदैर्घ्य सकारात्मक होनी चाहिए!",
        type: VALIDATION_STATUS.ERROR,
      },
    },
    amplitude: {
      min: 0,
      max: 100,
      warningZero: {
        message: "〰️ Zero amplitude means no wave - just a flat line!",
        hindiMessage: "शून्य आयाम = कोई तरंग नहीं!",
        type: VALIDATION_STATUS.WARNING,
      },
    },
  },

  // Chemistry - pH Scale Constraints
  ph_scale: {
    ph_value: {
      min: 0,
      max: 14,
      errorBelow: {
        message: "⚗️ pH can't be negative! Scale goes from 0 to 14.",
        hindiMessage: "pH नकारात्मक नहीं हो सकता!",
        type: VALIDATION_STATUS.ERROR,
      },
      errorAbove: {
        message: "⚗️ pH can't exceed 14! That's the maximum alkalinity.",
        hindiMessage: "pH 14 से अधिक नहीं हो सकता!",
        type: VALIDATION_STATUS.ERROR,
      },
      hintNeutral: {
        threshold: 7,
        tolerance: 0.1,
        message: "💧 pH 7 is neutral - like pure water!",
        hindiMessage: "pH 7 उदासीन है - शुद्ध पानी की तरह!",
        type: VALIDATION_STATUS.HINT,
      },
      hintAcid: {
        range: [0, 6.9],
        message: "🍋 Acidic range! Lower pH = stronger acid.",
        hindiMessage: "अम्लीय सीमा! कम pH = मजबूत अम्ल",
        type: VALIDATION_STATUS.HINT,
      },
      hintBase: {
        range: [7.1, 14],
        message: "🧼 Basic/Alkaline range! Higher pH = stronger base.",
        hindiMessage: "क्षारीय सीमा! अधिक pH = मजबूत क्षार",
        type: VALIDATION_STATUS.HINT,
      },
    },
  },

  // Temperature Constraints
  temperature: {
    kelvin: {
      min: 0,
      max: 10000,
      errorBelow: {
        message: "❄️ Absolute Zero! Temperature can't go below 0 Kelvin (-273.15°C).",
        hindiMessage: "परम शून्य! तापमान 0 केल्विन से नीचे नहीं जा सकता।",
        type: VALIDATION_STATUS.ERROR,
      },
      hintAbsoluteZero: {
        threshold: 0,
        tolerance: 1,
        message: "🥶 Near Absolute Zero - atoms almost stop moving!",
        hindiMessage: "परम शून्य के पास - परमाणु लगभग रुक जाते हैं!",
        type: VALIDATION_STATUS.HINT,
      },
    },
  },
};

// ============================================
// MAIN VALIDATOR CLASS
// ============================================
class PhysicsValidator {
  constructor() {
    this.lastFeedback = null;
    this.feedbackHistory = [];
    this.cooldownMs = 2000; // Prevent spam
    this.lastFeedbackTime = 0;
  }

  /**
   * Validate a single parameter change
   * @param {string} template - Template type (e.g., 'projectile', 'race_comparison')
   * @param {string} parameter - Parameter name (e.g., 'angle', 'velocity')
   * @param {number} value - New value
   * @param {object} allValues - All current parameter values (for cross-validation)
   * @returns {object|null} Feedback object or null if valid
   */
  validate(template, parameter, value, allValues = {}) {
    const constraints = PHYSICS_CONSTRAINTS[template];
    if (!constraints) return null;

    const paramConstraints = constraints[parameter];
    if (!paramConstraints) return null;

    // Check minimum constraint
    if (paramConstraints.min !== undefined && value < paramConstraints.min) {
      return this._createFeedback(
        paramConstraints.errorBelow || {
          message: `Value must be at least ${paramConstraints.min}`,
          type: VALIDATION_STATUS.ERROR,
        },
        template,
        parameter,
        value
      );
    }

    // Check maximum constraint
    if (paramConstraints.max !== undefined && value > paramConstraints.max) {
      return this._createFeedback(
        paramConstraints.errorAbove || {
          message: `Value must be at most ${paramConstraints.max}`,
          type: VALIDATION_STATUS.ERROR,
        },
        template,
        parameter,
        value
      );
    }

    // Check zero/low value warnings
    if (value === 0 && paramConstraints.warningZero) {
      return this._createFeedback(paramConstraints.warningZero, template, parameter, value);
    }

    if (paramConstraints.warningLow && value < paramConstraints.warningLow.threshold && value > 0) {
      return this._createFeedback(paramConstraints.warningLow, template, parameter, value);
    }

    // Check high value warnings
    if (paramConstraints.warningHigh && value > paramConstraints.warningHigh.threshold) {
      return this._createFeedback(paramConstraints.warningHigh, template, parameter, value);
    }

    // Check specific threshold hints
    const thresholdHints = ['hintMoon', 'hintEarth', 'hintNeutral', 'warningAt45', 'hintAbsoluteZero'];
    for (const hintKey of thresholdHints) {
      const hint = paramConstraints[hintKey];
      if (hint && hint.threshold !== undefined) {
        const tolerance = hint.tolerance || 0.1;
        if (Math.abs(value - hint.threshold) <= tolerance) {
          return this._createFeedback(hint, template, parameter, value);
        }
      }
    }

    // Check range hints
    const rangeHints = ['hintAudible', 'hintAcid', 'hintBase'];
    for (const hintKey of rangeHints) {
      const hint = paramConstraints[hintKey];
      if (hint && hint.range) {
        if (value >= hint.range[0] && value <= hint.range[1]) {
          // Only show range hints occasionally (not on every change)
          if (Math.random() < 0.1) { // 10% chance
            return this._createFeedback(hint, template, parameter, value);
          }
        }
      }
    }

    return null; // Valid, no feedback needed
  }

  /**
   * Validate all parameters at once
   * @param {string} template - Template type
   * @param {object} values - All parameter values
   * @returns {object|null} First feedback found or null
   */
  validateAll(template, values) {
    for (const [parameter, value] of Object.entries(values)) {
      const feedback = this.validate(template, parameter, value, values);
      if (feedback && feedback.status !== VALIDATION_STATUS.HINT) {
        return feedback; // Return first error/warning
      }
    }
    return null;
  }

  /**
   * Cross-validate related parameters
   * @param {string} template - Template type
   * @param {object} values - All parameter values
   * @returns {object|null} Cross-validation feedback
   */
  crossValidate(template, values) {
    // Projectile: angle + velocity combination
    if (template === 'projectile') {
      if (values.angle === 90 && values.velocity > 0) {
        return this._createFeedback({
          message: "🎯 90° = straight up! The ball will come right back down.",
          hindiMessage: "90° = सीधे ऊपर! गेंद वापस नीचे आएगी।",
          type: VALIDATION_STATUS.HINT,
        }, template, 'angle', values.angle);
      }
    }

    // Race: friction + curve combination
    if (template === 'race_comparison') {
      if (values.friction === 0 && values.curve_radius && values.curve_radius > 0) {
        return this._createFeedback({
          message: "💥 No friction + curved road = Car flies off tangentially!",
          hindiMessage: "शून्य घर्षण + मुड़ी सड़क = कार स्पर्शरेखा पर उड़ जाएगी!",
          type: VALIDATION_STATUS.ERROR,
          visualOverride: { animation: 'car_tangent_fly' },
          mentorMessage: "Centripetal force needs friction! Without it, inertia wins.",
        }, template, 'friction', 0);
      }
    }

    // Wave: frequency + wavelength = speed of light check
    if (template === 'wave' && values.frequency && values.wavelength) {
      const speed = values.frequency * values.wavelength;
      if (speed > 3e8) {
        return this._createFeedback({
          message: "⚡ That's faster than light! Nothing can travel at c = 3×10⁸ m/s.",
          hindiMessage: "यह प्रकाश से तेज है! कुछ भी c = 3×10⁸ m/s से तेज नहीं जा सकता।",
          type: VALIDATION_STATUS.WARNING,
        }, template, 'wave_speed', speed);
      }
    }

    return null;
  }

  /**
   * Create a feedback object
   */
  _createFeedback(constraint, template, parameter, value) {
    // Check cooldown to prevent spam
    const now = Date.now();
    if (now - this.lastFeedbackTime < this.cooldownMs) {
      // Only allow errors to bypass cooldown
      if (constraint.type !== VALIDATION_STATUS.ERROR) {
        return null;
      }
    }

    this.lastFeedbackTime = now;

    const feedback = {
      status: constraint.type || VALIDATION_STATUS.WARNING,
      message: constraint.message,
      hindiMessage: constraint.hindiMessage,
      parameter,
      value,
      template,
      timestamp: now,
      
      // Toast configuration
      toast: {
        type: constraint.type === VALIDATION_STATUS.ERROR ? 'error' : 
              constraint.type === VALIDATION_STATUS.WARNING ? 'warning' : 'info',
        duration: constraint.type === VALIDATION_STATUS.HINT ? 3000 : 5000,
        icon: this._getIcon(constraint.type),
      },

      // Visual override (if any)
      visualOverride: constraint.visualOverride || null,

      // Ghost Mentor message (if any)
      mentorMessage: constraint.mentorMessage || null,
    };

    // Store in history
    this.feedbackHistory.push(feedback);
    if (this.feedbackHistory.length > 50) {
      this.feedbackHistory.shift();
    }

    this.lastFeedback = feedback;
    return feedback;
  }

  /**
   * Get appropriate icon for feedback type
   */
  _getIcon(type) {
    switch (type) {
      case VALIDATION_STATUS.ERROR: return '🚫';
      case VALIDATION_STATUS.WARNING: return '⚠️';
      case VALIDATION_STATUS.HINT: return '💡';
      default: return 'ℹ️';
    }
  }

  /**
   * Get educational explanation for a constraint
   */
  getExplanation(template, parameter) {
    const explanations = {
      projectile: {
        angle: "The launch angle determines the shape of the trajectory. 45° gives maximum range (ignoring air resistance).",
        velocity: "Initial velocity determines how far and high the projectile goes. v² appears in both range and height formulas!",
        gravity: "Gravity pulls everything down at 9.8 m/s² on Earth. Moon has 1/6th gravity, Jupiter has 2.5× gravity!",
      },
      race_comparison: {
        velocity: "Velocity = Distance / Time. Higher velocity means covering more distance in the same time.",
        friction: "Friction provides the grip needed to change direction. Without it, objects continue in straight lines (Newton's 1st Law).",
        mass: "Mass resists acceleration. F = ma means heavier objects need more force to accelerate equally.",
      },
      wave: {
        frequency: "Frequency = oscillations per second (Hz). Higher frequency = higher pitch in sound, bluer in light.",
        wavelength: "Wavelength × Frequency = Wave Speed. Radio waves are long, X-rays are tiny!",
        amplitude: "Amplitude = maximum displacement. Bigger amplitude = louder sound, brighter light.",
      },
    };

    return explanations[template]?.[parameter] || null;
  }

  /**
   * Reset the validator state
   */
  reset() {
    this.lastFeedback = null;
    this.feedbackHistory = [];
    this.lastFeedbackTime = 0;
  }
}

// ============================================
// SINGLETON INSTANCE
// ============================================
const physicsValidator = new PhysicsValidator();

// ============================================
// EXPORTS
// ============================================
export default physicsValidator;
export { PhysicsValidator, PHYSICS_CONSTRAINTS };

// Convenience functions
export const validateParameter = (template, parameter, value, allValues) => 
  physicsValidator.validate(template, parameter, value, allValues);

export const validateAllParameters = (template, values) => 
  physicsValidator.validateAll(template, values);

export const crossValidateParameters = (template, values) => 
  physicsValidator.crossValidate(template, values);

export const getParameterExplanation = (template, parameter) => 
  physicsValidator.getExplanation(template, parameter);






