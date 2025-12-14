/**
 * 🧠 INTENT CLASSIFIER
 * ====================
 * 
 * The core reasoning layer that analyzes question structure to determine
 * COGNITIVE INTENT - not just topic, but HOW the student wants to understand.
 * 
 * This is subject-agnostic: the same classifier works for physics, chemistry,
 * biology, math, history, or any domain.
 * 
 * Key Insight: "Explain friction" vs "What if no friction" vs "Compare frictions"
 * have the SAME topic but DIFFERENT intents, requiring DIFFERENT visuals.
 */

// ============================================
// INTENT TYPES (Subject-Agnostic)
// ============================================

export const INTENT_TYPES = {
  // Core understanding intents
  CONCEPTUAL: 'conceptual',           // "explain", "what is", "describe"
  CAUSAL_INQUIRY: 'causal_inquiry',   // "why", "how come", "what causes"
  MECHANISTIC: 'mechanistic',         // "how does", "how works", "mechanism"
  
  // Reasoning intents
  COUNTERFACTUAL: 'counterfactual',   // "what if", "without", "imagine no"
  COMPARATIVE: 'comparative',          // "compare", "vs", "difference between"
  CLASSIFICATORY: 'classificatory',    // "types of", "kinds of", "categories"
  
  // Temporal/Process intents
  TEMPORAL: 'temporal',                // "what happens when", "over time", "process"
  SEQUENTIAL: 'sequential',            // "steps", "stages", "sequence"
  
  // Intuitive/Creative intents
  INTUITIVE: 'intuitive',              // "intuitively", "simply", "like", "imagine"
  ANALOGICAL: 'analogical',            // "similar to", "like", "analogy"
  
  // Quantitative intents
  QUANTITATIVE: 'quantitative',        // "calculate", "how much", "value of"
  RELATIONAL: 'relational',            // "relationship between", "depends on"
  
  // Edge case intents
  EDGE_CASE: 'edge_case',              // "fails", "limit", "extreme", "breaks"
  BOUNDARY: 'boundary',                // "maximum", "minimum", "threshold"
};

// ============================================
// INTENT DETECTION PATTERNS
// ============================================

/**
 * Multi-signal detection patterns for each intent type.
 * Each pattern has:
 * - keywords: words/phrases that indicate this intent
 * - questionStarters: how questions typically begin
 * - structuralPatterns: sentence structure indicators
 * - weight: relative importance of this signal
 */
