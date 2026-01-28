/**
 * 🧬 PROCEDURAL GENERATORS REGISTRY
 * ==================================
 * 
 * Registry of all procedural generators.
 * Each generator converts params into RenderGraph nodes.
 * 
 * BIOLOGY FIRST: Starting with cell biology generators.
 */

import { 
  ProceduralNode, 
  GroupNode, 
  EllipseNode, 
  PathNode, 
  CircleNode,
  RectNode,
  TextNode
} from '../RenderGraph';

// ============================================
// GENERATOR REGISTRY
// ============================================

const generators = new Map();

export function registerGenerator(type, generatorFn) {
  generators.set(type, generatorFn);
}

export function getGenerator(type) {
  return generators.get(type);
}

export function hasGenerator(type) {
  return generators.has(type);
}

export function listGenerators() {
  return Array.from(generators.keys());
}

/**
 * Generate RenderGraph nodes from a procedural spec
 */
export function generateNodes(generatorType, params, context = {}) {
  const generator = generators.get(generatorType);
  
  if (!generator) {
    console.warn(`Unknown generator type: ${generatorType}`);
    return createFallbackNode(params);
  }
  
  return generator(params, context);
}

function createFallbackNode(params) {
  return [new EllipseNode({
    width: params.width || 100,
    height: params.height || 100,
    fill: { type: 'solid', color: '#E5E7EB' },
    stroke: { color: '#9CA3AF', width: 2 },
  })];
}

// ============================================
// BIOLOGY GENERATORS
// ============================================

/**
 * ORGANIC_SHAPE: Cell-like irregular shape with membrane
 * 🎨 ALWAYS renders FILLED shapes - never just outlines!
 */
registerGenerator('organic_shape', (params, context) => {
  const {
    baseShape = 'ellipse',
    width = 200,
    height = 150,
    irregularity = 0.15,
    membrane = null,
    innerStructures = null,
    color = '#22C55E',
    innerColor = '#166534',
  } = params;

  const nodes = [];
  
  // 🎨 Create gradient fill from params (ALWAYS filled!)
  const fillColor = color || '#22C55E';
  const fill = { type: 'gradient', gradient: { type: 'radial', colors: [lightenColor(fillColor, 0.4), fillColor] } };
  
  // Generate irregular path for organic shape
  const path = generateOrganicPath(width, height, irregularity);
  
  // Main body - ALWAYS FILLED with gradient
  const bodyNode = new PathNode({
    id: `organic_body_${Date.now()}`,
    d: path,
    fill: fill,  // 🎨 ALWAYS use fill!
    stroke: { color: innerColor || darkenColor(fillColor), width: 2 },
  });
  nodes.push(bodyNode);
  
  // Membrane (double line) - additional visual detail
  if (membrane) {
    const membraneOuter = new PathNode({
      id: `membrane_outer_${Date.now()}`,
      d: path,
      fill: null,
      stroke: { color: membrane.color || innerColor || '#166534', width: membrane.thickness || 4 },
    });
    nodes.push(membraneOuter);
    
    if (membrane.double) {
      const innerPath = generateOrganicPath(width - 8, height - 8, irregularity);
      const membraneInner = new PathNode({
        id: `membrane_inner_${Date.now()}`,
        d: innerPath,
        fill: null,
        stroke: { color: membrane.color || innerColor || '#166534', width: 2 },
      });
      nodes.push(membraneInner);
    }
  }
  
  // Auto-add inner structures for visual richness
  const autoStructures = innerStructures || { type: 'dots', count: 3, color: innerColor || darkenColor(fillColor) };
  const structureNodes = generateInnerStructures(width, height, autoStructures);
  nodes.push(...structureNodes);
  
  return nodes;
});

/**
 * Generate SVG path for organic (slightly irregular) shape
 */
