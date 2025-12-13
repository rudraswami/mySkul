/**
 * 🔄 METAPHOR MAPPER
 * ===================
 * 
 * Substitutes visual elements with cultural metaphors
 * Integrates with ConceptBreaker and SceneComposer
 */

import {
  METAPHOR_DATABASE,
  getMetaphor,
  findMetaphorByKeyword,
  getConceptMapping,
  getSubstitution,
  searchMetaphorsByConcept,
} from './MetaphorDatabase';

// ============================================
// METAPHOR MAPPER CLASS
// ============================================

export class MetaphorMapper {
  constructor(options = {}) {
    this.options = {
      preferredRegion: 'india',
      enableSubstitution: true,
      fallbackToDefault: true,
      ...options,
    };
  }
  
  /**
   * Apply metaphor to blueprint
   * @param {Object} blueprint - Visual blueprint from ConceptBreaker
   * @param {string} metaphorId - Metaphor ID (or null to auto-detect)
   * @returns {Object} Blueprint with metaphor applied
   */
  apply(blueprint, metaphorId = null) {
    // Auto-detect metaphor if not provided
    if (!metaphorId && blueprint.metaphor) {
      metaphorId = blueprint.metaphor;
    }
    
    // If still no metaphor, try to find one based on concept
    if (!metaphorId) {
      const detected = this.detectMetaphor(blueprint.concept, blueprint.subject);
      metaphorId = detected?.id;
    }
    
    // If no metaphor found, return original blueprint
    if (!metaphorId) {
      return blueprint;
    }
    
    const metaphor = getMetaphor(metaphorId);
    if (!metaphor) {
      return blueprint;
    }
    
    // Apply metaphor transformations
    const transformed = {
      ...blueprint,
      metaphor: metaphorId,
      metaphorData: metaphor,
      
      // Transform items
      items: this.transformItems(blueprint.items || [], metaphor),
      
      // Transform labels
      labels: this.transformLabels(blueprint.labels || [], metaphor, blueprint.concept),
      
      // Add metaphor-specific elements
      doodles: [...(blueprint.doodles || []), ...this.addMetaphorDoodles(metaphor)],
      
      // Apply background
      background: this.applyBackground(metaphor),
      
      // Add cultural context
      culturalContext: {
        metaphor: metaphor.name,
        description: metaphor.description,
        category: metaphor.category,
      },
    };
    
    return transformed;
  }
  
  /**
   * Auto-detect metaphor from concept and subject
   */
  detectMetaphor(concept, subject) {
    if (!concept) return null;
    
    // Search by concept
    const matches = searchMetaphorsByConcept(concept);
    if (matches.length > 0) {
      return matches[0].metaphor;
    }
    
    // Search by keywords in concept text
    const conceptLower = concept.toLowerCase();
    const keywords = conceptLower.split(/\s+/);
    
    for (const keyword of keywords) {
      const metaphor = findMetaphorByKeyword(keyword);
      if (metaphor) {
        return metaphor;
      }
    }
    
    // Subject-based defaults
    const subjectDefaults = {
      physics: 'cricket',
      chemistry: 'chai',
      biology: 'monsoon',
      math: 'market',
    };
    
    const defaultId = subjectDefaults[subject?.toLowerCase()];
    return defaultId ? getMetaphor(defaultId) : null;
  }
  
  /**
   * Transform items (circles, shapes) with metaphor substitutions
   */
  transformItems(items, metaphor) {
    return items.map(item => {
      // Check for substitution
      const itemType = this.inferItemType(item);
      const substitution = getSubstitution(metaphor.id, itemType);
      
      if (substitution) {
        return {
          ...item,
          metaphorLabel: substitution.label,
          metaphorEmoji: substitution.emoji,
          metaphorSvg: substitution.svg,
          originalLabel: item.label,
        };
      }
      
      return item;
    });
  }
  
