/**
 * 🔌 SMARTBOARD ADAPTER
 * =====================
 * 
 * Seamless integration between NETRA and the existing SmartBoard component.
 * 
 * This adapter:
 * - Converts SmartBoard's artifact format to NETRA-compatible input
 * - Handles fallback to V6 Magic Notebook if needed
 * - Provides smooth transition between engines
 * - Maintains backward compatibility
 */

import React, { useMemo, useCallback } from 'react';
import NetraEngine from '../NetraEngine';

// ============================================
// ARTIFACT CONVERTER
// ============================================

/**
 * Convert SmartBoard artifact to NETRA input format
 */
export function convertArtifactToNetraInput(artifact) {
  if (!artifact) return null;

  // Extract question
  const question = 
    artifact.originalQuestion ||
    artifact.question ||
    artifact.concept ||
    artifact.topic ||
    null;

  // Extract context
  const context = {
    subject: artifact.subject || artifact.domain || 'physics',
    level: artifact.level || 'high_school',
    complexity: artifact.complexity || 'medium',
  };

  // Check if artifact has pre-generated scene (from backend)
  let preGeneratedScene = null;
  if (artifact.netraScene) {
    preGeneratedScene = artifact.netraScene;
  }

  return {
    question,
    context,
    preGeneratedScene,
  };
}

/**
 * Check if artifact is compatible with NETRA
 */
export function isNetraCompatible(artifact) {
  if (!artifact) return false;

  // NETRA can handle:
  // 1. Question-based artifacts
  // 2. Concept-based artifacts
  // 3. Blueprint-based artifacts (from V6, will convert)
  
  const hasQuestion = !!(
    artifact.originalQuestion ||
    artifact.question ||
    artifact.concept ||
    artifact.topic
  );

  const hasBlueprint = !!artifact.blueprint;

  return hasQuestion || hasBlueprint;
}

/**
 * Convert V6 Blueprint to NETRA ConceptGraph
 * (For backward compatibility with existing blueprints)
 */
export function convertV6BlueprintToConceptGraph(blueprint) {
  if (!blueprint) return null;

  // Import ConceptGraph here to avoid circular dependency
  const { ConceptGraph, ENTITY_TYPES, RELATIONSHIP_TYPES } = require('../core/ConceptGraph');

  const graph = new ConceptGraph();

  // Set metadata
  graph.setMetadata('domain', blueprint.subject || 'physics');
  graph.setMetadata('topic', blueprint.concept || 'Concept');
  graph.setMetadata('visualType', blueprint.mode?.toLowerCase() || 'scene');

  // Convert entities
  if (blueprint.entities) {
    blueprint.entities.forEach((entity, index) => {
      graph.addEntity(
        entity.id || `entity_${index}`,
        mapV6TypeToNetraType(entity.type),
        {
          label: entity.label,
          variant: entity.variant,
          visualHint: entity.type,
        }
      );
    });
  }

  // Convert items (V6 positioned items)
  if (blueprint.items) {
    blueprint.items.forEach((item, index) => {
      graph.addEntity(
        item.id || `item_${index}`,
        mapV6TypeToNetraType(item.type),
        {
          label: item.label,
          variant: item.variant,
          visualHint: item.type,
          position: item.position, // Preserve position
        }
      );
    });
  }

  // Convert relations/arrows
  const relations = blueprint.relations || blueprint.arrows || [];
  relations.forEach((rel) => {
    graph.addRelationship(
      rel.from || rel.from_,
      rel.to,
      mapV6RelationToNetraType(rel.label || rel.style),
      { label: rel.label }
    );
  });

  return graph;
}

/**
 * Map V6 entity type to NETRA type
 */
