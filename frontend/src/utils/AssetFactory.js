/**
 * 🏏 ASSET FACTORY - Context-Aware Indian Cultural Asset Resolver
 * ================================================================
 * 
 * PURPOSE:
 * Transform generic visual elements into culturally relevant,
 * India-focused assets based on context and theme.
 * 
 * FEATURES:
 * - Cultural Context Detection: Identifies Indian themes from questions
 * - Asset Mapping: Returns specific SVG paths/components
 * - Theme Adaptation: Backgrounds, colors, and styles adapt to context
 * - Hyper-Localisation: Wankhede Stadium, Delhi Metro, etc.
 * 
 * ARCHITECTURE:
 * Question → ContextAnalyzer → AssetFactory → Themed Visual
 */

// ============================================
// CULTURAL CONTEXTS
// ============================================
export const CULTURAL_CONTEXTS = {
  CRICKET: 'cricket',
  FOOTBALL: 'football',
  METRO: 'metro',
  RICKSHAW: 'rickshaw',
  DIWALI: 'diwali',
  HOLI: 'holi',
  SPACE_ISRO: 'space_isro',
  CHAI: 'chai',
  DEFAULT: 'default',
};

// ============================================
// KEYWORD → CONTEXT MAPPING
// ============================================
const CONTEXT_KEYWORDS = {
  [CULTURAL_CONTEXTS.CRICKET]: [
    'cricket', 'ball', 'bat', 'bowler', 'batsman', 'wicket', 'stumps',
    'ipl', 'virat', 'dhoni', 'sachin', 'wankhede', 'eden gardens',
    'six', 'four', 'boundary', 'catch', 'run out', 'yorker', 'googly',
    'spin', 'pace', 'seam', 'swing', 'lbw', 'century', 'hat trick',
  ],
  [CULTURAL_CONTEXTS.FOOTBALL]: [
    'football', 'soccer', 'goal', 'kick', 'penalty', 'messi', 'ronaldo',
    'world cup', 'premier league', 'fifa', 'striker', 'goalkeeper',
  ],
  [CULTURAL_CONTEXTS.METRO]: [
    'metro', 'train', 'station', 'platform', 'delhi metro', 'mumbai metro',
    'railway', 'track', 'locomotive', 'rajdhani', 'shatabdi', 'vande bharat',
  ],
  [CULTURAL_CONTEXTS.RICKSHAW]: [
    'rickshaw', 'auto', 'auto rickshaw', 'tuktuk', 'three wheeler',
    'taxi', 'cab', 'uber', 'ola', 'traffic', 'road', 'highway',
  ],
  [CULTURAL_CONTEXTS.DIWALI]: [
    'diwali', 'deepawali', 'firework', 'rocket', 'cracker', 'sparkler',
    'phooljhadi', 'anar', 'chakri', 'festival', 'lights', 'diya', 'lamp',
  ],
  [CULTURAL_CONTEXTS.HOLI]: [
    'holi', 'color', 'colour', 'rang', 'gulal', 'pichkari', 'balloon',
    'water balloon', 'festival of colors',
  ],
  [CULTURAL_CONTEXTS.SPACE_ISRO]: [
    'isro', 'chandrayaan', 'mangalyaan', 'rocket', 'satellite', 'space',
    'moon', 'mars', 'orbit', 'launch', 'sriharikota', 'pslv', 'gslv',
  ],
  [CULTURAL_CONTEXTS.CHAI]: [
    'chai', 'tea', 'cup', 'hot', 'beverage', 'cutting chai', 'tapri',
  ],
};

