/**
 * FormulaBinding.js
 * Phase 4.1: Bidirectional binding between sliders, objects, and formulas
 * 
 * Features:
 * - Reactive formula calculations
 * - Object property updates based on values
 * - Visual feedback on value changes
 * - History tracking for undo/redo
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

// Formula definitions with their variables and calculations
export const FORMULA_DEFINITIONS = {
  // Physics
  force: {
    formula: 'F = m × a',
    latex: 'F = m \\times a',
    variables: {
      F: { name: 'Force', unit: 'N', color: '#FF5722', min: 0, max: 100 },
      m: { name: 'Mass', unit: 'kg', color: '#4CAF50', min: 0.1, max: 10 },
      a: { name: 'Acceleration', unit: 'm/s²', color: '#2196F3', min: 0, max: 50 },
    },
    calculate: (vars) => ({
      F: vars.m * vars.a,
      m: vars.F / vars.a,
      a: vars.F / vars.m,
    }),
    dependent: 'F', // F is calculated from m and a
  },
  
  velocity: {
    formula: 'v = d / t',
    latex: 'v = \\frac{d}{t}',
    variables: {
      v: { name: 'Velocity', unit: 'm/s', color: '#9C27B0', min: 0, max: 100 },
      d: { name: 'Distance', unit: 'm', color: '#FF9800', min: 0, max: 1000 },
      t: { name: 'Time', unit: 's', color: '#00BCD4', min: 0.1, max: 100 },
    },
    calculate: (vars) => ({
      v: vars.d / vars.t,
      d: vars.v * vars.t,
      t: vars.d / vars.v,
    }),
    dependent: 'v',
  },
  
  momentum: {
    formula: 'p = m × v',
    latex: 'p = m \\times v',
    variables: {
      p: { name: 'Momentum', unit: 'kg·m/s', color: '#E91E63', min: 0, max: 500 },
      m: { name: 'Mass', unit: 'kg', color: '#4CAF50', min: 0.1, max: 50 },
      v: { name: 'Velocity', unit: 'm/s', color: '#9C27B0', min: 0, max: 100 },
    },
    calculate: (vars) => ({
      p: vars.m * vars.v,
      m: vars.p / vars.v,
      v: vars.p / vars.m,
    }),
    dependent: 'p',
  },
  
  kinetic_energy: {
    formula: 'KE = ½mv²',
    latex: 'KE = \\frac{1}{2}mv^2',
    variables: {
      KE: { name: 'Kinetic Energy', unit: 'J', color: '#FF5722', min: 0, max: 5000 },
      m: { name: 'Mass', unit: 'kg', color: '#4CAF50', min: 0.1, max: 50 },
      v: { name: 'Velocity', unit: 'm/s', color: '#9C27B0', min: 0, max: 100 },
    },
    calculate: (vars) => ({
      KE: 0.5 * vars.m * vars.v * vars.v,
      m: (2 * vars.KE) / (vars.v * vars.v),
      v: Math.sqrt((2 * vars.KE) / vars.m),
    }),
    dependent: 'KE',
  },
  
  potential_energy: {
    formula: 'PE = mgh',
    latex: 'PE = mgh',
    variables: {
      PE: { name: 'Potential Energy', unit: 'J', color: '#FF5722', min: 0, max: 5000 },
      m: { name: 'Mass', unit: 'kg', color: '#4CAF50', min: 0.1, max: 50 },
      g: { name: 'Gravity', unit: 'm/s²', color: '#795548', min: 1, max: 20, default: 9.8 },
      h: { name: 'Height', unit: 'm', color: '#2196F3', min: 0, max: 100 },
    },
    calculate: (vars) => ({
      PE: vars.m * vars.g * vars.h,
      m: vars.PE / (vars.g * vars.h),
      h: vars.PE / (vars.m * vars.g),
    }),
    dependent: 'PE',
  },
  
  gravity_force: {
    formula: 'W = mg',
    latex: 'W = mg',
    variables: {
      W: { name: 'Weight', unit: 'N', color: '#FF5722', min: 0, max: 1000 },
      m: { name: 'Mass', unit: 'kg', color: '#4CAF50', min: 0.1, max: 100 },
      g: { name: 'Gravity', unit: 'm/s²', color: '#795548', min: 1, max: 20, default: 9.8 },
    },
    calculate: (vars) => ({
      W: vars.m * vars.g,
      m: vars.W / vars.g,
    }),
    dependent: 'W',
  },
  
  ohms_law: {
    formula: 'V = IR',
    latex: 'V = IR',
    variables: {
      V: { name: 'Voltage', unit: 'V', color: '#FFC107', min: 0, max: 240 },
      I: { name: 'Current', unit: 'A', color: '#2196F3', min: 0, max: 10 },
      R: { name: 'Resistance', unit: 'Ω', color: '#FF5722', min: 0.1, max: 1000 },
    },
    calculate: (vars) => ({
      V: vars.I * vars.R,
      I: vars.V / vars.R,
      R: vars.V / vars.I,
    }),
    dependent: 'V',
  },
  
  // Chemistry
  moles: {
    formula: 'n = m / M',
    latex: 'n = \\frac{m}{M}',
    variables: {
      n: { name: 'Moles', unit: 'mol', color: '#9C27B0', min: 0, max: 100 },
      m: { name: 'Mass', unit: 'g', color: '#4CAF50', min: 0, max: 1000 },
      M: { name: 'Molar Mass', unit: 'g/mol', color: '#FF9800', min: 1, max: 500 },
    },
    calculate: (vars) => ({
      n: vars.m / vars.M,
      m: vars.n * vars.M,
      M: vars.m / vars.n,
    }),
    dependent: 'n',
  },
  
  // Math
  quadratic: {
    formula: 'y = ax² + bx + c',
    latex: 'y = ax^2 + bx + c',
    variables: {
      a: { name: 'a coefficient', unit: '', color: '#F44336', min: -10, max: 10, default: 1 },
      b: { name: 'b coefficient', unit: '', color: '#4CAF50', min: -20, max: 20, default: 0 },
      c: { name: 'c constant', unit: '', color: '#2196F3', min: -50, max: 50, default: 0 },
      x: { name: 'x value', unit: '', color: '#9C27B0', min: -10, max: 10, default: 0 },
      y: { name: 'y value', unit: '', color: '#FF9800', min: -100, max: 100 },
    },
    calculate: (vars) => ({
      y: vars.a * vars.x * vars.x + vars.b * vars.x + vars.c,
    }),
    dependent: 'y',
  },
  
  pythagoras: {
    formula: 'c² = a² + b²',
    latex: 'c^2 = a^2 + b^2',
    variables: {
      a: { name: 'Side a', unit: '', color: '#F44336', min: 0, max: 50 },
      b: { name: 'Side b', unit: '', color: '#4CAF50', min: 0, max: 50 },
      c: { name: 'Hypotenuse c', unit: '', color: '#2196F3', min: 0, max: 100 },
    },
    calculate: (vars) => ({
      c: Math.sqrt(vars.a * vars.a + vars.b * vars.b),
      a: Math.sqrt(vars.c * vars.c - vars.b * vars.b),
      b: Math.sqrt(vars.c * vars.c - vars.a * vars.a),
    }),
    dependent: 'c',
  },
  
  circle_area: {
    formula: 'A = πr²',
    latex: 'A = \\pi r^2',
    variables: {
      A: { name: 'Area', unit: '', color: '#FF5722', min: 0, max: 1000 },
      r: { name: 'Radius', unit: '', color: '#2196F3', min: 0, max: 20 },
    },
    calculate: (vars) => ({
      A: Math.PI * vars.r * vars.r,
      r: Math.sqrt(vars.A / Math.PI),
    }),
    dependent: 'A',
  },
};

// Object property mappings based on formula values
export const OBJECT_BINDINGS = {
  force: {
    ball: {
      size: { variable: 'm', scale: (v) => 10 + v * 3, min: 10, max: 40 },
      speed: { variable: 'a', scale: (v) => v / 10, min: 0.5, max: 5 },
    },
    arrow: {
      length: { variable: 'F', scale: (v) => 20 + v * 2, min: 20, max: 200 },
      thickness: { variable: 'F', scale: (v) => 2 + v / 10, min: 2, max: 12 },
      color: { variable: 'F', scale: (v) => v > 50 ? '#FF5722' : v > 20 ? '#FF9800' : '#FFC107' },
    },
  },
  
  velocity: {
    object: {
      speed: { variable: 'v', scale: (v) => v / 20, min: 0.1, max: 5 },
      blur: { variable: 'v', scale: (v) => Math.min(v / 10, 5), min: 0, max: 5 },
    },
    trail: {
      length: { variable: 'v', scale: (v) => Math.min(v / 5, 10), min: 1, max: 10 },
    },
  },
  
  momentum: {
    ball: {
      size: { variable: 'm', scale: (v) => 10 + v * 2, min: 10, max: 100 },
      glow: { variable: 'p', scale: (v) => v > 100 ? 20 : v > 50 ? 10 : 0 },
    },
  },
  
  energy: {
    object: {
      glow: { variable: 'KE', scale: (v) => Math.min(v / 100, 30), min: 0, max: 30 },
      vibration: { variable: 'KE', scale: (v) => v > 500 ? 5 : v > 100 ? 2 : 0 },
    },
  },
  
  gravity: {
    object: {
      fallSpeed: { variable: 'g', scale: (v) => v / 5, min: 0.5, max: 4 },
      y: { variable: 'h', scale: (v) => 200 - v * 2, min: 0, max: 200 },
    },
  },
};

/**
 * Custom hook for formula binding
 */
