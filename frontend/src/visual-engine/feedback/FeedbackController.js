/**
 * 📣 FEEDBACK CONTROLLER (SketchSense V5.0)
 * ==========================================
 * 
 * The Feedback Loop Architecture - Listens to all interactions
 * and triggers appropriate responses.
 * 
 * Responsibilities:
 * - Monitor state changes (sliders, clicks, drags)
 * - Track validator results
 * - Measure student time-in-mode
 * - Trigger micro-feedback
 * - Scaffold difficulty upgrades
 * - Show Ghost Mentor hints
 * 
 * Feedback Types:
 * - MICRO: Quick visual effects (shake, pulse, glow)
 * - MENTOR: Ghost Mentor message popup
 * - SCAFFOLD: Bloom's level progression
 * - CELEBRATION: Success animations
 */

// ============================================
// FEEDBACK TYPES
// ============================================
export const FEEDBACK_TYPES = {
  MICRO: 'micro',           // Quick visual feedback
  MENTOR: 'mentor',         // Ghost Mentor message
  SCAFFOLD: 'scaffold',     // Difficulty progression
  CELEBRATION: 'celebration', // Success/achievement
  HINT: 'hint',             // Learning hint
  WARNING: 'warning',       // Misconception warning
  ERROR: 'error',           // Invalid state
};

// ============================================
// MENTOR PERSONALITIES
// ============================================
export const MENTOR_PERSONAS = {
  FRIENDLY: {
    name: 'Sathi',
    avatar: '🧑‍🏫',
    style: 'friendly',
    prefixes: ['Hey!', 'Oops!', 'Great question!', 'Think about this:'],
  },
  ENCOURAGING: {
    name: 'Coach',
    avatar: '💪',
    style: 'encouraging',
    prefixes: ['You got this!', 'Almost there!', 'Keep going!', 'Nice try!'],
  },
  SCIENTIFIC: {
    name: 'Professor',
    avatar: '🔬',
    style: 'scientific',
    prefixes: ['Interesting observation:', 'Scientifically speaking:', 'Consider this:'],
  },
};

// ============================================
// FEEDBACK CONTROLLER CLASS
// ============================================
export class FeedbackController {
  constructor(options = {}) {
    this.listeners = new Map();
    this.stateHistory = [];
    this.interactionCount = 0;
    this.startTime = Date.now();
    this.currentDifficulty = options.initialDifficulty || 'recall';
    this.mentorPersona = options.mentorPersona || MENTOR_PERSONAS.FRIENDLY;
    
    // Configuration
    this.config = {
      // Time thresholds (ms)
      scaffoldUpgradeTime: 30000, // 30 seconds before suggesting upgrade
      hintDelay: 10000, // 10 seconds of inactivity before hint
      
      // Interaction thresholds
      interactionsForUnderstand: 5,
      interactionsForApply: 10,
      
      // Feedback cooldowns (ms)
      microFeedbackCooldown: 500,
      mentorCooldown: 5000,
      
      ...options.config,
    };
    
    this.lastFeedbackTime = {
      [FEEDBACK_TYPES.MICRO]: 0,
      [FEEDBACK_TYPES.MENTOR]: 0,
    };
  }
  
  // ============================================
  // EVENT SUBSCRIPTION
  // ============================================
  
  /**
   * Subscribe to feedback events
   */
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
    
