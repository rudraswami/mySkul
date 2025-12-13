/**
 * 📐 Layout Algorithms
 * ====================
 * 
 * Automatic positioning algorithms for visual elements
 */

// Layout algorithms (Phase 5 - COMPLETE)
export { default as ForceDirectedLayout, forceDirectedLayout } from './ForceDirectedLayout';
export { default as GridLayout, gridLayout, getGridBounds } from './GridLayout';
export { default as CircularLayout, circularLayout, hubLayout } from './CircularLayout';
export { default as TreeLayout, treeLayout, balancedTreeLayout } from './TreeLayout';
export { default as FlowLayout, flowLayout, zigzagLayout } from './FlowLayout';

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