function generateOrganicPath(width, height, irregularity) {
  const cx = 0;
  const cy = 0;
  const rx = width / 2;
  const ry = height / 2;
  const points = 12;
  
  let d = '';
  const pathPoints = [];
  
  for (let i = 0; i < points; i++) {
    const angle = (Math.PI * 2 * i) / points;
    const wobble = 1 + (Math.random() - 0.5) * irregularity * 2;
    const x = cx + Math.cos(angle) * rx * wobble;
    const y = cy + Math.sin(angle) * ry * wobble;
    pathPoints.push({ x, y });
  }
  
  // Create smooth bezier curve through points
  d = `M ${pathPoints[0].x} ${pathPoints[0].y}`;
  
  for (let i = 0; i < pathPoints.length; i++) {
    const p0 = pathPoints[(i - 1 + pathPoints.length) % pathPoints.length];
    const p1 = pathPoints[i];
    const p2 = pathPoints[(i + 1) % pathPoints.length];
    const p3 = pathPoints[(i + 2) % pathPoints.length];
    
    // Calculate control points for smooth curve
    const cp1x = p1.x + (p2.x - p0.x) * 0.2;
    const cp1y = p1.y + (p2.y - p0.y) * 0.2;
    const cp2x = p2.x - (p3.x - p1.x) * 0.2;
    const cp2y = p2.y - (p3.y - p1.y) * 0.2;
    
    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
  }
  
  d += ' Z';
  return d;
}

/**
 * Generate inner cell structures
 */
function generateInnerStructures(width, height, spec) {
  const nodes = [];
  const { type, count, color } = spec;
  
  const maxRadius = Math.min(width, height) * 0.35;
  
  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
    const dist = maxRadius * (0.3 + Math.random() * 0.5);
    const x = Math.cos(angle) * dist;
    const y = Math.sin(angle) * dist;
    
    if (type === 'dots') {
      nodes.push(new CircleNode({
        position: { x, y },
        width: 8 + Math.random() * 8,
        fill: { type: 'solid', color: color || '#166534' },
      }));
    } else if (type === 'organelles') {
      nodes.push(new EllipseNode({
        position: { x, y },
        width: 20 + Math.random() * 15,
        height: 12 + Math.random() * 10,
        transform: { rotation: Math.random() * 360 },
        fill: { type: 'solid', color: color || '#166534' },
      }));
    }
  }
  
  return nodes;
}

/**
 * CHLOROPLAST: Organelle with thylakoid stacks
 * 🎨 Beautiful, detailed rendering of chloroplast
 */
registerGenerator('chloroplast', (params, context) => {
  const {
    width = 220,
    height = 140,
    stackCount = 5,
    color = '#22C55E',
    innerColor = null,
  } = params;

  const nodes = [];
  const actualInnerColor = innerColor || darkenColor(color, 0.3);
  
  // 🎨 Outer membrane with beautiful gradient fill
  const outerPath = generateOrganicPath(width, height, 0.08);
  nodes.push(new PathNode({
    d: outerPath,
    fill: { type: 'gradient', gradient: { type: 'radial', colors: [lightenColor(color, 0.5), color] } },
    stroke: { color: actualInnerColor, width: 3 },
  }));
  
  // Inner membrane for double-membrane effect
  const innerPath = generateOrganicPath(width - 16, height - 16, 0.05);
  nodes.push(new PathNode({
    d: innerPath,
    fill: null,
    stroke: { color: actualInnerColor, width: 2 },
  }));
  
  // 🎨 Thylakoid stacks (grana) - the signature visual
  const stackWidth = width * 0.12;
  const stackHeight = height * 0.5;
  const spacing = width / (stackCount + 1);
  
  for (let i = 0; i < stackCount; i++) {
    const x = -width / 2 + spacing * (i + 1);
    const stackNode = generateThylakoidStack(x, 0, stackWidth, stackHeight, actualInnerColor);
    nodes.push(stackNode);
  }
  
  // 🎨 Add some stroma dots for realism
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI * 2 * i) / 6;
    const dist = Math.min(width, height) * 0.3;
    const x = Math.cos(angle) * dist;
    const y = Math.sin(angle) * dist;
    nodes.push(new CircleNode({
      position: { x, y },
      width: 6 + Math.random() * 4,
      fill: { type: 'solid', color: lightenColor(color, 0.2) },
    }));
  }
  
  return nodes;
});

/**
 * Generate thylakoid stack (granum)
 */
function generateThylakoidStack(x, y, width, height, color) {
  const group = new GroupNode({ position: { x, y } });
  const discCount = 5;
  const discHeight = height / (discCount + 1);
  
  for (let i = 0; i < discCount; i++) {
    const discY = -height / 2 + discHeight * (i + 0.5);
    group.addChild(new RectNode({
      position: { x: 0, y: discY },
      width: width,
      height: discHeight * 0.7,
      cornerRadius: 3,
      fill: { type: 'solid', color },
    }));
  }
  
  return group;
}

