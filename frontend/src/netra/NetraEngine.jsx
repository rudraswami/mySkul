/**
 * 🔮 NETRA ENGINE REACT COMPONENT v4.0
 * =====================================
 * 
 * The main React component for the NETRA Visual Teaching Engine.
 * 
 * v4.0 CHANGES:
 * - Uses SceneObjects instead of nodes for rich visual scenes
 * - SceneRenderer produces environments, actors, surfaces (NOT boxes!)
 * - Same topic + different intent = DIFFERENT visual scene
 * 
 * Usage:
 * <NetraEngine
 *   question="Explain Newton's third law with a rocket"
 *   context={{ subject: 'physics', level: 'high_school' }}
 *   onGenerated={(result) => console.log(result)}
 * />
 * 
 * This produces intelligent, varied, SCENE-BASED visuals — not diagrams.
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Core engine
import { Orchestrator, createOrchestrator } from './core/Orchestrator';

// Renderers - OLD (legacy) and NEW (scene-based)
import SVGRenderer from './rendering/SVGRenderer';
import AnimatedRenderer from './rendering/AnimatedRenderer';
import SceneRenderer from './rendering/SceneRenderer';  // NEW: Scene-based renderer!

// v5.0: Dynamic Visual Renderer (composition-based)
import DynamicVisualRenderer from './renderer/DynamicVisualRenderer';

// ============================================
// LOADING STATES - Beautiful Animated Loader
// ============================================

const LoadingState = ({ message = 'Creating your visual...' }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: 24,
      padding: 40,
      background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%)',
      borderRadius: 16,
      position: 'relative',
      overflow: 'hidden',
    }}
  >
    {/* Animated background particles */}
    <motion.div
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
      }}
    >
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          animate={{
            y: ['100%', '-100%'],
            x: [Math.random() * 20 - 10, Math.random() * 20 - 10],
            opacity: [0, 0.6, 0],
            scale: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 4 + Math.random() * 3,
            repeat: Infinity,
            delay: i * 0.4,
            ease: 'easeInOut',
          }}
          style={{
            position: 'absolute',
            left: `${10 + (i * 7) % 80}%`,
            bottom: 0,
            width: 8 + Math.random() * 12,
            height: 8 + Math.random() * 12,
            borderRadius: '50%',
            background: i % 3 === 0 ? '#8B5CF6' : i % 3 === 1 ? '#3B82F6' : '#10B981',
            filter: 'blur(1px)',
          }}
        />
      ))}
    </motion.div>
    
    {/* Central Visual Thinking Animation */}
    <div style={{ position: 'relative', width: 120, height: 120 }}>
      {/* Outer rotating ring */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          border: '3px dashed rgba(139, 92, 246, 0.3)',
        }}
      />
      
      {/* Inner pulsing ring */}
      <motion.div
        animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          position: 'absolute',
          inset: 10,
          borderRadius: '50%',
          border: '2px solid rgba(59, 130, 246, 0.5)',
          boxShadow: '0 0 20px rgba(59, 130, 246, 0.3)',
        }}
      />
      
      {/* Orbiting atoms */}
      {[0, 120, 240].map((angle, i) => (
        <motion.div
          key={i}
          animate={{ rotate: [angle, angle + 360] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
          }}
        >
          <motion.div
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 1, repeat: Infinity, delay: i * 0.3 }}
            style={{
              width: 14,
              height: 14,
              borderRadius: '50%',
              background: i === 0 ? '#8B5CF6' : i === 1 ? '#3B82F6' : '#10B981',
              boxShadow: `0 0 12px ${i === 0 ? '#8B5CF6' : i === 1 ? '#3B82F6' : '#10B981'}`,
              marginTop: -7,
            }}
          />
        </motion.div>
      ))}
      
      {/* Center brain icon */}
      <motion.div
        animate={{
          scale: [1, 1.15, 1],
          rotate: [0, 5, -5, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 40,
        }}
      >
        🧠
      </motion.div>
    </div>
    
    {/* Animated Message with typing effect */}
    <motion.div
      animate={{ opacity: [0.7, 1, 0.7] }}
      transition={{ duration: 2, repeat: Infinity }}
      style={{
        fontFamily: "'Inter', 'SF Pro Display', -apple-system, sans-serif",
        fontSize: 15,
        fontWeight: 500,
        color: '#475569',
        textAlign: 'center',
        letterSpacing: '-0.01em',
      }}
    >
      {message}
      <motion.span
        animate={{ opacity: [0, 1, 0] }}
        transition={{ duration: 0.8, repeat: Infinity }}
      >
        |
      </motion.span>
    </motion.div>
    
    {/* Multi-stage progress indicator */}
    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      {['Understanding', 'Composing', 'Rendering'].map((stage, i) => (
        <motion.div
          key={stage}
          animate={{
            scale: [1, 1.1, 1],
            backgroundColor: ['#e2e8f0', '#8B5CF6', '#e2e8f0'],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * 0.7,
          }}
          style={{
            padding: '6px 12px',
            borderRadius: 20,
            fontSize: 11,
            fontWeight: 500,
            color: '#64748b',
            background: '#e2e8f0',
          }}
        >
          {stage}
        </motion.div>
      ))}
    </div>
    
    {/* Beautiful gradient progress bar */}
    <div
      style={{
        width: 240,
        height: 6,
        background: 'rgba(226, 232, 240, 0.8)',
        borderRadius: 3,
        overflow: 'hidden',
        boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.1)',
      }}
    >
      <motion.div
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 1.8,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        style={{
          width: '60%',
          height: '100%',
          background: 'linear-gradient(90deg, #8B5CF6, #3B82F6, #10B981, #3B82F6, #8B5CF6)',
          backgroundSize: '200% 100%',
          borderRadius: 3,
        }}
      />
    </div>
  </motion.div>
);

