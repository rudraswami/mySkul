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
    paddingX = 80,
    paddingY = 80,
    alignment = 'center', // 'center' | 'left' | 'right'
    canvasWidth = 400,
    canvasHeight = 300,
  } = options;
  
  const positions = {};
  
  if (!items || items.length === 0) return positions;
  
  // Auto-calculate columns if not enough items
  const actualColumns = Math.min(columns, items.length);
  const rows = Math.ceil(items.length / actualColumns);
  
  // CANVAS-AWARE: Calculate spacing to fill available space
  const availableWidth = canvasWidth - 2 * paddingX;
  const availableHeight = canvasHeight - 2 * paddingY;
  
  const spacingX = actualColumns > 1 ? availableWidth / (actualColumns - 1) : 0;
  const spacingY = rows > 1 ? availableHeight / (rows - 1) : 0;
  
  // Starting position - center single items
  let startX;
  switch (alignment) {
    case 'left':
      startX = paddingX;
      break;
    case 'right':
      startX = canvasWidth - paddingX;
      break;
    case 'center':
    default:
      startX = actualColumns === 1 ? canvasWidth / 2 : paddingX;
  }
  
  const startY = rows === 1 ? canvasHeight / 2 : paddingY;
  
  items.forEach((item, index) => {
    const col = index % actualColumns;
    const row = Math.floor(index / actualColumns);
    
    positions[item.id] = {
      x: actualColumns === 1 ? startX : paddingX + col * spacingX,
      y: rows === 1 ? startY : paddingY + row * spacingY,
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

