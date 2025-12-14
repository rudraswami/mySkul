/**
 * 🎲 LAYOUT VARIATOR
 * ==================
 * 
 * Guarantees visual diversity by choosing different layouts each time.
 * 
 * Even the same form (e.g., Comparison) can have multiple layouts:
 * - split_screen: Left | Right
 * - stacked: Top / Bottom
 * - interleaved: A-B-A-B pattern
 * 
 * The variator ensures:
 * 1. Different layouts for repeated concepts
 * 2. Layout matches content complexity
 * 3. Random but weighted selection for variety
 */

import { STRUCTURAL_FORMS } from './FormSelector';

// ============================================
// LAYOUT VARIANTS PER FORM
// ============================================

export const LAYOUT_VARIANTS = {
  // Cause-Effect layouts
  [STRUCTURAL_FORMS.CAUSE_EFFECT]: {
    horizontal_flow: {
      name: 'Horizontal Flow',
      structure: 'left_to_right',
      positions: {
        cause: { x: 0.15, y: 0.45 },
        mechanism: { x: 0.5, y: 0.45 },
        effect: { x: 0.85, y: 0.45 },
      },
      connectorStyle: 'arrow_right',
      weight: 1.0,
    },
    vertical_cascade: {
      name: 'Vertical Cascade',
      structure: 'top_to_bottom',
      positions: {
        cause: { x: 0.5, y: 0.15 },
        mechanism: { x: 0.5, y: 0.5 },
        effect: { x: 0.5, y: 0.85 },
      },
      connectorStyle: 'arrow_down',
      weight: 0.7,
    },
    diagonal: {
      name: 'Diagonal Flow',
      structure: 'diagonal',
      positions: {
        cause: { x: 0.2, y: 0.2 },
        mechanism: { x: 0.5, y: 0.5 },
        effect: { x: 0.8, y: 0.8 },
      },
      connectorStyle: 'arrow_diagonal',
      weight: 0.5,
    },
    radial_burst: {
      name: 'Radial Burst',
      structure: 'center_out',
      positions: {
        cause: { x: 0.5, y: 0.5 },
        mechanism: { x: 0.3, y: 0.3 },
        effect: { x: 0.7, y: 0.7 },
      },
      connectorStyle: 'arrow_radial',
      weight: 0.4,
    },
  },
  
  // Comparison layouts
  [STRUCTURAL_FORMS.COMPARISON]: {
    split_screen: {
      name: 'Split Screen',
      structure: 'left_right',
      positions: {
        left_scenario: { x: 0.25, y: 0.5 },
        right_scenario: { x: 0.75, y: 0.5 },
        connector: { x: 0.5, y: 0.5 },
      },
      connectorStyle: 'vs_divider',
      weight: 1.0,
    },
    stacked: {
      name: 'Stacked',
      structure: 'top_bottom',
      positions: {
        left_scenario: { x: 0.5, y: 0.3 },
        right_scenario: { x: 0.5, y: 0.7 },
        connector: { x: 0.5, y: 0.5 },
      },
      connectorStyle: 'vs_horizontal',
      weight: 0.6,
    },
    interleaved: {
      name: 'Interleaved',
      structure: 'alternating',
      positions: {
        left_scenario: { x: 0.3, y: 0.4 },
        right_scenario: { x: 0.7, y: 0.6 },
        connector: { x: 0.5, y: 0.5 },
      },
      connectorStyle: 'diagonal_vs',
      weight: 0.4,
    },
  },
  
  // Counterfactual layouts
  [STRUCTURAL_FORMS.COUNTERFACTUAL]: {
    split_screen: {
      name: 'Reality vs Alternate',
      structure: 'left_right',
      positions: {
        reality: { x: 0.25, y: 0.5 },
        alternate: { x: 0.75, y: 0.5 },
        divergence_point: { x: 0.5, y: 0.2 },
      },
      connectorStyle: 'fork_divider',
      weight: 1.0,
    },
    timeline_fork: {
      name: 'Timeline Fork',
      structure: 'branching',
      positions: {
        reality: { x: 0.7, y: 0.3 },
        alternate: { x: 0.7, y: 0.7 },
        divergence_point: { x: 0.2, y: 0.5 },
      },
      connectorStyle: 'branch_arrow',
      weight: 0.8,
    },
  },
  
  // Hierarchy layouts
  [STRUCTURAL_FORMS.HIERARCHY]: {
    top_down_tree: {
      name: 'Top-Down Tree',
      structure: 'tree_vertical',
      positions: {
        root: { x: 0.5, y: 0.15 },
        branches: { x: 0.5, y: 0.5, spread: 'horizontal' },
        leaves: { x: 0.5, y: 0.85, spread: 'horizontal' },
      },
      connectorStyle: 'tree_branch',
      weight: 1.0,
    },
    radial_tree: {
      name: 'Radial Tree',
      structure: 'tree_radial',
      positions: {
        root: { x: 0.5, y: 0.5 },
        branches: { x: 0.5, y: 0.5, spread: 'radial', radius: 0.3 },
        leaves: { x: 0.5, y: 0.5, spread: 'radial', radius: 0.45 },
      },
      connectorStyle: 'radial_branch',
      weight: 0.6,
    },
    indented_list: {
      name: 'Indented List',
      structure: 'list',
      positions: {
        root: { x: 0.2, y: 0.1 },
        branches: { x: 0.35, y: 0.3, spread: 'vertical' },
        leaves: { x: 0.5, y: 0.6, spread: 'vertical' },
      },
      connectorStyle: 'indent_line',
      weight: 0.4,
    },
  },
  
  // Timeline layouts
  [STRUCTURAL_FORMS.TIMELINE]: {
    horizontal_timeline: {
      name: 'Horizontal Timeline',
      structure: 'left_to_right',
      positions: {
        start_state: { x: 0.1, y: 0.5 },
        events: { x: 0.5, y: 0.5, spread: 'horizontal' },
        end_state: { x: 0.9, y: 0.5 },
      },
      connectorStyle: 'timeline_arrow',
      weight: 1.0,
    },
    vertical_timeline: {
      name: 'Vertical Timeline',
      structure: 'top_to_bottom',
      positions: {
        start_state: { x: 0.5, y: 0.1 },
        events: { x: 0.5, y: 0.5, spread: 'vertical' },
        end_state: { x: 0.5, y: 0.9 },
      },
      connectorStyle: 'timeline_down',
      weight: 0.7,
    },
    spiral: {
      name: 'Spiral Timeline',
      structure: 'spiral',
      positions: {
        start_state: { x: 0.5, y: 0.5, angle: 0 },
        events: { x: 0.5, y: 0.5, spread: 'spiral' },
        end_state: { x: 0.5, y: 0.5, angle: 720 },
      },
      connectorStyle: 'spiral_path',
      weight: 0.3,
    },
  },
  
  // Force Diagram layouts
  [STRUCTURAL_FORMS.FORCE_DIAGRAM]: {
    centered: {
      name: 'Centered Body',
      structure: 'radial',
      positions: {
        center: { x: 0.5, y: 0.45 },
        forces: { x: 0.5, y: 0.45, spread: 'directional' },
        ground: { x: 0.5, y: 0.75 },
      },
      connectorStyle: 'force_arrow',
      weight: 1.0,
    },
    on_surface: {
      name: 'On Surface',
      structure: 'grounded',
      positions: {
        center: { x: 0.35, y: 0.45 },
        forces: { x: 0.35, y: 0.45, spread: 'directional' },
        ground: { x: 0.2, y: 0.65, width: 0.5 },
      },
      connectorStyle: 'force_arrow',
      weight: 0.8,
    },
  },
  
  // Metaphor Scene layouts
  [STRUCTURAL_FORMS.METAPHOR_SCENE]: {
    scene_illustration: {
      name: 'Scene Illustration',
      structure: 'scene',
      positions: {
        scene: { x: 0.5, y: 0.5, width: 0.9, height: 0.7 },
        actors: { x: 0.5, y: 0.5, spread: 'scene' },
        action: { x: 0.5, y: 0.4 },
        insight: { x: 0.5, y: 0.9 },
      },
      connectorStyle: 'action_bubble',
      weight: 1.0,
    },
    comic_panel: {
      name: 'Comic Panel',
      structure: 'panels',
      positions: {
        scene: { x: 0.5, y: 0.5, panels: 3 },
        actors: { x: 0.5, y: 0.5, spread: 'panel' },
        action: { x: 0.5, y: 0.5 },
        insight: { x: 0.5, y: 0.9 },
      },
      connectorStyle: 'speech_bubble',
      weight: 0.6,
    },
  },
  
  // Formula Focus layouts
  [STRUCTURAL_FORMS.FORMULA_FOCUS]: {
    equation_flow: {
      name: 'Equation Flow',
      structure: 'left_to_right',
      positions: {
        variables: { x: 0.2, y: 0.5, spread: 'vertical' },
        formula: { x: 0.5, y: 0.5 },
        result: { x: 0.8, y: 0.5 },
      },
      connectorStyle: 'equals_arrow',
      weight: 1.0,
    },
    variable_tree: {
      name: 'Variable Tree',
      structure: 'converging',
      positions: {
        variables: { x: 0.3, y: 0.3, spread: 'vertical' },
        formula: { x: 0.7, y: 0.5 },
        result: { x: 0.7, y: 0.8 },
      },
      connectorStyle: 'merge_arrow',
      weight: 0.6,
    },
  },
};