// ============================================
// ERROR STATE
// ============================================

const ErrorState = ({ error, onRetry }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: 16,
      padding: 40,
    }}
  >
    <div style={{ fontSize: 48 }}>😕</div>
    <div
      style={{
        fontFamily: "'Kalam', cursive",
        fontSize: 14,
        color: '#E74C3C',
        textAlign: 'center',
        maxWidth: 300,
      }}
    >
      {error || 'Something went wrong'}
    </div>
    {onRetry && (
      <button
        onClick={onRetry}
        style={{
          padding: '8px 20px',
          fontFamily: "'Kalam', cursive",
          fontSize: 14,
          background: '#3498DB',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer',
        }}
      >
        Try Again
      </button>
    )}
  </motion.div>
);

// ============================================
// EMPTY STATE
// ============================================

const EmptyState = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: 12,
    }}
  >
    <div style={{ fontSize: 40 }}>🔮</div>
    <div
      style={{
        fontFamily: "'Kalam', cursive",
        fontSize: 16,
        color: '#BDC3C7',
      }}
    >
      Ask a question to see visual magic
    </div>
  </motion.div>
);

// ============================================
// METADATA BADGE
// ============================================

const MetadataBadge = ({ metadata }) => {
  if (!metadata) return null;

  const icons = {
    physics: '⚛️',
    chemistry: '🧪',
    biology: '🧬',
    math: '📐',
    mathematics: '📐',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      style={{
        position: 'absolute',
        top: 12,
        right: 12,
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '6px 12px',
        background: 'rgba(255, 255, 255, 0.9)',
        borderRadius: 12,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        fontSize: 11,
        fontWeight: 600,
        color: '#666',
      }}
    >
      <span>{icons[metadata.domain] || '✨'}</span>
      <span>{metadata.topic || metadata.domain}</span>
      {metadata.strategy && (
        <>
          <span style={{ color: '#DDD' }}>|</span>
          <span style={{ color: '#999' }}>{metadata.strategy}</span>
        </>
      )}
    </motion.div>
  );
};

// ============================================
// MAIN NETRA ENGINE COMPONENT
// ============================================