  /**
   * Infer item type from label or properties
   */
  inferItemType(item) {
    const label = item.label?.toLowerCase() || '';
    
    // Common mappings
    if (label.includes('ball') || label.includes('sphere')) return 'ball';
    if (label.includes('person') || label.includes('man') || label.includes('figure')) return 'person';
    if (label.includes('vehicle') || label.includes('car')) return 'vehicle';
    if (label.includes('container') || label.includes('cup')) return 'container';
    if (label.includes('ground') || label.includes('surface')) return 'ground';
    
    // Default based on shape
    if (item.type === 'circle') return 'ball';
    if (item.type === 'rect') return 'object';
    
    return 'object';
  }
  
  /**
   * Transform labels with metaphor context
   */
  transformLabels(labels, metaphor, concept) {
    const conceptMapping = metaphor.concepts[concept?.toLowerCase()];
    
    // Add metaphor title if available
    if (conceptMapping) {
      return [
        {
          text: conceptMapping.label,
          fontSize: 18,
          color: '#333',
          bold: true,
          metaphorEnhanced: true,
        },
        ...labels,
      ];
    }
    
    return labels;
  }
  
  /**
   * Add metaphor-specific doodles
   */
  addMetaphorDoodles(metaphor) {
    const doodles = [];
    
    // Add emoji doodle based on metaphor
    const emojiMap = {
      cricket: '🏏',
      auto_rickshaw: '🛺',
      chai: '☕',
      dosa: '🥞',
      diwali: '🪔',
      holi: '🎨',
      local_train: '🚆',
      market: '🛒',
      monsoon: '🌧️',
      classroom: '📚',
    };
    
    const emoji = emojiMap[metaphor.id];
    if (emoji) {
      doodles.push({
        type: 'emoji',
        emoji,
        x: 360,
        y: 30,
        size: 30,
        opacity: 0.7,
      });
    }
    
    return doodles;
  }
  
  /**
   * Apply background styling
   */
  applyBackground(metaphor) {
    if (!metaphor.background) {
      return {
        color: '#FFFEF7',
        pattern: null,
      };
    }
    
    return {
      color: metaphor.background.color || '#FFFEF7',
      pattern: metaphor.background.pattern,
      elements: metaphor.background.elements || [],
    };
  }
  
  /**
   * Get available metaphors for a concept
   */
  getSuggestedMetaphors(concept, subject) {
    const suggestions = [];
    
    // Search by concept
    const byConceptMatches = searchMetaphorsByConcept(concept);
    suggestions.push(...byConceptMatches.map(m => m.metaphor));
    
    // Add subject defaults if not already included
    const subjectDefaults = {
      physics: ['cricket', 'auto_rickshaw', 'local_train'],
      chemistry: ['chai', 'dosa'],
      biology: ['monsoon', 'joint_family'],
      math: ['market', 'classroom'],
    };
    
    const defaults = subjectDefaults[subject?.toLowerCase()] || [];
    defaults.forEach(id => {
      const metaphor = getMetaphor(id);
      if (metaphor && !suggestions.find(s => s.id === id)) {
        suggestions.push(metaphor);
      }
    });
    
    return suggestions.slice(0, 5); // Top 5
  }
  
  /**
   * Explain metaphor connection
   */
  explainMetaphor(metaphorId, concept) {
    const metaphor = getMetaphor(metaphorId);
    if (!metaphor) return null;
    
    const mapping = getConceptMapping(metaphorId, concept);
    
    return {
      metaphor: metaphor.name,
      category: metaphor.category,
      connection: mapping?.description || `Understand ${concept} using ${metaphor.name}`,
      label: mapping?.label || metaphor.name,
      culturalContext: metaphor.description,
    };
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Create a metaphor mapper
 */
export function createMetaphorMapper(options) {
  return new MetaphorMapper(options);
}

/**
 * Quick apply metaphor
 */
export function applyMetaphor(blueprint, metaphorId) {
  const mapper = new MetaphorMapper();
  return mapper.apply(blueprint, metaphorId);
}

export default MetaphorMapper;

