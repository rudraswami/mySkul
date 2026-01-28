/**
 * 🎬 DEMO INTERCEPTOR
 * ===================
 * 
 * Catches specific demo questions and routes them to hardcoded premium visuals.
 * This ensures 100% reliability for VC demos - no LLM calls, no failures.
 * 
 * @author Netra Team
 * @version 1.0.0 (VC Demo)
 */

// Demo question patterns (fuzzy matching for variations)
const DEMO_QUESTIONS = {
  CIRCUIT: {
    id: 'circuit_electricity',
    patterns: [
      'electricity flows in a circuit',
      'electricity flow in circuit',
      'how electricity flows',
      'electric circuit',
      'circuit with visual',
      'electricity in a circuit',
      'current flows in circuit',
      'electric current flow',
    ],
    title: 'Electricity Flow in a Circuit',
    subject: 'physics',
  },
  PHOTOSYNTHESIS: {
    id: 'photosynthesis',
    patterns: [
      'photosynthesis',
      'photo synthesis',
      'plant makes food',
      'plants make glucose',
      'chlorophyll',
      'sunlight to food',
    ],
    title: 'Photosynthesis',
    subject: 'biology',
  },
};

/**
 * Normalize question for matching
 */
function normalizeQuestion(question) {
  return question
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Check if question matches a demo pattern
 */
function matchesDemoQuestion(question, demoConfig) {
  const normalized = normalizeQuestion(question);
  return demoConfig.patterns.some(pattern => normalized.includes(pattern));
}

/**
 * Get demo visual config if question matches
 * @param {string} question - User's question
 * @returns {object|null} - Demo config or null if not a demo question
 */
export function getDemoConfig(question) {
  if (!question) return null;
  
  // Check Circuit question
  if (matchesDemoQuestion(question, DEMO_QUESTIONS.CIRCUIT)) {
    console.log('🎬 [DEMO] Matched: Circuit Electricity Visual');
    return {
      ...DEMO_QUESTIONS.CIRCUIT,
      visualType: 'circuit',
      question: question,
    };
  }
  
  // Check Photosynthesis question
  if (matchesDemoQuestion(question, DEMO_QUESTIONS.PHOTOSYNTHESIS)) {
    console.log('🎬 [DEMO] Matched: Photosynthesis Visual');
    return {
      ...DEMO_QUESTIONS.PHOTOSYNTHESIS,
      visualType: 'photosynthesis',
      question: question,
    };
  }
  
  return null;
}

/**
 * Check if a question should use demo visual
 */
export function isDemoQuestion(question) {
  return getDemoConfig(question) !== null;
}

/**
 * Get all available demo questions for testing
 */
export function getAvailableDemoQuestions() {
  return [
    {
      question: 'Explain how electricity flows in a circuit with a visual',
      type: 'circuit',
      subject: 'physics',
    },
    {
      question: 'Explain photosynthesis with a visual',
      type: 'photosynthesis',
      subject: 'biology',
    },
  ];
}

export default {
  getDemoConfig,
  isDemoQuestion,
  getAvailableDemoQuestions,
  DEMO_QUESTIONS,
};
