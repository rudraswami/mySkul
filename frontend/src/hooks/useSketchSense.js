/**
 * useSketchSense Hook V5.0
 * ========================
 * React hook for integrating SketchSense Universal visual engine.
 * 
 * V5.0 FEATURES:
 * - Multi-mode rendering support
 * - Professor output integration
 * - Auto mode detection
 * - Dynamic layout support
 * - Math plot parsing
 * - Trajectory rendering
 * 
 * This hook provides an ENHANCEMENT layer on top of existing visuals.
 * It does NOT replace existing visual functionality.
 * 
 * Usage:
 * const { blueprint, isReady, renderMode } = useSketchSense({
 *   concept: 'force',
 *   subject: 'physics',
 *   enabled: true,
 *   professorOutput: response, // V5.0 NEW
 * });
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import apiClient from '../api/client';

// Rendering modes (V5.0)
const RENDER_MODES = {
  CLASSIC: 'classic',
  CONCEPT_MAP: 'concept_map',
  PROCESS_FLOW: 'process_flow',
  MATH_PLOT: 'math_plot',
  TRAJECTORY: 'trajectory',
  BALANCE_SCALE: 'balance_scale',
  TIMELINE: 'timeline',
  STRUCTURE: 'structure',
};

// Default configuration
const DEFAULT_CONFIG = {
  enabled: true,
  autoPlay: true,
  showTest: true,
  showInteractions: true,
  styleMode: 'sketch' // sketch | neon | chalkboard | minimal
};

/**
 * Detect rendering mode from artifact structure
 */
function detectModeFromArtifact(artifact) {
  if (!artifact) return RENDER_MODES.CLASSIC;
  
  // Explicit mode
  if (artifact.mode) return artifact.mode;
  if (artifact.render_directives?.mode) return artifact.render_directives.mode;
  
  const config = artifact.config || artifact;
  
  // Math plot
  if (artifact.expression || config.function || config.math_expression) {
    return RENDER_MODES.MATH_PLOT;
  }
  
  // Trajectory
  if (config.motion || config.vx !== undefined || config.trajectory_points) {
    return RENDER_MODES.TRAJECTORY;
  }
  
  // Concept map
  if (config.nodes && config.relationships) {
    return RENDER_MODES.CONCEPT_MAP;
  }
  
  // Balance scale
  if (config.left_items && config.right_items) {
    return RENDER_MODES.BALANCE_SCALE;
  }
  
  return RENDER_MODES.CLASSIC;
}

/**
 * Extract visual config from professor output
 */
function extractFromProfessorOutput(professorOutput) {
  if (!professorOutput) return null;
  
  // Check various locations where visual config might be
  if (professorOutput.visual_config) {
    return professorOutput.visual_config;
  }
  
  if (professorOutput.diagram) {
    return { mode: 'structure', config: professorOutput.diagram };
  }
  
  if (professorOutput.steps && professorOutput.steps.length > 0) {
    return {
      mode: 'process_flow',
      config: { steps: professorOutput.steps }
    };
  }
  
  if (professorOutput.formula_plot || professorOutput.graph) {
    return {
      mode: 'math_plot',
      config: professorOutput.formula_plot || professorOutput.graph
    };
  }
  
  return null;
}

/**
 * Hook to fetch and manage SketchSense V5.0 blueprints
 */
export function useSketchSense({
  concept,
  subject,
  question,
  enabled = true,
  config = {},
  // V5.0 NEW: Professor output integration
  professorOutput = null,
  renderDirectives = null,
}) {
  const [blueprint, setBlueprint] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isReady, setIsReady] = useState(false);
  
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };
  
  // V5.0: Merge professor output with blueprint
  const effectiveBlueprint = useMemo(() => {
    const fromProfessor = extractFromProfessorOutput(professorOutput);
    if (fromProfessor) {
      return {
        ...blueprint,
        ...fromProfessor,
        render_directives: renderDirectives,
      };
    }
    return blueprint;
  }, [blueprint, professorOutput, renderDirectives]);
  
  // V5.0: Detect rendering mode
  const renderMode = useMemo(() => {
    return detectModeFromArtifact(effectiveBlueprint);
  }, [effectiveBlueprint]);
  
  // Fetch blueprint from backend
  const fetchBlueprint = useCallback(async () => {
    if (!concept || !subject || !enabled) {
      setBlueprint(null);
      setIsReady(false);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Try to fetch from backend API
      const response = await apiClient.post('/api/ai/sketchsense/blueprint', {
        concept,
        subject,
        question,
        config: mergedConfig
      });
      
      if (response.data?.blueprint) {
        setBlueprint(response.data.blueprint);
        setIsReady(true);
      }
    } catch (err) {
      console.warn('SketchSense API not available, using fallback:', err.message);
      
      // Fallback: Generate client-side blueprint
      const fallbackBlueprint = generateFallbackBlueprint(concept, subject);
      setBlueprint(fallbackBlueprint);
      setIsReady(true);
    } finally {
      setIsLoading(false);
    }
  }, [concept, subject, question, enabled, mergedConfig]);
  
  // Fetch on mount and when dependencies change
  useEffect(() => {
    fetchBlueprint();
  }, [fetchBlueprint]);
  
  // Manual refresh function
  const refresh = useCallback(() => {
    fetchBlueprint();
  }, [fetchBlueprint]);
  
  // Enhance existing visual with SketchSense data
  const enhanceVisual = useCallback((existingVisual) => {
    if (!effectiveBlueprint || !existingVisual) return existingVisual;
    
    return {
      ...existingVisual,
      sketchsense_v2: effectiveBlueprint,
      enhanced: true,
      enhancementVersion: '5.0',
      renderMode,
    };
  }, [effectiveBlueprint, renderMode]);
  
  // V5.0: Get props for ConfigDrivenSketch
  const getSketchProps = useCallback(() => ({
    blueprint: effectiveBlueprint,
    concept,
    subject,
    question,
    professorOutput,
    renderDirectives,
  }), [effectiveBlueprint, concept, subject, question, professorOutput, renderDirectives]);
  
  return {
    // Original API (preserved)
    blueprint: effectiveBlueprint,
    isLoading,
    isReady,
    error,
    config: mergedConfig,
    refresh,
    enhanceVisual,
    
    // V5.0 NEW
    renderMode,
    getSketchProps,
    RENDER_MODES,
  };
}