function mapV6TypeToNetraType(v6Type) {
  const { ENTITY_TYPES } = require('../core/ConceptGraph');
  
  const typeMap = {
    circle: ENTITY_TYPES.BODY,
    rect: ENTITY_TYPES.STRUCTURE,
    node: ENTITY_TYPES.OBJECT,
    arrow: ENTITY_TYPES.FORCE,
    force: ENTITY_TYPES.FORCE,
    vector: ENTITY_TYPES.VECTOR,
    cell: ENTITY_TYPES.CELL,
    atom: ENTITY_TYPES.ATOM,
    molecule: ENTITY_TYPES.MOLECULE,
    graph: ENTITY_TYPES.FUNCTION,
    process: ENTITY_TYPES.PROCESS,
  };

  return typeMap[v6Type?.toLowerCase()] || ENTITY_TYPES.OBJECT;
}

/**
 * Map V6 relation to NETRA relationship type
 */
function mapV6RelationToNetraType(v6Relation) {
  const { RELATIONSHIP_TYPES } = require('../core/ConceptGraph');
  
  const relationMap = {
    affects: RELATIONSHIP_TYPES.ACTS_ON,
    causes: RELATIONSHIP_TYPES.CAUSES,
    produces: RELATIONSHIP_TYPES.PRODUCES,
    becomes: RELATIONSHIP_TYPES.BECOMES,
    contains: RELATIONSHIP_TYPES.CONTAINS,
    default: RELATIONSHIP_TYPES.ACTS_ON,
  };

  return relationMap[v6Relation?.toLowerCase()] || RELATIONSHIP_TYPES.ACTS_ON;
}

// ============================================
// SMARTBOARD ADAPTER COMPONENT
// ============================================

const SmartBoardAdapter = ({
  artifact,
  width = 600,
  height = 500,
  showGrid = true,
  showMetadata = true,
  onGenerated = null,
  onError = null,
  className = '',
  style = {},
}) => {
  // Convert artifact to NETRA input
  const netraInput = useMemo(() => {
    return convertArtifactToNetraInput(artifact);
  }, [artifact]);

  // Handle generation callback
  const handleGenerated = useCallback((result) => {
    console.log('🔌 [SmartBoardAdapter] NETRA generated:', result);
    onGenerated?.(result);
  }, [onGenerated]);

  // Handle error callback
  const handleError = useCallback((error) => {
    console.error('🔌 [SmartBoardAdapter] NETRA error:', error);
    onError?.(error);
  }, [onError]);

  // If no valid input, show placeholder
  if (!netraInput || !netraInput.question) {
    return (
      <div
        className={`smartboard-adapter empty ${className}`}
        style={{
          width,
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#FFFEF7',
          borderRadius: 12,
          ...style,
        }}
      >
        <div
          style={{
            fontFamily: "'Kalam', cursive",
            fontSize: 16,
            color: '#BDC3C7',
          }}
        >
          Ask a question to see visual explanation
        </div>
      </div>
    );
  }

  return (
    <NetraEngine
      question={netraInput.question}
      context={netraInput.context}
      preGeneratedScene={netraInput.preGeneratedScene}
      width={width}
      height={height}
      showGrid={showGrid}
      showMetadata={showMetadata}
      onGenerated={handleGenerated}
      onError={handleError}
      className={`smartboard-adapter ${className}`}
      style={style}
    />
  );
};

// ============================================
// REACT HOOK FOR SMARTBOARD INTEGRATION
// ============================================

/**
 * Hook for using NETRA within SmartBoard context
 */
export function useNetraWithSmartBoard(artifact, options = {}) {
  const netraInput = useMemo(() => {
    return convertArtifactToNetraInput(artifact);
  }, [artifact]);

  const isCompatible = useMemo(() => {
    return isNetraCompatible(artifact);
  }, [artifact]);

  return {
    question: netraInput?.question,
    context: netraInput?.context,
    preGeneratedScene: netraInput?.preGeneratedScene,
    isCompatible,
    
    // Utility: Check if should use NETRA or fallback
    shouldUseNetra: isCompatible && !!netraInput?.question,
  };
}

export default SmartBoardAdapter;