const INTENT_PATTERNS = {
  [INTENT_TYPES.CONCEPTUAL]: {
    keywords: [
      'explain', 'what is', 'what are', 'describe', 'tell me about',
      'define', 'meaning of', 'understand', 'basics of', 'introduction to',
      'concept of', 'idea of', 'about', 'overview',
    ],
    questionStarters: ['what is', 'what are', 'explain', 'describe'],
    structuralPatterns: [/^explain\s/i, /^what\s+is\s/i, /^describe\s/i],
    weight: 1.0,
  },
  
  [INTENT_TYPES.CAUSAL_INQUIRY]: {
    keywords: [
      'why', 'how come', 'what causes', 'reason for', 'because of',
      'leads to', 'results in', 'due to', 'cause of', 'origin of',
      'source of', 'root cause', 'underlying',
    ],
    questionStarters: ['why', 'how come', 'what causes'],
    structuralPatterns: [/^why\s/i, /what\s+causes/i, /reason\s+for/i],
    weight: 1.2, // Higher weight - more specific intent
  },
  
  [INTENT_TYPES.MECHANISTIC]: {
    keywords: [
      'how does', 'how do', 'how works', 'mechanism', 'process of',
      'works', 'functions', 'operates', 'way it works',
    ],
    questionStarters: ['how does', 'how do', 'how is'],
    structuralPatterns: [/^how\s+does/i, /^how\s+do/i, /mechanism/i],
    weight: 1.1,
  },
  
  [INTENT_TYPES.COUNTERFACTUAL]: {
    keywords: [
      'what if', 'without', 'imagine', 'suppose', 'if there was no',
      'in absence of', 'if we remove', 'hypothetically', 'what would happen',
      'alternate', 'if not', 'no longer',
    ],
    questionStarters: ['what if', 'imagine', 'suppose', 'without'],
    structuralPatterns: [/what\s+if/i, /without\s+\w+/i, /if\s+there\s+was\s+no/i],
    weight: 1.5, // High weight - very specific visual form needed
  },
  
  [INTENT_TYPES.COMPARATIVE]: {
    keywords: [
      'compare', 'versus', 'vs', 'difference between', 'different from',
      'similar to', 'contrast', 'distinguish', 'better than', 'worse than',
      'same as', 'unlike', 'whereas', 'while', 'both',
    ],
    questionStarters: ['compare', 'what is the difference'],
    structuralPatterns: [/compare\s/i, /vs\.?\s/i, /difference\s+between/i, /\svs\s/i],
    weight: 1.4,
  },
  
  [INTENT_TYPES.CLASSIFICATORY]: {
    keywords: [
      'types of', 'kinds of', 'categories', 'classification', 'forms of',
      'varieties', 'classes of', 'groups of', 'list', 'all the',
    ],
    questionStarters: ['what types', 'what kinds', 'how many types'],
    structuralPatterns: [/types\s+of/i, /kinds\s+of/i, /categories\s+of/i],
    weight: 1.3,
  },
  
  [INTENT_TYPES.TEMPORAL]: {
    keywords: [
      'what happens when', 'over time', 'changes', 'evolves', 'timeline',
      'before', 'after', 'during', 'sequence of events', 'progression',
      'history of', 'development of',
    ],
    questionStarters: ['what happens', 'when does', 'how long'],
    structuralPatterns: [/what\s+happens\s+when/i, /over\s+time/i, /timeline/i],
    weight: 1.2,
  },
  
  [INTENT_TYPES.SEQUENTIAL]: {
    keywords: [
      'steps', 'stages', 'phases', 'procedure', 'process', 'how to',
      'step by step', 'first', 'then', 'finally', 'order of',
    ],
    questionStarters: ['how to', 'what are the steps'],
    structuralPatterns: [/steps?\s+to/i, /how\s+to/i, /process\s+of/i],
    weight: 1.2,
  },
  
  [INTENT_TYPES.INTUITIVE]: {
    keywords: [
      'intuitively', 'simply', 'easy to understand', 'in simple terms',
      'like', 'imagine', 'picture', 'visualize', 'feel', 'sense',
      'basically', 'essentially', 'everyday', 'real life',
    ],
    questionStarters: ['can you show', 'help me visualize'],
    structuralPatterns: [/intuitively/i, /simple\s+terms/i, /easy\s+to\s+understand/i],
    weight: 1.3,
  },
  
  [INTENT_TYPES.ANALOGICAL]: {
    keywords: [
      'like', 'similar to', 'analogy', 'metaphor', 'think of it as',
      'comparable to', 'reminds me of', 'same as', 'equivalent to',
    ],
    questionStarters: ['is it like', 'what is it similar to'],
    structuralPatterns: [/like\s+a\s/i, /similar\s+to/i, /analogy/i],
    weight: 1.2,
  },
  
  [INTENT_TYPES.QUANTITATIVE]: {
    keywords: [
      'calculate', 'how much', 'value of', 'formula', 'equation',
      'compute', 'solve', 'find', 'determine', 'measure', 'quantity',
      'number', 'amount',
    ],
    questionStarters: ['calculate', 'how much', 'what is the value'],
    structuralPatterns: [/calculate/i, /how\s+much/i, /value\s+of/i, /formula\s+for/i],
    weight: 1.3,
  },
  
  [INTENT_TYPES.RELATIONAL]: {
    keywords: [
      'relationship between', 'depends on', 'affects', 'influences',
      'proportional', 'inversely', 'related to', 'connection between',
      'how does X affect Y',
    ],
    questionStarters: ['what is the relationship', 'how does X affect'],
    structuralPatterns: [/relationship\s+between/i, /depends\s+on/i, /affects?\s/i],
    weight: 1.2,
  },
  
  [INTENT_TYPES.EDGE_CASE]: {
    keywords: [
      'fails', 'breaks', 'limit', 'extreme', 'exception', 'special case',
      'edge case', 'boundary', 'when does it not work', 'limitations',
    ],
    questionStarters: ['when does', 'what if it fails'],
    structuralPatterns: [/fails?\s/i, /breaks?\s/i, /limit\s+of/i, /extreme/i],
    weight: 1.4,
  },
  
  [INTENT_TYPES.BOUNDARY]: {
    keywords: [
      'maximum', 'minimum', 'threshold', 'limit', 'boundary', 'peak',
      'highest', 'lowest', 'most', 'least', 'optimal', 'critical point',
    ],
    questionStarters: ['what is the maximum', 'what is the minimum'],
    structuralPatterns: [/maximum/i, /minimum/i, /threshold/i, /limit/i],
    weight: 1.2,
  },
};

// ============================================
// INTENT CLASSIFIER CLASS
// ============================================

export class IntentClassifier {
  constructor(options = {}) {
    this.options = {
      defaultIntent: INTENT_TYPES.CONCEPTUAL, // Safe fallback
      confidenceThreshold: 0.3,               // Minimum to consider an intent
      enableSecondary: true,                  // Detect secondary intent
      ...options,
    };
  }
  
