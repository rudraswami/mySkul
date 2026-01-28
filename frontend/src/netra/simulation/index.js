/**
 * 🎬 NETRA SIMULATION ENGINE v6.0
 * ================================
 * 
 * A complete simulation engine for educational visualizations.
 * 
 * Key components:
 * - SimulationRuntime: Continuous tick loop
 * - SimulationRenderer: React component for rendering
 * - ScriptCompiler: Convert SimulationScript → Runtime scene
 * - RuleInterpreter: Parse and execute rules
 * - OntologyLayoutEngine: Compute positions deterministically
 * - EntityTemplates: Pre-built visual templates
 * - DomainPalettes: Curated color schemes
 */

// Core runtime
export { SimulationRuntime, createSimulationRuntime } from './SimulationRuntime';

// React renderer
export { SimulationRenderer } from './SimulationRenderer';

// Script compilation
export { 
  compileScript, 
  validateScript, 
  enrichScript, 
  createPlaceholderScene 
} from './ScriptCompiler';

// Rule execution
export { RuleEngine, compileRule, compileRules } from './RuleInterpreter';

// Layout
export { computeLayout, applyLayout } from './OntologyLayoutEngine';

// Templates
export { 
  ENTITY_TEMPLATES, 
  getTemplate, 
  createEntityFromTemplate,
  getTemplatesByCategory 
} from './EntityTemplates';

// Palettes
export { 
  DOMAIN_PALETTES, 
  getPalette, 
  getRoleColor, 
  getBackgroundGradient,
  generateEntityColors 
} from './DomainPalettes';

// Default export
export default {
  createSimulationRuntime,
  compileScript,
  validateScript,
  SimulationRenderer
};
