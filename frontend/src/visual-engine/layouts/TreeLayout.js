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
    levelSpacing = 80,
    siblingSpacing = 60,
    rootX = 200,
    rootY = 50,
  } = options;
  
  // Build tree structure
  const tree = buildTree(items);
  if (!tree) return {};
  
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
  
  return root;
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