const NetraEngine = ({
  // Input
  question = null,
  context = {},
  
  // Pre-generated (skip generation)
  preGeneratedScene = null,
  preGeneratedComposition = null,  // NEW v5.0: Pre-generated CompositionSpec
  
  // Display
  width = 800,
  height = 600,
  showGrid = true,
  showMetadata = true,
  
  // Callbacks
  onGenerated = null,
  onError = null,
  onRenderComplete = null,
  onNarration = null,  // NEW v5.0: Narration events
  
  // Style
  className = '',
  style = {},
  
  // Options
  useLLM = false,                      // Use LLM for deep understanding
  apiClient = null,                    // API client for LLM calls
  useCompositionMode = true,           // v5.0: Use dynamic composition pipeline (DEFAULT ON)
}) => {
  // State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  
  // 🔧 FIX: Prevent duplicate requests + cleanup tracking
  const lastQuestionRef = useRef(null);
  const orchestratorRef = useRef(null);
  const loadingIntervalRef = useRef(null);
  const generationAbortRef = useRef(false);
  const mountedRef = useRef(true);

  // Track mount state for cleanup
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      generationAbortRef.current = true;
      if (loadingIntervalRef.current) {
        clearInterval(loadingIntervalRef.current);
        loadingIntervalRef.current = null;
      }
    };
  }, []);

  // Create orchestrator once
  useEffect(() => {
    orchestratorRef.current = createOrchestrator({
      width,
      height,
      useLLM,
      apiClient,
    });
  }, [width, height, useLLM, apiClient]);

  // Handle pre-generated scene
  useEffect(() => {
    if (preGeneratedScene) {
      setResult({
        success: true,
        sceneGraph: preGeneratedScene,
        metadata: preGeneratedScene.metadata || {},
      });
      setLoading(false);
      setError(null);
    }
  }, [preGeneratedScene]);

  // NEW v5.0: Handle pre-generated composition
  useEffect(() => {
    if (preGeneratedComposition) {
      setResult({
        success: true,
        composition: preGeneratedComposition,
        metadata: { 
          renderMode: 'composition',
          ...preGeneratedComposition.context,
        },
      });
      setLoading(false);
      setError(null);
    }
  }, [preGeneratedComposition]);

  // Generate visual when question changes
  useEffect(() => {
    if (preGeneratedScene) return; // Skip if using pre-generated
    if (!question) return;
    
    // ================================================================
    // 🎯 ENTERPRISE-GRADE VISUAL GATING (Cognito OS v1.0)
    // ================================================================
    // CRITICAL: Check if visual generation is actually needed
    // This is the LAST LINE OF DEFENSE before expensive visual generation
    // Backend must explicitly set visual_needed=true for generation to proceed
    // ================================================================
    if (context.visual_needed === false) {
      console.log('🚫 [NetraEngine] BLOCKED: visual_needed=false (context)', {
        question: question?.substring(0, 50),
        intent: context.intent,
        reason: context.visual_skip_reason || 'not_needed'
      });
      return;
    }
    
    // Secondary check: intent-based gating
    const NO_VISUAL_INTENTS = [
      'greeting', 'acknowledgment', 'chitchat', 'conversational',
      'clarification_or_followup', 'simple_fact'
    ];
    if (context.intent && NO_VISUAL_INTENTS.includes(context.intent)) {
      console.log('🚫 [NetraEngine] BLOCKED: intent not visual-worthy', {
        question: question?.substring(0, 50),
        intent: context.intent
      });
      return;
    }
    
    // Prevent duplicate requests
    const questionKey = `${question}_${context.subject || ''}_${context.level || ''}`;
    if (lastQuestionRef.current === questionKey && result) {
      console.log('🔮 [NetraEngine] Skipping duplicate request');
      return;
    }
    lastQuestionRef.current = questionKey;

    const generate = async () => {
      // 🔧 FIX: Reset abort flag for new generation
      generationAbortRef.current = false;
      
      setLoading(true);
      setError(null);
      
      // 🔧 FIX: Clear any existing interval before starting new one
      if (loadingIntervalRef.current) {
        clearInterval(loadingIntervalRef.current);
        loadingIntervalRef.current = null;
      }
      
      // Progressive loading messages (reduced frequency to prevent perf issues)
      const loadingMessages = [
        'Understanding your question...',
        'Analyzing concepts...',
        'Designing visual composition...',
        'Creating interactive elements...',
        'Finalizing animations...',
      ];
      let messageIndex = 0;
      loadingIntervalRef.current = setInterval(() => {
        if (!mountedRef.current) return;
        messageIndex = Math.min(messageIndex + 1, loadingMessages.length - 1);
        // Update loading message (handled by progress state in UI)
        console.log(`⏱️ [PROGRESS] ${loadingMessages[messageIndex]}`);
      }, 5000); // 🔧 FIX: Increased from 3s to 5s to reduce overhead

      try {
        console.log('═══════════════════════════════════════════════════');
        console.log('🔮 [NetraEngine v5.0] GENERATING VISUAL');
        console.log('🔮 Question:', question);
        console.log('🔮 Context:', context);
        console.log('🔮 visual_needed:', context.visual_needed);
        console.log('🔮 useCompositionMode:', useCompositionMode);
        console.log('⏱️ [TIMING] Generation started: ' + new Date().toISOString());
        console.log('═══════════════════════════════════════════════════');
        
        const generationStartTime = Date.now();
        const orchestrator = orchestratorRef.current;
        
        // NEW v5.0: Use composition mode if enabled
        // CRITICAL: Do NOT fall back to old scene mode - composition pipeline has its own fallbacks
        let genResult;
        
        // Check feature flag for legacy fallback (default: disabled)
        const USE_LEGACY_FALLBACK = false; // Set to true only for debugging
        
        if (useCompositionMode) {
          console.log('🎨 [NetraEngine v5.0] Using COMPOSITION mode (primary)...');
          try {
            genResult = await orchestrator.generateComposition(question, context);
            if (loadingIntervalRef.current) {
              clearInterval(loadingIntervalRef.current);
              loadingIntervalRef.current = null;
            }
            console.log(`⏱️ [TIMING] Total generation time: ${Date.now() - generationStartTime}ms`);
            
            // Log result
            if (genResult.success && genResult.composition?.atoms?.length > 0) {
              console.log('✅ [NetraEngine v5.0] Composition successful:', genResult.composition.atoms.length, 'atoms');
            } else {
              console.warn('⚠️ [NetraEngine v5.0] Composition returned:', {
                success: genResult.success,
                atomCount: genResult.composition?.atoms?.length || 0,
                error: genResult.error
              });
              
              // Only fall back to scene mode if explicitly enabled
              if (USE_LEGACY_FALLBACK && (!genResult.success || !genResult.composition?.atoms?.length)) {
                console.warn('🔄 [NetraEngine] Legacy fallback ENABLED - trying SCENE mode');
                genResult = await orchestrator.generate(question, context);
              }
            }
          } catch (composeError) {
            console.error('❌ [NetraEngine] Composition error:', composeError.message);
            
            // Only fall back to scene mode if explicitly enabled
            if (USE_LEGACY_FALLBACK) {
              console.warn('🔄 [NetraEngine] Legacy fallback ENABLED - trying SCENE mode');
              genResult = await orchestrator.generate(question, context);
            } else {
              // Return error state instead of falling back to old pipeline
              throw composeError;
            }
          }
        } else {
          console.log('🎬 [NetraEngine v4.0] Using SCENE mode (legacy)...');
          genResult = await orchestrator.generate(question, context);
          if (loadingIntervalRef.current) {
            clearInterval(loadingIntervalRef.current);
            loadingIntervalRef.current = null;
          }
        }
        
        // 🔧 FIX: Check if component still mounted before updating state
        if (!mountedRef.current || generationAbortRef.current) {
          console.log('⚠️ [NetraEngine] Generation completed but component unmounted/aborted, skipping state update');
          return;
        }
        
        if (genResult.success) {
          console.log('✅ [NetraEngine] Generation successful!');
          if (genResult.composition) {
            console.log('✅ Atoms:', genResult.composition.atoms?.length || 0);
            console.log('✅ Behaviors:', genResult.composition.behaviors?.length || 0);
            console.log('✅ Mode: COMPOSITION');
          } else {
            console.log('✅ Scene Objects:', genResult.sceneObjects?.length || 0, '(NOT boxes!)');
            console.log('✅ Intent:', genResult.reasoning?.intent?.primary);
            console.log('✅ Form:', genResult.reasoning?.form?.form);
          }
          console.log('✅ Metadata:', genResult.metadata);
          setResult(genResult);
          onGenerated?.(genResult);
        } else {
          console.error('❌ [NetraEngine] Generation failed:', genResult.error);
          throw new Error(genResult.error || 'Generation failed');
        }
      } catch (err) {
        if (loadingIntervalRef.current) {
          clearInterval(loadingIntervalRef.current);
          loadingIntervalRef.current = null;
        }
        console.error('🔮 [NetraEngine] Error:', err);
        if (mountedRef.current) {
          setError(err.message);
          onError?.(err);
        }
      } finally {
        if (loadingIntervalRef.current) {
          clearInterval(loadingIntervalRef.current);
          loadingIntervalRef.current = null;
        }
        if (mountedRef.current) {
          setLoading(false);
        }
      }
    };

    generate();
  }, [question, context.subject, context.level, context.visual_needed, context.intent, preGeneratedScene, useCompositionMode]);

  // Retry handler
  const handleRetry = useCallback(() => {
    lastQuestionRef.current = null;
    setError(null);
    setResult(null);
    // Will trigger re-generation via useEffect
  }, []);

  // Render complete handler
  const handleRenderComplete = useCallback(() => {
    console.log('🔮 [NetraEngine] Render complete');
    onRenderComplete?.();
  }, [onRenderComplete]);

  // Determine what to render
  const renderContent = () => {
    if (loading) {
      return <LoadingState message="Understanding concept..." />;
    }

    if (error) {
      return <ErrorState error={error} onRetry={handleRetry} />;
    }

    if (!result || (!result.sceneGraph && !result.sceneObjects && !result.composition)) {
      return <EmptyState />;
    }

    // ============================================
    // NEW v5.0: Check for COMPOSITION mode first (PRIMARY ENGINE)
    // ============================================
    // CRITICAL: If composition exists with atoms, ALWAYS use DynamicVisualRenderer
    // Don't require renderMode === 'composition' - just check for atoms
    const hasComposition = result.composition && result.composition.atoms && result.composition.atoms.length > 0;
    
    if (hasComposition) {
      console.log('🎨 [NetraEngine v5.0] Using DynamicVisualRenderer (COMPOSITION mode)');
      console.log('🎨 Atoms:', result.composition.atoms.length);
      console.log('🎨 Behaviors:', result.composition.behaviors?.length || 0);
      console.log('🎨 Narration:', result.composition.narration?.length || 0);
      return (
        <>
          <DynamicVisualRenderer
            composition={result.composition}
            width={width}
            height={height}
            onReady={handleRenderComplete}
            onNarration={onNarration}
          />
          {showMetadata && <MetadataBadge metadata={result.metadata} />}
        </>
      );
    }

    // Check if we should use the NEW SceneRenderer (v4.0)
    const hasSceneObjects = result.sceneObjects?.length > 0;
    const useSceneRendering = hasSceneObjects && result.metadata?.useSceneRenderer !== false;
    
    // Use AnimatedRenderer if we have animation beats (v3.0) or teaching sequence (v2.0)
    const hasV3Animation = result.animationBeats?.length > 0;
    const hasV2Narrative = result.teachingSequence?.beats?.length > 0;
    const hasAnimation = hasV3Animation || hasV2Narrative;
    
    // Log reasoning for debugging
    if (result.reasoning?.intent) {
      console.log('🧠 [NetraEngine v4.0] Reasoning:', {
        intent: result.reasoning.intent.primary,
        form: result.reasoning.form?.form,
        layout: result.reasoning.layout?.layout,
        animation: result.reasoning.animation?.strategy,
        sceneObjects: result.sceneObjects?.length || 0,
        useSceneRendering,
      });
    }
    
    return (
      <>
        {useSceneRendering ? (
          // 🎬 NEW v4.0: Scene-based rendering (NOT boxes!)
          <SceneRenderer
            sceneObjects={result.sceneObjects}
            width={width}
            height={height}
            domain={result.metadata?.domain || 'physics'}
            showLabels={true}
            onRenderComplete={handleRenderComplete}
          />
        ) : hasAnimation ? (
          // 🎬 Animated narrative rendering - intent-driven visual story (legacy)
          <AnimatedRenderer
            sceneGraph={result.sceneGraph}
            teachingSequence={result.teachingSequence}
            animationBeats={result.animationBeats}      // v3.0: Dynamic beats
            animationResult={result.reasoning?.animation} // v3.0: Animation strategy
            reasoning={result.reasoning}                // v3.0: Full reasoning context
            width={width}
            height={height}
            autoPlay={true}
            onBeatChange={(beatIndex, beat) => {
              console.log(`🎬 [NetraEngine] Beat ${beatIndex + 1}:`, beat.narration || beat.type);
            }}
            onComplete={() => {
              console.log('🎬 [NetraEngine] Teaching sequence complete!');
              handleRenderComplete();
            }}
          />
        ) : (
          // Static fallback (legacy)
          <SVGRenderer
            sceneGraph={result.sceneGraph}
            width={width}
            height={height}
            showGrid={showGrid}
            onRenderComplete={handleRenderComplete}
          />
        )}
        {showMetadata && <MetadataBadge metadata={result.metadata} />}
      </>
    );
  };

  return (
    <div
      className={`netra-engine ${className}`}
      style={{
        position: 'relative',
        width,
        height,
        background: 'transparent',
        overflow: 'hidden',
        borderRadius: 12,
        ...style,
      }}
    >
      <AnimatePresence mode="wait">
        {renderContent()}
      </AnimatePresence>
    </div>
  );
};

// ============================================
// EXPORTS
// ============================================

export default NetraEngine;
export { NetraEngine };