/**
 * LEAF: Beautiful leaf shape with veins
 * 🎨 Detailed, filled leaf with gradient and veins
 */
registerGenerator('leaf', (params, context) => {
  const {
    width = 160,
    height = 100,
    veins = true,
    serration = 0,
    color = '#22C55E',
    innerColor = null,
    stemLength = 25,
  } = params;

  const nodes = [];
  const veinColor = innerColor || darkenColor(color, 0.3);
  
  // 🎨 Leaf body with beautiful gradient fill
  const leafPath = generateLeafPath(width, height, serration);
  nodes.push(new PathNode({
    d: leafPath,
    fill: { type: 'gradient', gradient: { type: 'linear', direction: 'vertical', colors: [lightenColor(color, 0.3), color] } },
    stroke: { color: veinColor, width: 2 },
  }));
  
  // Main vein (midrib) - prominent
  if (veins) {
    nodes.push(new PathNode({
      d: `M 0 ${-height/2 + 5} L 0 ${height/2 - 5}`,
      fill: null,
      stroke: { color: veinColor, width: 3 },
    }));
    
    // 🎨 Side veins with natural curve
    const veinCount = 5;
    for (let i = 0; i < veinCount; i++) {
      const y = -height / 2 + (height / (veinCount + 1)) * (i + 1);
      const veinLength = (width / 2) * (1 - Math.abs(y) / (height / 2) * 0.4) * 0.8;
      
      // Left vein with natural curve
      nodes.push(new PathNode({
        d: `M 0 ${y} Q ${-veinLength * 0.6} ${y - 8} ${-veinLength} ${y - 15}`,
        fill: null,
        stroke: { color: veinColor, width: 1.5 },
      }));
      
      // Right vein with natural curve
      nodes.push(new PathNode({
        d: `M 0 ${y} Q ${veinLength * 0.6} ${y - 8} ${veinLength} ${y - 15}`,
        fill: null,
        stroke: { color: veinColor, width: 1.5 },
      }));
    }
  }
  
  // Stem with gradient thickness
  if (stemLength > 0) {
    nodes.push(new PathNode({
      d: `M 0 ${height/2} L 0 ${height/2 + stemLength}`,
      fill: null,
      stroke: { color: darkenColor(color, 0.4), width: 4 },
    }));
  }
  
  return nodes;
});

/**
 * Generate leaf shape path
 */
function generateLeafPath(width, height, serration) {
  const hw = width / 2;
  const hh = height / 2;
  
  // Simple leaf shape with optional serration
  if (serration <= 0) {
    return `M 0 ${-hh} 
            Q ${hw} ${-hh * 0.5} ${hw * 0.8} 0 
            Q ${hw} ${hh * 0.5} 0 ${hh} 
            Q ${-hw} ${hh * 0.5} ${-hw * 0.8} 0 
            Q ${-hw} ${-hh * 0.5} 0 ${-hh} Z`;
  }
  
  // Serrated leaf
  let d = `M 0 ${-hh}`;
  const points = 8;
  
  for (let i = 0; i <= points; i++) {
    const t = i / points;
    const x = Math.sin(t * Math.PI) * hw * (1 - t * 0.3);
    const y = -hh + t * height;
    const serr = Math.sin(t * Math.PI * 4) * serration * 5;
    d += ` L ${x + serr} ${y}`;
  }
  
  for (let i = points; i >= 0; i--) {
    const t = i / points;
    const x = -Math.sin(t * Math.PI) * hw * (1 - t * 0.3);
    const y = -hh + t * height;
    const serr = Math.sin(t * Math.PI * 4) * serration * 5;
    d += ` L ${x + serr} ${y}`;
  }
  
  d += ' Z';
  return d;
}

/**
 * MOLECULE: Atoms connected by bonds
 */
