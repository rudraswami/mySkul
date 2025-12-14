/**
 * 🌳 TREE LAYOUT
 * ==============
 * 
 * Hierarchical tree structure
 * Best for: Taxonomies, org charts, classification hierarchies
 * 
 * Uses simplified Reingold-Tilford algorithm
 */

/**
 * Tree Layout Algorithm
 * @param {Array} items - Items with parent relationships
 * @param {Object} options - Layout options
 * @returns {Object} Positioned items { [itemId]: {x, y, level} }
 */
export function treeLayout(items, options = {}) {
  const {
    orientation = 'vertical', // 'vertical' | 'horizontal'
    canvasWidth = 400,
    canvasHeight = 300,
    paddingX = 80,
    paddingY = 60,
  } = options;
  
  // Build tree structure
  const tree = buildTree(items);
  if (!tree) return {};
  
  // CANVAS-AWARE: Calculate spacing based on tree depth and width
  const treeDepth = getTreeDepth(tree);
  const availableHeight = canvasHeight - 2 * paddingY;
  const levelSpacing = treeDepth > 1 ? availableHeight / (treeDepth - 1) : 0;
  
  // Root position (center-top for vertical)
  const rootX = canvasWidth / 2;
  const rootY = paddingY;
  
  // Calculate max width needed at each level
  const levelWidths = getLevelWidths(tree);
  const maxWidth = Math.max(...Object.values(levelWidths));
  const availableWidth = canvasWidth - 2 * paddingX;
  const siblingSpacing = maxWidth > 1 ? availableWidth / maxWidth : availableWidth;
  
  // Calculate positions
  const positions = {};
  
  function traverse(node, level = 0, xOffset = 0) {
    const childCount = node.children?.length || 0;
    const totalWidth = childCount > 0 ? (childCount - 1) * siblingSpacing : 0;
    
    if (orientation === 'vertical') {
      positions[node.id] = {
        x: rootX + xOffset,
        y: rootY + level * levelSpacing,
        level,
      };
    } else {
      positions[node.id] = {
        x: rootY + level * levelSpacing,
        y: rootX + xOffset,
        level,
      };
    }
    
    // Position children
    if (childCount > 0) {
      const startOffset = -totalWidth / 2;
      node.children.forEach((child, index) => {
        traverse(child, level + 1, xOffset + startOffset + index * siblingSpacing);
      });
    }
  }
  
  traverse(tree);
  
  return positions;
}

/**
 * Build tree structure from flat items
 * Assumes items have 'parentId' property
 */
function buildTree(items) {
  if (!items || items.length === 0) return null;
  
  const itemMap = {};
  items.forEach(item => {
    itemMap[item.id] = { ...item, children: [] };
  });
  
  let root = null;
  
  items.forEach(item => {
    if (!item.parentId) {
      root = itemMap[item.id];
    } else {
      const parent = itemMap[item.parentId];
      if (parent) {
        parent.children.push(itemMap[item.id]);
      }
    }
  });
  
  // If no explicit root, use first item
  if (!root && items.length > 0) {
    root = itemMap[items[0].id];
  }
  
  return root;
}

/**
 * Get tree depth (number of levels)
 */
function getTreeDepth(node, depth = 1) {
  if (!node || !node.children || node.children.length === 0) {
    return depth;
  }
  return Math.max(...node.children.map(child => getTreeDepth(child, depth + 1)));
}

/**
 * Get width (number of nodes) at each level
 */
function getLevelWidths(node, level = 0, widths = {}) {
  if (!node) return widths;
  
  widths[level] = (widths[level] || 0) + 1;
  
  if (node.children) {
    node.children.forEach(child => {
      getLevelWidths(child, level + 1, widths);
    });
  }
  
  return widths;
}

/**
 * Balanced tree layout (for complete binary trees)
 */
export function balancedTreeLayout(items, options = {}) {
  const {
    levelSpacing = 80,
    rootX = 200,
    rootY = 50,
  } = options;
  
  const positions = {};
  
  function positionNode(index, level, xOffset) {
    if (index >= items.length) return;
    
    const item = items[index];
    const x = rootX + xOffset;
    const y = rootY + level * levelSpacing;
    
    positions[item.id] = { x, y, level };
    
    // Position children
    const childSpacing = levelSpacing / Math.pow(2, level + 1);
    positionNode(2 * index + 1, level + 1, xOffset - childSpacing); // Left child
    positionNode(2 * index + 2, level + 1, xOffset + childSpacing); // Right child
  }
  
  positionNode(0, 0, 0);
  
  return positions;
}

export default treeLayout;

