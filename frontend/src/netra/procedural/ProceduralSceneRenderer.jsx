/**
 * 🎬 PROCEDURAL SCENE RENDERER (React Component)
 * ==============================================
 * 
 * React wrapper for ProceduralRenderer.
 * Handles:
 * - Canvas lifecycle
 * - Scene loading/unloading
 * - Choreography playback
 * - Narration display
 * - Interaction UI
 * 
 * USAGE:
 * <ProceduralSceneRenderer 
 *   plan={proceduralScenePlan}
 *   width={720}
 *   height={520}
 *   onNarration={handleNarration}
 *   onReady={handleReady}
 * />
 */

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ProceduralRenderer from './ProceduralRenderer';

// ============================================
// NARRATION DISPLAY COMPONENT
// ============================================

const NarrationDisplay = ({ narration, visible }) => {
  if (!visible || !narration?.text) return null;
  
  const emphasisStyles = {
    normal: 'text-base text-gray-700',
    high: 'text-lg text-blue-800 font-semibold',
    whisper: 'text-sm text-gray-500 italic',
  };
  
  const positionStyles = {
    top: 'top-4',
    center: 'top-1/2 -translate-y-1/2',
    bottom: 'bottom-4',
  };
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3 }}
        className={`absolute left-1/2 -translate-x-1/2 ${positionStyles[narration.position || 'bottom']} max-w-md px-6 py-3 bg-white/95 rounded-xl shadow-lg border border-gray-100`}
      >
        <p className={emphasisStyles[narration.emphasis || 'normal']}>
          {narration.text}
        </p>
      </motion.div>
    </AnimatePresence>
  );
};

// ============================================
// LOADING STATE COMPONENT
// ============================================

