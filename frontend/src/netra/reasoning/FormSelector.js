/**
 * 🎨 FORM SELECTOR
 * ================
 * 
 * Maps cognitive intent to universal visual FORMS (not templates).
 * 
 * A form is a STRUCTURAL pattern, not content:
 * - Cause-Effect: A → B → C
 * - Comparison: A | B
 * - Hierarchy: Tree structure
 * 
 * The same form works for ANY domain:
 * - Friction vs No Friction (physics) → Comparison form
 * - Prokaryote vs Eukaryote (biology) → Same Comparison form
 * - Democracy vs Dictatorship (civics) → Same Comparison form
 * 
 * This is subject-agnostic visual intelligence.
 */

import { INTENT_TYPES } from './IntentClassifier';

// ============================================
// STRUCTURAL FORMS (Subject-Agnostic Layouts)
// ============================================

export const STRUCTURAL_FORMS = {
  // Flow structures
  CAUSE_EFFECT: 'cause_effect',         // A → B → C (linear causation)
  CAUSAL_CHAIN: 'causal_chain',         // A → B → C with zoom/depth
  CYCLE: 'cycle',                        // A → B → C → A (circular)
  
  // Comparative structures
  COMPARISON: 'comparison',              // A | B (side by side)
  COUNTERFACTUAL: 'counterfactual_split', // Reality | Alternate
  OPPOSITION: 'opposition',              // A ↔ B (balance, tension)
  
  // Hierarchical structures
  HIERARCHY: 'hierarchy',                // Tree/classification
  PART_WHOLE: 'part_whole',             // Exploded view
  
  // Temporal structures
  TIMELINE: 'timeline',                  // T1 → T2 → T3
  PROGRESSION: 'progression',            // Before → During → After
  STAGES: 'stages',                      // Step 1, Step 2, Step 3
  
  // Relational structures
  SYSTEM_GRAPH: 'system_graph',          // Network of connections
  FORCE_DIAGRAM: 'force_diagram',        // Forces acting on a point
  DEPENDENCY_MAP: 'dependency_map',      // What depends on what
  
  // Formula/Quantitative structures
  FORMULA_FOCUS: 'formula_focus',        // Variables → Equation → Result
  GRAPH_PLOT: 'graph_plot',              // X-Y relationship
  
  // Story/Metaphor structures
  METAPHOR_SCENE: 'metaphor_scene',      // Real-world analogy
  STORY_SEQUENCE: 'story_sequence',      // Narrative panels
  
  // Edge case structures
  THRESHOLD_DIAGRAM: 'threshold_diagram', // Normal → Threshold → Failure
  LIMIT_ANALYSIS: 'limit_analysis',      // Approaching extremes
};

// ============================================
// INTENT TO FORM MAPPING RULES
// ============================================

/**
 * These are RULES, not templates.
 * Each intent maps to one or more valid forms.
 * The selector chooses based on context.
 */