// ============================================
// ASSET MAPPINGS
// ============================================
const ASSET_MAP = {
  // Projectile objects
  projectile: {
    [CULTURAL_CONTEXTS.CRICKET]: {
      svg: 'cricket_ball_seam',
      emoji: '🏏',
      color: '#DC2626',
      label: 'Cricket Ball',
      description: 'Red leather ball with raised seam',
    },
    [CULTURAL_CONTEXTS.FOOTBALL]: {
      svg: 'football',
      emoji: '⚽',
      color: '#FFFFFF',
      label: 'Football',
      description: 'Standard football',
    },
    [CULTURAL_CONTEXTS.DIWALI]: {
      svg: 'rocket_diwali',
      emoji: '🎆',
      color: '#F59E0B',
      label: 'Diwali Rocket',
      description: 'Festive rocket firework',
    },
    [CULTURAL_CONTEXTS.HOLI]: {
      svg: 'water_balloon',
      emoji: '🎈',
      color: '#EC4899',
      label: 'Color Balloon',
      description: 'Water balloon filled with colors',
    },
    [CULTURAL_CONTEXTS.SPACE_ISRO]: {
      svg: 'isro_satellite',
      emoji: '🛰️',
      color: '#3B82F6',
      label: 'ISRO Satellite',
      description: 'Indian space satellite',
    },
    [CULTURAL_CONTEXTS.DEFAULT]: {
      svg: 'generic_ball',
      emoji: '⚪',
      color: '#6B7280',
      label: 'Ball',
      description: 'Generic spherical object',
    },
  },

  // Vehicle objects
  vehicle: {
    [CULTURAL_CONTEXTS.METRO]: {
      svg: 'delhi_metro',
      emoji: '🚇',
      color: '#DC2626',
      label: 'Delhi Metro',
      description: 'Modern Delhi Metro train',
    },
    [CULTURAL_CONTEXTS.RICKSHAW]: {
      svg: 'auto_rickshaw',
      emoji: '🛺',
      color: '#22C55E',
      label: 'Auto Rickshaw',
      description: 'Classic Indian auto-rickshaw',
    },
    [CULTURAL_CONTEXTS.DEFAULT]: {
      svg: 'generic_car',
      emoji: '🚗',
      color: '#3B82F6',
      label: 'Car',
      description: 'Generic vehicle',
    },
  },

  // Background/Scene
  background: {
    [CULTURAL_CONTEXTS.CRICKET]: {
      pattern: 'pitch_grass',
      gradient: 'linear-gradient(to bottom, #60A5FA 0%, #60A5FA 35%, #22C55E 35%, #16A34A 100%)',
      label: 'Cricket Ground',
      elements: ['boundary_rope', 'stumps', 'crease'],
    },
    [CULTURAL_CONTEXTS.METRO]: {
      pattern: 'platform_tiles',
      gradient: 'linear-gradient(to bottom, #E5E7EB 0%, #9CA3AF 100%)',
      label: 'Metro Station',
      elements: ['platform', 'tracks', 'overhead_wires'],
    },
    [CULTURAL_CONTEXTS.RICKSHAW]: {
      pattern: 'road_asphalt',
      gradient: 'linear-gradient(to bottom, #87CEEB 0%, #E5E7EB 50%, #374151 100%)',
      label: 'Indian Road',
      elements: ['traffic_signal', 'pothole', 'speed_breaker'],
    },
    [CULTURAL_CONTEXTS.DIWALI]: {
      pattern: 'night_sky',
      gradient: 'linear-gradient(to bottom, #1E1B4B 0%, #312E81 50%, #1E1B4B 100%)',
      label: 'Diwali Night',
      elements: ['diyas', 'rangoli', 'stars'],
    },
    [CULTURAL_CONTEXTS.SPACE_ISRO]: {
      pattern: 'space_stars',
      gradient: 'linear-gradient(to bottom, #0F172A 0%, #1E293B 50%, #0F172A 100%)',
      label: 'Space',
      elements: ['stars', 'earth', 'moon'],
    },
    [CULTURAL_CONTEXTS.DEFAULT]: {
      pattern: 'grid_paper',
      gradient: 'linear-gradient(to bottom, #F9FAFB 0%, #E5E7EB 100%)',
      label: 'Neutral',
      elements: [],
    },
  },

  // Person/Character
  person: {
    [CULTURAL_CONTEXTS.CRICKET]: {
      svg: 'cricketer',
      emoji: '🏏',
      variants: ['batsman', 'bowler', 'fielder', 'umpire'],
    },
    [CULTURAL_CONTEXTS.DEFAULT]: {
      svg: 'generic_person',
      emoji: '🧑',
      variants: ['student', 'teacher'],
    },
  },

  // Location markers
  marker: {
    [CULTURAL_CONTEXTS.CRICKET]: {
      svg: 'stumps',
      emoji: '🎯',
    },
    [CULTURAL_CONTEXTS.METRO]: {
      svg: 'metro_station_marker',
      emoji: '🚉',
    },
    [CULTURAL_CONTEXTS.DEFAULT]: {
      svg: 'pin',
      emoji: '📍',
    },
  },
};

