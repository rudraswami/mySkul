import React, { useMemo, useCallback, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MetroTrain } from './entities/MetroTrain';
import { Track } from './entities/Track';
import { DirectionArrow } from './entities/DirectionArrow';
import { CricketBall } from './entities/CricketBall';

/**
 * SCENE RENDERER
 * The heart of the visual system.
 * Takes scene spec and renders entities with animations.
 * 
 * Input: sceneSpec = { background, entities, actions, ... }
 * Output: Fully animated, interactive scene
 */
const SceneRenderer = ({
  sceneSpec = {},
  animationSequence = [],
  currentStageIndex = 0,
  isPlaying = true,
}) => {
  const [entityPositions, setEntityPositions] = useState({});
  const [entityStates, setEntityStates] = useState({});

  // Ensure animationSequence is always an array (handle null/undefined)
  const safeAnimationSequence = useMemo(() => {
    if (!animationSequence) return [];
    if (Array.isArray(animationSequence)) return animationSequence;
    // If it's an object, try to extract array from it
    if (typeof animationSequence === 'object' && animationSequence.actions) {
      return Array.isArray(animationSequence.actions) ? animationSequence.actions : [];
    }
    return [];
  }, [animationSequence]);

  console.log('[SceneRenderer] Rendering scene:', sceneSpec);
  console.log('[SceneRenderer] Stage index:', currentStageIndex);
  console.log('[SceneRenderer] Animation sequence:', safeAnimationSequence);

  // Entity type to SVG component mapping
  // Backend sends: entity_id like 'metro_train', 'cricket_ball', 'direction_arrow'
  // We map: entity_id → React component
  const ENTITY_MAP = {
    // Physics entities
    metro_train: MetroTrain,
    train: MetroTrain,
    car: MetroTrain, // Placeholder - can be enhanced
    track: Track,
    rail: Track,
    direction_arrow: DirectionArrow,
    arrow: DirectionArrow,
    speedometer: DirectionArrow, // Placeholder
    cricket_ball: CricketBall,
    ball: CricketBall,
    
    // Chemistry placeholders (will add real components)
    atom_nucleus: CricketBall, // Placeholder  
    electron: CricketBall,
    electron_shells: CricketBall,
    
    // Biology placeholders
    chloroplast: CricketBall,
    mitochondria: CricketBall,
    
    // Math placeholders
    parabola_curve: DirectionArrow,
    line: Track,
    
    // Generic/unknown concepts
    generic: CricketBall,  // Fallback for unknown concepts
    concept_element_0: CricketBall,
    concept_element_1: CricketBall,
    concept_element_2: CricketBall,
    concept_element_3: CricketBall,
    concept_element_4: CricketBall,
    main_concept: CricketBall,  // Main concept entity
    component_1: CricketBall,  // Component entities
    component_2: CricketBall,
    example_1: CricketBall,  // Example entities
    example_2: CricketBall,
  };

  // Get background style
  const getBackgroundStyle = useCallback(() => {
    const sceneType = sceneSpec.scene_type || sceneSpec.background || 'default';
    const backgroundStyles = {
      delhi_metro_road: {
        background: 'linear-gradient(to bottom, #87CEEB 0%, #E8E8E8 30%, #FFB6C1 100%)',
        description: 'Delhi street scene',
      },
      cricket_stadium: {
        background: 'linear-gradient(to bottom, #87CEEB 0%, #228B22 60%, #8B7355 100%)',
        description: 'Cricket field',
      },
      chemistry_lab: {
        background: 'linear-gradient(to bottom, #F0F8FF 0%, #E6E6FA 100%)',
        description: 'Lab environment',
      },
      default: {
        background: 'linear-gradient(to bottom, #E3F2FD 0%, #F5F5F5 100%)',
        description: 'Generic scene',
      },
    };
    return backgroundStyles[sceneType] || backgroundStyles.default;
  }, [sceneSpec]);

  // Render individual entity
  const renderEntity = useCallback((entity, index) => {
    if (!entity) return null;

    // Map entity ID to SVG component (use entity.id, not entity.type)
    const EntityComponent = ENTITY_MAP[entity.id] || ENTITY_MAP[entity.type];

    if (!EntityComponent) {
      console.warn(`[SceneRenderer] Unknown entity type: ${entity.type} (id: ${entity.id})`);
      // Render fallback box with entity info
      return (
        <g key={`entity-${index}`} opacity="0.5">
          <rect
            x={entity.initial_position?.x || entity.x || 0}
            y={entity.initial_position?.y || entity.y || 0}
            width="60"
            height="60"
            fill="#FF6B6B"
            stroke="#FF0000"
            strokeWidth="2"
            rx="4"
          />
          <text
            x={(entity.initial_position?.x || entity.x || 0) + 30}
            y={(entity.initial_position?.y || entity.y || 0) + 35}
            textAnchor="middle"
            fontSize="10"
            fill="white"
            fontWeight="bold"
          >
            {entity.id}
          </text>
        </g>
      );
    }

    // Get animations for this entity (match by entity.id)
    const entityAnimations = safeAnimationSequence.filter(
      (action) => action.entity === entity.id
    );

    console.log(`[SceneRenderer] Entity ${entity.id}:`, {
      type: entity.type,
      initialPos: entity.initial_position,
      animations: entityAnimations.map(a => ({ action: a.action, to: a.to })),
    });

    // Calculate target position and rotation from the FIRST animation
    let targetX = entity.initial_position?.x || 0;
    let targetY = entity.initial_position?.y || 0;
    let targetRotate = 0;
    let animationDuration = 1.5;

    entityAnimations.forEach((action) => {
      if (action.action === 'move') {
        targetX = action.to?.x || targetX;
        targetY = action.to?.y || targetY;
        animationDuration = (action.duration_ms || 1500) / 1000;
      } else if (action.action === 'rotate') {
        targetRotate = action.to?.rotation || 0;
        animationDuration = (action.duration_ms || 1200) / 1000;
      }
    });

    return (
      <motion.g
        key={`entity-${index}`}
        initial={{
          x: entity.initial_position?.x || 0,
          y: entity.initial_position?.y || 0,
          rotate: 0,
          opacity: 1,
        }}
        animate={{
          x: targetX,
          y: targetY,
          rotate: targetRotate,
          opacity: 1,
        }}
        transition={{
          duration: animationDuration,
          ease: 'easeInOut',
          delay: 0.2,
        }}
      >
        <EntityComponent
          x={0}
          y={0}
          size={entity.size?.width || entity.size || 60}
          color={entity.props?.color || entity.color || '#000'}
        />
      </motion.g>
    );
  }, [safeAnimationSequence]);

  // Main render
  if (!sceneSpec || !sceneSpec.entities || sceneSpec.entities.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-200 rounded-lg">
        <div className="text-center">
          <p className="text-gray-600 font-semibold">No scene data</p>
          <p className="text-sm text-gray-500">Scene: {sceneSpec.background}</p>
        </div>
      </div>
    );
  }

  const bgStyle = getBackgroundStyle();

  return (
    <div
      className="w-full rounded-lg overflow-hidden shadow-lg"
      style={{
        background: bgStyle.background,
        minHeight: '400px',
        position: 'relative',
      }}
    >
      {/* SVG Canvas for rendering */}
      <svg
        width="100%"
        height="400"
        viewBox="0 0 800 400"
        preserveAspectRatio="xMidYMid meet"
        style={{
          background: 'transparent',
        }}
      >
        {/* Render all entities */}
        {sceneSpec.entities?.map((entity, idx) => renderEntity(entity, idx))}
      </svg>

      {/* Debug info */}
      <div
        className="absolute top-2 left-2 bg-black/70 text-white text-xs p-2 rounded"
        style={{ maxWidth: '200px', zIndex: 10 }}
      >
        <div>Entities: {sceneSpec.entities?.length || 0}</div>
        <div>Actions: {safeAnimationSequence?.length || 0}</div>
        <div>Stage: {currentStageIndex + 1}</div>
      </div>
    </div>
  );
};

export default SceneRenderer;

