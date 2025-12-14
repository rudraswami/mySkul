/**
 * 📦 CONTENT MAPPER
 * =================
 * 
 * Fills form SLOTS with actual content from the ConceptGraph.
 * 
 * This is where abstract structure meets concrete content:
 * - Form says: "I need a left_scenario and right_scenario"
 * - ContentMapper fills: left = "with friction", right = "without friction"
 * 
 * Subject-agnostic: same mapper works for physics, chemistry, biology.
 * The ConceptGraph provides the content; this mapper just organizes it.
 */

import { STRUCTURAL_FORMS, FORM_SPECIFICATIONS } from './FormSelector';
import { INTENT_TYPES } from './IntentClassifier';

// ============================================
// CONTENT GROUPING STRATEGIES
// ============================================

/**
 * How to group/split entities based on intent
 */
const GROUPING_STRATEGIES = {
  // For comparison: split into two groups
  split_by_type: (entities, context) => {
    const groups = { left: [], right: [] };
    const types = [...new Set(entities.map(e => e.type))];
    
    if (types.length >= 2) {
      // Split by entity type
      const midpoint = Math.ceil(types.length / 2);
      const leftTypes = types.slice(0, midpoint);
      
      entities.forEach(e => {
        if (leftTypes.includes(e.type)) {
          groups.left.push(e);
        } else {
          groups.right.push(e);
        }
      });
    } else {
      // Split evenly
      const midpoint = Math.ceil(entities.length / 2);
      groups.left = entities.slice(0, midpoint);
      groups.right = entities.slice(midpoint);
    }
    
    return groups;
  },
  
  // For counterfactual: create reality vs alternate
  split_counterfactual: (entities, context) => {
    // Reality: all entities as they are
    // Alternate: modified version or subset
    return {
      reality: entities,
      alternate: entities.map(e => ({
        ...e,
        properties: {
          ...e.properties,
          modified: true,
          label: `No ${e.properties?.label || e.id}`,
        },
      })),
    };
  },
  
  // For timeline: order by importance or sequence
  order_temporal: (entities, context) => {
    const ordered = [...entities].sort((a, b) => {
      const impA = a.properties?.importance === 'high' ? 0 : 1;
      const impB = b.properties?.importance === 'high' ? 0 : 1;
      return impA - impB;
    });
    
    return {
      start: ordered[0],
      events: ordered.slice(1, -1),
      end: ordered[ordered.length - 1],
    };
  },
  
  // For hierarchy: find parent-child relationships
  build_hierarchy: (entities, relationships) => {
    const root = entities.find(e => 
      e.properties?.importance === 'high' || 
      e.type === 'body' || 
      e.type === 'object'
    ) || entities[0];
    
    const children = entities.filter(e => e !== root);
    
    return {
      root,
      branches: children,
    };
  },
  
  // For force diagram: center + surrounding
  arrange_radial: (entities, context) => {
    const bodies = entities.filter(e => e.type === 'body' || e.type === 'object');
    const forces = entities.filter(e => e.type === 'force');
    const structures = entities.filter(e => e.type === 'structure');
    
    return {
      center: bodies[0] || entities[0],
      forces: forces,
      ground: structures[0] || null,
    };
  },
  
  // For cause-effect: find chain
  build_causal_chain: (entities, relationships) => {
    // Find entities that are causes (have outgoing relationships)
    const causeIds = new Set(relationships.map(r => r.from));
    const effectIds = new Set(relationships.map(r => r.to));
    
    // Pure causes (not effects of anything)
    const causes = entities.filter(e => causeIds.has(e.id) && !effectIds.has(e.id));
    // Pure effects (not causes of anything)  
    const effects = entities.filter(e => effectIds.has(e.id) && !causeIds.has(e.id));
    // Middle (both cause and effect)
    const middle = entities.filter(e => causeIds.has(e.id) && effectIds.has(e.id));
    
    return {
      cause: causes[0] || entities[0],
      mechanism: middle,
      effect: effects[0] || entities[entities.length - 1],
    };
  },
};

// ============================================
// CONTENT MAPPER CLASS
// ============================================

export class ContentMapper {
  constructor(options = {}) {
    this.options = {
      generateLabels: true,
      includeFormulas: true,
      ...options,
    };
  }
  
  /**
   * Map ConceptGraph content to form slots
   * @param {Object} conceptGraph - The parsed concept graph
   * @param {Object} formResult - Result from FormSelector
   * @param {Object} intentResult - Result from IntentClassifier
   * @returns {Object} Filled form with content in slots
   */
  map(conceptGraph, formResult, intentResult) {
    const form = formResult.form;
    const specification = formResult.specification;
    const slots = specification.slots;
    
    // Extract entities and relationships from concept graph
    const entities = Array.from(conceptGraph.entities.values()).map((e, i) => ({
      id: Array.from(conceptGraph.entities.keys())[i],
      ...e,
    }));
    const relationships = conceptGraph.relationships || [];
    
    console.log(`📦 [ContentMapper] Mapping ${entities.length} entities to form: ${form}`);
    
    // Choose grouping strategy based on form
    const groupedContent = this.groupContent(form, entities, relationships, intentResult);
    
    // Fill slots with grouped content
    const filledSlots = this.fillSlots(slots, groupedContent, conceptGraph.metadata);
    
    // Generate labels and annotations
    const annotations = this.generateAnnotations(conceptGraph, intentResult);
    
    const result = {
      form,
      specification,
      slots: filledSlots,
      annotations,
      metadata: {
        topic: conceptGraph.metadata.topic,
        domain: conceptGraph.metadata.domain,
        entityCount: entities.length,
        relationshipCount: relationships.length,
      },
      
      // Original data for renderer
      entities,
      relationships,
    };
    
    console.log(`📦 [ContentMapper] Filled ${Object.keys(filledSlots).length} slots`);
    
    return result;
  }
  