/**
 * Generate a fallback blueprint when API is not available
 * This ensures the UI still works during development
 */
function generateFallbackBlueprint(concept, subject) {
  const conceptTitle = concept.charAt(0).toUpperCase() + concept.slice(1);
  
  return {
    style: 'sketchsense',
    version: '2.0',
    stages: {
      coreSketch: {
        elements: [
          {
            id: 'concept_node',
            type: 'node',
            position: { x: 0.5, y: 0.4 },
            style: { fill: '#FF9933', stroke: '#000080', glow: true },
            content: conceptTitle,
            hindiContent: getHindiTerm(concept)
          },
          {
            id: 'related_0',
            type: 'node',
            position: { x: 0.25, y: 0.7 },
            style: { fill: '#138808', stroke: '#000080' },
            content: 'Related 1'
          },
          {
            id: 'related_1',
            type: 'node',
            position: { x: 0.5, y: 0.7 },
            style: { fill: '#138808', stroke: '#000080' },
            content: 'Related 2'
          },
          {
            id: 'related_2',
            type: 'node',
            position: { x: 0.75, y: 0.7 },
            style: { fill: '#138808', stroke: '#000080' },
            content: 'Related 3'
          },
          {
            id: 'arrow_0',
            type: 'arrow',
            position: { x: 0.5, y: 0.5, x2: 0.25, y2: 0.65 }
          },
          {
            id: 'arrow_1',
            type: 'arrow',
            position: { x: 0.5, y: 0.5, x2: 0.5, y2: 0.65 }
          },
          {
            id: 'arrow_2',
            type: 'arrow',
            position: { x: 0.5, y: 0.5, x2: 0.75, y2: 0.65 }
          }
        ]
      },
      animatedInsight: {
        animations: [
          { targetId: 'concept_node', type: 'draw_stroke', durationMs: 800 },
          { targetId: 'arrow_0', type: 'vector_grow', durationMs: 400, delayMs: 800 },
          { targetId: 'arrow_1', type: 'vector_grow', durationMs: 400, delayMs: 1000 },
          { targetId: 'arrow_2', type: 'vector_grow', durationMs: 400, delayMs: 1200 }
        ]
      },
      realLifeExample: {
        example: getRealLifeExample(concept, subject),
        emoji: getEmoji(concept),
        context: 'indian'
      },
      formulaOverlay: getFormula(concept),
      microTest: getMicroTest(subject)
    },
    interaction: {
      sliders: [],
      tapHighlights: [{ type: 'tap', targetId: 'concept_node', config: {} }],
      revealOnTap: []
    },
    style_config: {
      strokeStyle: 'sketch',
      neonHighlights: true,
      colorPalette: 'indian'
    }
  };
}

// Helper functions for fallback blueprint
function getHindiTerm(concept) {
  const terms = {
    force: 'बल',
    velocity: 'वेग',
    acceleration: 'त्वरण',
    mass: 'द्रव्यमान',
    energy: 'ऊर्जा',
    momentum: 'संवेग',
    photosynthesis: 'प्रकाश संश्लेषण',
    gravity: 'गुरुत्वाकर्षण'
  };
  return terms[concept.toLowerCase()] || null;
}

function getRealLifeExample(concept, subject) {
  const examples = {
    force: 'Diwali rocket pushing up → Newton\'s 3rd law in action! 🚀',
    velocity: 'Auto-rickshaw speed in traffic = distance/time! 🛺',
    gravity: 'Mango falling from tree → 9.8 m/s² everywhere! 🥭',
    photosynthesis: 'Tulsi plant making food from sunlight! 🌿'
  };
  return examples[concept.toLowerCase()] || `Real-life example of ${concept} in daily Indian life!`;
}

function getEmoji(concept) {
  const emojis = {
    force: '💪',
    velocity: '🚀',
    gravity: '🍎',
    photosynthesis: '🌿',
    acids: '🍋',
    bases: '🧼'
  };
  return emojis[concept.toLowerCase()] || '✨';
}

function getFormula(concept) {
  const formulas = {
    force: { formula: 'F = ma', latex: 'F = m \\times a', units: 'Newton (N)' },
    velocity: { formula: 'v = d/t', latex: 'v = \\frac{d}{t}', units: 'm/s' },
    acceleration: { formula: 'a = (v-u)/t', latex: 'a = \\frac{v-u}{t}', units: 'm/s²' },
    momentum: { formula: 'p = mv', latex: 'p = m \\times v', units: 'kg·m/s' }
  };
  return formulas[concept.toLowerCase()] || null;
}

function getMicroTest(subject) {
  const tests = {
    physics: {
      question: 'A 2kg object accelerates at 3m/s². What\'s the force?',
      options: ['5N', '6N', '1N', '9N'],
      correctIndex: 1,
      explanation: 'F = ma = 2 × 3 = 6N'
    },
    chemistry: {
      question: 'pH of lemon juice is approximately?',
      options: ['2-3', '7', '10-11', '14'],
      correctIndex: 0,
      explanation: 'Lemon juice is acidic with pH around 2-3'
    }
  };
  return tests[subject.toLowerCase()] || tests.physics;
}

export default useSketchSense;