registerGenerator('molecule', (params, context) => {
  const {
    atoms = [],
    bonds = [],
    style = '2d',
  } = params;

  const nodes = [];
  const atomColors = {
    'C': '#374151',
    'O': '#EF4444',
    'H': '#E5E7EB',
    'N': '#3B82F6',
    'S': '#EAB308',
    'P': '#F97316',
  };
  
  // Draw bonds first (behind atoms)
  for (const bond of bonds) {
    const fromAtom = atoms.find(a => a.id === bond.from);
    const toAtom = atoms.find(a => a.id === bond.to);
    
    if (fromAtom && toAtom) {
      const bondNode = new PathNode({
        d: `M ${fromAtom.position.x} ${fromAtom.position.y} L ${toAtom.position.x} ${toAtom.position.y}`,
        stroke: { color: '#6B7280', width: bond.type === 'double' ? 4 : bond.type === 'triple' ? 6 : 3 },
      });
      nodes.push(bondNode);
      
      // Double/triple bond lines
      if (bond.type === 'double' || bond.type === 'triple') {
        const dx = toAtom.position.x - fromAtom.position.x;
        const dy = toAtom.position.y - fromAtom.position.y;
        const len = Math.sqrt(dx * dx + dy * dy);
        const nx = -dy / len * 4;
        const ny = dx / len * 4;
        
        nodes.push(new PathNode({
          d: `M ${fromAtom.position.x + nx} ${fromAtom.position.y + ny} L ${toAtom.position.x + nx} ${toAtom.position.y + ny}`,
          stroke: { color: '#6B7280', width: 2 },
        }));
        
        if (bond.type === 'triple') {
          nodes.push(new PathNode({
            d: `M ${fromAtom.position.x - nx} ${fromAtom.position.y - ny} L ${toAtom.position.x - nx} ${toAtom.position.y - ny}`,
            stroke: { color: '#6B7280', width: 2 },
          }));
        }
      }
    }
  }
  
  // Draw atoms
  for (const atom of atoms) {
    const radius = atom.radius || 15;
    const color = atom.color || atomColors[atom.element] || '#9CA3AF';
    
    // Atom circle
    const atomNode = new CircleNode({
      position: atom.position,
      width: radius * 2,
      fill: { type: 'gradient', gradient: { type: 'radial', colors: [lightenColor(color), color] } },
      stroke: { color: darkenColor(color), width: 2 },
      effects: [{ type: 'shadow', params: { offsetX: 2, offsetY: 2 } }],
    });
    nodes.push(atomNode);
    
    // Atom label
    if (atom.label !== false) {
      nodes.push(new TextNode({
        position: atom.position,
        text: atom.element,
        fontSize: radius * 0.8,
        fontWeight: 'bold',
        fill: { type: 'solid', color: getContrastColor(color) },
      }));
    }
  }
  
  return nodes;
});

// ============================================
// PHYSICS GENERATORS
// ============================================

/**
 * SURFACE: Ground/surface with texture
 */
registerGenerator('surface', (params, context) => {
  const {
    width = 600,
    height = 30,
    texture = 'rough',
    friction = 0.5,
    color = '#78716C',
    perspective = false,
  } = params;

  const nodes = [];
  
  // Main surface
  nodes.push(new RectNode({
    width,
    height,
    fill: { type: 'gradient', gradient: { type: 'linear', direction: 'vertical', colors: [lightenColor(color), color] } },
    stroke: { color: darkenColor(color), width: 2 },
  }));
  
  // Texture overlay
  if (texture === 'rough') {
    for (let i = 0; i < width / 20; i++) {
      const x = -width / 2 + i * 20 + Math.random() * 10;
      const y = -height / 2 + Math.random() * height;
      nodes.push(new CircleNode({
        position: { x, y },
        width: 3 + Math.random() * 4,
        fill: { type: 'solid', color: darkenColor(color) },
      }));
    }
  }
  
  return nodes;
});

// ============================================
// MORE BIOLOGY GENERATORS
// ============================================

/**
 * MITOCHONDRIA: Organelle with cristae folds
 */
registerGenerator('mitochondria', (params, context) => {
  const {
    width = 150,
    height = 80,
    cristaeFolds = 5,
    color = '#EC4899',
    innerColor = null,
  } = params;

  const nodes = [];
  const actualInnerColor = innerColor || darkenColor(color, 0.3);
  
  // Outer membrane (bean shape)
  const outerPath = generateMitochondriaPath(width, height);
  nodes.push(new PathNode({
    d: outerPath,
    fill: { type: 'gradient', gradient: { type: 'radial', colors: [lightenColor(color, 0.4), color] } },
    stroke: { color: actualInnerColor, width: 3 },
  }));
  
  // Inner membrane (slightly smaller)
  const innerPath = generateMitochondriaPath(width - 10, height - 10);
  nodes.push(new PathNode({
    d: innerPath,
    fill: null,
    stroke: { color: actualInnerColor, width: 2 },
  }));
  
  // Cristae folds
  for (let i = 0; i < cristaeFolds; i++) {
    const x = -width * 0.35 + (width * 0.7 / (cristaeFolds + 1)) * (i + 1);
    const foldHeight = height * (0.4 + Math.random() * 0.2);
    const foldPath = `M ${x} ${-foldHeight/2} Q ${x + 8} 0 ${x} ${foldHeight/2}`;
    nodes.push(new PathNode({
      d: foldPath,
      fill: null,
      stroke: { color: actualInnerColor, width: 2 },
    }));
  }
  
  return nodes;
});

