/**
 * ✋ HAND MOTION PATH CALCULATOR
 * ==============================
 * 
 * Calculates smooth motion paths for the drawing hand
 * Synchronizes hand movement with stroke drawing
 */

/**
 * Calculate a smooth Bezier curve path between two points
 * @param {Object} start - {x, y}
 * @param {Object} end - {x, y}
 * @param {number} curvature - 0-1, amount of curve
 * @returns {string} SVG path string
 */
export function calculateBezierPath(start, end, curvature = 0.3) {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  
  // Control point offset perpendicular to line
  const controlOffset = distance * curvature;
  const angle = Math.atan2(dy, dx);
  const perpAngle = angle + Math.PI / 2;
  
  // Mid control point
  const midX = (start.x + end.x) / 2;
  const midY = (start.y + end.y) / 2;
  const controlX = midX + Math.cos(perpAngle) * controlOffset;
  const controlY = midY + Math.sin(perpAngle) * controlOffset;
  
  return `M ${start.x} ${start.y} Q ${controlX} ${controlY} ${end.x} ${end.y}`;
}

/**
 * Calculate multiple waypoints along a path
 * @param {Object[]} points - Array of {x, y} points
 * @param {number} smoothness - How smooth the path should be
 * @returns {string} SVG path string
 */
export function calculateSmoothPath(points, smoothness = 0.3) {
  if (points.length < 2) return '';
  if (points.length === 2) {
    return calculateBezierPath(points[0], points[1], smoothness);
  }
  
  let path = `M ${points[0].x} ${points[0].y}`;
  
  for (let i = 0; i < points.length - 1; i++) {
    const start = points[i];
    const end = points[i + 1];
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    const controlOffset = distance * smoothness;
    const angle = Math.atan2(dy, dx);
    const perpAngle = angle + Math.PI / 2;
    
    const midX = (start.x + end.x) / 2;
    const midY = (start.y + end.y) / 2;
    const controlX = midX + Math.cos(perpAngle) * controlOffset * (i % 2 === 0 ? 1 : -1);
    const controlY = midY + Math.sin(perpAngle) * controlOffset * (i % 2 === 0 ? 1 : -1);
    
    path += ` Q ${controlX} ${controlY} ${end.x} ${end.y}`;
  }
  
  return path;
}

/**
 * Get position along a path at a given progress (0-1)
 * @param {Object} start - {x, y}
 * @param {Object} end - {x, y}
 * @param {number} progress - 0 to 1
 * @returns {Object} {x, y, angle}
 */
export function getPositionAlongPath(start, end, progress) {
  const x = start.x + (end.x - start.x) * progress;
  const y = start.y + (end.y - start.y) * progress;
  const angle = Math.atan2(end.y - start.y, end.x - start.x) * (180 / Math.PI);
  
  return { x, y, angle };
}

/**
 * Get position along a Bezier curve at progress (0-1)
 * @param {Object} start - {x, y}
 * @param {Object} control - {x, y}
 * @param {Object} end - {x, y}
 * @param {number} progress - 0 to 1
 * @returns {Object} {x, y, angle}
 */
export function getPositionAlongBezier(start, control, end, progress) {
  const t = progress;
  const t2 = t * t;
  const mt = 1 - t;
  const mt2 = mt * mt;
  
  // Quadratic Bezier formula
  const x = mt2 * start.x + 2 * mt * t * control.x + t2 * end.x;
  const y = mt2 * start.y + 2 * mt * t * control.y + t2 * end.y;
  
  // Calculate tangent angle
  const dx = 2 * (1 - t) * (control.x - start.x) + 2 * t * (end.x - control.x);
  const dy = 2 * (1 - t) * (control.y - start.y) + 2 * t * (end.y - control.y);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  
  return { x, y, angle };
}

/**
 * Generate waypoints from blueprint items
 * @param {Array} items - Blueprint items with positions
 * @param {Array} drawOrder - Order to draw items in
 * @returns {Array} Array of {x, y, delay} waypoints
 */
export function generateWaypointsFromBlueprint(items, drawOrder = null) {
  if (!items || items.length === 0) return [];
  
  const orderedItems = drawOrder
    ? drawOrder.map(id => items.find(item => item.id === id)).filter(Boolean)
    : items.filter(item => item.position);
  
  return orderedItems.map((item, index) => ({
    x: item.position.x,
    y: item.position.y,
    delay: index * 0.5, // 0.5s between waypoints
    itemId: item.id,
  }));
}

/**
 * Calculate hand rotation angle to face drawing direction
 * @param {Object} from - {x, y}
 * @param {Object} to - {x, y}
 * @returns {number} Angle in degrees
 */
