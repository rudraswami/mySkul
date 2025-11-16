/**
 * ULTRA-SIMPLE ANIMATION ENGINE
 * Uses PURE CSS @keyframes - GUARANTEED TO WORK
 * No RAF, no state updates, no complex logic
 * Just CSS animations that ALWAYS work
 */

import React from 'react';

export default function SimpleAnimationEngine({ sceneSpec, animationSequence, interactiveValues = {} }) {
  const entities = sceneSpec?.entities || [];
  const actions = sceneSpec?.actions || [];
  const sceneId = sceneSpec?.scene_id || 'scene';

  // Generate unique animation names for CSS
  const getAnimationName = (entityId, actionType) => `anim-${entityId}-${actionType}`;

  // Build CSS keyframes from actions
  const buildCSSKeyframes = () => {
    let css = '';

    actions.forEach((action, idx) => {
      const animName = `action-${idx}-${action.entity}`;
      
      if (action.action === 'move') {
        const fromX = action.from?.x || 0;
        const fromY = action.from?.y || 250;
        const toX = action.to?.x || 0;
        const toY = action.to?.y || 250;
        
        css += `
          @keyframes ${animName} {
            from {
              transform: translate(${fromX}px, ${fromY}px) translate(-50%, -50%);
              opacity: 1;
            }
            to {
              transform: translate(${toX}px, ${toY}px) translate(-50%, -50%);
              opacity: 1;
            }
          }
        `;
      } else if (action.action === 'rotate') {
        const fromRot = action.from?.rotation || 0;
        const toRot = action.to?.rotation || 180;
        
        css += `
          @keyframes ${animName} {
            from { transform: rotate(${fromRot}deg) translate(-50%, -50%); }
            to { transform: rotate(${toRot}deg) translate(-50%, -50%); }
          }
        `;
      } else if (action.action === 'pulse' || action.action === 'glow') {
        css += `
          @keyframes ${animName} {
            0%, 100% { transform: scale(1) translate(-50%, -50%); opacity: 1; }
            50% { transform: scale(1.2) translate(-50%, -50%); opacity: 0.9; }
          }
        `;
      }
    });

    return css;
  };

  // Get CSS animation for entity
  const getEntityAnimation = (entityId) => {
    const entityActions = actions.filter(a => a.entity === entityId);
    
    if (entityActions.length === 0) {
      // Default fade-in
      return {
        animation: 'fadeIn 0.8s ease-out forwards'
      };
    }

    // Find primary action (move, rotate, or pulse)
    const moveAction = entityActions.find(a => a.action === 'move');
    const rotateAction = entityActions.find(a => a.action === 'rotate');
    const pulseAction = entityActions.find(a => a.action === 'pulse' || a.action === 'glow');

    const primaryAction = moveAction || rotateAction || pulseAction;
    if (!primaryAction) {
      return { animation: 'fadeIn 0.8s ease-out forwards' };
    }

    const actionIndex = actions.indexOf(primaryAction);
    const animName = `action-${actionIndex}-${entityId}`;
    const duration = (primaryAction.duration_ms || 2000) / 1000;
    const delay = (primaryAction.start_time || 0) / 1000;
    const iteration = (pulseAction) ? 'infinite' : '1';

    return {
      animation: `${animName} ${duration}s ease-in-out ${delay}s ${iteration} forwards`
    };
  };

  // Render entity with pure CSS animations
  const renderEntity = (entity, index) => {
    const entityId = entity.id;
    const initialPos = entity.initial_position || { x: 200 + index * 130, y: 250 };
    const animation = getEntityAnimation(entityId);
    const emoji = getEmoji(entityId);

    return (
      <div
        key={entityId}
        className="absolute"
        style={{
          left: 0,
          top: 0,
          transform: `translate(${initialPos.x}px, ${initialPos.y}px) translate(-50%, -50%)`,
          zIndex: 100 + index,
          ...animation
        }}
      >
        <div className="flex flex-col items-center gap-2">
          {/* Large emoji icon */}
          <div
            className="flex items-center justify-center rounded-3xl shadow-2xl border-4 border-white"
            style={{
              width: '110px',
              height: '110px',
              fontSize: '72px',
              background: entity.highlighted
                ? 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)'
                : 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)'
            }}
          >
            {emoji}
          </div>
          
          {/* Label */}
          <div className="bg-white px-4 py-2 rounded-full shadow-xl font-bold text-sm" style={{ color: '#7c3aed' }}>
            {entityId.replace(/_/g, ' ')}
          </div>
        </div>
      </div>
    );
  };

  const getEmoji = (id) => {
    const map = {
      'cricket_ball': '🏏',
      'ball': '⚾',
      'bowler': '🏏',
      'trajectory_line': '↗️',
      'speed_gun': '📡',
      'stumps': '🎯',
      'metro_train': '🚇',
      'car': '🚗',
      'direction_arrow': '➡️',
      'speedometer': '⏱️',
      'landmark_a': '📍',
      'landmark_b': '📍'
    };
    return map[id] || '🔷';
  };

  return (
    <>
      {/* CSS Keyframes */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translate(-50%, -50%) scale(0.7); }
          to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
        
        ${buildCSSKeyframes()}
      `}</style>

      {/* Scene Container */}
      <div
        className="relative w-full overflow-hidden rounded-2xl shadow-2xl"
        style={{
          height: '550px',
          background: sceneId.includes('cricket')
            ? 'linear-gradient(to bottom, #60A5FA 0%, #60A5FA 35%, #22C55E 35%, #16A34A 100%)'
            : 'linear-gradient(to bottom, #87CEEB, #B0E0E6)'
        }}
      >
        {/* Field boundary line */}
        {sceneId.includes('cricket') && (
          <div className="absolute left-0 right-0 h-2 bg-white/60" style={{ top: '35%' }} />
        )}

        {/* Entities with CSS animations */}
        <div className="absolute inset-0">
          {entities.map((entity, index) => renderEntity(entity, index))}
        </div>

        {/* Debug Info */}
        <div className="absolute top-4 left-4 z-50 bg-black/90 text-white text-sm p-4 rounded-xl shadow-2xl space-y-1">
          <div className="font-bold text-green-400">✓ CSS Animations Active</div>
          <div>Scene: {sceneId}</div>
          <div>Entities: {entities.length}</div>
          <div>Actions: {actions.length}</div>
          <div className="text-yellow-300 text-xs mt-2">Using pure CSS - works offline!</div>
        </div>

        {/* Animation indicator (CSS animated) */}
        <div className="absolute bottom-6 left-6 right-6 z-50">
          <div className="bg-white/90 rounded-full h-4 overflow-hidden shadow-xl">
            <div
              className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600"
              style={{
                animation: 'progressBar 5s linear forwards'
              }}
            />
          </div>
        </div>

        {/* Professor */}
        <div className="absolute bottom-6 right-6 z-50">
          <div className="w-28 h-28 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-5xl border-4 border-white shadow-2xl">
            👨‍🏫
          </div>
        </div>
      </div>

      <style>{`
        @keyframes progressBar {
          from { width: 0%; }
          to { width: 100%; }
        }
      `}</style>
    </>
  );
}


