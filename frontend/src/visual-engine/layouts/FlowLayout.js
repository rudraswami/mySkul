/**
 * ➡️ FLOW LAYOUT
 * ===============
 * 
 * Left-to-right or top-to-bottom sequential flow
 * Best for: Process steps, timelines, sequential logic
 */

/**
 * Flow Layout Algorithm
 * @param {Array} items - Items to layout
 * @param {Object} options - Layout options
 * @returns {Object} Positioned items { [itemId]: {x, y} }
 */
export function flowLayout(items, options = {}) {
  const {
    direction = 'horizontal', // 'horizontal' | 'vertical'
    spacing = 80,
    paddingStart = 60,
    alignment = 'center', // For cross-axis
    canvasWidth = 400,
    canvasHeight = 300,
  } = options;
  
  const positions = {};
  
  if (direction === 'horizontal') {
    // Left to right
    const totalWidth = (items.length - 1) * spacing;
    const startX = paddingStart;
    const y = alignment === 'center' 
      ? canvasHeight / 2 
      : (alignment === 'top' ? paddingStart : canvasHeight - paddingStart);
    
    items.forEach((item, index) => {
      positions[item.id] = {
        x: startX + index * spacing,
        y,
      };
    });
  } else {
    // Top to bottom
    const totalHeight = (items.length - 1) * spacing;
    const startY = paddingStart;
    const x = alignment === 'center' 
      ? canvasWidth / 2 
      : (alignment === 'left' ? paddingStart : canvasWidth - paddingStart);
    
    items.forEach((item, index) => {
      positions[item.id] = {
        x,
        y: startY + index * spacing,
      };
    });
  }
  
  return positions;
}

/**
 * Zigzag flow layout
 */
export function zigzagLayout(items, options = {}) {
  const {
    amplitude = 50, // How far items zigzag
    spacing = 80,
    paddingStart = 60,
    canvasWidth = 400,
    canvasHeight = 300,
  } = options;
  
  const positions = {};
  const centerY = canvasHeight / 2;
  
  items.forEach((item, index) => {
    const offset = (index % 2 === 0) ? -amplitude : amplitude;
    
    positions[item.id] = {
      x: paddingStart + index * spacing,
      y: centerY + offset,
    };
  });
  
  return positions;
}

export default flowLayout;

