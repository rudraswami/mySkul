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
    paddingStart = 80,
    paddingEnd = 80,
    alignment = 'center', // For cross-axis
    canvasWidth = 400,
    canvasHeight = 300,
  } = options;
  
  const positions = {};
  
  if (!items || items.length === 0) return positions;
  
  if (direction === 'horizontal') {
    // CANVAS-AWARE: Spread items across full width
    const availableWidth = canvasWidth - paddingStart - paddingEnd;
    const spacing = items.length > 1 ? availableWidth / (items.length - 1) : 0;
    const startX = items.length === 1 ? canvasWidth / 2 : paddingStart;
    
    // Vertical position based on alignment
    const y = alignment === 'center' 
      ? canvasHeight / 2 
      : (alignment === 'top' ? paddingStart : canvasHeight - paddingEnd);
    
    items.forEach((item, index) => {
      positions[item.id] = {
        x: items.length === 1 ? startX : paddingStart + index * spacing,
        y,
      };
    });
  } else {
    // CANVAS-AWARE: Spread items across full height
    const availableHeight = canvasHeight - paddingStart - paddingEnd;
    const spacing = items.length > 1 ? availableHeight / (items.length - 1) : 0;
    const startY = items.length === 1 ? canvasHeight / 2 : paddingStart;
    
    // Horizontal position based on alignment
    const x = alignment === 'center' 
      ? canvasWidth / 2 
      : (alignment === 'left' ? paddingStart : canvasWidth - paddingEnd);
    
    items.forEach((item, index) => {
      positions[item.id] = {
        x,
        y: items.length === 1 ? startY : paddingStart + index * spacing,
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

