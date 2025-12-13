/**
 * ⚙️ Engine Context
 * ==================
 * 
 * React Context for sharing state across the Magic Notebook Engine
 */

import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';

// ============================================
// CONTEXT DEFINITION
// ============================================

const EngineContext = createContext(null);

// ============================================
// ENGINE PROVIDER
// ============================================

export const EngineProvider = ({ children, initialBlueprint = null }) => {
  // Core State
  const [blueprint, setBlueprint] = useState(initialBlueprint);
  const [animationPhase, setAnimationPhase] = useState('idle'); // 'idle' | 'drawing' | 'interactive' | 'complete'
  const [currentBeat, setCurrentBeat] = useState(0);
  
  // Interactive State
  const [interactiveValues, setInteractiveValues] = useState({});
  
  // Validation State
  const [validationFeedback, setValidationFeedback] = useState(null);
  
  // Narrative State
  const [narrativeText, setNarrativeText] = useState('');
  const [handPosition, setHandPosition] = useState({ x: 0, y: 0 });
  const [handPose, setHandPose] = useState('idle'); // 'idle' | 'drawing' | 'pointing'
  
  // Performance Tracking
  const [renderTime, setRenderTime] = useState(0);
  
  // ============================================
  // ACTIONS
  // ============================================
  
  /**
   * Update blueprint
   */
  const updateBlueprint = useCallback((newBlueprint) => {
    setBlueprint(newBlueprint);
    setAnimationPhase('idle');
    setCurrentBeat(0);
  }, []);
  
  /**
   * Update interactive value
   */
  const updateInteractiveValue = useCallback((key, value) => {
    setInteractiveValues(prev => ({
      ...prev,
      [key]: value,
    }));
  }, []);
  
  /**
   * Set multiple interactive values
   */
  const setInteractiveValuesAll = useCallback((values) => {
    setInteractiveValues(values);
  }, []);
  
  /**
   * Progress to next beat
   */
  const nextBeat = useCallback(() => {
    setCurrentBeat(prev => {
      const maxBeats = blueprint?.beats?.length || 5;
      return Math.min(prev + 1, maxBeats);
    });
  }, [blueprint]);
  
  /**
   * Reset animation
   */
  const resetAnimation = useCallback(() => {
    setAnimationPhase('idle');
    setCurrentBeat(0);
    setNarrativeText('');
    setHandPosition({ x: 0, y: 0 });
    setHandPose('idle');
  }, []);
  
  /**
   * Start drawing animation
   */
  const startDrawing = useCallback(() => {
    setAnimationPhase('drawing');
  }, []);
  
  /**
   * Complete drawing, enable interaction
   */
  const enableInteraction = useCallback(() => {
    setAnimationPhase('interactive');
  }, []);
  
  /**
   * Mark animation as complete
   */
  const completeAnimation = useCallback(() => {
    setAnimationPhase('complete');
  }, []);
  
  /**
   * Update hand state
   */
  const updateHand = useCallback((position, pose) => {
    if (position) setHandPosition(position);
    if (pose) setHandPose(pose);
  }, []);
  
  /**
   * Show validation feedback
   */
  const showValidation = useCallback((feedback) => {
    setValidationFeedback(feedback);
    
    // Auto-hide after 4 seconds
    setTimeout(() => {
      setValidationFeedback(null);
    }, 4000);
  }, []);
  
  /**
   * Clear validation feedback
   */
  const clearValidation = useCallback(() => {
    setValidationFeedback(null);
  }, []);
  
  // ============================================
  // COMPUTED VALUES
  // ============================================
  
  const isDrawing = useMemo(() => animationPhase === 'drawing', [animationPhase]);
  const isInteractive = useMemo(() => animationPhase === 'interactive' || animationPhase === 'complete', [animationPhase]);
  const isComplete = useMemo(() => animationPhase === 'complete', [animationPhase]);
  
  const currentBeatData = useMemo(() => {
    if (!blueprint?.beats || currentBeat === 0) return null;
    return blueprint.beats[currentBeat - 1] || null;
  }, [blueprint, currentBeat]);
  
  const totalBeats = useMemo(() => {
    return blueprint?.beats?.length || 0;
  }, [blueprint]);
  
  // ============================================
  // CONTEXT VALUE
  // ============================================
  
  const value = useMemo(() => ({
    // State
    blueprint,
    animationPhase,
    currentBeat,
    interactiveValues,
    validationFeedback,
    narrativeText,
    handPosition,
    handPose,
    renderTime,
    
    // Computed
    isDrawing,
    isInteractive,
    isComplete,
    currentBeatData,
    totalBeats,
    
    // Actions
    updateBlueprint,
    updateInteractiveValue,
    setInteractiveValuesAll,
    nextBeat,
    resetAnimation,
    startDrawing,
    enableInteraction,
    completeAnimation,
    updateHand,
    setNarrativeText,
    showValidation,
    clearValidation,
    setRenderTime,
  }), [
    blueprint,
    animationPhase,
    currentBeat,
    interactiveValues,
    validationFeedback,
    narrativeText,
    handPosition,
    handPose,
    renderTime,
    isDrawing,
    isInteractive,
    isComplete,
    currentBeatData,
    totalBeats,
    updateBlueprint,
    updateInteractiveValue,
    setInteractiveValuesAll,
    nextBeat,
    resetAnimation,
    startDrawing,
    enableInteraction,
    completeAnimation,
    updateHand,
    showValidation,
    clearValidation,
  ]);
  
  return (
    <EngineContext.Provider value={value}>
      {children}
    </EngineContext.Provider>
  );
};

// ============================================
// HOOK
// ============================================

/**
 * Use Engine Context
 * @returns {EngineContextValue}
 * @throws {Error} If used outside EngineProvider
 */
export const useEngine = () => {
  const context = useContext(EngineContext);
  
  if (!context) {
    throw new Error('useEngine must be used within an EngineProvider');
  }
  
  return context;
};

// ============================================
// EXPORTS
// ============================================

export { EngineContext };
export default EngineProvider;

