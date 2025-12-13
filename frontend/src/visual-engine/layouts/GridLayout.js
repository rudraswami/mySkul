/**
 * 📐 GRID LAYOUT
 * ==============
 * 
 * Regular grid arrangement for items
 * Best for: Periodic tables, comparison grids, structured data
 */

/**
 * Grid Layout Algorithm
 * @param {Array} items - Items to layout
 * @param {Object} options - Layout options
 * @returns {Object} Positioned items { [itemId]: {x, y} }
 */
export function gridLayout(items, options = {}) {
  const {
    columns = 3,
    spacing = 80,
    paddingX = 60,
    paddingY = 60,
    alignment = 'center', // 'center' | 'left' | 'right'
    canvasWidth = 400,
    canvasHeight = 300,
  } = options;
  
  const positions = {};
  const rows = Math.ceil(items.length / columns);
  
  // Calculate grid dimensions
  const gridWidth = (columns - 1) * spacing;
  const gridHeight = (rows - 1) * spacing;
  
  // Starting position based on alignment
  let startX;
  switch (alignment) {
    case 'left':
      startX = paddingX;
      break;
    case 'right':
      startX = canvasWidth - paddingX - gridWidth;
      break;
    case 'center':
    default:
      startX = (canvasWidth - gridWidth) / 2;
  }
  
  const startY = (canvasHeight - gridHeight) / 2;
  
  items.forEach((item, index) => {
    const col = index % columns;
    const row = Math.floor(index / columns);
    
    positions[item.id] = {
      x: startX + col * spacing,
      y: startY + row * spacing,
    };
  });
  
  return positions;
}

/**
 * Get grid bounds
 */
export function getGridBounds(itemCount, columns, spacing) {
  const rows = Math.ceil(itemCount / columns);
  return {
    width: (columns - 1) * spacing,
    height: (rows - 1) * spacing,
  };
}

export default gridLayout;