function generateMitochondriaPath(width, height) {
  const hw = width / 2;
  const hh = height / 2;
  // Bean-like elongated shape
  return `M ${-hw} 0 
          Q ${-hw} ${-hh} 0 ${-hh * 0.8}
          Q ${hw} ${-hh} ${hw} 0
          Q ${hw} ${hh} 0 ${hh * 0.8}
          Q ${-hw} ${hh} ${-hw} 0 Z`;
}

/**
 * NUCLEUS: Cell nucleus with chromatin
 */
registerGenerator('nucleus', (params, context) => {
  const {
    width = 120,
    height = 120,
    chromatinDensity = 0.6,
    color = '#6366F1',
    nucleolusColor = '#4F46E5',
  } = params;

  const nodes = [];
  
  // Nuclear envelope (double membrane)
  const outerPath = generateOrganicPath(width, height, 0.08);
  nodes.push(new PathNode({
    d: outerPath,
    fill: { type: 'gradient', gradient: { type: 'radial', colors: [lightenColor(color, 0.5), color] } },
    stroke: { color: darkenColor(color), width: 3 },
  }));
  
  const innerPath = generateOrganicPath(width - 8, height - 8, 0.05);
  nodes.push(new PathNode({
    d: innerPath,
    fill: null,
    stroke: { color: darkenColor(color), width: 2 },
  }));
  
  // Chromatin strands
  const strandCount = Math.floor(chromatinDensity * 8);
  for (let i = 0; i < strandCount; i++) {
    const angle = (Math.PI * 2 * i) / strandCount;
    const radius = (Math.min(width, height) / 2) * (0.3 + Math.random() * 0.4);
    const startX = Math.cos(angle) * radius * 0.5;
    const startY = Math.sin(angle) * radius * 0.5;
    const endX = Math.cos(angle + 0.5) * radius;
    const endY = Math.sin(angle + 0.5) * radius;
    
    nodes.push(new PathNode({
      d: `M ${startX} ${startY} Q ${(startX + endX) / 2 + 10} ${(startY + endY) / 2 - 10} ${endX} ${endY}`,
      fill: null,
      stroke: { color: darkenColor(color, 0.1), width: 2 },
    }));
  }
  
  // Nucleolus (darker sphere inside)
  const nucleolusSize = Math.min(width, height) * 0.25;
  nodes.push(new CircleNode({
    position: { x: width * 0.1, y: -height * 0.05 },
    width: nucleolusSize,
    fill: { type: 'gradient', gradient: { type: 'radial', colors: [nucleolusColor, darkenColor(nucleolusColor)] } },
    stroke: { color: darkenColor(nucleolusColor), width: 1 },
  }));
  
  return nodes;
});

/**
 * DNA_HELIX: DNA double helix
 */
