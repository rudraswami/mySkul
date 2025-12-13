/**
 * 🎨 SCENE COMPOSER
 * =================
 * 
 * Takes ConceptBreaker output and positions elements spatially
 * 
 * Input: Entities, relations, mode
 * Output: Positioned blueprint with x,y coordinates
 * 
 * Uses layout algorithms from layouts/
 */

import {
  forceDirectedLayout,
  gridLayout,
  circularLayout,
  treeLayout,
  flowLayout,
  LAYOUT_TYPES,
} from '../layouts';

// ============================================
// SCENE COMPOSER
// ============================================

export class SceneComposer {
  constructor(options = {}) {
    this.options = {
      canvasWidth: 400,
      canvasHeight: 300,
      padding: 60,
      defaultSpacing: 80,
      ...options,
    };
  }
  
  /**
   * Compose a complete scene from ConceptBreaker output
   * @param {Object} conceptData - Output from ConceptBreaker
   * @returns {Object} Positioned blueprint ready for rendering
   */
  compose(conceptData) {
    const {
      mode,
      entities = [],
      relations = [],
      controls = [],
      beats = [],
      metaphor,
      subject,
      concept,
    } = conceptData;
    
    // Choose layout algorithm based on mode
    const layoutType = this.selectLayout(mode);
    const positions = this.applyLayout(entities, relations, layoutType);
    
    // Build complete blueprint
    const blueprint = {
      mode,
      concept,
      subject,
      metaphor,
      
      // Items with positions
      items: entities.map(entity => ({
        ...entity,
        position: positions[entity.id] || { x: 200, y: 150 },
      })),
      
      // Arrows (connections)
      arrows: relations.map(rel => ({
        from: rel.from,
        to: rel.to,
        label: rel.label,
        style: rel.style || 'default',
        curved: rel.curved || false,
      })),
      
      // Labels (additional text)
      labels: this.generateLabels(conceptData),
      
      // Highlights (emphasis)
      highlights: conceptData.highlights || [],
      
      // Figures (stick figures)
      figures: this.generateFigures(conceptData),
      
      // Doodles (decorations)
      doodles: this.generateDoodles(conceptData),
      
      // Controls (interactive elements)
      controls,
      
      // Narrative beats
      beats,
    };
    
    return blueprint;
  }
  
  /**
   * Select appropriate layout algorithm based on mode
   */
  selectLayout(mode) {
    const layoutMap = {
      SCENE: LAYOUT_TYPES.FLOW,
      COMPARISON: LAYOUT_TYPES.GRID,
      PROCESS: LAYOUT_TYPES.FLOW,
      CYCLE: LAYOUT_TYPES.CIRCULAR,
      STRUCTURE: LAYOUT_TYPES.HUB,
      GRAPH: LAYOUT_TYPES.FLOW,
      TIMELINE: LAYOUT_TYPES.FLOW,
      HIERARCHY: LAYOUT_TYPES.TREE,
    };
    
    return layoutMap[mode] || LAYOUT_TYPES.FLOW;
  }
  
  /**
   * Apply layout algorithm to position items
   */
  applyLayout(entities, relations, layoutType) {
    const options = {
      canvasWidth: this.options.canvasWidth,
      canvasHeight: this.options.canvasHeight,
      spacing: this.options.defaultSpacing,
      paddingStart: this.options.padding,
    };
    
    switch (layoutType) {
      case LAYOUT_TYPES.GRID:
        return gridLayout(entities, { ...options, columns: 2 });
      
      case LAYOUT_TYPES.CIRCULAR:
        return circularLayout(entities, options);
      
      case LAYOUT_TYPES.FLOW:
        return flowLayout(entities, { ...options, direction: 'horizontal' });
      
      case LAYOUT_TYPES.TREE:
        return treeLayout(entities, options);
      
      case LAYOUT_TYPES.FORCE_DIRECTED:
        return forceDirectedLayout(entities, relations, options);
      
      default:
        return flowLayout(entities, options);
    }
  }
  
  /**
   * Generate labels from concept data
   */
  generateLabels(conceptData) {
    const labels = [];
    
    // Title label
    if (conceptData.concept) {
      labels.push({
        text: conceptData.concept,
        x: this.options.canvasWidth / 2,
        y: 30,
        fontSize: 22,
        underline: true,
        typewriter: true,
      });
    }
    
    // Additional labels from concept data
    if (conceptData.labels) {
      labels.push(...conceptData.labels);
    }
    
    return labels;
  }
  
  /**
   * Generate stick figures from concept data
   */
  generateFigures(conceptData) {
    const figures = [];
    
    // Add figures based on metaphor
    if (conceptData.metaphor === 'cricket') {
      figures.push({
        x: 80,
        y: 180,
        pose: 'pushing',
        expression: 'happy',
      });
    } else if (conceptData.metaphor === 'auto_rickshaw') {
      figures.push({
        x: 60,
        y: 180,
        pose: 'running',
        expression: 'neutral',
      });
    }
    
    // Add custom figures
    if (conceptData.figures) {
      figures.push(...conceptData.figures);
    }
    
    return figures;
  }
  
  /**
   * Generate doodles (decorative elements)
   */
  generateDoodles(conceptData) {
    const doodles = [];
    
    // Add sparkle for positive concepts
    if (conceptData.sentiment === 'positive' || conceptData.mode === 'SCENE') {
      doodles.push({
        type: 'sparkle',
        x: this.options.canvasWidth - 40,
        y: 40,
        size: 25,
      });
    }
    
    // Add custom doodles
    if (conceptData.doodles) {
      doodles.push(...conceptData.doodles);
    }
    
    return doodles;
  }
  
  /**
   * Optimize layout (adjust for overlaps)
   */
  optimizeLayout(positions, minDistance = 40) {
    const posArray = Object.entries(positions);
    
    // Simple overlap detection and adjustment
    for (let i = 0; i < posArray.length; i++) {
      for (let j = i + 1; j < posArray.length; j++) {
        const [idA, posA] = posArray[i];
        const [idB, posB] = posArray[j];
        
        const dx = posB.x - posA.x;
        const dy = posB.y - posA.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < minDistance && distance > 0) {
          const pushDistance = (minDistance - distance) / 2;
          const angle = Math.atan2(dy, dx);
          
          posA.x -= Math.cos(angle) * pushDistance;
          posA.y -= Math.sin(angle) * pushDistance;
          posB.x += Math.cos(angle) * pushDistance;
          posB.y += Math.sin(angle) * pushDistance;
        }
      }
    }
    
    return positions;
  }
}

/**
 * Create a scene composer
 */
export function createSceneComposer(options) {
  return new SceneComposer(options);
}

/**
 * Quick compose helper (for simple use cases)
 */
export function composeScene(conceptData, options) {
  const composer = new SceneComposer(options);
  return composer.compose(conceptData);
}

export default SceneComposer;

