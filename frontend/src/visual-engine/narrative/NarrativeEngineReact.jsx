/**
 * 🎬 NARRATIVE ENGINE (REACT WRAPPER)
 * ====================================
 * 
 * React component wrapper for NarrativeEngine
 * Provides hooks and component integration
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { NarrativeEngine } from './NarrativeEngine';
import DrawingHand from './DrawingHand';
import TextBubble, { HintBubble, InsightBubble, EncouragementBubble, MemoryHookBubble } from './TextBubble';

// ============================================
// HOOK: useNarrativeEngine
// ============================================

/**
 * React hook for narrative engine
 */
export function useNarrativeEngine(blueprint, options = {}) {
  const engineRef = useRef(null);
  const [state, setState] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Initialize engine
  useEffect(() => {
    if (!blueprint) return;
    
    engineRef.current = new NarrativeEngine(blueprint, options);
    setState(engineRef.current.getState());
    setIsInitialized(true);
    
    return () => {
      if (engineRef.current) {
        engineRef.current.stop();
      }
    };
  }, [blueprint, options]);
  
  // Animation loop
  useEffect(() => {
    if (!isInitialized || !engineRef.current) return;
    
    let lastTime = Date.now();
    let animationFrame;
    
    const animate = () => {
      const now = Date.now();
      const deltaTime = (now - lastTime) / 1000;
      lastTime = now;
      
      if (engineRef.current && engineRef.current.isPlaying) {
        const newState = engineRef.current.update(deltaTime);
        setState(newState);
      }
      
      animationFrame = requestAnimationFrame(animate);
    };
    
    animationFrame = requestAnimationFrame(animate);
    
    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [isInitialized]);
  
  // Control methods
  const play = useCallback(() => {
    engineRef.current?.play();
    setState(engineRef.current?.getState());
  }, []);
  
  const pause = useCallback(() => {
    engineRef.current?.pause();
    setState(engineRef.current?.getState());
  }, []);
  
  const stop = useCallback(() => {
    engineRef.current?.stop();
    setState(engineRef.current?.getState());
  }, []);
  
  const seekTo = useCallback((time) => {
    engineRef.current?.seekTo(time);
    setState(engineRef.current?.getState());
  }, []);
  
  const nextBeat = useCallback(() => {
    engineRef.current?.nextBeat();
    setState(engineRef.current?.getState());
  }, []);
  
  const previousBeat = useCallback(() => {
    engineRef.current?.previousBeat();
    setState(engineRef.current?.getState());
  }, []);
  
  return {
    state,
    engine: engineRef.current,
    play,
    pause,
    stop,
    seekTo,
    nextBeat,
    previousBeat,
    isInitialized,
  };
}

// ============================================
// COMPONENT: NarrativePlayer
// ============================================

/**
 * Complete narrative player with hand and bubbles
 */
export const NarrativePlayer = ({
  blueprint,
  options = {},
  onComplete,
  showControls = true,
  className = '',
}) => {
  const {
    state,
    play,
    pause,
    stop,
    nextBeat,
    previousBeat,
    isInitialized,
  } = useNarrativeEngine(blueprint, {
    ...options,
    onComplete,
  });
  
  if (!isInitialized || !state) {
    return <div>Loading narrative...</div>;
  }
  
  // Select bubble component
  const getBubbleComponent = () => {
    switch (state.bubble.type) {
      case 'hint':
        return HintBubble;
      case 'insight':
        return InsightBubble;
      case 'highlight':
        return EncouragementBubble;
      case 'memory':
        return MemoryHookBubble;
      default:
        return TextBubble;
    }
  };
  
  const BubbleComponent = getBubbleComponent();
  
  return (
    <div className={`narrative-player ${className}`} style={{ position: 'relative' }}>
      {/* Drawing Hand */}
      {state.hand.visible && (
        <DrawingHand
          x={state.hand.x}
          y={state.hand.y}
          rotation={state.hand.angle}
          pose={state.hand.pose}
          visible={state.hand.visible}
        />
      )}
      
      {/* Text Bubble */}
      {state.bubble.visible && (
        <BubbleComponent
          text={state.bubble.text}
          x={state.hand.x - 100}
          y={state.hand.y - 120}
          anchorX={state.hand.x}
          anchorY={state.hand.y}
          visible={state.bubble.visible}
          typewriter={true}
        />
      )}
      
      {/* Controls */}
      {showControls && (
        <div
          style={{
            position: 'absolute',
            bottom: 10,
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            gap: '8px',
            padding: '12px',
            background: 'rgba(255,255,255,0.9)',
            borderRadius: '24px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 1000,
          }}
        >
          <button onClick={previousBeat} disabled={state.currentBeat === 1}>
            ⏮️
          </button>
          
          {state.isPlaying ? (
            <button onClick={pause}>⏸️</button>
          ) : (
            <button onClick={play}>▶️</button>
          )}
          
          <button onClick={stop}>⏹️</button>
          
          <button onClick={nextBeat} disabled={state.currentBeat === state.beatData?.beat}>
            ⏭️
          </button>
          
          <div style={{ padding: '0 12px', display: 'flex', alignItems: 'center' }}>
            Beat {state.currentBeat} / {blueprint.beats?.length || 5}
          </div>
        </div>
      )}
      
      {/* Progress Bar */}
      {showControls && (
        <div
          style={{
            position: 'absolute',
            bottom: 60,
            left: 20,
            right: 20,
            height: '4px',
            background: 'rgba(0,0,0,0.1)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              background: '#3B82F6',
              width: `${state.progress * 100}%`,
              transition: 'width 0.1s linear',
            }}
          />
        </div>
      )}
    </div>
  );
};

// ============================================
// EXPORTS
// ============================================

export default NarrativePlayer;