// Default layout for forms not explicitly defined
const DEFAULT_LAYOUT = {
  default: {
    name: 'Default Grid',
    structure: 'grid',
    positions: {
      default: { x: 0.5, y: 0.5, spread: 'grid' },
    },
    connectorStyle: 'arrow',
    weight: 1.0,
  },
};

// ============================================
// LAYOUT VARIATOR CLASS
// ============================================

export class LayoutVariator {
  constructor(options = {}) {
    this.options = {
      avoidRepetition: true,
      weightedSelection: true,
      considerComplexity: true,
      ...options,
    };
    
    this.recentLayouts = []; // Track last N layouts used
    this.maxHistory = 5;
  }
  
  /**
   * Choose a layout variant for the given form
   * @param {Object} formResult - Result from FormSelector
   * @param {Object} filledForm - Result from ContentMapper
   * @returns {Object} Selected layout with positions
   */
  choose(formResult, filledForm) {
    const form = formResult.form;
    const variants = LAYOUT_VARIANTS[form] || DEFAULT_LAYOUT;
    
    console.log(`🎲 [LayoutVariator] Choosing layout for form: ${form}`);
    
    // Get available variants as array
    const variantEntries = Object.entries(variants);
    
    // Filter out recently used layouts if avoiding repetition
    let candidates = variantEntries;
    if (this.options.avoidRepetition) {
      candidates = variantEntries.filter(([key]) => !this.recentLayouts.includes(key));
      // If all filtered out, reset and use all
      if (candidates.length === 0) {
        candidates = variantEntries;
        this.recentLayouts = [];
      }
    }
    
    // Select based on content complexity
    if (this.options.considerComplexity) {
      const complexity = this.assessComplexity(filledForm);
      candidates = this.filterByComplexity(candidates, complexity);
    }
    
    // Weighted random selection
    let selected;
    if (this.options.weightedSelection) {
      selected = this.weightedSelect(candidates);
    } else {
      const randomIndex = Math.floor(Math.random() * candidates.length);
      selected = candidates[randomIndex];
    }
    
    const [layoutKey, layoutSpec] = selected;
    
    // Track usage
    this.recentLayouts.push(layoutKey);
    if (this.recentLayouts.length > this.maxHistory) {
      this.recentLayouts.shift();
    }
    
    const result = this.createResult(layoutKey, layoutSpec, form);
    
    console.log(`🎲 [LayoutVariator] Selected: ${layoutSpec.name}`);
    
    return result;
  }
  
