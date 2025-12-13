/**
 * 🧪 CHEMISTRY VALIDATOR
 * =======================
 * 
 * Validates chemistry concepts
 * - Valency and bonding
 * - Charge balance
 * - Electronegativity
 * - pH ranges
 * - Periodic table constraints
 */

import { BaseValidator, VALIDATION_STATUS, FEEDBACK_TYPE } from './BaseValidator';

// ============================================
// CHEMISTRY DATA
// ============================================

const VALENCY = {
  H: 1, He: 0,
  Li: 1, Be: 2, B: 3, C: 4, N: 3, O: 2, F: 1, Ne: 0,
  Na: 1, Mg: 2, Al: 3, Si: 4, P: 3, S: 2, Cl: 1, Ar: 0,
  K: 1, Ca: 2,
  // Add more as needed
};

const ELECTRONEGATIVITY = {
  H: 2.20, C: 2.55, N: 3.04, O: 3.44, F: 3.98,
  Na: 0.93, Cl: 3.16, K: 0.82,
  // Add more as needed
};

// ============================================
// CHEMISTRY VALIDATOR
// ============================================

export class ChemistryValidator extends BaseValidator {
  constructor(options = {}) {
    super({ subject: 'chemistry', ...options });
    this.initializeRules();
  }
  
  /**
   * Initialize chemistry validation rules
   */
  initializeRules() {
    // Rule 1: Valency must be satisfied
    this.addRule({
      id: 'valency_satisfied',
      name: 'Valency Satisfied',
      description: 'All atoms must satisfy their valency',
      check: (value, context) => {
        if (context.property === 'bonds' && context.element) {
          const valency = VALENCY[context.element];
          if (valency !== undefined) {
            return value === valency;
          }
        }
        return true;
      },
      message: (value, context) => {
        const element = context.element;
        const expectedValency = VALENCY[element];
        return `${element} has ${value} bonds, but needs ${expectedValency}! 🔗 Check valency rules.`;
      },
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
      suggestion: (value, context) => {
        const needed = VALENCY[context.element] - value;
        return needed > 0
          ? `Add ${needed} more bond(s) to ${context.element}`
          : `Remove ${-needed} bond(s) from ${context.element}`;
      },
    });
    
    // Rule 2: Charge balance in ionic compounds
    this.addRule({
      id: 'charge_balance',
      name: 'Charge Balance',
      description: 'Total charge must be zero in neutral compounds',
      check: (value, context) => {
        if (context.property === 'totalCharge' && context.compound === 'ionic') {
          return value === 0;
        }
        return true;
      },
      message: (value) => `Total charge = ${value > 0 ? '+' : ''}${value}! ⚡ Compounds are neutral (charge = 0).`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
      suggestion: (value) => {
        return value > 0
          ? 'Add more negative ions or remove positive ions'
          : 'Add more positive ions or remove negative ions';
      },
    });
    
    // Rule 3: pH range
    this.addRule({
      id: 'ph_range',
      name: 'pH Range',
      description: 'pH must be between 0 and 14',
      check: (value, context) => {
        if (context.property === 'pH') {
          return value >= 0 && value <= 14;
        }
        return true;
      },
      message: (value) => `pH = ${value.toFixed(1)} is invalid! 🧪 pH scale is 0-14 (0=acidic, 7=neutral, 14=basic).`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SHAKE,
    });
    
    // Rule 4: Electronegativity difference (bond type)
    this.addRule({
      id: 'electronegativity_difference',
      name: 'Electronegativity Check',
      description: 'Bond type should match electronegativity difference',
      check: (value, context) => {
        if (context.property === 'bondType' && context.element1 && context.element2) {
          const en1 = ELECTRONEGATIVITY[context.element1];
          const en2 = ELECTRONEGATIVITY[context.element2];
          
          if (en1 !== undefined && en2 !== undefined) {
            const diff = Math.abs(en1 - en2);
            
            // Covalent: diff < 0.5, Polar: 0.5-1.7, Ionic: > 1.7
            if (value === 'covalent') return diff < 0.5;
            if (value === 'polar') return diff >= 0.5 && diff <= 1.7;
            if (value === 'ionic') return diff > 1.7;
          }
        }
        return true;
      },
      message: (value, context) => {
        const en1 = ELECTRONEGATIVITY[context.element1];
        const en2 = ELECTRONEGATIVITY[context.element2];
        const diff = Math.abs(en1 - en2).toFixed(2);
        const expected = diff < 0.5 ? 'covalent' : (diff <= 1.7 ? 'polar' : 'ionic');
        return `Bond type "${value}" doesn't match electronegativity difference (${diff}). Should be "${expected}". 🔬`;
      },
      severity: VALIDATION_STATUS.WARNING,
      feedback: FEEDBACK_TYPE.GHOST_MENTOR,
    });
    
    // Rule 5: Noble gases don't bond
    this.addRule({
      id: 'noble_gas_inert',
      name: 'Noble Gas Inertness',
      description: 'Noble gases (He, Ne, Ar, etc.) rarely form bonds',
      check: (value, context) => {
        if (context.property === 'bonds' && context.element) {
          const nobleGases = ['He', 'Ne', 'Ar', 'Kr', 'Xe', 'Rn'];
          if (nobleGases.includes(context.element)) {
            return value === 0;
          }
        }
        return true;
      },
      message: (value, context) => `${context.element} is a noble gas! 👑 It has full outer shell and doesn't form bonds easily.`,
      severity: VALIDATION_STATUS.ERROR,
      feedback: FEEDBACK_TYPE.SCRIBBLE,
    });
    
    // Rule 6: Oxidation state reasonable
    this.addRule({
      id: 'oxidation_state',
      name: 'Oxidation State',
      description: 'Oxidation state should be within reasonable range',
      check: (value, context) => {
        if (context.property === 'oxidationState') {
          // Most elements: -4 to +8
          return value >= -4 && value <= 8;
        }
        return true;
      },
      message: (value) => `Oxidation state ${value > 0 ? '+' : ''}${value} is unusual! 🧮 Check your electron counting.`,
      severity: VALIDATION_STATUS.WARNING,
      feedback: FEEDBACK_TYPE.GHOST_MENTOR,
    });
  }
  
  /**
   * Validate a molecular formula
   */
  validateFormula(formula) {
    // Simple validation: check if formula has balanced charges
    // This is a simplified example
    const results = {
      valid: true,
      errors: [],
      warnings: [],
      formula,
    };
    
    // Parse formula (simplified)
    const atoms = this.parseFormula(formula);
    
    // Check valency for each atom
    atoms.forEach(atom => {
      const validation = this.validate(atom.bonds || 0, {
        property: 'bonds',
        element: atom.element,
      });
      
      if (!validation.valid) {
        results.valid = false;
        results.errors.push(...validation.results);
      }
    });
    
    return results;
  }
  
  /**
   * Parse chemical formula (simplified)
   */
  parseFormula(formula) {
    // Very simplified parser for demo
    // In production, use a proper chemistry library
    const atoms = [];
    const regex = /([A-Z][a-z]?)(\d*)/g;
    let match;
    
    while ((match = regex.exec(formula)) !== null) {
      const element = match[1];
      const count = match[2] ? parseInt(match[2]) : 1;
      
      for (let i = 0; i < count; i++) {
        atoms.push({ element });
      }
    }
    
    return atoms;
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Quick chemistry validation
 */
export function validateChemistry(value, property, context = {}) {
  const validator = new ChemistryValidator();
  return validator.validate(value, { ...context, property });
}

export default ChemistryValidator;