// ============================================
// FAMOUS INDIAN REFERENCES
// ============================================
const INDIAN_REFERENCES = {
  cricket: {
    locations: ['Wankhede Stadium', 'Eden Gardens', 'Chinnaswamy Stadium', 'Mohali'],
    players: ['Virat Kohli', 'MS Dhoni', 'Sachin Tendulkar', 'Rohit Sharma'],
    teams: ['Mumbai Indians', 'Chennai Super Kings', 'Royal Challengers'],
  },
  metro: {
    lines: ['Blue Line', 'Yellow Line', 'Red Line', 'Magenta Line'],
    stations: ['Rajiv Chowk', 'Kashmere Gate', 'HUDA City Centre'],
  },
  space: {
    missions: ['Chandrayaan-3', 'Mangalyaan', 'Aditya-L1'],
    centers: ['ISRO Sriharikota', 'Vikram Sarabhai Space Centre'],
  },
};

// ============================================
// MAIN ASSET FACTORY CLASS
// ============================================
class AssetFactory {
  constructor() {
    this.cachedContext = null;
    this.cachedQuestion = null;
  }

  /**
   * Detect cultural context from question text
   * @param {string} question - User's question
   * @returns {string} Cultural context identifier
   */
  detectContext(question) {
    if (!question) return CULTURAL_CONTEXTS.DEFAULT;
    
    // Use cached result if same question
    if (question === this.cachedQuestion) {
      return this.cachedContext;
    }

    const lowerQuestion = question.toLowerCase();
    let bestMatch = CULTURAL_CONTEXTS.DEFAULT;
    let maxMatches = 0;

    // Count keyword matches for each context
    for (const [context, keywords] of Object.entries(CONTEXT_KEYWORDS)) {
      const matches = keywords.filter(keyword => 
        lowerQuestion.includes(keyword.toLowerCase())
      ).length;

      if (matches > maxMatches) {
        maxMatches = matches;
        bestMatch = context;
      }
    }

    // Cache result
    this.cachedQuestion = question;
    this.cachedContext = bestMatch;

    return bestMatch;
  }

  /**
   * Get asset for object type + cultural context
   * @param {string} objectType - Type of object (e.g., 'projectile', 'vehicle')
   * @param {string} context - Cultural context (optional, will auto-detect)
   * @param {string} question - Question for context detection (optional)
   * @returns {object} Asset configuration
   */
  getAsset(objectType, context = null, question = null) {
    // Auto-detect context if not provided
    const effectiveContext = context || (question ? this.detectContext(question) : CULTURAL_CONTEXTS.DEFAULT);

    // Get asset map for this object type
    const objectAssets = ASSET_MAP[objectType];
    if (!objectAssets) {
      console.warn(`[AssetFactory] Unknown object type: ${objectType}`);
      return this._getDefaultAsset(objectType);
    }

    // Get context-specific asset, fallback to default
    const asset = objectAssets[effectiveContext] || objectAssets[CULTURAL_CONTEXTS.DEFAULT];

    return {
      ...asset,
      context: effectiveContext,
      objectType,
    };
  }

  /**
   * Get background/scene configuration
   * @param {string} context - Cultural context
   * @param {string} question - Question for context detection (optional)
   * @returns {object} Background configuration
   */
  getBackground(context = null, question = null) {
    const effectiveContext = context || (question ? this.detectContext(question) : CULTURAL_CONTEXTS.DEFAULT);
    
    const bg = ASSET_MAP.background[effectiveContext] || ASSET_MAP.background[CULTURAL_CONTEXTS.DEFAULT];

    return {
      ...bg,
      context: effectiveContext,
    };
  }