  /**
   * Group content based on form type
   */
  groupContent(form, entities, relationships, intentResult) {
    switch (form) {
      case STRUCTURAL_FORMS.COMPARISON:
        return GROUPING_STRATEGIES.split_by_type(entities, {});
      
      case STRUCTURAL_FORMS.COUNTERFACTUAL:
        return GROUPING_STRATEGIES.split_counterfactual(entities, {});
      
      case STRUCTURAL_FORMS.TIMELINE:
      case STRUCTURAL_FORMS.PROGRESSION:
        return GROUPING_STRATEGIES.order_temporal(entities, {});
      
      case STRUCTURAL_FORMS.HIERARCHY:
        return GROUPING_STRATEGIES.build_hierarchy(entities, relationships);
      
      case STRUCTURAL_FORMS.FORCE_DIAGRAM:
        return GROUPING_STRATEGIES.arrange_radial(entities, {});
      
      case STRUCTURAL_FORMS.CAUSE_EFFECT:
      case STRUCTURAL_FORMS.CAUSAL_CHAIN:
        return GROUPING_STRATEGIES.build_causal_chain(entities, relationships);
      
      default:
        // Default: just return all entities
        return { all: entities };
    }
  }
  
  /**
   * Fill form slots with grouped content
   */
  fillSlots(slots, groupedContent, metadata) {
    const filled = {};
    
    for (const [slotName, slotSpec] of Object.entries(slots)) {
      // Try to find matching content for this slot
      const content = this.findContentForSlot(slotName, slotSpec, groupedContent);
      
      if (content || !slotSpec.optional) {
        filled[slotName] = {
          ...slotSpec,
          content: content || this.createPlaceholder(slotName, metadata),
          isEmpty: !content,
        };
      }
    }
    
    return filled;
  }
  
  /**
   * Find content that matches a slot
   */
  findContentForSlot(slotName, slotSpec, groupedContent) {
    // Direct match by slot name
    if (groupedContent[slotName]) {
      return groupedContent[slotName];
    }
    
    // Match by role
    const role = slotSpec.role;
    
    // Map common roles to grouped content keys
    const roleMapping = {
      'option_a': 'left',
      'option_b': 'right',
      'actual_world': 'reality',
      'hypothetical': 'alternate',
      'initiator': 'cause',
      'result': 'effect',
      'process': 'mechanism',
      'parent_category': 'root',
      'subcategories': 'branches',
      'body': 'center',
      'force_vector': 'forces',
      'reference': 'ground',
      'initial': 'start',
      'milestones': 'events',
      'final': 'end',
    };
    
    const mappedKey = roleMapping[role];
    if (mappedKey && groupedContent[mappedKey]) {
      return groupedContent[mappedKey];
    }
    
    // Fallback: return all content if nothing specific found
    if (groupedContent.all) {
      return groupedContent.all;
    }
    
    return null;
  }
  
  /**
   * Create placeholder content when slot is empty
   */
  createPlaceholder(slotName, metadata) {
    return {
      id: `placeholder_${slotName}`,
      type: 'placeholder',
      properties: {
        label: metadata.topic || 'Concept',
        visualHint: 'generic',
      },
    };
  }
  
  /**
   * Generate annotations based on intent
   */
  generateAnnotations(conceptGraph, intentResult) {
    const annotations = [];
    const topic = conceptGraph.metadata.topic || 'Concept';
    
    // Title annotation
    annotations.push({
      type: 'title',
      text: topic,
      position: 'top_center',
    });
    
    // Intent-specific annotations
    switch (intentResult.primary) {
      case INTENT_TYPES.COUNTERFACTUAL:
        annotations.push({
          type: 'comparison_label',
          text: 'With vs Without',
          position: 'top_center',
        });
        break;
      
      case INTENT_TYPES.COMPARATIVE:
        annotations.push({
          type: 'vs_marker',
          text: 'VS',
          position: 'center',
        });
        break;
      
      case INTENT_TYPES.CAUSAL_INQUIRY:
        annotations.push({
          type: 'question',
          text: 'Why?',
          position: 'bottom_center',
        });
        break;
      
      case INTENT_TYPES.QUANTITATIVE:
        // Add formula if available
        const summary = conceptGraph.metadata.summary;
        if (summary) {
          annotations.push({
            type: 'formula',
            text: summary,
            position: 'bottom_center',
          });
        }
        break;
    }
    
    return annotations;
  }
}

// ============================================
// EXPORTS
// ============================================

export function createContentMapper(options) {
  return new ContentMapper(options);
}

export default ContentMapper;

