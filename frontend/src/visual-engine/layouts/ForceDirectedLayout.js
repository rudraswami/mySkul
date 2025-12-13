/**
 * 🧲 FORCE-DIRECTED LAYOUT
 * =========================
 * 
 * Physics-based layout using attraction/repulsion forces
 * Best for: Concept maps, network diagrams, organic layouts
 * 
 * Simplified force simulation (no D3 dependency)
 */

/**
 * Force-Directed Layout Algorithm
 * @param {Array} items - Items to layout
 * @param {Array} connections - Connections between items
 * @param {Object} options - Layout options
 * @returns {Object} Positioned items { [itemId]: {x, y} }
 */
export function forceDirectedLayout(items, connections = [], options = {}) {
  const {
    iterations = 50,
    repulsionStrength = 100,
    attractionStrength = 0.1,
    centerGravity = 0.05,
    canvasWidth = 400,
    canvasHeight = 300,
    damping = 0.8,
  } = options;
  
  // Initialize positions randomly
  const nodes = items.map(item => ({
    id: item.id,
    x: item.position?.x || Math.random() * canvasWidth,
    y: item.position?.y || Math.random() * canvasHeight,
    vx: 0, // velocity x
    vy: 0, // velocity y
  }));
  
  const nodeMap = {};
  nodes.forEach(node => {
    nodeMap[node.id] = node;
  });
  
  // Simulation loop
  for (let iter = 0; iter < iterations; iter++) {
    // Apply repulsion forces (all nodes repel each other)
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const nodeA = nodes[i];
        const nodeB = nodes[j];
        
        const dx = nodeB.x - nodeA.x;
        const dy = nodeB.y - nodeA.y;
        const distance = Math.sqrt(dx * dx + dy * dy) || 1;
        
        // Repulsion force (inverse square)
        const force = repulsionStrength / (distance * distance);
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;
        
        nodeA.vx -= fx;
        nodeA.vy -= fy;
        nodeB.vx += fx;
        nodeB.vy += fy;
      }
    }
    
    // Apply attraction forces (connected nodes attract)
    connections.forEach(conn => {
      const nodeA = nodeMap[conn.from];
      const nodeB = nodeMap[conn.to];
      
      if (!nodeA || !nodeB) return;
      
      const dx = nodeB.x - nodeA.x;
      const dy = nodeB.y - nodeA.y;
      const distance = Math.sqrt(dx * dx + dy * dy) || 1;
      
      // Spring force
      const force = distance * attractionStrength;
      const fx = (dx / distance) * force;
      const fy = (dy / distance) * force;
      
      nodeA.vx += fx;
      nodeA.vy += fy;
      nodeB.vx -= fx;
      nodeB.vy -= fy;
    });
    
    // Apply center gravity (pull towards canvas center)
    const centerX = canvasWidth / 2;
    const centerY = canvasHeight / 2;
    
    nodes.forEach(node => {
      const dx = centerX - node.x;
      const dy = centerY - node.y;
      
      node.vx += dx * centerGravity;
      node.vy += dy * centerGravity;
    });
    
    // Update positions with damping
    nodes.forEach(node => {
      node.x += node.vx;
      node.y += node.vy;
      
      node.vx *= damping;
      node.vy *= damping;
      
      // Keep within canvas bounds
      node.x = Math.max(30, Math.min(canvasWidth - 30, node.x));
      node.y = Math.max(30, Math.min(canvasHeight - 30, node.y));
    });
  }
  
  // Convert to position object
  const positions = {};
  nodes.forEach(node => {
    positions[node.id] = { x: node.x, y: node.y };
  });
  
  return positions;
}

export default forceDirectedLayout;