  /**
   * Get a fun Indian reference for the context
   * @param {string} context - Cultural context
   * @returns {object|null} Reference object
   */
  getIndianReference(context) {
    const contextKey = context === CULTURAL_CONTEXTS.CRICKET ? 'cricket' :
                       context === CULTURAL_CONTEXTS.METRO ? 'metro' :
                       context === CULTURAL_CONTEXTS.SPACE_ISRO ? 'space' : null;

    if (!contextKey || !INDIAN_REFERENCES[contextKey]) return null;

    const refs = INDIAN_REFERENCES[contextKey];
    const category = Object.keys(refs)[Math.floor(Math.random() * Object.keys(refs).length)];
    const items = refs[category];
    const item = items[Math.floor(Math.random() * items.length)];

    return {
      category,
      item,
      fullText: `${category}: ${item}`,
    };
  }

  /**
   * Transform generic config to themed config
   * @param {object} config - Original visual config
   * @param {string} question - User's question
   * @returns {object} Transformed config with cultural theming
   */
  transformConfig(config, question) {
    const context = this.detectContext(question);
    
    if (context === CULTURAL_CONTEXTS.DEFAULT) {
      return config; // No transformation needed
    }

    const transformedConfig = { ...config };

    // Transform object_a and object_b if they exist (race template)
    if (config.object_a) {
      const asset = this.getAsset(config.object_a.type || 'projectile', context);
      transformedConfig.object_a = {
        ...config.object_a,
        ...asset,
        originalType: config.object_a.type,
      };
    }

    if (config.object_b) {
      const asset = this.getAsset(config.object_b.type || 'projectile', context);
      transformedConfig.object_b = {
        ...config.object_b,
        ...asset,
        originalType: config.object_b.type,
      };
    }

    // Add background theming
    transformedConfig.background = this.getBackground(context);

    // Add Indian reference for memory hook enhancement
    const reference = this.getIndianReference(context);
    if (reference) {
      transformedConfig.indianReference = reference;
    }

    // Add context metadata
    transformedConfig._culturalContext = context;
    transformedConfig._transformed = true;

    return transformedConfig;
  }

  /**
   * Get default asset for unknown type
   */
  _getDefaultAsset(objectType) {
    return {
      svg: 'generic_shape',
      emoji: '🔷',
      color: '#6B7280',
      label: objectType || 'Object',
      description: 'Generic object',
      context: CULTURAL_CONTEXTS.DEFAULT,
      objectType,
    };
  }

  /**
   * Get all available contexts
   */
  getAvailableContexts() {
    return Object.values(CULTURAL_CONTEXTS);
  }

  /**
   * Check if context has special theming
   */
  hasSpecialTheming(context) {
    return context !== CULTURAL_CONTEXTS.DEFAULT;
  }
}

