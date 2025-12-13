/**
 * 🔀 MODE ROUTER
 * ===============
 * 
 * Selects and renders the appropriate mode based on blueprint
 * Central orchestrator for 8 master modes
 */

import React from 'react';
import SceneMode from './SceneMode';
import ComparisonMode from './ComparisonMode';
import ProcessMode from './ProcessMode';
import CycleMode from './CycleMode';
import StructureMode from './StructureMode';
import GraphMode from './GraphMode';
import TimelineMode from './TimelineMode';
import HierarchyMode from './HierarchyMode';

// Mode enum (matches ConceptBreaker)
export const MODES = {
  SCENE: 'SCENE',
  COMPARISON: 'COMPARISON',
  PROCESS: 'PROCESS',
  CYCLE: 'CYCLE',
  STRUCTURE: 'STRUCTURE',
  GRAPH: 'GRAPH',
  TIMELINE: 'TIMELINE',
  HIERARCHY: 'HIERARCHY',
};

/**
 * Mode Router Component
 * Selects appropriate mode renderer based on blueprint
 */
export const ModeRouter = ({
  blueprint,
  animationState = {},
  fallbackMode = MODES.SCENE,
}) => {
  const mode = blueprint.mode || fallbackMode;
  
  // Select mode component
  const ModeComponent = getModeComponent(mode);
  
  if (!ModeComponent) {
    console.warn(`Unknown mode: ${mode}, falling back to SCENE`);
    return <SceneMode blueprint={blueprint} animationState={animationState} />;
  }
  
  return <ModeComponent blueprint={blueprint} animationState={animationState} />;
};

/**
 * Get mode component by mode type
 */
export function getModeComponent(mode) {
  const modeMap = {
    [MODES.SCENE]: SceneMode,
    [MODES.COMPARISON]: ComparisonMode,
    [MODES.PROCESS]: ProcessMode,
    [MODES.CYCLE]: CycleMode,
    [MODES.STRUCTURE]: StructureMode,
    [MODES.GRAPH]: GraphMode,
    [MODES.TIMELINE]: TimelineMode,
    [MODES.HIERARCHY]: HierarchyMode,
  };
  
  return modeMap[mode] || null;
}

/**
 * Get mode metadata
 */
export function getModeMetadata(mode) {
  const metadata = {
    [MODES.SCENE]: {
      name: 'Scene',
      icon: '🎬',
      description: 'Physical scenarios, forces, motion',
      bestFor: ['Physics concepts', 'Cause-effect', 'Real-world scenarios'],
    },
    [MODES.COMPARISON]: {
      name: 'Comparison',
      icon: '⚖️',
      description: 'Side-by-side comparison (X vs Y)',
      bestFor: ['Comparing concepts', 'Pros vs cons', 'Differences'],
    },
    [MODES.PROCESS]: {
      name: 'Process',
      icon: '🔄',
      description: 'Step-by-step sequential flow',
      bestFor: ['Processes', 'Algorithms', 'Procedures'],
    },
    [MODES.CYCLE]: {
      name: 'Cycle',
      icon: '♻️',
      description: 'Circular loops and repeating processes',
      bestFor: ['Natural cycles', 'Feedback loops', 'Circular processes'],
    },
    [MODES.STRUCTURE]: {
      name: 'Structure',
      icon: '🏗️',
      description: 'Labeled diagrams and anatomical structures',
      bestFor: ['Anatomy', 'Molecular structure', 'System components'],
    },
    [MODES.GRAPH]: {
      name: 'Graph',
      icon: '📊',
      description: 'Mathematical plots and function graphs',
      bestFor: ['Functions', 'Data plots', 'Relationships'],
    },
    [MODES.TIMELINE]: {
      name: 'Timeline',
      icon: '⏰',
      description: 'Chronological sequences and historical events',
      bestFor: ['History', 'Evolution', 'Sequential events'],
    },
    [MODES.HIERARCHY]: {
      name: 'Hierarchy',
      icon: '🌳',
      description: 'Tree structures and hierarchical relationships',
      bestFor: ['Taxonomies', 'Org charts', 'Classification'],
    },
  };
  
  return metadata[mode] || null;
}

/**
 * Get all available modes
 */
export function getAllModes() {
  return Object.values(MODES).map(mode => ({
    mode,
    ...getModeMetadata(mode),
  }));
}

export default ModeRouter;