export function useFormulaBinding(formulaType, initialValues = {}) {
  const formulaDef = FORMULA_DEFINITIONS[formulaType];
  
  // Initialize values with defaults
  const getInitialValues = useCallback(() => {
    const values = {};
    Object.entries(formulaDef?.variables || {}).forEach(([key, config]) => {
      values[key] = initialValues[key] ?? config.default ?? (config.min + config.max) / 2;
    });
    return values;
  }, [formulaDef, initialValues]);
  
  const [values, setValues] = useState(getInitialValues);
  const [history, setHistory] = useState([getInitialValues()]);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [lastChanged, setLastChanged] = useState(null);
  const [animatingValue, setAnimatingValue] = useState(null);
  
  // Calculate dependent variable
  const calculatedValues = useMemo(() => {
    if (!formulaDef) return values;
    
    try {
      const calculated = formulaDef.calculate(values);
      return { ...values, ...calculated };
    } catch (e) {
      return values;
    }
  }, [values, formulaDef]);
  
  // Update a single value
  const setValue = useCallback((variable, newValue) => {
    setValues(prev => {
      const updated = { ...prev, [variable]: newValue };
      
      // Recalculate dependent variable
      if (formulaDef && variable !== formulaDef.dependent) {
        try {
          const calculated = formulaDef.calculate(updated);
          updated[formulaDef.dependent] = calculated[formulaDef.dependent];
        } catch (e) {
          // Keep previous value on error
        }
      }
      
      return updated;
    });
    
    setLastChanged(variable);
    setAnimatingValue(variable);
    setTimeout(() => setAnimatingValue(null), 300);
    
    // Add to history
    setHistory(prev => [...prev.slice(0, historyIndex + 1), values]);
    setHistoryIndex(prev => prev + 1);
  }, [formulaDef, historyIndex, values]);
  
  // Batch update multiple values
  const setMultipleValues = useCallback((newValues) => {
    setValues(prev => {
      const updated = { ...prev, ...newValues };
      
      if (formulaDef) {
        try {
          const calculated = formulaDef.calculate(updated);
          updated[formulaDef.dependent] = calculated[formulaDef.dependent];
        } catch (e) {
          // Keep previous values on error
        }
      }
      
      return updated;
    });
  }, [formulaDef]);
  
  // Undo/Redo
  const undo = useCallback(() => {
    if (historyIndex > 0) {
      setHistoryIndex(prev => prev - 1);
      setValues(history[historyIndex - 1]);
    }
  }, [historyIndex, history]);
  
  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(prev => prev + 1);
      setValues(history[historyIndex + 1]);
    }
  }, [historyIndex, history]);
  
  // Reset to initial values
  const reset = useCallback(() => {
    const initial = getInitialValues();
    setValues(initial);
    setHistory([initial]);
    setHistoryIndex(0);
    setLastChanged(null);
  }, [getInitialValues]);
  
  // Get object property based on binding
  const getObjectProperty = useCallback((objectType, propertyName) => {
    const bindings = OBJECT_BINDINGS[formulaType]?.[objectType];
    if (!bindings || !bindings[propertyName]) return null;
    
    const binding = bindings[propertyName];
    const value = calculatedValues[binding.variable];
    
    if (typeof binding.scale === 'function') {
      const scaled = binding.scale(value);
      return Math.max(binding.min || 0, Math.min(binding.max || Infinity, scaled));
    }
    
    return value;
  }, [formulaType, calculatedValues]);
  
  // Get variable config
  const getVariableConfig = useCallback((variable) => {
    return formulaDef?.variables?.[variable] || null;
  }, [formulaDef]);
  
  // Check if value is at extreme
  const isAtExtreme = useCallback((variable) => {
    const config = getVariableConfig(variable);
    if (!config) return { min: false, max: false };
    
    const value = calculatedValues[variable];
    return {
      min: value <= config.min,
      max: value >= config.max,
    };
  }, [calculatedValues, getVariableConfig]);
  
  return {
    // Values
    values: calculatedValues,
    rawValues: values,
    
    // Setters
    setValue,
    setMultipleValues,
    reset,
    
    // History
    undo,
    redo,
    canUndo: historyIndex > 0,
    canRedo: historyIndex < history.length - 1,
    
    // State
    lastChanged,
    animatingValue,
    
    // Helpers
    getObjectProperty,
    getVariableConfig,
    isAtExtreme,
    
    // Formula info
    formula: formulaDef?.formula,
    latex: formulaDef?.latex,
    variables: formulaDef?.variables || {},
    dependent: formulaDef?.dependent,
  };
}

/**
 * Format value with unit
 */
export function formatValue(value, variable, formulaType) {
  const config = FORMULA_DEFINITIONS[formulaType]?.variables?.[variable];
  if (!config) return String(value);
  
  const formatted = typeof value === 'number' ? value.toFixed(2) : value;
  return config.unit ? `${formatted} ${config.unit}` : formatted;
}

/**
 * Get color for value change animation
 */
export function getChangeColor(oldValue, newValue) {
  if (newValue > oldValue) return '#4CAF50'; // Green for increase
  if (newValue < oldValue) return '#F44336'; // Red for decrease
  return '#9E9E9E'; // Gray for no change
}

/**
 * Calculate percentage of value within range
 */
export function valueToPercent(value, min, max) {
  return ((value - min) / (max - min)) * 100;
}

/**
 * Calculate value from percentage within range
 */
export function percentToValue(percent, min, max) {
  return min + (percent / 100) * (max - min);
}

export default {
  FORMULA_DEFINITIONS,
  OBJECT_BINDINGS,
  useFormulaBinding,
  formatValue,
  getChangeColor,
  valueToPercent,
  percentToValue,
};