const INTENT_FORM_MAPPING = {
  [INTENT_TYPES.CONCEPTUAL]: {
    primary: STRUCTURAL_FORMS.CAUSE_EFFECT,
    alternatives: [STRUCTURAL_FORMS.SYSTEM_GRAPH, STRUCTURAL_FORMS.FORCE_DIAGRAM],
    description: 'Show what it is and how it works',
  },
  
  [INTENT_TYPES.CAUSAL_INQUIRY]: {
    primary: STRUCTURAL_FORMS.CAUSAL_CHAIN,
    alternatives: [STRUCTURAL_FORMS.CAUSE_EFFECT],
    description: 'Trace back from effect to root cause',
  },
  
  [INTENT_TYPES.MECHANISTIC]: {
    primary: STRUCTURAL_FORMS.STAGES,
    alternatives: [STRUCTURAL_FORMS.CAUSE_EFFECT, STRUCTURAL_FORMS.SYSTEM_GRAPH],
    description: 'Show the mechanism step by step',
  },
  
  [INTENT_TYPES.COUNTERFACTUAL]: {
    primary: STRUCTURAL_FORMS.COUNTERFACTUAL,
    alternatives: [STRUCTURAL_FORMS.COMPARISON],
    description: 'Compare reality with alternate scenario',
  },
  
  [INTENT_TYPES.COMPARATIVE]: {
    primary: STRUCTURAL_FORMS.COMPARISON,
    alternatives: [STRUCTURAL_FORMS.OPPOSITION],
    description: 'Show two things side by side',
  },
  
  [INTENT_TYPES.CLASSIFICATORY]: {
    primary: STRUCTURAL_FORMS.HIERARCHY,
    alternatives: [STRUCTURAL_FORMS.PART_WHOLE],
    description: 'Show types/categories in tree structure',
  },
  
  [INTENT_TYPES.TEMPORAL]: {
    primary: STRUCTURAL_FORMS.TIMELINE,
    alternatives: [STRUCTURAL_FORMS.PROGRESSION],
    description: 'Show change over time',
  },
  
  [INTENT_TYPES.SEQUENTIAL]: {
    primary: STRUCTURAL_FORMS.STAGES,
    alternatives: [STRUCTURAL_FORMS.TIMELINE, STRUCTURAL_FORMS.PROGRESSION],
    description: 'Show ordered steps',
  },
  
  [INTENT_TYPES.INTUITIVE]: {
    primary: STRUCTURAL_FORMS.METAPHOR_SCENE,
    alternatives: [STRUCTURAL_FORMS.STORY_SEQUENCE],
    description: 'Show relatable real-world scenario',
  },
  
  [INTENT_TYPES.ANALOGICAL]: {
    primary: STRUCTURAL_FORMS.METAPHOR_SCENE,
    alternatives: [STRUCTURAL_FORMS.COMPARISON],
    description: 'Show the analogy visually',
  },
  
  [INTENT_TYPES.QUANTITATIVE]: {
    primary: STRUCTURAL_FORMS.FORMULA_FOCUS,
    alternatives: [STRUCTURAL_FORMS.GRAPH_PLOT],
    description: 'Emphasize the mathematical relationship',
  },
  
  [INTENT_TYPES.RELATIONAL]: {
    primary: STRUCTURAL_FORMS.DEPENDENCY_MAP,
    alternatives: [STRUCTURAL_FORMS.GRAPH_PLOT, STRUCTURAL_FORMS.SYSTEM_GRAPH],
    description: 'Show how things depend on each other',
  },
  
  [INTENT_TYPES.EDGE_CASE]: {
    primary: STRUCTURAL_FORMS.THRESHOLD_DIAGRAM,
    alternatives: [STRUCTURAL_FORMS.PROGRESSION],
    description: 'Show what happens at extremes',
  },
  
  [INTENT_TYPES.BOUNDARY]: {
    primary: STRUCTURAL_FORMS.LIMIT_ANALYSIS,
    alternatives: [STRUCTURAL_FORMS.GRAPH_PLOT, STRUCTURAL_FORMS.THRESHOLD_DIAGRAM],
    description: 'Show limits and boundaries',
  },
};

// ============================================
// FORM SPECIFICATIONS
// ============================================

/**
 * Each form has a structural specification defining its SLOTS.
 * Slots are abstract positions that get filled with content.
 */
