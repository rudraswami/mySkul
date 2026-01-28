/**
 * 🗺️ ONTOLOGY LAYOUT ENGINE
 * ==========================
 * 
 * Computes entity positions based on visual ontology.
 * NO LLM-generated coordinates - all deterministic.
 * 
 * Each ontology has specific layout patterns that maximize clarity.
 */

// Layout strategies per ontology + world
const LAYOUT_STRATEGIES = {
  // ============================================
  // PHYSICAL MECHANICAL
  // ============================================
  physical_mechanical: {
    surface_friction: (entities, stage) => {
      // Subject on top, surface at bottom, force attached to subject
      const result = {};
      const centerX = stage.width / 2;
      const surfaceY = stage.height * 0.75;
      
      entities.forEach(entity => {
        switch (entity.role) {
          case 'subject':
            result[entity.id] = { x: centerX, y: surfaceY - 80 };
            break;
          case 'environment':
            result[entity.id] = { x: centerX, y: surfaceY };
            break;
          case 'force':
            // Attach to subject, offset to the right
            result[entity.id] = { x: centerX + 80, y: surfaceY - 80 };
            break;
          case 'label':
          case 'indicator':
            result[entity.id] = { x: centerX, y: stage.height * 0.15 };
            break;
          default:
            result[entity.id] = { x: centerX, y: stage.height / 2 };
        }
      });
      return result;
    },
    
    projectile_motion: (entities, stage) => {
      // Subject at left, trajectory path, ground at bottom
      const result = {};
      entities.forEach(entity => {
        switch (entity.role) {
          case 'subject':
            result[entity.id] = { x: stage.width * 0.15, y: stage.height * 0.7 };
            break;
          case 'environment':
            result[entity.id] = { x: stage.width / 2, y: stage.height * 0.85 };
            break;
          case 'force':
            result[entity.id] = { x: stage.width * 0.15 + 50, y: stage.height * 0.7 - 50 };
            break;
          default:
            result[entity.id] = { x: stage.width / 2, y: stage.height * 0.2 };
        }
      });
      return result;
    },
    
    collision_system: (entities, stage) => {
      // Multiple subjects spread horizontally
      const result = {};
      const subjects = entities.filter(e => e.role === 'subject');
      const spacing = stage.width / (subjects.length + 1);
      
      let subjectIndex = 0;
      entities.forEach(entity => {
        switch (entity.role) {
          case 'subject':
            result[entity.id] = { 
              x: spacing * (subjectIndex + 1), 
              y: stage.height / 2 
            };
            subjectIndex++;
            break;
          case 'environment':
            result[entity.id] = { x: stage.width / 2, y: stage.height * 0.85 };
            break;
          default:
            result[entity.id] = { x: stage.width / 2, y: stage.height * 0.15 };
        }
      });
      return result;
    },
    
    pendulum_swing: (entities, stage) => {
      const result = {};
      const pivotY = stage.height * 0.2;
      
      entities.forEach(entity => {
        switch (entity.role) {
          case 'subject':  // The bob
            result[entity.id] = { x: stage.width / 2, y: stage.height * 0.6 };
            break;
          case 'environment':  // The pivot
            result[entity.id] = { x: stage.width / 2, y: pivotY };
            break;
          case 'force':
            result[entity.id] = { x: stage.width / 2 + 60, y: stage.height * 0.6 };
            break;
          default:
            result[entity.id] = { x: stage.width / 2, y: stage.height * 0.1 };
        }
      });
      return result;
    }
  },
  
  // ============================================
  // SYSTEMIC CAUSAL
  // ============================================
  systemic_causal: {
    cyclic_process: (entities, stage) => {
      // Circular arrangement
      const result = {};
      const centerX = stage.width / 2;
      const centerY = stage.height / 2;
      const radius = Math.min(stage.width, stage.height) * 0.3;
      
      const nodes = entities.filter(e => e.role === 'subject' || e.role === 'node');
      nodes.forEach((entity, i) => {
        const angle = (i / nodes.length) * Math.PI * 2 - Math.PI / 2;
        result[entity.id] = {
          x: centerX + Math.cos(angle) * radius,
          y: centerY + Math.sin(angle) * radius
        };
      });
      
      // Labels/indicators at center or top
      entities.filter(e => e.role === 'label' || e.role === 'indicator').forEach(entity => {
        result[entity.id] = { x: centerX, y: stage.height * 0.1 };
      });
      
      // Connectors will be computed based on from/to
      entities.filter(e => e.role === 'connector').forEach(entity => {
        result[entity.id] = { x: 0, y: 0 };  // Position computed from endpoints
      });
      
      return result;
    },
    
    chain_reaction: (entities, stage) => {
      // Horizontal chain, left to right
      const result = {};
      const nodes = entities.filter(e => e.role === 'subject' || e.role === 'node');
      const spacing = stage.width / (nodes.length + 1);
      const y = stage.height / 2;
      
      nodes.forEach((entity, i) => {
        result[entity.id] = { x: spacing * (i + 1), y };
      });
      
      entities.filter(e => e.role !== 'subject' && e.role !== 'node').forEach(entity => {
        result[entity.id] = { x: stage.width / 2, y: stage.height * 0.15 };
      });
      
      return result;
    },
    
    flow_network: (entities, stage) => {
      // Tree-like structure, source at top
      const result = {};
      const levels = {};
      
      // Group by level (simplified - assume linear for now)
      entities.forEach((entity, i) => {
        if (entity.role === 'subject' || entity.role === 'node') {
          const level = Math.floor(i / 2);
          if (!levels[level]) levels[level] = [];
          levels[level].push(entity);
        }
      });
      
      Object.entries(levels).forEach(([level, levelEntities]) => {
        const levelNum = parseInt(level);
        const spacing = stage.width / (levelEntities.length + 1);
        const y = (levelNum + 1) * (stage.height / (Object.keys(levels).length + 1));
        
        levelEntities.forEach((entity, i) => {
          result[entity.id] = { x: spacing * (i + 1), y };
        });
      });
      
      // Non-nodes
      entities.filter(e => !['subject', 'node'].includes(e.role)).forEach(entity => {
        result[entity.id] = result[entity.id] || { x: stage.width / 2, y: stage.height * 0.1 };
      });
      
      return result;
    }
  },
  
  // ============================================
  // SPATIAL STRUCTURAL
  // ============================================
  spatial_structural: {
    layered_explode: (entities, stage) => {
      // Vertical stack of layers
      const result = {};
      const layers = entities.filter(e => e.template === 'layer' || e.role === 'layer');
      const spacing = stage.height / (layers.length + 2);
      
      layers.forEach((entity, i) => {
        result[entity.id] = { x: stage.width / 2, y: spacing * (i + 1) };
      });
      
      // Labels to the side
      entities.filter(e => e.role === 'label').forEach((entity, i) => {
        result[entity.id] = { x: stage.width * 0.85, y: spacing * (i + 1) };
      });
      
      return result;
    },
    
    radial_structure: (entities, stage) => {
      // Center entity with orbiting parts
      const result = {};
      const centerX = stage.width / 2;
      const centerY = stage.height / 2;
      
      const center = entities.find(e => e.role === 'subject');
      if (center) {
        result[center.id] = { x: centerX, y: centerY };
      }
      
      const orbiting = entities.filter(e => e.role !== 'subject' && e.role !== 'label');
      const radius = Math.min(stage.width, stage.height) * 0.25;
      
      orbiting.forEach((entity, i) => {
        const angle = (i / orbiting.length) * Math.PI * 2;
        result[entity.id] = {
          x: centerX + Math.cos(angle) * radius,
          y: centerY + Math.sin(angle) * radius
        };
      });
      
      return result;
    },
    
    nested_containers: (entities, stage) => {
      // Concentric rectangles
      const result = {};
      const centerX = stage.width / 2;
      const centerY = stage.height / 2;
      
      const containers = entities.filter(e => e.role === 'environment' || e.template === 'region');
      containers.forEach((entity, i) => {
        result[entity.id] = { x: centerX, y: centerY };
        // Size will be adjusted by renderer based on nesting level
      });
      
      const subjects = entities.filter(e => e.role === 'subject');
      subjects.forEach((entity, i) => {
        result[entity.id] = { x: centerX, y: centerY };
      });
      
      return result;
    }
  },
  
  // ============================================
  // CHRONOLOGICAL EVOLUTIONARY
  // ============================================
  chronological_evolutionary: {
    timeline_horizontal: (entities, stage) => {
      // Left to right timeline
      const result = {};
      const timelineY = stage.height * 0.6;
      const events = entities.filter(e => e.role === 'subject' || e.role === 'event');
      const spacing = stage.width / (events.length + 1);
      
      events.forEach((entity, i) => {
        result[entity.id] = { x: spacing * (i + 1), y: timelineY };
      });
      
      // Axis line
      entities.filter(e => e.template === 'axis').forEach(entity => {
        result[entity.id] = { x: stage.width / 2, y: timelineY + 50 };
      });
      
      // Labels above
      entities.filter(e => e.role === 'label').forEach((entity, i) => {
        result[entity.id] = { x: spacing * (i + 1), y: timelineY - 80 };
      });
      
      return result;
    },
    
    stage_morph: (entities, stage) => {
      // Stages spread horizontally with morphing between
      return this.timeline_horizontal(entities, stage);
    }
  },
  
  // ============================================
  // QUANTITATIVE MATHEMATICAL
  // ============================================
  quantitative_mathematical: {
    function_graph: (entities, stage) => {
      const result = {};
      const graphCenter = { x: stage.width / 2, y: stage.height / 2 };
      
      entities.forEach(entity => {
        switch (entity.template) {
          case 'axis':
            result[entity.id] = graphCenter;
            break;
          case 'graph_line':
            result[entity.id] = graphCenter;
            break;
          case 'tracer_dot':
            result[entity.id] = { x: graphCenter.x - 150, y: graphCenter.y };
            break;
          default:
            result[entity.id] = { x: stage.width / 2, y: stage.height * 0.1 };
        }
      });
      
      return result;
    },
    
    bar_comparison: (entities, stage) => {
      const result = {};
      const bars = entities.filter(e => e.role === 'subject');
      const spacing = stage.width / (bars.length + 1);
      const baseY = stage.height * 0.8;
      
      bars.forEach((entity, i) => {
        result[entity.id] = { x: spacing * (i + 1), y: baseY };
      });
      
      return result;
    }
  },
  
  // ============================================
  // ABSTRACT RELATIONAL
  // ============================================
  abstract_relational: {
    venn_overlap: (entities, stage) => {
      const result = {};
      const centerY = stage.height / 2;
      const offset = stage.width * 0.15;
      
      const groups = entities.filter(e => e.template === 'region');
      if (groups.length >= 2) {
        result[groups[0].id] = { x: stage.width / 2 - offset, y: centerY };
        result[groups[1].id] = { x: stage.width / 2 + offset, y: centerY };
      }
      
      // Labels
      entities.filter(e => e.role === 'label').forEach((entity, i) => {
        result[entity.id] = { 
          x: i === 0 ? stage.width * 0.25 : stage.width * 0.75, 
          y: stage.height * 0.2 
        };
      });
      
      return result;
    },
    
    hierarchy_tree: (entities, stage) => {
      // Top-down tree
      const result = {};
      const root = entities.find(e => e.role === 'subject');
      if (root) {
        result[root.id] = { x: stage.width / 2, y: stage.height * 0.2 };
      }
      
      const children = entities.filter(e => e.role !== 'subject' && e.role !== 'label');
      const spacing = stage.width / (children.length + 1);
      
      children.forEach((entity, i) => {
        result[entity.id] = { x: spacing * (i + 1), y: stage.height * 0.6 };
      });
      
      return result;
    },
    
    comparison_split: (entities, stage) => {
      // Left-right split
      const result = {};
      const items = entities.filter(e => e.role === 'subject');
      
      items.forEach((entity, i) => {
        const x = i % 2 === 0 ? stage.width * 0.25 : stage.width * 0.75;
        result[entity.id] = { x, y: stage.height / 2 };
      });
      
      return result;
    }
  }
};

