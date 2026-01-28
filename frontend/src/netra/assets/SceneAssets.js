/**
 * 🎨 SCENE ASSETS LIBRARY
 * =======================
 * 
 * Pre-built SVG assets for rich visual scenes.
 * These replace primitive shapes with actual illustrations.
 * 
 * ARCHITECTURE:
 * - LLM selects assets by ID, doesn't draw shapes
 * - Assets have anchor points for connections
 * - Assets can be animated (transform, opacity, filters)
 */

// ============================================
// BIOLOGY ASSETS
// ============================================

export const BIOLOGY_ASSETS = {
  // Photosynthesis scene
  plant_in_pot: {
    id: 'plant_in_pot',
    name: 'Plant in Pot',
    category: 'biology',
    width: 300,
    height: 400,
    anchors: {
      leaf: { x: 0.3, y: 0.3 },
      stem: { x: 0.5, y: 0.6 },
      roots: { x: 0.5, y: 0.85 },
      pot: { x: 0.5, y: 0.9 },
    },
    svg: `<svg viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
      <!-- Pot -->
      <path d="M75 320 L90 380 L210 380 L225 320 Z" fill="#D2691E" stroke="#8B4513" stroke-width="3"/>
      <ellipse cx="150" cy="320" rx="75" ry="15" fill="#CD853F"/>
      <ellipse cx="150" cy="320" rx="60" ry="10" fill="#8B4513"/>
      
      <!-- Soil -->
      <ellipse cx="150" cy="320" rx="55" ry="8" fill="#3D2914"/>
      
      <!-- Stem -->
      <path d="M150 320 Q145 250 150 180" stroke="#228B22" stroke-width="8" fill="none" stroke-linecap="round"/>
      
      <!-- Leaves -->
      <ellipse cx="100" cy="200" rx="50" ry="25" fill="#32CD32" transform="rotate(-30 100 200)"/>
      <ellipse cx="200" cy="180" rx="45" ry="22" fill="#32CD32" transform="rotate(25 200 180)"/>
      <ellipse cx="120" cy="140" rx="40" ry="20" fill="#3CB371" transform="rotate(-15 120 140)"/>
      <ellipse cx="180" cy="120" rx="42" ry="21" fill="#3CB371" transform="rotate(20 180 120)"/>
      <ellipse cx="150" cy="90" rx="35" ry="18" fill="#2E8B57"/>
      
      <!-- Leaf veins -->
      <path d="M70 200 Q100 200 130 195" stroke="#228B22" stroke-width="1" fill="none"/>
      <path d="M170 180 Q200 178 230 185" stroke="#228B22" stroke-width="1" fill="none"/>
    </svg>`,
  },

  leaf_cross_section: {
    id: 'leaf_cross_section',
    name: 'Leaf Cross Section',
    category: 'biology',
    width: 280,
    height: 180,
    anchors: {
      stomata: { x: 0.5, y: 0.95 },
      chloroplast: { x: 0.5, y: 0.5 },
      surface: { x: 0.5, y: 0.05 },
    },
    svg: `<svg viewBox="0 0 280 180" xmlns="http://www.w3.org/2000/svg">
      <!-- Leaf outline -->
      <path d="M20 90 Q140 20 260 90 Q140 160 20 90" fill="#90EE90" stroke="#228B22" stroke-width="3"/>
      
      <!-- Upper epidermis -->
      <path d="M30 70 Q140 30 250 70" stroke="#006400" stroke-width="2" fill="none"/>
      
      <!-- Lower epidermis -->
      <path d="M30 110 Q140 150 250 110" stroke="#006400" stroke-width="2" fill="none"/>
      
      <!-- Chloroplasts (stacked discs) -->
      <g class="chloroplast-group">
        <ellipse cx="80" cy="85" rx="20" ry="12" fill="#32CD32" stroke="#228B22" stroke-width="1"/>
        <ellipse cx="80" cy="82" rx="15" ry="4" fill="#228B22"/>
        <ellipse cx="80" cy="88" rx="15" ry="4" fill="#228B22"/>
        
        <ellipse cx="140" cy="90" rx="22" ry="14" fill="#32CD32" stroke="#228B22" stroke-width="1"/>
        <ellipse cx="140" cy="86" rx="16" ry="4" fill="#228B22"/>
        <ellipse cx="140" cy="94" rx="16" ry="4" fill="#228B22"/>
        
        <ellipse cx="200" cy="85" rx="20" ry="12" fill="#32CD32" stroke="#228B22" stroke-width="1"/>
        <ellipse cx="200" cy="82" rx="15" ry="4" fill="#228B22"/>
        <ellipse cx="200" cy="88" rx="15" ry="4" fill="#228B22"/>
      </g>
      
      <!-- Stomata -->
      <ellipse cx="140" cy="145" rx="15" ry="8" fill="#006400"/>
      <ellipse cx="140" cy="145" rx="8" ry="3" fill="#90EE90"/>
    </svg>`,
  },

  chloroplast_detail: {
    id: 'chloroplast_detail',
    name: 'Chloroplast Detail',
    category: 'biology',
    width: 200,
    height: 120,
    anchors: {
      thylakoid: { x: 0.5, y: 0.5 },
      stroma: { x: 0.3, y: 0.3 },
      membrane: { x: 0.9, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">
      <!-- Outer membrane -->
      <ellipse cx="100" cy="60" rx="95" ry="55" fill="#90EE90" stroke="#228B22" stroke-width="3"/>
      
      <!-- Inner membrane -->
      <ellipse cx="100" cy="60" rx="85" ry="45" fill="#98FB98" stroke="#32CD32" stroke-width="2"/>
      
      <!-- Thylakoid stacks (grana) -->
      <g class="grana">
        <rect x="30" y="40" width="35" height="40" rx="5" fill="#228B22"/>
        <rect x="35" y="35" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="45" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="55" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="65" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="75" width="25" height="5" rx="2" fill="#006400"/>
      </g>
      
      <g class="grana" transform="translate(60, 0)">
        <rect x="30" y="40" width="35" height="40" rx="5" fill="#228B22"/>
        <rect x="35" y="35" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="45" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="55" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="65" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="75" width="25" height="5" rx="2" fill="#006400"/>
      </g>
      
      <g class="grana" transform="translate(120, 0)">
        <rect x="30" y="40" width="35" height="40" rx="5" fill="#228B22"/>
        <rect x="35" y="35" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="45" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="55" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="65" width="25" height="5" rx="2" fill="#006400"/>
        <rect x="35" y="75" width="25" height="5" rx="2" fill="#006400"/>
      </g>
      
      <!-- Stroma label area -->
      <text x="100" y="105" text-anchor="middle" font-size="10" fill="#006400">Stroma</text>
    </svg>`,
  },

  sun_rays: {
    id: 'sun_rays',
    name: 'Sun with Rays',
    category: 'common',
    width: 150,
    height: 150,
    anchors: {
      center: { x: 0.5, y: 0.5 },
      ray_down: { x: 0.5, y: 1.0 },
    },
    svg: `<svg viewBox="0 0 150 150" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="sunGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:#FFF9C4"/>
          <stop offset="70%" style="stop-color:#FFD54F"/>
          <stop offset="100%" style="stop-color:#FF9800"/>
        </radialGradient>
        <filter id="sunGlow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <!-- Rays -->
      <g filter="url(#sunGlow)">
        <line x1="75" y1="75" x2="75" y2="10" stroke="#FFD54F" stroke-width="8" stroke-linecap="round"/>
        <line x1="75" y1="75" x2="75" y2="140" stroke="#FFD54F" stroke-width="8" stroke-linecap="round"/>
        <line x1="75" y1="75" x2="10" y2="75" stroke="#FFD54F" stroke-width="8" stroke-linecap="round"/>
        <line x1="75" y1="75" x2="140" y2="75" stroke="#FFD54F" stroke-width="8" stroke-linecap="round"/>
        <line x1="75" y1="75" x2="28" y2="28" stroke="#FFD54F" stroke-width="6" stroke-linecap="round"/>
        <line x1="75" y1="75" x2="122" y2="28" stroke="#FFD54F" stroke-width="6" stroke-linecap="round"/>
        <line x1="75" y1="75" x2="28" y2="122" stroke="#FFD54F" stroke-width="6" stroke-linecap="round"/>
        <line x1="75" y1="75" x2="122" y2="122" stroke="#FFD54F" stroke-width="6" stroke-linecap="round"/>
      </g>
      
      <!-- Sun circle -->
      <circle cx="75" cy="75" r="35" fill="url(#sunGradient)" filter="url(#sunGlow)"/>
    </svg>`,
  },

  molecule_co2: {
    id: 'molecule_co2',
    name: 'CO₂ Molecule',
    category: 'chemistry',
    width: 80,
    height: 40,
    anchors: {
      center: { x: 0.5, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 80 40" xmlns="http://www.w3.org/2000/svg">
      <circle cx="20" cy="20" r="12" fill="#EF4444" stroke="#B91C1C" stroke-width="2"/>
      <circle cx="40" cy="20" r="10" fill="#1F2937" stroke="#111827" stroke-width="2"/>
      <circle cx="60" cy="20" r="12" fill="#EF4444" stroke="#B91C1C" stroke-width="2"/>
      <text x="20" y="24" text-anchor="middle" font-size="8" fill="white" font-weight="bold">O</text>
      <text x="40" y="24" text-anchor="middle" font-size="8" fill="white" font-weight="bold">C</text>
      <text x="60" y="24" text-anchor="middle" font-size="8" fill="white" font-weight="bold">O</text>
    </svg>`,
  },

  molecule_h2o: {
    id: 'molecule_h2o',
    name: 'H₂O Molecule',
    category: 'chemistry',
    width: 60,
    height: 50,
    anchors: {
      center: { x: 0.5, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 60 50" xmlns="http://www.w3.org/2000/svg">
      <circle cx="30" cy="30" r="14" fill="#3B82F6" stroke="#1D4ED8" stroke-width="2"/>
      <circle cx="15" cy="15" r="8" fill="#E5E7EB" stroke="#9CA3AF" stroke-width="2"/>
      <circle cx="45" cy="15" r="8" fill="#E5E7EB" stroke="#9CA3AF" stroke-width="2"/>
      <text x="30" y="34" text-anchor="middle" font-size="10" fill="white" font-weight="bold">O</text>
      <text x="15" y="18" text-anchor="middle" font-size="7" fill="#374151" font-weight="bold">H</text>
      <text x="45" y="18" text-anchor="middle" font-size="7" fill="#374151" font-weight="bold">H</text>
    </svg>`,
  },

  molecule_o2: {
    id: 'molecule_o2',
    name: 'O₂ Molecule',
    category: 'chemistry',
    width: 50,
    height: 30,
    anchors: {
      center: { x: 0.5, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 50 30" xmlns="http://www.w3.org/2000/svg">
      <circle cx="15" cy="15" r="12" fill="#10B981" stroke="#059669" stroke-width="2"/>
      <circle cx="35" cy="15" r="12" fill="#10B981" stroke="#059669" stroke-width="2"/>
      <text x="15" y="19" text-anchor="middle" font-size="9" fill="white" font-weight="bold">O</text>
      <text x="35" y="19" text-anchor="middle" font-size="9" fill="white" font-weight="bold">O</text>
    </svg>`,
  },

  molecule_glucose: {
    id: 'molecule_glucose',
    name: 'Glucose Molecule',
    category: 'chemistry',
    width: 70,
    height: 70,
    anchors: {
      center: { x: 0.5, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 70 70" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="glucoseGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#FDE68A"/>
          <stop offset="100%" style="stop-color:#F59E0B"/>
        </linearGradient>
      </defs>
      <!-- Hexagon shape for glucose -->
      <polygon points="35,5 60,20 60,50 35,65 10,50 10,20" 
               fill="url(#glucoseGradient)" stroke="#D97706" stroke-width="3"/>
      <text x="35" y="32" text-anchor="middle" font-size="8" fill="#78350F" font-weight="bold">C₆H₁₂O₆</text>
      <text x="35" y="44" text-anchor="middle" font-size="7" fill="#92400E">Glucose</text>
    </svg>`,
  },

  arrow_flow: {
    id: 'arrow_flow',
    name: 'Flow Arrow',
    category: 'common',
    width: 100,
    height: 30,
    anchors: {
      start: { x: 0, y: 0.5 },
      end: { x: 1, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 100 30" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#6B7280"/>
        </marker>
      </defs>
      <line x1="5" y1="15" x2="85" y2="15" stroke="#6B7280" stroke-width="3" marker-end="url(#arrowhead)"/>
    </svg>`,
  },
};

// ============================================
// PHYSICS ASSETS
// ============================================

export const PHYSICS_ASSETS = {
  inclined_plane: {
    id: 'inclined_plane',
    name: 'Inclined Plane',
    category: 'physics',
    width: 400,
    height: 200,
    anchors: {
      top: { x: 0.85, y: 0.15 },
      bottom: { x: 0.1, y: 0.85 },
      surface: { x: 0.5, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="planeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#94A3B8"/>
          <stop offset="100%" style="stop-color:#64748B"/>
        </linearGradient>
      </defs>
      <!-- Ground -->
      <rect x="0" y="175" width="400" height="25" fill="#78716C"/>
      
      <!-- Inclined plane -->
      <polygon points="20,175 380,175 380,30" fill="url(#planeGradient)" stroke="#475569" stroke-width="3"/>
      
      <!-- Surface texture lines -->
      <g stroke="#CBD5E1" stroke-width="1">
        <line x1="60" y1="170" x2="100" y2="155"/>
        <line x1="120" y1="160" x2="160" y2="145"/>
        <line x1="180" y1="150" x2="220" y2="135"/>
        <line x1="240" y1="140" x2="280" y2="125"/>
        <line x1="300" y1="130" x2="340" y2="115"/>
      </g>
    </svg>`,
  },

  block_object: {
    id: 'block_object',
    name: 'Block/Box',
    category: 'physics',
    width: 80,
    height: 60,
    anchors: {
      center: { x: 0.5, y: 0.5 },
      top: { x: 0.5, y: 0 },
      bottom: { x: 0.5, y: 1 },
    },
    svg: `<svg viewBox="0 0 80 60" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="blockGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#EF4444"/>
          <stop offset="100%" style="stop-color:#B91C1C"/>
        </linearGradient>
      </defs>
      <!-- 3D effect -->
      <polygon points="10,15 70,15 80,5 20,5" fill="#FCA5A5"/>
      <polygon points="70,15 70,55 80,45 80,5" fill="#DC2626"/>
      <!-- Main face -->
      <rect x="10" y="15" width="60" height="40" fill="url(#blockGradient)" stroke="#991B1B" stroke-width="2"/>
    </svg>`,
  },

  ball_object: {
    id: 'ball_object',
    name: 'Ball/Sphere',
    category: 'physics',
    width: 60,
    height: 60,
    anchors: {
      center: { x: 0.5, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="ballGradient" cx="30%" cy="30%" r="70%">
          <stop offset="0%" style="stop-color:#93C5FD"/>
          <stop offset="70%" style="stop-color:#3B82F6"/>
          <stop offset="100%" style="stop-color:#1D4ED8"/>
        </radialGradient>
      </defs>
      <circle cx="30" cy="30" r="28" fill="url(#ballGradient)" stroke="#1E40AF" stroke-width="2"/>
      <!-- Highlight -->
      <ellipse cx="22" cy="22" rx="8" ry="6" fill="rgba(255,255,255,0.4)"/>
    </svg>`,
  },

  force_arrow: {
    id: 'force_arrow',
    name: 'Force Arrow',
    category: 'physics',
    width: 120,
    height: 40,
    anchors: {
      start: { x: 0, y: 0.5 },
      end: { x: 1, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 120 40" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="forceGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#22C55E"/>
          <stop offset="100%" style="stop-color:#16A34A"/>
        </linearGradient>
      </defs>
      <!-- Arrow body -->
      <rect x="5" y="15" width="80" height="10" rx="2" fill="url(#forceGradient)"/>
      <!-- Arrow head -->
      <polygon points="85,8 115,20 85,32" fill="#16A34A"/>
      <!-- Label -->
      <text x="45" y="13" text-anchor="middle" font-size="10" fill="#166534" font-weight="bold">F</text>
    </svg>`,
  },

  friction_surface: {
    id: 'friction_surface',
    name: 'Friction Surface',
    category: 'physics',
    width: 500,
    height: 40,
    anchors: {
      top: { x: 0.5, y: 0 },
      left: { x: 0, y: 0.5 },
      right: { x: 1, y: 0.5 },
    },
    svg: `<svg viewBox="0 0 500 40" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="500" height="40" fill="#78716C"/>
      <!-- Texture -->
      <g fill="#57534E">
        ${Array.from({length: 25}, (_, i) => 
          `<circle cx="${10 + i * 20}" cy="${10 + (i % 2) * 8}" r="3"/>`
        ).join('')}
        ${Array.from({length: 25}, (_, i) => 
          `<circle cx="${10 + i * 20}" cy="${25 + (i % 2) * 8}" r="2"/>`
        ).join('')}
      </g>
    </svg>`,
  },
};

// ============================================
// SCENE TEMPLATES
// ============================================

export const SCENE_TEMPLATES = {
  photosynthesis: {
    name: 'Photosynthesis',
    domain: 'biology',
    assets: [
      { assetId: 'sun_rays', position: { x: 100, y: 80 }, scale: 0.8, zIndex: 5 },
      { assetId: 'plant_in_pot', position: { x: 450, y: 280 }, scale: 0.9, zIndex: 10, isHero: true },
      { assetId: 'leaf_cross_section', position: { x: 180, y: 320 }, scale: 1.0, zIndex: 15 },
      { assetId: 'molecule_co2', position: { x: 80, y: 280 }, scale: 1.0, zIndex: 20 },
      { assetId: 'molecule_h2o', position: { x: 80, y: 380 }, scale: 1.0, zIndex: 20 },
      { assetId: 'molecule_o2', position: { x: 600, y: 180 }, scale: 1.0, zIndex: 20, initialHidden: true },
      { assetId: 'molecule_glucose', position: { x: 600, y: 350 }, scale: 1.0, zIndex: 20, initialHidden: true },
    ],
    flows: [
      { from: 'sun_rays', to: 'leaf_cross_section', type: 'energy', color: '#FCD34D' },
      { from: 'molecule_co2', to: 'leaf_cross_section', type: 'input', color: '#94A3B8' },
      { from: 'molecule_h2o', to: 'leaf_cross_section', type: 'input', color: '#3B82F6' },
      { from: 'leaf_cross_section', to: 'molecule_o2', type: 'output', color: '#10B981', delay: 2000 },
      { from: 'leaf_cross_section', to: 'molecule_glucose', type: 'output', color: '#F59E0B', delay: 2500 },
    ],
    narration: [
      { delay: 500, text: 'Sunlight provides energy to the leaf' },
      { delay: 2000, text: 'CO₂ and H₂O enter the chloroplasts where photosynthesis occurs' },
      { delay: 4000, text: 'Oxygen is released and glucose is produced as stored energy' },
    ],
  },

  friction: {
    name: 'Friction on Inclined Plane',
    domain: 'physics',
    assets: [
      { assetId: 'inclined_plane', position: { x: 360, y: 320 }, scale: 1.0, zIndex: 5, isHero: true },
      { assetId: 'block_object', position: { x: 340, y: 100 }, scale: 1.0, zIndex: 15 },
      { assetId: 'force_arrow', position: { x: 280, y: 180 }, scale: 0.8, zIndex: 20, rotation: 30 },
    ],
    flows: [],
    narration: [
      { delay: 500, text: 'A block sits on an inclined plane' },
      { delay: 2000, text: 'Gravity pulls it down while friction resists the motion' },
      { delay: 4000, text: 'The net force determines if the block slides or stays in place' },
    ],
  },
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

export function getAssetById(id) {
  return BIOLOGY_ASSETS[id] || PHYSICS_ASSETS[id] || null;
}

export function getAssetsByCategory(category) {
  const all = { ...BIOLOGY_ASSETS, ...PHYSICS_ASSETS };
  return Object.values(all).filter(a => a.category === category);
}

export function getSceneTemplate(name) {
  return SCENE_TEMPLATES[name] || null;
}

export function getAllAssetIds() {
  return [
    ...Object.keys(BIOLOGY_ASSETS),
    ...Object.keys(PHYSICS_ASSETS),
  ];
}

export default {
  BIOLOGY_ASSETS,
  PHYSICS_ASSETS,
  SCENE_TEMPLATES,
  getAssetById,
  getAssetsByCategory,
  getSceneTemplate,
  getAllAssetIds,
};
