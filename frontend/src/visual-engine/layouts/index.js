/**
 * 📐 Layout Algorithms
 * ====================
 * 
 * Automatic positioning algorithms for visual elements
 */

// IMPORT first (so variables are in scope for use below)
import { forceDirectedLayout } from './ForceDirectedLayout';
import { gridLayout, getGridBounds } from './GridLayout';
import { circularLayout, hubLayout } from './CircularLayout';
import { treeLayout, balancedTreeLayout } from './TreeLayout';
import { flowLayout, zigzagLayout } from './FlowLayout';

// RE-EXPORT for external consumers
export { forceDirectedLayout } from './ForceDirectedLayout';
export { gridLayout, getGridBounds } from './GridLayout';
export { circularLayout, hubLayout } from './CircularLayout';
export { treeLayout, balancedTreeLayout } from './TreeLayout';
export { flowLayout, zigzagLayout } from './FlowLayout';

// Default class exports
export { default as ForceDirectedLayout } from './ForceDirectedLayout';
export { default as GridLayout } from './GridLayout';
export { default as CircularLayout } from './CircularLayout';
export { default as TreeLayout } from './TreeLayout';
export { default as FlowLayout } from './FlowLayout';

// Layout types enum
export const LAYOUT_TYPES = {
  GRID: 'grid',
  CIRCULAR: 'circular',
  FLOW: 'flow',
  TREE: 'tree',
  FORCE_DIRECTED: 'force_directed',
  HUB: 'hub',
  BALANCED_TREE: 'balanced_tree',
  ZIGZAG: 'zigzag',
};

/**
 * Get layout algorithm by type
 */
export function getLayout(type) {
  switch (type) {
    case LAYOUT_TYPES.GRID:
      return gridLayout;
    case LAYOUT_TYPES.CIRCULAR:
      return circularLayout;
    case LAYOUT_TYPES.FLOW:
      return flowLayout;
    case LAYOUT_TYPES.TREE:
      return treeLayout;
    case LAYOUT_TYPES.FORCE_DIRECTED:
      return forceDirectedLayout;
    case LAYOUT_TYPES.HUB:
      return hubLayout;
    case LAYOUT_TYPES.BALANCED_TREE:
      return balancedTreeLayout;
    case LAYOUT_TYPES.ZIGZAG:
      return zigzagLayout;
    default:
      return flowLayout;
  }
}

export default {
  forceDirectedLayout,
  gridLayout,
  circularLayout,
  treeLayout,
  flowLayout,
  hubLayout,
  balancedTreeLayout,
  zigzagLayout,
  getLayout,
  LAYOUT_TYPES,
};