export const FORM_SPECIFICATIONS = {
  [STRUCTURAL_FORMS.CAUSE_EFFECT]: {
    name: 'Cause-Effect Flow',
    structure: 'linear',
    slots: {
      cause: { role: 'initiator', position: 'start' },
      mechanism: { role: 'process', position: 'middle', optional: true },
      effect: { role: 'result', position: 'end' },
    },
    connectors: ['arrow'],
    supportedLayouts: ['horizontal_flow', 'vertical_cascade', 'diagonal'],
  },
  
  [STRUCTURAL_FORMS.CAUSAL_CHAIN]: {
    name: 'Causal Chain (Deep)',
    structure: 'linear_deep',
    slots: {
      surface_effect: { role: 'visible_result', position: 'top' },
      intermediate: { role: 'mechanism', position: 'middle', repeatable: true },
      root_cause: { role: 'origin', position: 'bottom' },
    },
    connectors: ['arrow_reverse', 'zoom'],
    supportedLayouts: ['vertical_dive', 'zoom_chain'],
  },
  
  [STRUCTURAL_FORMS.COMPARISON]: {
    name: 'Side-by-Side Comparison',
    structure: 'parallel',
    slots: {
      left_scenario: { role: 'option_a', position: 'left' },
      right_scenario: { role: 'option_b', position: 'right' },
      connector: { role: 'difference_marker', position: 'center', optional: true },
      conclusion: { role: 'insight', position: 'bottom', optional: true },
    },
    connectors: ['vs_marker', 'difference_arrow'],
    supportedLayouts: ['split_screen', 'stacked', 'interleaved'],
  },
  
  [STRUCTURAL_FORMS.COUNTERFACTUAL]: {
    name: 'Reality vs Alternate',
    structure: 'parallel_contrast',
    slots: {
      reality: { role: 'actual_world', position: 'left', label: 'Reality' },
      alternate: { role: 'hypothetical', position: 'right', label: 'What If?' },
      divergence_point: { role: 'key_difference', position: 'center' },
    },
    connectors: ['diverge_arrow', 'contrast_marker'],
    supportedLayouts: ['split_screen', 'timeline_fork'],
  },
  
  [STRUCTURAL_FORMS.OPPOSITION]: {
    name: 'Balance/Tension',
    structure: 'bilateral',
    slots: {
      force_a: { role: 'protagonist', position: 'left' },
      force_b: { role: 'antagonist', position: 'right' },
      equilibrium: { role: 'balance_point', position: 'center' },
    },
    connectors: ['tension_arrow', 'balance_scale'],
    supportedLayouts: ['tug_of_war', 'scale_balance', 'push_pull'],
  },
  
  [STRUCTURAL_FORMS.HIERARCHY]: {
    name: 'Classification Tree',
    structure: 'tree',
    slots: {
      root: { role: 'parent_category', position: 'top' },
      branches: { role: 'subcategories', position: 'middle', repeatable: true },
      leaves: { role: 'instances', position: 'bottom', repeatable: true },
    },
    connectors: ['branch_line'],
    supportedLayouts: ['top_down_tree', 'radial_tree', 'indented_list'],
  },
  
  [STRUCTURAL_FORMS.TIMELINE]: {
    name: 'Timeline',
    structure: 'temporal',
    slots: {
      start_state: { role: 'initial', position: 'left' },
      events: { role: 'milestones', position: 'middle', repeatable: true },
      end_state: { role: 'final', position: 'right' },
    },
    connectors: ['time_arrow', 'event_marker'],
    supportedLayouts: ['horizontal_timeline', 'vertical_timeline', 'spiral'],
  },
  
  [STRUCTURAL_FORMS.STAGES]: {
    name: 'Step-by-Step',
    structure: 'sequential',
    slots: {
      steps: { role: 'stage', repeatable: true },
    },
    connectors: ['step_arrow', 'numbering'],
    supportedLayouts: ['numbered_flow', 'chevron', 'ladder'],
  },
  
  [STRUCTURAL_FORMS.SYSTEM_GRAPH]: {
    name: 'System Network',
    structure: 'network',
    slots: {
      nodes: { role: 'component', repeatable: true },
      connections: { role: 'relationship', repeatable: true },
    },
    connectors: ['bidirectional_arrow', 'labeled_edge'],
    supportedLayouts: ['force_directed', 'circular', 'grid'],
  },
  
  [STRUCTURAL_FORMS.FORCE_DIAGRAM]: {
    name: 'Force Diagram',
    structure: 'radial',
    slots: {
      center: { role: 'body', position: 'center' },
      forces: { role: 'force_vector', repeatable: true },
      ground: { role: 'reference', position: 'bottom', optional: true },
    },
    connectors: ['force_arrow'],
    supportedLayouts: ['centered', 'on_surface'],
  },
  
  [STRUCTURAL_FORMS.FORMULA_FOCUS]: {
    name: 'Formula Emphasis',
    structure: 'equation',
    slots: {
      variables: { role: 'inputs', position: 'left', repeatable: true },
      formula: { role: 'equation', position: 'center' },
      result: { role: 'output', position: 'right' },
    },
    connectors: ['equals', 'arrow'],
    supportedLayouts: ['equation_flow', 'variable_tree'],
  },
  
  [STRUCTURAL_FORMS.METAPHOR_SCENE]: {
    name: 'Real-World Scene',
    structure: 'scene',
    slots: {
      scene: { role: 'environment', position: 'background' },
      actors: { role: 'characters', repeatable: true },
      action: { role: 'what_happens', position: 'center' },
      insight: { role: 'takeaway', position: 'bottom' },
    },
    connectors: ['action_arrow', 'thought_bubble'],
    supportedLayouts: ['scene_illustration', 'comic_panel'],
  },
  
  [STRUCTURAL_FORMS.THRESHOLD_DIAGRAM]: {
    name: 'Threshold/Limit',
    structure: 'progressive',
    slots: {
      normal_zone: { role: 'safe_state', position: 'left' },
      threshold: { role: 'critical_point', position: 'center' },
      failure_zone: { role: 'failed_state', position: 'right' },
    },
    connectors: ['gradient_arrow', 'warning_marker'],
    supportedLayouts: ['gradient_bar', 'cliff_edge'],
  },
};