/**
 * Compute positions for all entities based on ontology and world
 */
export function computeLayout(script, stageSize = { width: 800, height: 600 }) {
  const { ontology, world, entities } = script;
  
  // Get layout strategy
  const ontologyStrategies = LAYOUT_STRATEGIES[ontology];
  if (!ontologyStrategies) {
    console.warn(`[OntologyLayoutEngine] Unknown ontology: ${ontology}, using default`);
    return defaultLayout(entities, stageSize);
  }
  
  const strategy = ontologyStrategies[world];
  if (!strategy) {
    console.warn(`[OntologyLayoutEngine] Unknown world: ${world}, using first available`);
    const firstStrategy = Object.values(ontologyStrategies)[0];
    return firstStrategy(entities, stageSize);
  }
  
  return strategy(entities, stageSize);
}

/**
 * Default fallback layout (grid)
 */
function defaultLayout(entities, stage) {
  const result = {};
  const cols = Math.ceil(Math.sqrt(entities.length));
  const cellWidth = stage.width / (cols + 1);
  const cellHeight = stage.height / (Math.ceil(entities.length / cols) + 1);
  
  entities.forEach((entity, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    result[entity.id] = {
      x: cellWidth * (col + 1),
      y: cellHeight * (row + 1)
    };
  });
  
  return result;
}

/**
 * Apply layout to entities (mutates positions)
 */
export function applyLayout(entities, layout) {
  entities.forEach(entity => {
    if (layout[entity.id]) {
      entity.position = layout[entity.id];
    }
  });
  return entities;
}

export default { computeLayout, applyLayout };