  /**
   * Classify the cognitive intent of a question
   * @param {string} question - The student's question
   * @returns {Object} Classification result with primary/secondary intent and confidence
   */
  classify(question) {
    if (!question || typeof question !== 'string') {
      console.warn('⚠️ [IntentClassifier] Invalid question, using default');
      return this.createResult(this.options.defaultIntent, 0.5);
    }
    
    const normalizedQuestion = question.toLowerCase().trim();
    const scores = {};
    
    console.log('🧠 [IntentClassifier] Analyzing:', question);
    
    // Score each intent type
    for (const [intentType, patterns] of Object.entries(INTENT_PATTERNS)) {
      scores[intentType] = this.scoreIntent(normalizedQuestion, patterns);
    }
    
    // Sort by score
    const sortedIntents = Object.entries(scores)
      .sort((a, b) => b[1] - a[1])
      .filter(([_, score]) => score > 0);
    
    // Determine primary intent
    const primaryIntent = sortedIntents.length > 0 && sortedIntents[0][1] >= this.options.confidenceThreshold
      ? sortedIntents[0][0]
      : this.options.defaultIntent;
    
    const primaryScore = sortedIntents.length > 0 ? sortedIntents[0][1] : 0.5;
    
    // Determine secondary intent (if enabled and different from primary)
    let secondaryIntent = null;
    let secondaryScore = 0;
    
    if (this.options.enableSecondary && sortedIntents.length > 1) {
      const [secondType, secondScore_] = sortedIntents[1];
      if (secondScore_ >= this.options.confidenceThreshold && secondType !== primaryIntent) {
        secondaryIntent = secondType;
        secondaryScore = secondScore_;
      }
    }
    
    const result = this.createResult(primaryIntent, primaryScore, secondaryIntent, secondaryScore);
    
    console.log('🧠 [IntentClassifier] Result:', {
      primary: result.primary,
      confidence: result.confidence.toFixed(2),
      secondary: result.secondary,
    });
    
    return result;
  }
  
  /**
   * Score how well a question matches an intent pattern
   */
  scoreIntent(question, patterns) {
    let score = 0;
    
    // Keyword matching
    for (const keyword of patterns.keywords) {
      if (question.includes(keyword.toLowerCase())) {
        score += 0.3 * patterns.weight;
      }
    }
    
    // Question starter matching (higher weight)
    for (const starter of patterns.questionStarters) {
      if (question.startsWith(starter.toLowerCase())) {
        score += 0.5 * patterns.weight;
      }
    }
    
    // Structural pattern matching (highest weight)
    for (const pattern of patterns.structuralPatterns) {
      if (pattern.test(question)) {
        score += 0.6 * patterns.weight;
      }
    }
    
    return score;
  }
  
  /**
   * Create a standardized result object
   */
  createResult(primary, confidence, secondary = null, secondaryConfidence = 0) {
    return {
      primary,
      confidence: Math.min(confidence, 1.0), // Cap at 1.0
      secondary,
      secondaryConfidence,
      
      // Helper methods
      isPrimary: (intent) => primary === intent,
      hasSecondary: () => secondary !== null,
      isCounterfactual: () => primary === INTENT_TYPES.COUNTERFACTUAL,
      isComparative: () => primary === INTENT_TYPES.COMPARATIVE,
      isQuantitative: () => primary === INTENT_TYPES.QUANTITATIVE,
      
      // Get visualization hints
      getVisualizationHints: () => this.getHintsForIntent(primary, secondary),
    };
  }
  
  /**
   * Get visualization hints for an intent
   */
  getHintsForIntent(primary, secondary) {
    const hints = {
      needsComparison: [INTENT_TYPES.COMPARATIVE, INTENT_TYPES.COUNTERFACTUAL].includes(primary),
      needsTimeline: [INTENT_TYPES.TEMPORAL, INTENT_TYPES.SEQUENTIAL].includes(primary),
      needsHierarchy: [INTENT_TYPES.CLASSIFICATORY].includes(primary),
      needsMetaphor: [INTENT_TYPES.INTUITIVE, INTENT_TYPES.ANALOGICAL].includes(primary),
      needsFormula: [INTENT_TYPES.QUANTITATIVE, INTENT_TYPES.RELATIONAL].includes(primary),
      needsCausalChain: [INTENT_TYPES.CAUSAL_INQUIRY, INTENT_TYPES.MECHANISTIC].includes(primary),
      needsEdgeCase: [INTENT_TYPES.EDGE_CASE, INTENT_TYPES.BOUNDARY].includes(primary),
    };
    
    return hints;
  }
}

// ============================================
// EXPORTS
// ============================================

export function createIntentClassifier(options) {
  return new IntentClassifier(options);
}

export default IntentClassifier;

