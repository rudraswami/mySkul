/**
 * Concept to TOON Mapping Utility
 * Maps concept keywords to TOON templates
 */

import { forceTOON, frictionTOON } from '../templates/force.toon';
import { motionTOON, velocityTOON, accelerationTOON } from '../templates/motion.toon';
import { gravityTOON, freeFallTOON } from '../templates/gravity.toon';

/**
 * All available TOON templates
 */
const TOON_TEMPLATES = {
  // Force related
  force: forceTOON,
  friction: frictionTOON,
  'newton': forceTOON, // Newton's laws relate to force
  'push': forceTOON,
  'pull': forceTOON,
  
  // Motion related
  motion: motionTOON,
  velocity: velocityTOON,
  speed: motionTOON,
  acceleration: accelerationTOON,
  
  // Gravity related
  gravity: gravityTOON,
  gravitation: gravityTOON,
  'free fall': freeFallTOON,
  freefall: freeFallTOON,
  'falling': gravityTOON,
  weight: gravityTOON,
  
  // Hindi keywords
  'बल': forceTOON,
  'गति': motionTOON,
  'वेग': velocityTOON,
  'त्वरण': accelerationTOON,
  'गुरुत्व': gravityTOON,
  'घर्षण': frictionTOON,
};

/**
 * Get TOON template for a concept
 * @param {string} concept - Concept name or keyword
 * @returns {Object|null} TOON template or null if not found
 */
export function getTOONTemplateForConcept(concept) {
  if (!concept) return null;
  
  const lowerConcept = concept.toLowerCase().trim();
  
  // Direct match
  if (TOON_TEMPLATES[lowerConcept]) {
    return TOON_TEMPLATES[lowerConcept];
  }
  
  // Check if any keyword is contained in the concept
  for (const [key, template] of Object.entries(TOON_TEMPLATES)) {
    if (lowerConcept.includes(key)) {
      return template;
    }
  }
  
  return null;
}

/**
 * Generate TOON from concept name with context
 * @param {string} concept - Concept name
 * @param {Object} context - Student context (language, region, etc.)
 * @returns {Object} TOON configuration
 */
export function generateTOONFromConcept(concept, context = {}) {
  const template = getTOONTemplateForConcept(concept);
  
  if (template) {
    return {
      ...template,
      language: context.language || 'hinglish',
      region: context.region || 'north',
    };
  }

  // Default generic template for unknown concepts
  return {
    topic: concept,
    scene: 'classroom',
    analogy: `Let's understand ${concept} with a simple example!`,
    actors: [
      { 
        id: 'professor', 
        type: 'professor', 
        position: { x: 0.1, y: 0.6 },
        initialState: 'explaining' 
      }
    ],
    props: [],
    labels: [
      {
        id: 'topic_label',
        text: concept,
        style: 'badge',
        x: 50,
        y: 15,
      }
    ],
    steps: [
      {
        id: 'step_1',
        title: `Understanding ${concept}`,
        animations: [],
        duration: 3000,
      }
    ],
    interactions: [],
  };
}

/**
 * Check if a template exists for a concept
 * @param {string} concept - Concept to check
 * @returns {boolean}
 */
export function hasTemplate(concept) {
  return getTOONTemplateForConcept(concept) !== null;
}

/**
 * Get all available concepts
 * @returns {string[]} List of concept names
 */
export function getAvailableConcepts() {
  return [...new Set(Object.keys(TOON_TEMPLATES))];
}

/**
 * Extract concept from a question string
 * @param {string} question - User's question
 * @returns {string|null} Extracted concept or null
 */
export function extractConceptFromQuestion(question) {
  if (!question) return null;
  
  const q = question.toLowerCase();
  
  // Priority order for concept extraction
  const conceptPriority = [
    'force', 'friction', 'motion', 'velocity', 'acceleration', 
    'gravity', 'gravitation', 'free fall', 'newton',
    'बल', 'गति', 'वेग', 'त्वरण', 'गुरुत्व', 'घर्षण'
  ];
  
  for (const concept of conceptPriority) {
    if (q.includes(concept)) {
      return concept;
    }
  }
  
  return null;
}

export default getTOONTemplateForConcept;
