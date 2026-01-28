/**
 * 🗂️ ATOM REGISTRY
 * =================
 * 
 * Central registry for all Atom types.
 * 
 * - Validates atom types against registered list
 * - Instantiates atoms by type name
 * - Provides param schemas for validation
 */

// Import atom implementations
import { Atom } from './Atom';
import { RigidBody } from './RigidBody';
import { Surface } from './Surface';
import { ForceVector } from './ForceVector';
import { Entity } from './Entity';
import { Label } from './Label';
import { Connector } from './Connector';
import { Region } from './Region';
import { SVGAsset } from './SVGAsset';

// Registry storage
const atomTypes = new Map();

/**
 * Register an atom type
 */
export function registerAtom(type, AtomClass) {
  if (atomTypes.has(type)) {
    console.warn(`[AtomRegistry] Overwriting atom type: ${type}`);
  }
  atomTypes.set(type, AtomClass);
}

/**
 * Check if atom type is registered
 */
export function isRegistered(type) {
  return atomTypes.has(type);
}

/**
 * Get all registered atom types
 */
export function getRegisteredTypes() {
  return Array.from(atomTypes.keys());
}

/**
 * Create atom instance by type
 */
export function createAtom(type, id, params = {}) {
  const AtomClass = atomTypes.get(type);
  
  if (!AtomClass) {
    console.error(`[AtomRegistry] Unknown atom type: ${type}`);
    // Fallback to generic Entity
    return new Entity(id, { ...params, _fallbackType: type });
  }
  
  return new AtomClass(id, params);
}

/**
 * Get param schema for atom type
 */
export function getParamSchema(type) {
  const AtomClass = atomTypes.get(type);
  if (!AtomClass) return null;
  return AtomClass.getParamSchema?.() || {};
}

/**
 * Validate params against schema
 */
export function validateParams(type, params) {
  const schema = getParamSchema(type);
  const errors = [];
  
  for (const [key, rules] of Object.entries(schema)) {
    const value = params[key];
    
    if (rules.required && value === undefined) {
      errors.push(`Missing required param: ${key}`);
    }
    
    if (value !== undefined && rules.type) {
      if (rules.type === 'number' && typeof value !== 'number') {
        errors.push(`Param ${key} must be a number`);
      }
      if (rules.type === 'string' && typeof value !== 'string') {
        errors.push(`Param ${key} must be a string`);
      }
    }
    
    if (value !== undefined && rules.min !== undefined && value < rules.min) {
      errors.push(`Param ${key} must be >= ${rules.min}`);
    }
    
    if (value !== undefined && rules.max !== undefined && value > rules.max) {
      errors.push(`Param ${key} must be <= ${rules.max}`);
    }
  }
  
  return { valid: errors.length === 0, errors };
}

// ============================================
// REGISTER BUILT-IN ATOMS
// ============================================

// Universal atoms
registerAtom('Entity', Entity);
registerAtom('Label', Label);
registerAtom('Connector', Connector);
registerAtom('Region', Region);

// Physics atoms
registerAtom('RigidBody', RigidBody);
registerAtom('Surface', Surface);
registerAtom('ForceVector', ForceVector);

// 🎨 Rich visual assets (NanoBanana-style)
registerAtom('SVGAsset', SVGAsset);
registerAtom('Asset', SVGAsset);  // Alias

// Aliases for flexibility
registerAtom('Annotation', Label);  // Alias

// Export registry functions
export const AtomRegistry = {
  register: registerAtom,
  isRegistered,
  getRegisteredTypes,
  create: createAtom,
  getParamSchema,
  validateParams
};

export default AtomRegistry;
