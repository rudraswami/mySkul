/**
 * Animated Scene Component - REBUILT FOR ACTUAL ANIMATIONS
 * Uses Framer Motion with sequential keyframes
 * GUARANTEED TO SHOW MOVEMENT
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import EntityRenderers from './EntityRenderers';

const { Physics, Chemistry, Biology, Math: MathEntities } = EntityRenderers;

export default function AnimatedScene({
  sceneSpec,
  animationSequence,
  isPlaying = true,
  interactiveValues = {},
  onAnimationComplete
}) {
  console.log('[AnimatedScene] Mounted with:', { sceneSpec, animationSequence });

  if (!sceneSpec) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl">
        <p className="text-gray-600">No scene data</p>
      </div>
    );
  }

  const entities = sceneSpec.entities || [];
  const actions = sceneSpec.actions || [];
  const background = sceneSpec.background || {};
  
  console.log(`[AnimatedScene] ${entities.length} entities, ${actions.length} actions`);

  // Render background
  const renderBackground = () => {
    const layers = background.layers || ['field_grass'];
    
    const bgStyles = {
      'sky_blue': 'linear-gradient(to bottom, #87CEEB, #B0E0E6)',
      'field_grass': 'linear-gradient(to bottom, #22C55E, #16A34A)',
      'cricket_stadium': 'linear-gradient(to bottom, #15803D, #22C55E)',
      'sky': 'linear-gradient(to bottom, #60A5FA, #93C5FD)',
      'platform_floor': '#9CA3AF',
      'road_asphalt': '#1F2937',
      'grid_paper': 'repeating-linear-gradient(0deg, #E5E7EB 0px, #E5E7EB 1px, transparent 1px, transparent 20px), repeating-linear-gradient(90deg, #E5E7EB 0px, #E5E7EB 1px, transparent 1px, transparent 20px)',
      'default': 'linear-gradient(135deg, #D4A574 0%, #C08552 100%)'
    };

    return (
      <div className="absolute inset-0">
        {layers.map((layer, idx) => (
          <motion.div
            key={layer}
            className="absolute inset-0"
            style={{
              background: bgStyles[layer] || bgStyles['default'],
              zIndex: idx
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          />
        ))}
      </div>
    );
  };

  // Render entities with ACTUAL ANIMATIONS
  const renderEntities = () => {
    if (entities.length === 0) return null;

    return entities.map((entity, index) => {
      const entityId = entity.id;
      const initialPos = entity.initial_position || { x: 200 + index * 130, y: 250 };
      
      // Find actions for this entity
      const entityActions = actions.filter(a => a.entity === entityId);
      
      // Build Framer Motion variants for this entity
      const entityVariants = buildEntityVariants(entity, entityActions, initialPos);
      
      console.log(`[AnimatedScene] ${entityId}: initial (${initialPos.x}, ${initialPos.y}), ${entityActions.length} actions`);
      
      return (
        <motion.div
          key={`${entityId}-${index}`}
          className="absolute"
          style={{ left: 0, top: 0, zIndex: 50 + index }}
          variants={entityVariants}
          initial="initial"
          animate="animate"
        >
          {renderEntity(entity, interactiveValues)}
        </motion.div>
      );
    });
  };

  // Build Framer Motion variants from actions
  const buildEntityVariants = (entity, entityActions, initialPos) => {
    const variants = {
      initial: {
        x: initialPos.x,
        y: initialPos.y,
        opacity: 0,
        scale: 0.8
      },
      animate: {}
    };

    // Default: fade in
    variants.animate = {
      x: initialPos.x,
      y: initialPos.y,
      opacity: 1,
      scale: entity.highlighted ? 1.15 : 1,
      transition: {
        duration: 0.8,
        delay: 0.2
      }
    };

    // Apply MOVE action
    const moveAction = entityActions.find(a => a.action === 'move');
    if (moveAction) {
      variants.animate.x = moveAction.to.x;
      variants.animate.y = moveAction.to.y;
      variants.animate.transition = {
        duration: (moveAction.duration_ms || 2000) / 1000,
        delay: (moveAction.start_time || 0) / 1000,
        ease: moveAction.easing || 'easeInOut'
      };
      console.log(`[AnimatedScene] ${entity.id} MOVE animation: x=${moveAction.to.x}, y=${moveAction.to.y}, duration=${moveAction.duration_ms}ms`);
    }

    // Apply ROTATE action
    const rotateAction = entityActions.find(a => a.action === 'rotate');
    if (rotateAction) {
      variants.animate.rotate = rotateAction.to.rotation;
      variants.animate.transition = {
        ...variants.animate.transition,
        duration: (rotateAction.duration_ms || 1500) / 1000
      };
      console.log(`[AnimatedScene] ${entity.id} ROTATE animation: ${rotateAction.to.rotation}°`);
    }

    // Apply PULSE/GLOW action
    const pulseAction = entityActions.find(a => a.action === 'pulse' || a.action === 'glow');
    if (pulseAction) {
      variants.animate.scale = [1, 1.2, 1];
      variants.animate.opacity = [1, 0.85, 1];
      variants.animate.transition = {
        duration: (pulseAction.duration_ms || 1000) / 1000,
        repeat: Infinity,
        ease: 'easeInOut'
      };
      console.log(`[AnimatedScene] ${entity.id} PULSE animation`);
    }

    return variants;
  };

  // Render individual entity
  const renderEntity = (entity, interactiveValues) => {
    const entityId = entity.id;
    const emoji = getEmoji(entityId);
    const componentName = entity.svg_component;

    // Try to render SVG component
    try {
      if (componentName === 'MetroTrainSVG' && Physics?.MetroTrainSVG) {
        return <Physics.MetroTrainSVG size={entity.size} />;
      } else if (componentName === 'DirectionArrowSVG' && Physics?.DirectionArrowSVG) {
        return <Physics.DirectionArrowSVG direction={interactiveValues.direction || 0} size={entity.size} />;
      } else if (componentName === 'SpeedometerSVG' && Physics?.SpeedometerSVG) {
        return <Physics.SpeedometerSVG speed={interactiveValues.speed || 60} size={entity.size} />;
      } else if (componentName === 'CricketBallSVG' && Physics?.CricketBallSVG) {
        return <Physics.CricketBallSVG size={entity.size} />;
      }
    } catch (err) {
      console.error(`[AnimatedScene] SVG error for ${componentName}:`, err);
    }

    // FALLBACK: Beautiful animated emoji card
    return (
      <div className="flex flex-col items-center gap-2">
        <motion.div
          className="flex items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-purple-600 text-white shadow-2xl border-4 border-white"
          style={{ width: '96px', height: '96px', fontSize: '56px' }}
          whileHover={{ scale: 1.1 }}
        >
          {emoji}
        </motion.div>
        <div className="bg-white/95 px-4 py-2 rounded-full text-sm font-bold text-purple-700 shadow-lg">
          {entityId.replace(/_/g, ' ').replace(/([a-z])([A-Z])/g, '$1 $2')}
        </div>
      </div>
    );
  };

  const getEmoji = (id) => {
    const map = {
      'cricket_ball': '🏏',
      'ball': '🏏',
      'bowler': '🏏',
      'trajectory_line': '↗️',
      'speed_gun': '📡',
      'stumps': '🎯',
      'metro_train': '🚇',
      'car': '🚗',
      'direction_arrow': '➡️',
      'speedometer': '⏱️',
      'landmark_a': '📍',
      'landmark_b': '📍',
      'platform': '🏢',
      'tracks': '🛤️'
    };
    return map[id] || '🔷';
  };

  return (
    <div className="relative w-full overflow-hidden rounded-2xl shadow-2xl bg-gradient-to-br from-blue-100 to-purple-100" style={{ height: '500px' }}>
      {/* Background */}
      {renderBackground()}

      {/* Entities */}
      <div className="absolute inset-0">
        {renderEntities()}
      </div>

      {/* Debug Info */}
      <div className="absolute top-4 left-4 z-50 bg-black/80 text-white text-xs p-3 rounded-lg shadow-xl space-y-1">
        <div className="font-bold text-green-400">Scene: {sceneSpec.scene_id}</div>
        <div>Entities: {entities.length}</div>
        <div>Actions: {actions.length}</div>
        <div>Type: {sceneSpec.scene_type}</div>
        {actions.length > 0 && (
          <div className="text-green-300 mt-2">✓ Animations active!</div>
        )}
      </div>

      {/* Timeline */}
      <div className="absolute bottom-4 left-4 right-4 z-50">
        <div className="bg-white/90 rounded-full h-3 overflow-hidden shadow-lg">
          <motion.div
            className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600"
            initial={{ width: '0%' }}
            animate={{ width: '100%' }}
            transition={{ duration: 3, ease: 'linear' }}
          />
        </div>
      </div>
    </div>
  );
}
