/**
 * ⭕ CIRCULAR LAYOUT
 * ==================
 * 
 * Radial arrangement around a center point
 * Best for: Cycles, circular processes, hub-and-spoke diagrams
 */

/**
 * Circular Layout Algorithm
 * @param {Array} items - Items to layout
 * @param {Object} options - Layout options
 * @returns {Object} Positioned items { [itemId]: {x, y} }
 */
export function circularLayout(items, options = {}) {
  const {
    radius = 100,
    centerX = 200,
    centerY = 150,
    startAngle = -90, // Start at top (12 o'clock)
    clockwise = true,
    equalSpacing = true,
  } = options;
  
  const positions = {};
  const angleStep = 360 / items.length;
  
  items.forEach((item, index) => {
    const angle = equalSpacing
      ? startAngle + (clockwise ? 1 : -1) * angleStep * index
      : (item.angle || startAngle + angleStep * index);
    
    const rad = (angle * Math.PI) / 180;
    
    positions[item.id] = {
      x: centerX + radius * Math.cos(rad),
      y: centerY + radius * Math.sin(rad),
      angle, // Store angle for arrow calculations
    };
  });
  
  return positions;
}

/**
 * Circular layout with center node
 */
export function hubLayout(items, centerItem, options = {}) {
  const {
    radius = 100,
    centerX = 200,
    centerY = 150,
  } = options;
  
  const positions = {};
  
  // Position center
  if (centerItem) {
    positions[centerItem.id] = { x: centerX, y: centerY };
  }
  
  // Position satellites
  const satellites = centerItem ? items.filter(i => i.id !== centerItem.id) : items;
  const satellitePositions = circularLayout(satellites, { ...options, radius, centerX, centerY });
  
  return { ...positions, ...satellitePositions };
}

export default circularLayout;