    return () => this.off(eventType, callback);
  }
  
  /**
   * Unsubscribe from feedback events
   */
  off(eventType, callback) {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }
  
  /**
   * Emit feedback event
   */
  emit(eventType, data) {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (e) {
          console.error('Feedback callback error:', e);
        }
      });
    }
    
    // Also emit to 'all' listeners
    const allListeners = this.listeners.get('all');
    if (allListeners) {
      allListeners.forEach(callback => callback({ type: eventType, ...data }));
    }
  }
  
  // ============================================
  // STATE TRACKING
  // ============================================
  
  /**
   * Track state change from interactive controls
   */
  trackStateChange(parameter, oldValue, newValue, source = 'slider') {
    const timestamp = Date.now();
    
    this.stateHistory.push({
      parameter,
      oldValue,
      newValue,
      source,
      timestamp,
      sessionTime: timestamp - this.startTime,
    });
    
    this.interactionCount++;
    
    // Trim history if too long
    if (this.stateHistory.length > 100) {
      this.stateHistory = this.stateHistory.slice(-50);
    }
    
    // Check for scaffold upgrade
    this.checkScaffoldProgress();
  }
  
  /**
   * Track time spent on current visual
   */
  getTimeSpent() {
    return Date.now() - this.startTime;
  }
  
  /**
   * Reset session tracking
   */
  resetSession() {
    this.stateHistory = [];
    this.interactionCount = 0;
    this.startTime = Date.now();
  }
  
  // ============================================
  // FEEDBACK TRIGGERS
  // ============================================
  
  /**
   * Trigger micro-feedback (visual effects)
   */
  triggerMicroFeedback(effect, options = {}) {
    const now = Date.now();
    if (now - this.lastFeedbackTime[FEEDBACK_TYPES.MICRO] < this.config.microFeedbackCooldown) {
      return; // Cooldown not met
    }
    
    this.lastFeedbackTime[FEEDBACK_TYPES.MICRO] = now;
    
    this.emit(FEEDBACK_TYPES.MICRO, {
      effect, // 'shake', 'pulse', 'glow', 'skid', etc.
      duration: options.duration || 500,
      intensity: options.intensity || 1,
      targetElement: options.target,
    });
  }
  
  /**
   * Trigger Ghost Mentor message
   */
  triggerMentorMessage(message, options = {}) {
    const now = Date.now();
    if (now - this.lastFeedbackTime[FEEDBACK_TYPES.MENTOR] < this.config.mentorCooldown) {
      return; // Cooldown not met
    }
    
    this.lastFeedbackTime[FEEDBACK_TYPES.MENTOR] = now;
    
    const persona = options.persona || this.mentorPersona;
    const prefix = persona.prefixes[Math.floor(Math.random() * persona.prefixes.length)];
    
    this.emit(FEEDBACK_TYPES.MENTOR, {
      message: options.raw ? message : `${prefix} ${message}`,
      hindiMessage: options.hindiMessage,
      avatar: persona.avatar,
      name: persona.name,
      type: options.type || 'info', // 'info', 'warning', 'error', 'success'
      duration: options.duration || 5000,
      position: options.position || 'top-center',
    });
  }
  
  /**
   * Trigger hint after inactivity
   */
  triggerHint(hint, options = {}) {
    this.emit(FEEDBACK_TYPES.HINT, {
      hint,
      interactive: options.interactive || false,
      action: options.action, // Suggested action to take
    });
  }
  
  /**
   * Trigger validation warning
   */
  triggerValidationWarning(validationResult) {
    if (!validationResult || validationResult.isValid) return;
    
    // Trigger visual effect
    if (validationResult.visualEffect) {
      this.triggerMicroFeedback(validationResult.visualEffect, {
        intensity: 1.5,
      });
    }
    
    // Trigger mentor message
    if (validationResult.mentorMessage) {
      this.triggerMentorMessage(validationResult.mentorMessage, {
        hindiMessage: validationResult.hindiMessage,
        type: 'warning',
        raw: true,
      });
    }
    
    this.emit(FEEDBACK_TYPES.WARNING, validationResult);
  }
  
  /**
   * Trigger celebration on success
   */
  triggerCelebration(achievement, options = {}) {
    this.emit(FEEDBACK_TYPES.CELEBRATION, {
      achievement,
      message: options.message || 'Great job! 🎉',
      points: options.points || 0,
      badge: options.badge,
      animation: options.animation || 'confetti',
    });
    
    this.triggerMentorMessage(options.message || 'You did it!', {
      type: 'success',
      raw: true,
    });
  }
  
  // ============================================
  // SCAFFOLD PROGRESSION
  // ============================================
  
  /**
   * Check if student is ready for difficulty upgrade
   */
  checkScaffoldProgress() {
    const timeSpent = this.getTimeSpent();
    const interactions = this.interactionCount;
    
    let suggestedLevel = this.currentDifficulty;
    
    // Check progression criteria
    if (this.currentDifficulty === 'recall') {
      if (interactions >= this.config.interactionsForUnderstand || 
          timeSpent >= this.config.scaffoldUpgradeTime) {
        suggestedLevel = 'understand';
      }
    } else if (this.currentDifficulty === 'understand') {
      if (interactions >= this.config.interactionsForApply || 
          timeSpent >= this.config.scaffoldUpgradeTime * 2) {
        suggestedLevel = 'apply';
      }
    }
    
    if (suggestedLevel !== this.currentDifficulty) {
      this.suggestScaffoldUpgrade(suggestedLevel);
    }
  }
  
  /**
   * Suggest scaffold level upgrade
   */
  suggestScaffoldUpgrade(newLevel) {
    this.emit(FEEDBACK_TYPES.SCAFFOLD, {
      currentLevel: this.currentDifficulty,
      suggestedLevel: newLevel,
      message: this.getScaffoldMessage(newLevel),
      autoUpgrade: false, // Let parent component decide
    });
  }
  
  /**
   * Confirm scaffold upgrade
   */
  upgradeScaffold(newLevel) {
    const oldLevel = this.currentDifficulty;
    this.currentDifficulty = newLevel;
    
    this.triggerCelebration('level_up', {
      message: `Leveled up to ${newLevel}! 🚀`,
    });
    
    return { oldLevel, newLevel };
  }
  
  /**
   * Get scaffold progression message
   */
  getScaffoldMessage(level) {
    const messages = {
      understand: "You're doing great! Ready to see how everything connects?",
      apply: "Excellent progress! Let's try some interactive simulations!",
    };
    return messages[level] || "Keep learning!";
  }
  
  // ============================================
  // ANALYTICS
  // ============================================
  
  /**
   * Get interaction analytics
   */
  getAnalytics() {
    const timeSpent = this.getTimeSpent();
    const interactionRate = this.interactionCount / (timeSpent / 1000); // per second
    
    // Analyze parameter usage
    const parameterUsage = {};
    this.stateHistory.forEach(entry => {
      parameterUsage[entry.parameter] = (parameterUsage[entry.parameter] || 0) + 1;
    });
    
    return {
      timeSpent,
      interactionCount: this.interactionCount,
      interactionRate,
      currentDifficulty: this.currentDifficulty,
      parameterUsage,
      mostUsedParameter: Object.entries(parameterUsage)
        .sort((a, b) => b[1] - a[1])[0]?.[0] || null,
    };
  }
}

// ============================================
// SINGLETON INSTANCE
// ============================================
let feedbackInstance = null;

export function getFeedbackController(options = {}) {
  if (!feedbackInstance) {
    feedbackInstance = new FeedbackController(options);
  }
  return feedbackInstance;
}

export function resetFeedbackController(options = {}) {
  feedbackInstance = new FeedbackController(options);
  return feedbackInstance;
}

// Default export
export default FeedbackController;