registerGenerator('dna_helix', (params, context) => {
  const {
    length = 200,
    turns = 3,
    color = '#8B5CF6',
    secondaryColor = '#EC4899',
    width = 40,
  } = params;

  const nodes = [];
  const steps = turns * 12;
  const stepHeight = length / steps;
  
  // Generate helix points
  const strand1Points = [];
  const strand2Points = [];
  
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const angle = t * turns * Math.PI * 2;
    const y = -length / 2 + t * length;
    const x1 = Math.sin(angle) * (width / 2);
    const x2 = Math.sin(angle + Math.PI) * (width / 2);
    
    strand1Points.push({ x: x1, y });
    strand2Points.push({ x: x2, y });
  }
  
  // Draw strands
  let strand1Path = `M ${strand1Points[0].x} ${strand1Points[0].y}`;
  let strand2Path = `M ${strand2Points[0].x} ${strand2Points[0].y}`;
  
  for (let i = 1; i < strand1Points.length; i++) {
    strand1Path += ` L ${strand1Points[i].x} ${strand1Points[i].y}`;
    strand2Path += ` L ${strand2Points[i].x} ${strand2Points[i].y}`;
  }
  
  nodes.push(new PathNode({
    d: strand1Path,
    fill: null,
    stroke: { color: color, width: 4 },
  }));
  
  nodes.push(new PathNode({
    d: strand2Path,
    fill: null,
    stroke: { color: secondaryColor, width: 4 },
  }));
  
  // Base pair rungs
  for (let i = 0; i < steps; i += 2) {
    const angle = (i / steps) * turns * Math.PI * 2;
    // Only draw when strands are visible (not crossing over)
    if (Math.abs(Math.sin(angle)) > 0.3) {
      const y = -length / 2 + (i / steps) * length;
      const x1 = strand1Points[i].x;
      const x2 = strand2Points[i].x;
      
      nodes.push(new PathNode({
        d: `M ${x1} ${y} L ${x2} ${y}`,
        fill: null,
        stroke: { color: lightenColor(color, 0.3), width: 2 },
      }));
    }
  }
  
  return nodes;
});

// ============================================
// CHEMISTRY GENERATORS
// ============================================

/**
 * ATOM_ORBITAL: Atom with electron shells
 */
registerGenerator('atom_orbital', (params, context) => {
  const {
    element = 'C',
    shellConfig = [2, 4],  // Electrons per shell
    size = 100,
    animated = false,
    color = '#3B82F6',
  } = params;

  const nodes = [];
  
  // Nucleus
  const nucleusSize = size * 0.15;
  nodes.push(new CircleNode({
    width: nucleusSize,
    fill: { type: 'gradient', gradient: { type: 'radial', colors: [lightenColor(color), darkenColor(color)] } },
    stroke: { color: darkenColor(color), width: 2 },
  }));
  
  // Element symbol
  nodes.push(new TextNode({
    text: element,
    fontSize: nucleusSize * 0.6,
    fontWeight: 'bold',
    fill: { type: 'solid', color: '#FFFFFF' },
  }));
  
  // Electron shells
  const shellCount = shellConfig.length;
  shellConfig.forEach((electronCount, shellIndex) => {
    const shellRadius = (size / 2) * (0.4 + shellIndex * 0.3);
    
    // Shell orbit circle
    nodes.push(new CircleNode({
      width: shellRadius * 2,
      fill: null,
      stroke: { color: `rgba(${hexToRgbArray(color).join(',')}, 0.3)`, width: 1 },
    }));
    
    // Electrons
    for (let e = 0; e < electronCount; e++) {
      const angle = (Math.PI * 2 * e) / electronCount;
      const x = Math.cos(angle) * shellRadius;
      const y = Math.sin(angle) * shellRadius;
      
      nodes.push(new CircleNode({
        position: { x, y },
        width: 8,
        fill: { type: 'solid', color: '#EF4444' },
        stroke: { color: '#B91C1C', width: 1 },
      }));
    }
  });
  
  return nodes;
});

/**
 * REACTION_ZONE: Highlighted reaction area
 */
registerGenerator('reaction_zone', (params, context) => {
  const {
    width = 150,
    height = 100,
    intensity = 0.8,
    color = '#F59E0B',
    pulseAnimation = true,
  } = params;

  const nodes = [];
  
  // Glowing zone background
  for (let i = 3; i >= 1; i--) {
    const scale = 1 + i * 0.1;
    const alpha = intensity * (1 - i * 0.2);
    nodes.push(new EllipseNode({
      width: width * scale,
      height: height * scale,
      fill: { type: 'solid', color: `rgba(${hexToRgbArray(color).join(',')}, ${alpha * 0.3})` },
    }));
  }
  
  // Core zone
  nodes.push(new EllipseNode({
    width,
    height,
    fill: { type: 'gradient', gradient: { type: 'radial', colors: [`rgba(${hexToRgbArray(color).join(',')}, 0.6)`, `rgba(${hexToRgbArray(color).join(',')}, 0.2)`] } },
    stroke: { color: color, width: 2 },
  }));
  
  return nodes;
});

// ============================================
// PHYSICS GENERATORS
// ============================================