// ============================================
// SVG PATHS FOR ASSETS
// ============================================
export const SVG_ASSETS = {
  cricket_ball_seam: `
    <svg viewBox="0 0 60 60">
      <circle cx="30" cy="30" r="28" fill="#DC2626" stroke="#991B1B" stroke-width="2"/>
      <path d="M 10 20 Q 30 25 50 20" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M 10 40 Q 30 35 50 40" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
      <!-- Seam stitches -->
      <circle cx="15" cy="22" r="1.5" fill="white"/>
      <circle cx="25" cy="23" r="1.5" fill="white"/>
      <circle cx="35" cy="23" r="1.5" fill="white"/>
      <circle cx="45" cy="22" r="1.5" fill="white"/>
    </svg>
  `,

  auto_rickshaw: `
    <svg viewBox="0 0 100 60">
      <!-- Body -->
      <rect x="15" y="15" width="70" height="35" rx="8" fill="#22C55E" stroke="#166534" stroke-width="2"/>
      <!-- Roof -->
      <rect x="20" y="5" width="50" height="12" rx="4" fill="#166534"/>
      <!-- Windshield -->
      <rect x="60" y="18" width="20" height="15" rx="2" fill="#93C5FD" opacity="0.8"/>
      <!-- Wheels -->
      <circle cx="30" cy="52" r="8" fill="#1F2937"/>
      <circle cx="70" cy="52" r="8" fill="#1F2937"/>
      <circle cx="30" cy="52" r="4" fill="#6B7280"/>
      <circle cx="70" cy="52" r="4" fill="#6B7280"/>
      <!-- Headlight -->
      <circle cx="88" cy="30" r="5" fill="#FDE047"/>
    </svg>
  `,

  delhi_metro: `
    <svg viewBox="0 0 140 50">
      <!-- Body -->
      <rect x="5" y="10" width="130" height="35" rx="8" fill="#DC2626" stroke="#991B1B" stroke-width="2"/>
      <!-- Windows -->
      <rect x="15" y="15" width="25" height="18" rx="3" fill="#BFDBFE" opacity="0.9"/>
      <rect x="50" y="15" width="25" height="18" rx="3" fill="#BFDBFE" opacity="0.9"/>
      <rect x="90" y="15" width="25" height="18" rx="3" fill="#BFDBFE" opacity="0.9"/>
      <!-- DMRC Logo placeholder -->
      <circle cx="125" cy="25" r="8" fill="white"/>
      <text x="125" y="28" text-anchor="middle" font-size="8" fill="#DC2626" font-weight="bold">M</text>
      <!-- Door -->
      <rect x="78" y="18" width="8" height="22" fill="#7F1D1D"/>
    </svg>
  `,

  rocket_diwali: `
    <svg viewBox="0 0 40 80">
      <!-- Stick -->
      <rect x="18" y="40" width="4" height="40" fill="#92400E"/>
      <!-- Body -->
      <rect x="12" y="20" width="16" height="25" rx="3" fill="#DC2626"/>
      <!-- Nose cone -->
      <polygon points="20,5 12,20 28,20" fill="#F59E0B"/>
      <!-- Fins -->
      <polygon points="12,45 5,45 12,35" fill="#DC2626"/>
      <polygon points="28,45 35,45 28,35" fill="#DC2626"/>
      <!-- Fuse -->
      <path d="M 20 45 Q 22 50 20 55" stroke="#F97316" stroke-width="2" fill="none"/>
    </svg>
  `,

  isro_satellite: `
    <svg viewBox="0 0 100 60">
      <!-- Solar panels -->
      <rect x="5" y="22" width="25" height="16" fill="#3B82F6" stroke="#1D4ED8" stroke-width="1"/>
      <rect x="70" y="22" width="25" height="16" fill="#3B82F6" stroke="#1D4ED8" stroke-width="1"/>
      <!-- Panel lines -->
      <line x1="12" y1="22" x2="12" y2="38" stroke="#1D4ED8" stroke-width="0.5"/>
      <line x1="19" y1="22" x2="19" y2="38" stroke="#1D4ED8" stroke-width="0.5"/>
      <line x1="77" y1="22" x2="77" y2="38" stroke="#1D4ED8" stroke-width="0.5"/>
      <line x1="84" y1="22" x2="84" y2="38" stroke="#1D4ED8" stroke-width="0.5"/>
      <!-- Body -->
      <rect x="30" y="15" width="40" height="30" rx="4" fill="#F59E0B" stroke="#D97706" stroke-width="2"/>
      <!-- Antenna -->
      <circle cx="50" cy="10" r="4" fill="#E5E7EB" stroke="#9CA3AF" stroke-width="1"/>
      <line x1="50" y1="14" x2="50" y2="20" stroke="#9CA3AF" stroke-width="2"/>
      <!-- ISRO text -->
      <text x="50" y="33" text-anchor="middle" font-size="8" fill="white" font-weight="bold">ISRO</text>
    </svg>
  `,
};

// ============================================
// SINGLETON INSTANCE
// ============================================
const assetFactory = new AssetFactory();

// ============================================
// EXPORTS
// ============================================
export default assetFactory;
export { AssetFactory };

// Convenience functions
export const detectCulturalContext = (question) => 
  assetFactory.detectContext(question);

export const getThemedAsset = (objectType, context, question) => 
  assetFactory.getAsset(objectType, context, question);

export const getThemedBackground = (context, question) => 
  assetFactory.getBackground(context, question);

export const transformToThemedConfig = (config, question) => 
  assetFactory.transformConfig(config, question);