// ============================================
// FORM SELECTOR CLASS
// ============================================

export class FormSelector {
  constructor(options = {}) {
    this.options = {
      preferPrimary: true,
      considerContext: true,
      ...options,
    };
    
    this.lastUsedForm = null; // Track for variation
  }
  
  /**
   * Select the best visual form for an intent
   * @param {Object} intentResult - Result from IntentClassifier
   * @param {Object} context - Additional context (content complexity, etc.)
   * @returns {Object} Selected form with specification
   */
  select(intentResult, context = {}) {
    const primaryIntent = intentResult.primary;
    const mapping = INTENT_FORM_MAPPING[primaryIntent];
    
    if (!mapping) {
      console.warn(`⚠️ [FormSelector] No mapping for intent: ${primaryIntent}`);
      return this.createResult(STRUCTURAL_FORMS.CAUSE_EFFECT, intentResult);
    }
    
    // Determine which form to use
    let selectedForm = mapping.primary;
    
    // Consider alternatives for variation
    if (!this.options.preferPrimary || this.shouldUseAlternative(mapping, context)) {
      const alternatives = mapping.alternatives || [];
      if (alternatives.length > 0) {
        // Avoid using the same form twice in a row
        const validAlternatives = alternatives.filter(f => f !== this.lastUsedForm);
        if (validAlternatives.length > 0) {
          selectedForm = validAlternatives[Math.floor(Math.random() * validAlternatives.length)];
        }
      }
    }
    
    // Also avoid repeating the primary form
    if (selectedForm === this.lastUsedForm && mapping.alternatives?.length > 0) {
      selectedForm = mapping.alternatives[0];
    }
    
    this.lastUsedForm = selectedForm;
    
    const result = this.createResult(selectedForm, intentResult);
    
    console.log('🎨 [FormSelector] Selected form:', {
      intent: primaryIntent,
      form: selectedForm,
      description: mapping.description,
    });
    
    return result;
  }
  
  /**
   * Decide whether to use an alternative form
   */
  shouldUseAlternative(mapping, context) {
    // Use alternative if content is complex
    if (context.entityCount > 5) return true;
    
    // Use alternative if secondary intent suggests it
    if (context.secondaryIntent) return true;
    
    // Random variation (20% of the time)
    if (Math.random() < 0.2) return true;
    
    return false;
  }
  
  /**
   * Create a standardized result object
   */
  createResult(formType, intentResult) {
    const specification = FORM_SPECIFICATIONS[formType] || FORM_SPECIFICATIONS[STRUCTURAL_FORMS.CAUSE_EFFECT];
    
    return {
      form: formType,
      specification,
      intent: intentResult.primary,
      
      // Helper methods
      getSlots: () => specification.slots,
      getSupportedLayouts: () => specification.supportedLayouts || [],
      getConnectors: () => specification.connectors || [],
      isComparison: () => [STRUCTURAL_FORMS.COMPARISON, STRUCTURAL_FORMS.COUNTERFACTUAL, STRUCTURAL_FORMS.OPPOSITION].includes(formType),
      isTimeline: () => [STRUCTURAL_FORMS.TIMELINE, STRUCTURAL_FORMS.PROGRESSION, STRUCTURAL_FORMS.STAGES].includes(formType),
      isHierarchy: () => [STRUCTURAL_FORMS.HIERARCHY, STRUCTURAL_FORMS.PART_WHOLE].includes(formType),
    };
  }
  
  /**
   * Get specification for a form
   */
  getSpecification(formType) {
    return FORM_SPECIFICATIONS[formType] || null;
  }
}

// ============================================
// EXPORTS
// ============================================

export function createFormSelector(options) {
  return new FormSelector(options);
}

export default FormSelector;