/**
 * WAVE: Sinusoidal wave
 */
registerGenerator('wave', (params, context) => {
  const {
    width = 400,
    amplitude = 50,
    frequency = 2,
    phase = 0,
    animated = true,
    color = '#3B82F6',
    fill = false,
  } = params;

  const nodes = [];
  const points = [];
  const steps = 60;
  
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = -width / 2 + t * width;
    const y = Math.sin((t * frequency * Math.PI * 2) + phase) * amplitude;
    points.push({ x, y });
  }
  
  let path = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    path += ` L ${points[i].x} ${points[i].y}`;
  }
  
  if (fill) {
    path += ` L ${width / 2} ${amplitude} L ${-width / 2} ${amplitude} Z`;
    nodes.push(new PathNode({
      d: path,
      fill: { type: 'solid', color: `rgba(${hexToRgbArray(color).join(',')}, 0.2)` },
      stroke: { color: color, width: 3 },
    }));
  } else {
    nodes.push(new PathNode({
      d: path,
      fill: null,
      stroke: { color: color, width: 3 },
    }));
  }
  
  // Add wave crests markers
  for (let i = 0; i < frequency; i++) {
    const crestX = -width / 2 + (width / frequency) * (i + 0.25);
    const crestY = -amplitude;
    nodes.push(new CircleNode({
      position: { x: crestX, y: crestY },
      width: 8,
      fill: { type: 'solid', color: lightenColor(color) },
    }));
  }
  
  return nodes;
});

/**
 * FORCE_FIELD: Gradient force field visualization
 */
registerGenerator('force_field', (params, context) => {
  const {
    width = 200,
    height = 200,
    direction = 'radial',  // radial, linear
    intensity = 0.7,
    color = '#8B5CF6',
    arrowCount = 8,
  } = params;

  const nodes = [];
  
  // Field background
  nodes.push(new EllipseNode({
    width,
    height,
    fill: { type: 'gradient', gradient: { 
      type: direction === 'radial' ? 'radial' : 'linear',
      colors: [`rgba(${hexToRgbArray(color).join(',')}, ${intensity * 0.4})`, `rgba(${hexToRgbArray(color).join(',')}, 0.05)`]
    }},
  }));
  
  // Force arrows
  for (let i = 0; i < arrowCount; i++) {
    const angle = (Math.PI * 2 * i) / arrowCount;
    const dist = Math.min(width, height) * 0.35;
    const x = Math.cos(angle) * dist;
    const y = Math.sin(angle) * dist;
    
    // Arrow pointing outward (or inward based on direction)
    const arrowLength = 20;
    const arrowAngle = direction === 'radial' ? angle : Math.PI / 2;
    const endX = x + Math.cos(arrowAngle) * arrowLength;
    const endY = y + Math.sin(arrowAngle) * arrowLength;
    
    nodes.push(new PathNode({
      d: `M ${x} ${y} L ${endX} ${endY}`,
      stroke: { color: color, width: 2 },
    }));
    
    // Arrow head
    const headSize = 6;
    const headAngle1 = arrowAngle + Math.PI * 0.8;
    const headAngle2 = arrowAngle - Math.PI * 0.8;
    nodes.push(new PathNode({
      d: `M ${endX} ${endY} L ${endX + Math.cos(headAngle1) * headSize} ${endY + Math.sin(headAngle1) * headSize} M ${endX} ${endY} L ${endX + Math.cos(headAngle2) * headSize} ${endY + Math.sin(headAngle2) * headSize}`,
      stroke: { color: color, width: 2 },
    }));
  }
  
  return nodes;
});

/**
 * MOTION_TRAIL: Motion path trail
 */
