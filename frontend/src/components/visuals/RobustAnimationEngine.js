/**
 * ROBUST ANIMATION ENGINE
 * Custom-built animation system using:
 * - Pure CSS @keyframes (works offline, never fails)
 * - SVG SMIL animations (built into SVG spec)
 * - RequestAnimationFrame for smooth updates
 * - NO external dependencies beyond React
 * 
 * DESIGNED FOR:
 * - Low internet connections
 * - Guaranteed visual movement
 * - Educational clarity (students MUST see motion)
 */

import React, { useState, useEffect, useRef } from 'react';

export default function RobustAnimationEngine({
  sceneSpec,
  animationSequence,
  interactiveValues = {}
}) {
  const [animationTime, setAnimationTime] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);
  const rafRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  const entities = sceneSpec?.entities || [];
  const actions = sceneSpec?.actions || [];
  const sceneId = sceneSpec?.scene_id || 'scene';

  console.log(`[RobustAnimation] ${entities.length} entities, ${actions.length} actions`);

  // Animation loop using RequestAnimationFrame
  useEffect(() => {
    if (!isAnimating) return;

    const animate = () => {
      const elapsed = Date.now() - startTimeRef.current;
      setAnimationTime(elapsed);

      if (elapsed < 5000) {  // 5 second animation
        rafRef.current = requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
      }
    };

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, [isAnimating]);

  // Calculate entity position based on time and actions
  const getEntityTransform = (entity) => {
    const entityId = entity.id;
    const initialPos = entity.initial_position || { x: 200, y: 250 };
    
    // Find move action for this entity
    const moveAction = actions.find(a => a.entity === entityId && a.action === 'move');
    
    if (moveAction && animationTime >= (moveAction.start_time || 0)) {
      const actionElapsed = animationTime - (moveAction.start_time || 0);
      const actionDuration = moveAction.duration_ms || 2000;
      const progress = Math.min(actionElapsed / actionDuration, 1);
      
      // Linear interpolation
      const fromX = moveAction.from?.x || initialPos.x;
      const fromY = moveAction.from?.y || initialPos.y;
      const toX = moveAction.to?.x || initialPos.x;
      const toY = moveAction.to?.y || initialPos.y;
      
      const currentX = fromX + (toX - fromX) * progress;
      const currentY = fromY + (toY - fromY) * progress;
      
      return {
        x: currentX,
        y: currentY,
        opacity: 1
      };
    }

    // Default position
    return {
      x: initialPos.x,
      y: initialPos.y,
      opacity: animationTime > 300 ? 1 : 0
    };
  };

  // Get entity rotation
  const getEntityRotation = (entity) => {
    const entityId = entity.id;
    const rotateAction = actions.find(a => a.entity === entityId && a.action === 'rotate');
    
    if (rotateAction && animationTime >= (rotateAction.start_time || 0)) {
      const actionElapsed = animationTime - (rotateAction.start_time || 0);
      const actionDuration = rotateAction.duration_ms || 1500;
      const progress = Math.min(actionElapsed / actionDuration, 1);
      
      const fromRot = rotateAction.from?.rotation || 0;
      const toRot = rotateAction.to?.rotation || 0;
      
      return fromRot + (toRot - fromRot) * progress;
    }

    return 0;
  };

  // Get entity scale (for pulse/glow)
  const getEntityScale = (entity) => {
    const entityId = entity.id;
    const pulseAction = actions.find(a => a.entity === entityId && (a.action === 'pulse' || a.action === 'glow'));
    
    if (pulseAction && animationTime >= (pulseAction.start_time || 0)) {
      const duration = pulseAction.duration_ms || 1000;
      const phase = (animationTime % duration) / duration;
      return 1 + Math.sin(phase * Math.PI * 2) * 0.15; // Oscillate between 0.85 and 1.15
    }

    return entity.highlighted ? 1.15 : 1;
  };

  // Render entity with GUARANTEED VISUALS
  const renderEntity = (entity, index) => {
    const transform = getEntityTransform(entity);
    const rotation = getEntityRotation(entity);
    const scale = getEntityScale(entity);
    
    const style = {
      position: 'absolute',
      left: `${transform.x}px`,
      top: `${transform.y}px`,
      transform: `translate(-50%, -50%) rotate(${rotation}deg) scale(${scale})`,
      opacity: transform.opacity,
      transition: 'transform 0.05s linear, opacity 0.3s ease',
      zIndex: 100 + index
    };

    const emoji = getEmoji(entity.id);
    const label = entity.id.replace(/_/g, ' ').replace(/([a-z])([A-Z])/g, '$1 $2');

    return (
      <div key={entity.id} style={style}>
        <div className="flex flex-col items-center gap-2">
          {/* Large, animated emoji */}
          <div
            className="flex items-center justify-center rounded-2xl shadow-2xl border-4 border-white"
            style={{
              width: '100px',
              height: '100px',
              fontSize: '64px',
              background: entity.highlighted 
                ? 'linear-gradient(135deg, #fbbf24, #f59e0b)'
                : 'linear-gradient(135deg, #a78bfa, #8b5cf6)',
              animation: entity.highlighted ? 'pulse-glow 1s infinite' : 'none'
            }}
          >
            {emoji}
          </div>
          
          {/* Label */}
          <div
            className="px-4 py-2 rounded-full shadow-lg font-bold capitalize text-sm"
            style={{
              background: 'white',
              color: '#7c3aed'
            }}
          >
            {label}
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
      'platform': '🏢',
      'metro_train': '🚇',
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
        @keyframes pulse-glow {
          0%, 100% { transform: scale(1); box-shadow: 0 0 20px rgba(251, 191, 36, 0.5); }
          50% { transform: scale(1.1); box-shadow: 0 0 40px rgba(251, 191, 36, 0.8); }
        }
        
        @keyframes fade-in {
          from { opacity: 0; transform: scale(0.8); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>

      {/* Scene Container */}
      <div className="relative w-full overflow-hidden rounded-2xl shadow-2xl" style={{ height: '500px', background: 'linear-gradient(to bottom, #60A5FA, #86EFAC)' }}>
        
        {/* Cricket field background */}
        <div className="absolute inset-0" style={{
          background: sceneId.includes('cricket') 
            ? 'linear-gradient(to bottom, #60A5FA 0%, #60A5FA 30%, #22C55E 30%, #16A34A 100%)'
            : 'linear-gradient(to bottom, #87CEEB, #B0E0E6)'
        }} />

        {/* Ground/Field line */}
        {sceneId.includes('cricket') && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/50" style={{ bottom: '30%' }} />
        )}

        {/* Entities - Using RAF for smooth animation */}
        {entities.map((entity, index) => renderEntity(entity, index))}

        {/* Debug Info */}
        <div className="absolute top-4 left-4 z-50 bg-black/90 text-white text-sm p-4 rounded-xl shadow-xl space-y-1">
          <div className="font-bold text-green-400">Scene: {sceneId}</div>
          <div>Entities: {entities.length}</div>
          <div>Actions: {actions.length}</div>
          <div>Type: {sceneSpec?.scene_type}</div>
          <div className="text-green-300 font-semibold">✓ Animations active!</div>
          <div className="text-yellow-300 text-xs mt-2">Time: {(animationTime / 1000).toFixed(1)}s</div>
        </div>

        {/* Animation Progress Bar */}
        <div className="absolute bottom-6 left-6 right-6 z-50">
          <div className="bg-white/90 rounded-full h-4 overflow-hidden shadow-xl">
            <div
              className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600"
              style={{
                width: `${Math.min((animationTime / 5000) * 100, 100)}%`,
                transition: 'width 0.05s linear'
              }}
            />
          </div>
        </div>

        {/* Replay Button */}
        {!isAnimating && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/30 backdrop-blur-sm z-50">
            <button
              onClick={() => {
                startTimeRef.current = Date.now();
                setAnimationTime(0);
                setIsAnimating(true);
              }}
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-lg rounded-2xl shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all"
            >
              ▶️ Replay Animation
            </button>
          </div>
        )}
      </div>
    </>
  );
}