export function calculateHandRotation(from, to) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  
  // Adjust for hand orientation (pointing right by default)
  return angle;
}

/**
 * Apply easing to progress value
 * @param {number} progress - 0 to 1
 * @param {string} easingType - 'linear' | 'easeIn' | 'easeOut' | 'easeInOut'
 * @returns {number} Eased progress 0 to 1
 */
export function applyEasing(progress, easingType = 'easeInOut') {
  switch (easingType) {
    case 'linear':
      return progress;
    case 'easeIn':
      return progress * progress;
    case 'easeOut':
      return progress * (2 - progress);
    case 'easeInOut':
      return progress < 0.5
        ? 2 * progress * progress
        : -1 + (4 - 2 * progress) * progress;
    default:
      return progress;
  }
}

/**
 * Synchronize hand movement with stroke drawing animation
 * @param {number} strokeProgress - 0 to 1, progress of stroke drawing
 * @param {Object} start - {x, y}
 * @param {Object} end - {x, y}
 * @returns {Object} {x, y, angle, pose}
 */
export function synchronizeHandWithStroke(strokeProgress, start, end) {
  const easedProgress = applyEasing(strokeProgress, 'easeInOut');
  const position = getPositionAlongPath(start, end, easedProgress);
  
  // Determine pose based on progress
  let pose = 'drawing';
  if (strokeProgress < 0.05) {
    pose = 'idle'; // Just starting
  } else if (strokeProgress > 0.95) {
    pose = 'pointing'; // Just finished
  }
  
  return {
    ...position,
    pose,
  };
}

/**
 * Generate a complete hand motion timeline
 * @param {Array} waypoints - Array of {x, y, delay} waypoints
 * @param {number} drawDuration - Duration per stroke in seconds
 * @returns {Array} Timeline of {time, x, y, angle, pose}
 */
export function generateHandTimeline(waypoints, drawDuration = 1.5) {
  if (waypoints.length === 0) return [];
  
  const timeline = [];
  let currentTime = 0;
  
  // Start position (idle)
  timeline.push({
    time: 0,
    x: waypoints[0].x,
    y: waypoints[0].y,
    angle: 0,
    pose: 'idle',
  });
  
  // Movement between waypoints
  for (let i = 0; i < waypoints.length - 1; i++) {
    const start = waypoints[i];
    const end = waypoints[i + 1];
    const angle = calculateHandRotation(start, end);
    
    currentTime += start.delay || 0;
    
    // Drawing phase
    timeline.push({
      time: currentTime,
      x: start.x,
      y: start.y,
      angle,
      pose: 'drawing',
    });
    
    currentTime += drawDuration;
    
    // End of stroke
    timeline.push({
      time: currentTime,
      x: end.x,
      y: end.y,
      angle,
      pose: 'pointing',
    });
    
    // Pause at waypoint
    currentTime += 0.2;
    
    timeline.push({
      time: currentTime,
      x: end.x,
      y: end.y,
      angle,
      pose: 'idle',
    });
  }
  
  return timeline;
}

/**
 * Get hand state at specific time in timeline
 * @param {Array} timeline - Generated timeline
 * @param {number} currentTime - Current time in seconds
 * @returns {Object} {x, y, angle, pose}
 */
export function getHandStateAtTime(timeline, currentTime) {
  if (timeline.length === 0) {
    return { x: 0, y: 0, angle: 0, pose: 'idle' };
  }
  
  // Find the two timeline points to interpolate between
  let before = timeline[0];
  let after = timeline[timeline.length - 1];
  
  for (let i = 0; i < timeline.length - 1; i++) {
    if (currentTime >= timeline[i].time && currentTime <= timeline[i + 1].time) {
      before = timeline[i];
      after = timeline[i + 1];
      break;
    }
  }
  
  // If exact match
  if (before.time === after.time) {
    return before;
  }
  
  // Interpolate
  const progress = (currentTime - before.time) / (after.time - before.time);
  const easedProgress = applyEasing(progress, 'easeInOut');
  
  return {
    x: before.x + (after.x - before.x) * easedProgress,
    y: before.y + (after.y - before.y) * easedProgress,
    angle: before.angle + (after.angle - before.angle) * easedProgress,
    pose: progress < 0.5 ? before.pose : after.pose,
  };
}

export default {
  calculateBezierPath,
  calculateSmoothPath,
  getPositionAlongPath,
  getPositionAlongBezier,
  generateWaypointsFromBlueprint,
  calculateHandRotation,
  applyEasing,
  synchronizeHandWithStroke,
  generateHandTimeline,
  getHandStateAtTime,
};