  /**
   * Assess content complexity
   */
  assessComplexity(filledForm) {
    const entityCount = filledForm.metadata?.entityCount || 0;
    
    if (entityCount <= 3) return 'simple';
    if (entityCount <= 6) return 'medium';
    return 'complex';
  }
  
  /**
   * Filter layouts by complexity
   */
  filterByComplexity(candidates, complexity) {
    // For complex content, prefer simpler layouts
    if (complexity === 'complex') {
      // Filter to layouts with higher weights (usually simpler)
      const simpler = candidates.filter(([_, spec]) => spec.weight >= 0.7);
      return simpler.length > 0 ? simpler : candidates;
    }
    
    // For simple content, any layout works
    return candidates;
  }
  
  /**
   * Weighted random selection
   */
  weightedSelect(candidates) {
    const totalWeight = candidates.reduce((sum, [_, spec]) => sum + (spec.weight || 1), 0);
    let random = Math.random() * totalWeight;
    
    for (const entry of candidates) {
      const weight = entry[1].weight || 1;
      random -= weight;
      if (random <= 0) {
        return entry;
      }
    }
    
    return candidates[candidates.length - 1];
  }
  
  /**
   * Create standardized result
   */
  createResult(layoutKey, layoutSpec, form) {
    return {
      layout: layoutKey,
      name: layoutSpec.name,
      structure: layoutSpec.structure,
      positions: layoutSpec.positions,
      connectorStyle: layoutSpec.connectorStyle,
      form,
      
      // Helper methods
      getPosition: (slotName) => layoutSpec.positions[slotName] || { x: 0.5, y: 0.5 },
      getConnectorStyle: () => layoutSpec.connectorStyle,
      isHorizontal: () => layoutSpec.structure.includes('left_right') || layoutSpec.structure.includes('left_to_right'),
      isVertical: () => layoutSpec.structure.includes('top_bottom') || layoutSpec.structure.includes('top_to_bottom'),
    };
  }
  
  /**
   * Reset layout history (for testing or new sessions)
   */
  resetHistory() {
    this.recentLayouts = [];
  }
}

// ============================================
// EXPORTS
// ============================================

export function createLayoutVariator(options) {
  return new LayoutVariator(options);
}

export default LayoutVariator;

