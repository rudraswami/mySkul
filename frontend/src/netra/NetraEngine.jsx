/**
 * 🔮 NETRA ENGINE REACT COMPONENT
 * ================================
 * 
 * The main React component for the NETRA Visual Reasoning Engine.
 * 
 * Usage:
 * <NetraEngine
 *   question="Explain Newton's third law with a rocket"
 *   context={{ subject: 'physics', level: 'high_school' }}
 *   onGenerated={(result) => console.log(result)}
 * />
 * 
 * This is a drop-in replacement for MagicNotebookEngine that produces
 * intelligent, varied, semantic visuals — not repeated patterns.
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Core engine
import { Orchestrator, createOrchestrator } from './core/Orchestrator';

// Renderers
import SVGRenderer from './rendering/SVGRenderer';
import AnimatedRenderer from './rendering/AnimatedRenderer';

// ============================================
// LOADING STATES
// ============================================

const LoadingState = ({ message = 'Understanding concept...' }) => (
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
      gap: 16,
      padding: 40,
    }}
  >
    {/* Animated brain icon */}
    <motion.div
      animate={{
        scale: [1, 1.1, 1],
        rotate: [0, 5, -5, 0],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      style={{ fontSize: 48 }}
    >
      🧠
    </motion.div>
    
    {/* Message */}
    <div
      style={{
        fontFamily: "'Kalam', cursive",
        fontSize: 16,
        color: '#7F8C8D',
      }}
    >
      {message}
    </div>
    
    {/* Progress bar */}
    <div
      style={{
        width: 200,
        height: 4,
        background: '#ECF0F1',
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      <motion.div
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        style={{
          width: '50%',
          height: '100%',
          background: 'linear-gradient(90deg, #3498DB, #9B59B6)',
          borderRadius: 2,
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
  
  // Display
  width = 800,
  height = 600,
  showGrid = true,
  showMetadata = true,
  
  // Callbacks
  onGenerated = null,
  onError = null,
  onRenderComplete = null,
  
  // Style
  className = '',
  style = {},
  
  // Options
  useLLM = false,                      // Use LLM for deep understanding
  apiClient = null,                    // API client for LLM calls
}) => {
  // State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  
  // Prevent duplicate requests
  const lastQuestionRef = useRef(null);
  const orchestratorRef = useRef(null);

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

  // Generate visual when question changes
  useEffect(() => {
    if (preGeneratedScene) return; // Skip if using pre-generated
    if (!question) return;
    
    // Prevent duplicate requests
    const questionKey = `${question}_${context.subject || ''}_${context.level || ''}`;
    if (lastQuestionRef.current === questionKey && result) {
      console.log('🔮 [NetraEngine] Skipping duplicate request');
      return;
    }
    lastQuestionRef.current = questionKey;

    const generate = async () => {
      setLoading(true);
      setError(null);

      try {
        console.log('═══════════════════════════════════════════════════');
        console.log('🔮 [NetraEngine] GENERATING VISUAL');
        console.log('🔮 [NetraEngine] Question:', question);
        console.log('🔮 [NetraEngine] Context:', context);
        console.log('═══════════════════════════════════════════════════');
        
        const orchestrator = orchestratorRef.current;
        const genResult = await orchestrator.generate(question, context);
        
        if (genResult.success) {
          console.log('✅ [NetraEngine] Generation successful!');
          console.log('✅ [NetraEngine] SceneGraph nodes:', genResult.sceneGraph?.nodes?.size || 0);
          console.log('✅ [NetraEngine] Metadata:', genResult.metadata);
          setResult(genResult);
          onGenerated?.(genResult);
        } else {
          console.error('❌ [NetraEngine] Generation failed:', genResult.error);
          throw new Error(genResult.error || 'Generation failed');
        }
      } catch (err) {
        console.error('🔮 [NetraEngine] Error:', err);
        setError(err.message);
        onError?.(err);
      } finally {
        setLoading(false);
      }
    };

    generate();
  }, [question, context.subject, context.level, preGeneratedScene]);

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

    if (!result || !result.sceneGraph) {
      return <EmptyState />;
    }

    // Use AnimatedRenderer if we have animation beats (v3.0) or teaching sequence (v2.0)
    const hasV3Animation = result.animationBeats?.length > 0;
    const hasV2Narrative = result.teachingSequence?.beats?.length > 0;
    const hasAnimation = hasV3Animation || hasV2Narrative;
    
    // Log reasoning for debugging
    if (result.reasoning?.intent) {
      console.log('🧠 [NetraEngine] Reasoning:', {
        intent: result.reasoning.intent.primary,
        form: result.reasoning.form?.form,
        layout: result.reasoning.layout?.layout,
        animation: result.reasoning.animation?.strategy,
      });
    }
    
    return (
      <>
        {hasAnimation ? (
          // 🎬 Animated narrative rendering - intent-driven visual story
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
          // Static fallback
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