registerGenerator('motion_trail', (params, context) => {
  const {
    points = [{ x: 0, y: 0 }, { x: 100, y: 50 }],
    fadeLength = 5,
    color = '#EF4444',
    dotted = false,
    showArrow = true,
  } = params;

  if (points.length < 2) return [];
  
  const nodes = [];
  
  // Trail path
  let path = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    path += ` L ${points[i].x} ${points[i].y}`;
  }
  
  nodes.push(new PathNode({
    d: path,
    stroke: { 
      color: color, 
      width: 3,
      dash: dotted ? [8, 4] : null,
    },
  }));
  
  // Fade trail dots
  const totalLength = points.reduce((sum, p, i) => {
    if (i === 0) return 0;
    const prev = points[i - 1];
    return sum + Math.sqrt((p.x - prev.x) ** 2 + (p.y - prev.y) ** 2);
  }, 0);
  
  for (let i = 0; i < fadeLength; i++) {
    const t = i / fadeLength;
    const idx = Math.floor(t * (points.length - 1));
    const localT = (t * (points.length - 1)) - idx;
    const p1 = points[idx];
    const p2 = points[Math.min(idx + 1, points.length - 1)];
    
    const x = p1.x + (p2.x - p1.x) * localT;
    const y = p1.y + (p2.y - p1.y) * localT;
    const alpha = 1 - t;
    
    nodes.push(new CircleNode({
      position: { x, y },
      width: 6 * alpha + 2,
      fill: { type: 'solid', color: `rgba(${hexToRgbArray(color).join(',')}, ${alpha})` },
    }));
  }
  
  // Arrow at end
  if (showArrow && points.length >= 2) {
    const last = points[points.length - 1];
    const prev = points[points.length - 2];
    const angle = Math.atan2(last.y - prev.y, last.x - prev.x);
    const headSize = 10;
    
    const headAngle1 = angle + Math.PI * 0.8;
    const headAngle2 = angle - Math.PI * 0.8;
    
    nodes.push(new PathNode({
      d: `M ${last.x} ${last.y} L ${last.x + Math.cos(headAngle1) * headSize} ${last.y + Math.sin(headAngle1) * headSize} M ${last.x} ${last.y} L ${last.x + Math.cos(headAngle2) * headSize} ${last.y + Math.sin(headAngle2) * headSize}`,
      stroke: { color: color, width: 3 },
    }));
  }
  
  return nodes;
});

/**
 * FLOW_PATH: Curved path for flow visualization
 */
registerGenerator('flow_path', (params, context) => {
  const {
    points = [],
    curvature = 0.5,
    animated = true,
    dashPattern = null,
    color = '#3B82F6',
    width = 3,
  } = params;

  if (points.length < 2) return [];
  
  // Generate bezier curve through points
  let d = `M ${points[0].x} ${points[0].y}`;
  
  for (let i = 1; i < points.length; i++) {
    const p0 = points[i - 1];
    const p1 = points[i];
    const midX = (p0.x + p1.x) / 2;
    const midY = (p0.y + p1.y) / 2;
    
    const cpX = midX + (Math.random() - 0.5) * curvature * 50;
    const cpY = midY + (Math.random() - 0.5) * curvature * 50;
    
    d += ` Q ${cpX} ${cpY} ${p1.x} ${p1.y}`;
  }
  
  const pathNode = new PathNode({
    d,
    stroke: { 
      color, 
      width,
      dash: dashPattern || (animated ? [10, 5] : null),
    },
  });
  
  return [pathNode];
});

// ============================================
// UTILITY FUNCTIONS
// ============================================

function lightenColor(hex, amount = 0.3) {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.min(255, (num >> 16) + 255 * amount);
  const g = Math.min(255, ((num >> 8) & 0x00FF) + 255 * amount);
  const b = Math.min(255, (num & 0x0000FF) + 255 * amount);
  return `#${((1 << 24) + (Math.round(r) << 16) + (Math.round(g) << 8) + Math.round(b)).toString(16).slice(1)}`;
}

function darkenColor(hex, amount = 0.2) {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.max(0, (num >> 16) * (1 - amount));
  const g = Math.max(0, ((num >> 8) & 0x00FF) * (1 - amount));
  const b = Math.max(0, (num & 0x0000FF) * (1 - amount));
  return `#${((1 << 24) + (Math.round(r) << 16) + (Math.round(g) << 8) + Math.round(b)).toString(16).slice(1)}`;
}

function getContrastColor(hex) {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = (num >> 16) & 0xFF;
  const g = (num >> 8) & 0xFF;
  const b = num & 0xFF;
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#1F2937' : '#FFFFFF';
}

function hexToRgbArray(hex) {
  const num = parseInt(hex.replace('#', ''), 16);
  return [
    (num >> 16) & 0xFF,
    (num >> 8) & 0xFF,
    num & 0xFF
  ];
}

// ============================================
// EXPORTS
// ============================================

export default {
  registerGenerator,
  getGenerator,
  hasGenerator,
  listGenerators,
  generateNodes,
};
