/**
 * 🧬 BIOLOGY VALIDATOR
 * =====================
 * 
 * Validates biology concepts
 * - Blood flow direction
 * - Organ functions
 * - Cell processes
 * - Ecosystem relationships
 */

import { BaseValidator, VALIDATION_STATUS, FEEDBACK_TYPE } from './BaseValidator';

// ============================================
// BIOLOGY DATA
// ============================================

const BLOOD_FLOW = {
  heart: {
    right_atrium: ['right_ventricle'],
    right_ventricle: ['lungs'],
    lungs: ['left_atrium'],
    left_atrium: ['left_ventricle'],
    left_ventricle: ['body'],
    body: ['right_atrium'],
  },
};

const CELL_ORGANELLES = {
  nucleus: { function: 'genetic_control' },
  mitochondria: { function: 'energy_production' },
  ribosome: { function: 'protein_synthesis' },
  chloroplast: { function: 'photosynthesis', cellType: 'plant' },
  cell_wall: { cellType: 'plant' },
};

// ============================================
// BIOLOGY VALIDATOR
// ============================================

export class BiologyValidator extends BaseValidator {
  constructor(options = {}) {
    super({ subject: 'biology', ...options });
    this.initializeRules();
  }
  
  /**
   * Initialize biology validation rules
   */
  initializeRules() {
    // Rule 1: Blood flow direction
    this.addRule({
      id: 'blood_flow_direction',
      name: 'Blood Flow Direction',
      description: 'Blood must flow in the correct direction',
      check: (value, context) => {
        if (context.property === 'bloodFlow' && context.from && context.to) {
          const validTargets = BLOOD_FLOW.heart[context.from];
          return validTargets && validTargets.includes(context.to);
        }
        return true;
      },
      message: (value, context) => `Blood cannot flow from ${context.from} to ${context.to}! ❤️ Check circulatory system diagram.`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
      suggestion: (value, context) => {
        const correct = BLOOD_FLOW.heart[context.from];
        return correct ? `Blood from ${context.from} goes to: ${correct.join(', ')}` : 'Check the path.';
      },
    });
    
    // Rule 2: Plant cells vs animal cells
    this.addRule({
      id: 'cell_type_organelle',
      name: 'Cell Type Organelle',
      description: 'Certain organelles only exist in specific cell types',
      check: (value, context) => {
        if (context.property === 'organelle' && context.cellType) {
          const organelleData = CELL_ORGANELLES[value];
          if (organelleData && organelleData.cellType) {
            return organelleData.cellType === context.cellType;
          }
        }
        return true;
      },
      message: (value, context) => {
        const organelleData = CELL_ORGANELLES[value];
        return `${value} only exists in ${organelleData?.cellType} cells! 🌱 ${context.cellType} cells don't have this.`;
      },
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
    });
    
    // Rule 3: pH of blood
    this.addRule({
      id: 'blood_ph',
      name: 'Blood pH Range',
      description: 'Human blood pH must be 7.35-7.45',
      check: (value, context) => {
        if (context.property === 'pH' && context.fluid === 'blood') {
          return value >= 7.35 && value <= 7.45;
        }
        return true;
      },
      message: (value) => `Blood pH = ${value.toFixed(2)} is dangerous! 🩸 Normal blood pH is 7.35-7.45 (slightly alkaline).`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
      suggestion: () => 'Blood pH outside this range causes acidosis or alkalosis (life-threatening).',
    });
    
    // Rule 4: Temperature for humans
    this.addRule({
      id: 'body_temperature',
      name: 'Body Temperature',
      description: 'Human body temperature should be around 37°C',
      check: (value, context) => {
        if (context.property === 'temperature' && context.organism === 'human') {
          return value >= 36 && value <= 38;
        }
        return true;
      },
      message: (value) => `Body temperature ${value.toFixed(1)}°C is abnormal! 🌡️ Normal is 36-38°C (96.8-100.4°F).`,
      severity: VALIDATION_STATUS.WARNING,
      feedback: FEEDBACK_TYPE.GHOST_MENTOR,
      suggestion: (value) => {
        if (value < 36) return 'Below 36°C indicates hypothermia.';
        return 'Above 38°C indicates fever.';
      },
    });
    
    // Rule 5: Photosynthesis inputs/outputs
    this.addRule({
      id: 'photosynthesis_equation',
      name: 'Photosynthesis Equation',
      description: 'Photosynthesis: CO2 + H2O + light → glucose + O2',
      check: (value, context) => {
        if (context.process === 'photosynthesis' && context.property === 'product') {
          const validProducts = ['glucose', 'oxygen', 'O2'];
          return validProducts.includes(value);
        }
        return true;
      },
      message: (value) => `${value} is not a photosynthesis product! 🌿 Plants produce glucose and oxygen.`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
      suggestion: () => 'Photosynthesis: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂',
    });
    
    // Rule 6: Food chain direction
    this.addRule({
      id: 'food_chain_direction',
      name: 'Food Chain Direction',
      description: 'Energy flows from producers to consumers',
      check: (value, context) => {
        if (context.property === 'energy_flow') {
          const validFlows = {
            producer: ['primary_consumer'],
            primary_consumer: ['secondary_consumer'],
            secondary_consumer: ['tertiary_consumer'],
          };
          
          if (context.from && context.to) {
            const valid = validFlows[context.from];
            return valid && valid.includes(context.to);
          }
        }
        return true;
      },
      message: (value, context) => `Energy cannot flow from ${context.from} to ${context.to}! 🌾 Energy flows up the food chain.`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
    });
    
    // Rule 7: DNA base pairing
    this.addRule({
      id: 'dna_base_pairing',
      name: 'DNA Base Pairing',
      description: 'DNA bases pair: A-T and G-C',
      check: (value, context) => {
        if (context.property === 'basePair' && context.base1) {
          const validPairs = {
            A: 'T',
            T: 'A',
            G: 'C',
            C: 'G',
          };
          
          return validPairs[context.base1] === value;
        }
        return true;
      },
      message: (value, context) => `${context.base1}-${value} is not a valid DNA base pair! 🧬 Remember: A-T and G-C.`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
      suggestion: (value, context) => {
        const correct = { A: 'T', T: 'A', G: 'C', C: 'G' }[context.base1];
        return `${context.base1} pairs with ${correct}`;
      },
    });
  }
  
  /**
   * Validate a biological process
   */
  validateProcess(processName, inputs, outputs) {
    const results = {
      valid: true,
      errors: [],
      warnings: [],
      process: processName,
    };
    
    // Validate based on process type
    if (processName === 'photosynthesis') {
      // Check inputs and outputs
      const expectedInputs = ['CO2', 'H2O', 'light'];
      const expectedOutputs = ['glucose', 'O2'];
      
      // Simple validation
      // In production, do more sophisticated checking
    }
    
    return results;
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Quick biology validation
 */
export function validateBiology(value, property, context = {}) {
  const validator = new BiologyValidator();
  return validator.validate(value, { ...context, property });
}

export default BiologyValidator;

