/**
 * 🇮🇳 METAPHOR DATABASE
 * ======================
 * 
 * India-first cultural metaphors for educational concepts
 * Makes learning relatable using everyday Indian contexts
 */

// ============================================
// METAPHOR CATEGORIES
// ============================================

export const METAPHOR_CATEGORIES = {
  SPORTS: 'sports',
  TRANSPORT: 'transport',
  FOOD: 'food',
  FESTIVALS: 'festivals',
  DAILY_LIFE: 'daily_life',
  NATURE: 'nature',
  FAMILY: 'family',
};

// ============================================
// METAPHOR DATABASE
// ============================================

export const METAPHOR_DATABASE = {
  // ==================== SPORTS ====================
  cricket: {
    id: 'cricket',
    category: METAPHOR_CATEGORIES.SPORTS,
    name: 'Cricket',
    description: 'India\'s favorite sport',
    keywords: ['cricket', 'ball', 'bat', 'bowler', 'batsman', 'wicket', 'six', 'boundary', 'stadium'],
    
    // Concept mappings
    concepts: {
      force: {
        label: '🏏 Cricket Ball',
        object: 'cricket_ball',
        action: 'bowling',
        agent: 'bowler',
      },
      motion: {
        label: 'Ball trajectory',
        scene: 'cricket_pitch',
      },
      centripetal_force: {
        label: 'Spin bowling',
        description: 'The ball curves through air like a spinner\'s delivery',
      },
      momentum: {
        label: 'Powerful six',
        description: 'Heavy ball hit with high speed = massive momentum!',
      },
    },
    
    // Visual substitutions
    substitutions: {
      ball: { emoji: '🏏', svg: 'cricket_ball', label: 'Cricket Ball' },
      person: { emoji: '🏃', svg: 'batsman', label: 'Batsman' },
      ground: { emoji: '🏟️', svg: 'cricket_pitch', label: 'Pitch' },
      target: { emoji: '🎯', svg: 'wickets', label: 'Wickets' },
    },
    
    // Background hints
    background: {
      color: '#90EE90',
      pattern: 'grass_field',
      elements: ['boundary_line', 'pitch_marks'],
    },
  },
  
  // ==================== TRANSPORT ====================
  auto_rickshaw: {
    id: 'auto_rickshaw',
    category: METAPHOR_CATEGORIES.TRANSPORT,
    name: 'Auto Rickshaw',
    description: 'Iconic three-wheeler',
    keywords: ['auto', 'rickshaw', 'tuk-tuk', 'three-wheeler'],
    
    concepts: {
      friction: {
        label: '🛺 Auto on road',
        description: 'Friction between tires and road controls speed',
      },
      acceleration: {
        label: 'Auto speeding up',
        description: 'Driver presses gas → auto accelerates',
      },
      mass: {
        label: 'Passengers in auto',
        description: 'More passengers = more mass = harder to accelerate',
      },
    },
    
    substitutions: {
      vehicle: { emoji: '🛺', svg: 'auto_rickshaw', label: 'Auto' },
      road: { emoji: '🛣️', svg: 'indian_road', label: 'Road' },
      person: { emoji: '👨', svg: 'driver', label: 'Driver' },
    },
    
    background: {
      color: '#FFE5B4',
      pattern: 'road',
      elements: ['lane_markings', 'speed_bump'],
    },
  },
  
  local_train: {
    id: 'local_train',
    category: METAPHOR_CATEGORIES.TRANSPORT,
    name: 'Local Train',
    description: 'Mumbai local train',
    keywords: ['train', 'local', 'railway', 'mumbai local', 'metro'],
    
    concepts: {
      momentum: {
        label: '🚆 Local train',
        description: 'Heavy train moving fast = huge momentum!',
      },
      kinetic_energy: {
        label: 'Train in motion',
        description: 'KE = ½mv² - massive energy in moving train',
      },
    },
    
    substitutions: {
      vehicle: { emoji: '🚆', svg: 'local_train', label: 'Train' },
      track: { emoji: '🛤️', svg: 'railway_track', label: 'Track' },
    },
  },
  
  // ==================== FOOD ====================
  chai: {
    id: 'chai',
    category: METAPHOR_CATEGORIES.FOOD,
    name: 'Chai (Tea)',
    description: 'India\'s beloved tea',
    keywords: ['chai', 'tea', 'cutting', 'cup', 'stall'],
    
    concepts: {
      heat_transfer: {
        label: '☕ Hot chai cooling',
        description: 'Chai transfers heat to air and cup',
      },
      temperature: {
        label: 'Chai temperature',
        description: 'From boiling (100°C) to sipping hot (60°C)',
      },
      evaporation: {
        label: 'Steam from chai',
        description: 'Water molecules escape as vapor',
      },
    },
    
    substitutions: {
      container: { emoji: '☕', svg: 'chai_cup', label: 'Chai Cup' },
      liquid: { emoji: '🫖', svg: 'chai', label: 'Chai' },
      heat_source: { emoji: '🔥', svg: 'stove', label: 'Chulha' },
    },
  },
  
  dosa: {
    id: 'dosa',
    category: METAPHOR_CATEGORIES.FOOD,
    name: 'Dosa',
    description: 'South Indian crispy crepe',
    keywords: ['dosa', 'idli', 'sambar', 'tawa', 'batter'],
    
    concepts: {
      heat_conduction: {
        label: '🥞 Dosa on hot tawa',
        description: 'Heat conducts from tawa to dosa batter',
      },
      chemical_reaction: {
        label: 'Fermentation of batter',
        description: 'Bacteria + rice batter → CO₂ + fluffy texture',
      },
    },
    
    substitutions: {
      flat_object: { emoji: '🥞', svg: 'dosa', label: 'Dosa' },
      surface: { emoji: '🍳', svg: 'tawa', label: 'Tawa' },
    },
  },
  
  // ==================== FESTIVALS ====================
  diwali: {
    id: 'diwali',
    category: METAPHOR_CATEGORIES.FESTIVALS,
    name: 'Diwali',
    description: 'Festival of lights',
    keywords: ['diwali', 'diya', 'lamp', 'crackers', 'fireworks', 'deepavali'],
    
    concepts: {
      light: {
        label: '🪔 Diya (lamp)',
        description: 'Diya spreads light in all directions',
      },
      energy: {
        label: 'Firecrackers',
        description: 'Chemical energy → light + sound + heat',
      },
      combustion: {
        label: 'Burning crackers',
        description: 'Rapid oxidation reaction',
      },
    },
    
    substitutions: {
      light_source: { emoji: '🪔', svg: 'diya', label: 'Diya' },
      explosion: { emoji: '🎆', svg: 'cracker', label: 'Firecracker' },
    },
    
    background: {
      color: '#FFD700',
      pattern: 'festive',
      elements: ['rangoli', 'lights'],
    },
  },
  
  holi: {
    id: 'holi',
    category: METAPHOR_CATEGORIES.FESTIVALS,
    name: 'Holi',
    description: 'Festival of colors',
    keywords: ['holi', 'color', 'gulal', 'pichkari', 'water'],
    
    concepts: {
      projectile_motion: {
        label: '💦 Pichkari (water gun)',
        description: 'Water follows parabolic trajectory',
      },
      dispersion: {
        label: 'Gulal spreading',
        description: 'Color powder disperses in air',
      },
    },
    
    substitutions: {
      particle: { emoji: '🎨', svg: 'gulal', label: 'Gulal' },
      liquid: { emoji: '💦', svg: 'colored_water', label: 'Colored Water' },
    },
  },
  
  // ==================== DAILY LIFE ====================
  market: {
    id: 'market',
    category: METAPHOR_CATEGORIES.DAILY_LIFE,
    name: 'Sabzi Mandi (Market)',
    description: 'Local vegetable market',
    keywords: ['market', 'bazaar', 'sabzi', 'vendor', 'mandi'],
    
    concepts: {
      supply_demand: {
        label: '🛒 Market economics',
        description: 'Price changes with supply and demand',
      },
      weighing: {
        label: 'Weighing vegetables',
        description: 'Mass measurement using balance',
      },
    },
    
    substitutions: {
      person: { emoji: '🧑‍🌾', svg: 'vendor', label: 'Vendor' },
      place: { emoji: '🏪', svg: 'market_stall', label: 'Stall' },
      object: { emoji: '🥕', svg: 'vegetables', label: 'Sabzi' },
    },
  },
  
  classroom: {
    id: 'classroom',
    category: METAPHOR_CATEGORIES.DAILY_LIFE,
    name: 'Indian Classroom',
    description: 'School classroom',
    keywords: ['classroom', 'school', 'teacher', 'blackboard', 'chalk'],
    
    concepts: {
      sound: {
        label: '🔔 School bell',
        description: 'Sound waves travel through air',
      },
      reflection: {
        label: 'Light from blackboard',
        description: 'Chalk reflects light to our eyes',
      },
    },
    
    substitutions: {
      person: { emoji: '👨‍🏫', svg: 'teacher', label: 'Teacher' },
      board: { emoji: '📋', svg: 'blackboard', label: 'Blackboard' },
    },
  },
  
  // ==================== NATURE ====================
  monsoon: {
    id: 'monsoon',
    category: METAPHOR_CATEGORIES.NATURE,
    name: 'Monsoon',
    description: 'Indian rainy season',
    keywords: ['monsoon', 'rain', 'clouds', 'thunder', 'lightning'],
    
    concepts: {
      water_cycle: {
        label: '🌧️ Monsoon rains',
        description: 'Evaporation → clouds → rain → rivers',
      },
      electricity: {
        label: 'Lightning',
        description: 'Static electricity discharge in clouds',
      },
    },
    
    substitutions: {
      water: { emoji: '💧', svg: 'rain_drop', label: 'Rain' },
      cloud: { emoji: '☁️', svg: 'monsoon_cloud', label: 'Cloud' },
    },
  },
  
  // ==================== FAMILY ====================
  joint_family: {
    id: 'joint_family',
    category: METAPHOR_CATEGORIES.FAMILY,
    name: 'Joint Family',
    description: 'Traditional Indian family structure',
    keywords: ['family', 'joint family', 'relatives', 'generations'],
    
    concepts: {
      hierarchy: {
        label: '👨‍👩‍👧‍👦 Family tree',
        description: 'Generations and relationships',
      },
      network: {
        label: 'Family connections',
        description: 'How everyone is related',
      },
    },
    
    substitutions: {
      node: { emoji: '👤', svg: 'family_member', label: 'Relative' },
      connection: { emoji: '🔗', svg: 'relationship', label: 'Relation' },
    },
  },
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get metaphor by ID
 */
export function getMetaphor(id) {
  return METAPHOR_DATABASE[id] || null;
}

/**
 * Get metaphors by category
 */
export function getMetaphorsByCategory(category) {
  return Object.values(METAPHOR_DATABASE).filter(m => m.category === category);
}

/**
 * Get metaphors by keyword
 */
export function findMetaphorByKeyword(keyword) {
  const keywordLower = keyword.toLowerCase();
  
  for (const metaphor of Object.values(METAPHOR_DATABASE)) {
    if (metaphor.keywords.some(kw => kw.includes(keywordLower) || keywordLower.includes(kw))) {
      return metaphor;
    }
  }
  
  return null;
}

/**
 * Get concept mapping for metaphor
 */
export function getConceptMapping(metaphorId, concept) {
  const metaphor = getMetaphor(metaphorId);
  return metaphor?.concepts[concept] || null;
}

/**
 * Get substitution for element
 */
export function getSubstitution(metaphorId, element) {
  const metaphor = getMetaphor(metaphorId);
  return metaphor?.substitutions[element] || null;
}

/**
 * Get all available metaphor IDs
 */
export function getAllMetaphorIds() {
  return Object.keys(METAPHOR_DATABASE);
}

/**
 * Search metaphors by concept
 */
export function searchMetaphorsByConcept(concept) {
  const conceptLower = concept.toLowerCase();
  const results = [];
  
  for (const [id, metaphor] of Object.entries(METAPHOR_DATABASE)) {
    if (metaphor.concepts[conceptLower]) {
      results.push({
        metaphorId: id,
        metaphor,
        mapping: metaphor.concepts[conceptLower],
      });
    }
  }
  
  return results;
}

export default METAPHOR_DATABASE;