const LoadingState = ({ domain = 'general' }) => {
  const domainColors = {
    biology: '#10B981',
    physics: '#3B82F6',
    chemistry: '#8B5CF6',
    math: '#6366F1',
    general: '#6B7280',
  };
  
  const color = domainColors[domain] || domainColors.general;
  
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-b from-slate-50 to-slate-100">
      <div className="flex flex-col items-center gap-4">
        {/* Procedural loading animation */}
        <svg width="80" height="80" viewBox="0 0 80 80">
          <motion.circle
            cx="40"
            cy="40"
            r="30"
            fill="none"
            stroke={color}
            strokeWidth="3"
            strokeDasharray="180"
            strokeDashoffset="0"
            strokeLinecap="round"
            initial={{ rotate: 0 }}
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          />
          <motion.circle
            cx="40"
            cy="40"
            r="20"
            fill="none"
            stroke={color}
            strokeWidth="2"
            strokeDasharray="120"
            opacity={0.5}
            initial={{ rotate: 0 }}
            animate={{ rotate: -360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          />
          <motion.circle
            cx="40"
            cy="40"
            r="8"
            fill={color}
            initial={{ scale: 0.8 }}
            animate={{ scale: 1.2 }}
            transition={{ duration: 0.8, repeat: Infinity, repeatType: 'reverse' }}
          />
        </svg>
        <p className="text-sm text-gray-500 font-medium">
          Building your simulation...
        </p>
      </div>
    </div>
  );
};

// ============================================
// MAIN COMPONENT
// ============================================

const ProceduralSceneRenderer = ({
  plan,
  width = 720,
  height = 520,
  domain = 'general',
  onNarration,
  onReady,
  onInteraction,
  autoPlay = true,
  className = '',
}) => {
  const canvasRef = useRef(null);
  const rendererRef = useRef(null);
  const mountedRef = useRef(true);
  
  const [isLoading, setIsLoading] = useState(true);
  const [narration, setNarration] = useState({ text: null, emphasis: 'normal', visible: false });
  const [sceneReady, setSceneReady] = useState(false);
  
  // Memoize plan ID to detect changes
  const planId = useMemo(() => {
    return plan ? JSON.stringify(plan.intent || {}) + (plan.version || '1.0') : 'none';
  }, [plan]);

  // ============================================
  // RENDERER LIFECYCLE
  // ============================================

  useEffect(() => {
    mountedRef.current = true;
    
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!canvasRef.current || !plan) {
      setIsLoading(true);
      return;
    }
    
    console.log('🎬 [ProceduralSceneRenderer] Loading scene...');
    
    // Cleanup previous renderer
    if (rendererRef.current) {
      rendererRef.current.destroy();
      rendererRef.current = null;
    }
    
    // Create new renderer
    const renderer = new ProceduralRenderer(canvasRef.current, width, height);
    rendererRef.current = renderer;
    
    // Set callbacks
    renderer.onNarration = (narrData) => {
      if (!mountedRef.current) return;
      
      setNarration({ ...narrData, visible: true });
      
      // Auto-hide after duration
      setTimeout(() => {
        if (mountedRef.current) {
          setNarration(prev => ({ ...prev, visible: false }));
        }
      }, 4000);
      
      // External callback
      if (onNarration) {
        onNarration(narrData);
      }
    };
    
    renderer.onReady = () => {
      if (!mountedRef.current) return;
      
      console.log('🎬 [ProceduralSceneRenderer] Scene ready!');
      setIsLoading(false);
      setSceneReady(true);
      
      if (onReady) {
        onReady();
      }
    };
    
    // Load the scene
    try {
      renderer.loadScene(plan);
      
      if (autoPlay) {
        renderer.start();
      }
    } catch (err) {
      console.error('🎬 [ProceduralSceneRenderer] Failed to load scene:', err);
      setIsLoading(false);
    }
    
    // Cleanup
    return () => {
      if (rendererRef.current) {
        rendererRef.current.destroy();
        rendererRef.current = null;
      }
    };
  }, [planId, width, height, autoPlay]); // Use planId instead of plan to prevent infinite loops

  // ============================================
  // INTERACTION HANDLERS
  // ============================================

  const handleCanvasClick = useCallback((e) => {
    if (!rendererRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    console.log('🎬 [ProceduralSceneRenderer] Canvas click:', { x, y });
    
    // Could implement hit-testing here for interactions
    if (onInteraction) {
      onInteraction({ type: 'click', x, y });
    }
  }, [onInteraction]);

  // ============================================
  // RENDER
  // ============================================

  return (
    <div 
      className={`relative overflow-visible ${className}`}
      style={{ width, height }}
    >
      {/* Canvas */}
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onClick={handleCanvasClick}
        className="block"
        style={{ 
          background: 'transparent',
        }}
      />
      
      {/* Loading State */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0"
          >
            <LoadingState domain={domain} />
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Narration Overlay */}
      <NarrationDisplay narration={narration} visible={narration.visible} />
      
      {/* Interaction Controls (could add sliders, toggles here) */}
      {plan?.interactions?.length > 0 && (
        <div className="absolute bottom-4 left-4 right-4 flex justify-center gap-4">
          {plan.interactions.map((interaction, idx) => (
            <InteractionControl 
              key={interaction.id || idx}
              interaction={interaction}
              onChange={(value) => {
                if (onInteraction) {
                  onInteraction({ type: interaction.type, id: interaction.id, value });
                }
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// INTERACTION CONTROL COMPONENT
// ============================================

const InteractionControl = ({ interaction, onChange }) => {
  const { type, label, range } = interaction;
  const [value, setValue] = useState(range?.default || 0.5);
  
  const handleChange = (e) => {
    const newValue = parseFloat(e.target.value);
    setValue(newValue);
    if (onChange) {
      onChange(newValue);
    }
  };
  
  if (type === 'slider') {
    return (
      <div className="flex flex-col items-center gap-1 bg-white/90 px-4 py-2 rounded-lg shadow-sm">
        <label className="text-xs font-medium text-gray-600">{label}</label>
        <input
          type="range"
          min={range?.min || 0}
          max={range?.max || 1}
          step={range?.step || 0.1}
          value={value}
          onChange={handleChange}
          className="w-32 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
        <span className="text-xs text-gray-500">{value.toFixed(2)}</span>
      </div>
    );
  }
  
  if (type === 'toggle') {
    return (
      <button
        onClick={() => {
          const newValue = value === 1 ? 0 : 1;
          setValue(newValue);
          if (onChange) onChange(newValue);
        }}
        className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
          value === 1 
            ? 'bg-blue-500 text-white' 
            : 'bg-gray-200 text-gray-700'
        }`}
      >
        {label}
      </button>
    );
  }
  
  return null;
};

// ============================================
// EXPORTS
// ============================================

export default ProceduralSceneRenderer;
export { NarrationDisplay, LoadingState, InteractionControl };
