/**
 * 🎨 RESPONSE FORMATTER V2.0
 * ==========================
 * 
 * Transforms plain AI responses into engaging, structured content.
 * 
 * Features:
 * - Auto-detects sections from AI response
 * - Adds gamification elements
 * - Generates memory hooks
 * - Adds Indian context
 * - Creates quick recall cards
 * 
 * Input: Plain text or structured AI response
 * Output: Enhanced response object for AdaptiveResponseCard
 */

import React, { useMemo } from 'react';
import AdaptiveResponseCard from './AdaptiveResponseCard';

// Section detection patterns
const SECTION_PATTERNS = {
  definition: /(?:what is|definition|meaning|साधारण भाषा में)/i,
  formula: /(?:formula|equation|सूत्र|=|→)/i,
  steps: /(?:steps?|process|procedure|how to)/i,
  example: /(?:example|for instance|जैसे कि|like a)/i,
  important: /(?:important|key|crucial|must remember|याद रखें)/i,
  mistake: /(?:mistake|wrong|error|don't|avoid|गलती)/i,
};

// Indian context examples database
const INDIAN_CONTEXT_DB = {
  photosynthesis: [
    {
      emoji: '🥭',
      title: 'Mango Tree in your backyard',
      description: 'Just like how your Aam ka ped makes sweet mangoes using sunlight, all plants make food through photosynthesis!',
    },
    {
      emoji: '🌾',
      title: 'Rice fields of Punjab',
      description: 'The golden wheat and rice that becomes your roti - all made through photosynthesis!',
    },
  ],
  force: [
    {
      emoji: '🏏',
      title: 'Dhoni hitting a six',
      description: 'When MS Dhoni hits the ball, he applies FORCE. More force = ball goes farther!',
    },
    {
      emoji: '🛺',
      title: 'Auto rickshaw push start',
      description: 'Ever pushed an auto to start it? That\'s you applying force!',
    },
  ],
  velocity: [
    {
      emoji: '🚂',
      title: 'Rajdhani Express',
      description: 'Rajdhani travels at 130 km/h velocity. That\'s 130 km covered every hour in a specific direction!',
    },
  ],
  cell: [
    {
      emoji: '🏭',
      title: 'Mitochondria = Reliance Power Plant',
      description: 'Just like Reliance generates electricity for Mumbai, mitochondria generates energy (ATP) for the cell!',
    },
  ],
  gravity: [
    {
      emoji: '🍎',
      title: 'Apple falling in Shimla',
      description: 'When apple falls from tree in Shimla orchards - that\'s gravity pulling it down at 9.8 m/s²!',
    },
  ],
};

// Memory hooks database
const MEMORY_HOOKS_DB = {
  photosynthesis: {
    mnemonic: 'Plants COOK food: CO₂ + O₂ + (K)Light → Food',
    analogy: 'Plants are like solar-powered kitchens. Sun = stove, CO₂ = ingredients, Glucose = cooked food!',
    story: 'Imagine a tiny chef (chloroplast) inside every leaf, cooking glucose using sunlight as fuel and CO₂ as ingredients.',
  },
  force: {
    mnemonic: 'F = Ma (Fatima = Mass × Acceleration)',
    analogy: 'Force is like a bully - the bigger the mass, the harder you need to push!',
  },
  velocity: {
    mnemonic: 'V = D/T (Very = Distance/Time)',
    analogy: 'Velocity is like your Google Maps showing "ETA 2 hours for 100 km" - that\'s 50 km/h velocity!',
  },
  cell: {
    mnemonic: 'CELL = Can Every Living (thing) Live without it? NO!',
    analogy: 'Cell is like a mini factory - nucleus is the boss, mitochondria is the power department!',
  },
};

// Topper tips database
const TOPPER_TIPS_DB = {
  photosynthesis: [
    {
      content: 'Always draw the diagram! Examiners give 1 mark just for a neat labeled diagram.',
      source: 'NEET AIR 156 (2023)',
    },
    {
      content: 'Remember: Light reaction in THYLAKOID, Dark reaction in STROMA. This is asked every year!',
      source: 'JEE Advanced Topper',
    },
  ],
  force: [
    {
      content: 'In numericals, always write the formula first, then substitute values. You get marks for steps!',
      source: 'JEE AIR 89',
    },
  ],
  default: [
    {
      content: 'Revise this topic 3 times - Day 1, Day 3, Day 7. You\'ll never forget!',
      source: 'Topper Strategy',
    },
  ],
};

// Common mistakes database
const COMMON_MISTAKES_DB = {
  photosynthesis: [
    {
      wrong: 'Photosynthesis happens at night',
      correct: 'Photosynthesis only happens in presence of light (day time)',
    },
    {
      wrong: 'Plants only release oxygen',
      correct: 'Plants release O₂ during day (photosynthesis) and CO₂ at night (respiration)',
    },
    {
      wrong: 'CO₂ is released as product',
      correct: 'CO₂ is a REACTANT, O₂ is the product along with glucose',
    },
  ],
  force: [
    {
      wrong: 'Force and mass are same thing',
      correct: 'Force = mass × acceleration. Mass is constant, Force depends on acceleration',
    },
  ],
  velocity: [
    {
      wrong: 'Speed and velocity are same',
      correct: 'Speed is scalar (no direction), Velocity is vector (has direction)',
    },
  ],
};

// Quick recall cards generator
const generateQuickRecallCards = (topic) => {
  const cardsDB = {
    photosynthesis: [
      { question: 'What is the formula for photosynthesis?', answer: '6CO₂ + 6H₂O + Light → C₆H₁₂O₆ + 6O₂' },
      { question: 'Where does photosynthesis occur?', answer: 'In chloroplasts (specifically in chlorophyll)' },
      { question: 'What are the products?', answer: 'Glucose (C₆H₁₂O₆) and Oxygen (O₂)' },
      { question: 'What are the reactants?', answer: 'Carbon dioxide (CO₂), Water (H₂O), and Light energy' },
    ],
    force: [
      { question: 'What is the formula for Force?', answer: 'F = m × a (mass × acceleration)' },
      { question: 'What is the SI unit of Force?', answer: 'Newton (N)' },
      { question: 'What happens when F = 0?', answer: 'Object stays at rest or moves with constant velocity' },
    ],
    velocity: [
      { question: 'Formula for velocity?', answer: 'v = d/t (displacement/time)' },
      { question: 'Velocity vs Speed?', answer: 'Velocity has direction (vector), Speed doesn\'t (scalar)' },
      { question: 'SI unit of velocity?', answer: 'm/s (meters per second)' },
    ],
    default: [
      { question: 'Did you understand this concept?', answer: 'Review it once more if not sure!' },
    ],
  };

  return cardsDB[topic.toLowerCase()] || cardsDB.default;
};

// Main formatter function
export const formatResponse = (rawResponse, topic = 'general', subject = 'science') => {
  const topicLower = topic.toLowerCase().replace(/\s+/g, '_');

  // Build enhanced response object
  const enhancedResponse = {
    // Hook - Attention grabber
    hook: {
      text: rawResponse.hook || `Let's master ${topic} together! This is a favorite topic in exams. 🎯`,
      emoji: subject === 'biology' ? '🌿' : subject === 'physics' ? '⚡' : subject === 'chemistry' ? '🧪' : '📚',
    },

    // Definition
    definition: rawResponse.definition || {
      title: `What is ${topic}?`,
      content: rawResponse.mainContent || 'Loading...',
      hindiTerm: rawResponse.hindiTerm || '',
    },

    // Formula (if applicable)
    formula: rawResponse.formula || null,

    // Steps (if applicable)
    steps: rawResponse.steps || null,

    // Exam Focus
    examFocus: {
      points: rawResponse.keyPoints || [
        'This is frequently asked in exams',
        'Memorize the formula',
        'Practice numerical problems',
      ],
      marksBreakdown: rawResponse.marksBreakdown || [
        { topic: 'Definition', marks: 2 },
        { topic: 'Formula', marks: 1 },
        { topic: 'Diagram', marks: 2 },
      ],
    },

    // Memory Hook
    memory: MEMORY_HOOKS_DB[topicLower] || {
      mnemonic: 'Create your own memory trick!',
      analogy: 'Think of a real-life example that connects to this concept.',
    },

    // Indian Context
    indianContext: {
      examples: INDIAN_CONTEXT_DB[topicLower] || [
        {
          emoji: '🇮🇳',
          title: 'Connect to daily life',
          description: 'Think about how this concept applies to things around you!',
        },
      ],
    },

    // Common Mistakes
    commonMistakes: {
      items: COMMON_MISTAKES_DB[topicLower] || [
        {
          wrong: 'Rushing through the concept',
          correct: 'Take time to understand each part properly',
        },
      ],
    },

    // Topper Tips
    topperTips: {
      items: TOPPER_TIPS_DB[topicLower] || TOPPER_TIPS_DB.default,
    },

    // Quick Recall Cards
    quickRecall: {
      cards: generateQuickRecallCards(topicLower),
    },

    // XP and Progress
    xp: 15,
    progress: 65,
    streak: 3,
  };

  return enhancedResponse;
};

// React component wrapper
const ResponseFormatter = ({
  rawResponse,
  topic = 'general',
  subject = 'science',
  showProgress = true,
}) => {
  const formattedResponse = useMemo(
    () => formatResponse(rawResponse, topic, subject),
    [rawResponse, topic, subject]
  );

  return (
    <AdaptiveResponseCard
      response={formattedResponse}
      showProgress={showProgress}
    />
  );
};

export default ResponseFormatter;

