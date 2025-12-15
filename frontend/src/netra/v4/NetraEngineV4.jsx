/**
 * 🔮 NETRA v4.0 - Visual Intelligence Engine (Frontend)
 * =====================================================
 * 
 * Production-grade React component for rendering AI-generated educational visuals.
 * Uses Imagen-generated images with interactive teaching overlays.
 * 
 * Features:
 * - Renders unique, AI-generated images (not procedural SVG)
 * - Interactive hotspots for guided learning
 * - Step-by-step teaching flow with narration
 * - Annotation overlays
 * - Responsive and accessible
 * 
 * Usage:
 * <NetraEngineV4
 *   question="Explain photosynthesis"
 *   onGenerated={(result) => console.log(result)}
 * />
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import TeachingOverlay from './TeachingOverlay';
import { generateVisual, analyzeQuestion } from './api';

// ============================================
// LOADING STATE
// ============================================

const LoadingState = ({ message = 'Creating your visual...', stage = 'analyzing' }) => {
  const stages = {
    analyzing: { icon: '🧠', text: 'Understanding your question...' },
    strategizing: { icon: '📐', text: 'Planning the perfect visual...' },
    generating: { icon: '🎨', text: 'Generating unique image...' },
    teaching: { icon: '📚', text: 'Adding teaching elements...' },
  };

  const current = stages[stage] || stages.analyzing;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center justify-center h-full gap-6 p-8"
    >
      {/* Animated icon */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 5, -5, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="text-6xl"
      >
        {current.icon}
      </motion.div>

      {/* Message */}
      <div className="text-center">
        <div className="text-lg font-medium text-gray-700 mb-2">
          {current.text}
        </div>
        <div className="text-sm text-gray-500">
          {message}
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-64 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <motion.div
          animate={{ x: ['-100%', '100%'] }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="w-1/2 h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
        />
      </div>
    </motion.div>
  );
};

// ============================================
// ERROR STATE
// ============================================

const ErrorState = ({ error, onRetry }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="flex flex-col items-center justify-center h-full gap-4 p-8"
  >
    <div className="text-5xl">😕</div>
    <div className="text-center">
      <div className="text-lg font-medium text-red-600 mb-2">
        Something went wrong
      </div>
      <div className="text-sm text-gray-600 max-w-md">
        {error || 'Failed to generate visual. Please try again.'}
      </div>
    </div>
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
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
    className="flex flex-col items-center justify-center h-full gap-3"
  >
    <div className="text-5xl">🔮</div>
    <div className="text-gray-400 font-medium">
      Ask a question to see visual magic
    </div>
  </motion.div>
);

// ============================================
// IMAGE RENDERER
// ============================================

const ImageRenderer = ({ visual, onLoad, onError }) => {
  const [loaded, setLoaded] = useState(false);

  if (!visual?.image_base64) return null;

  const imageUrl = `data:image/${visual.image_format || 'png'};base64,${visual.image_base64}`;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: loaded ? 1 : 0 }}
      className="relative w-full h-full"
    >
      <img
        src={imageUrl}
        alt="Educational visual"
        className="w-full h-full object-contain"
        onLoad={() => {
          setLoaded(true);
          onLoad?.();
        }}
        onError={(e) => {
          console.error('Image load error:', e);
          onError?.('Failed to load image');
        }}
      />
    </motion.div>
  );
};

// ============================================
// METADATA BADGE
// ============================================

const MetadataBadge = ({ metadata }) => {
  if (!metadata) return null;

  const intentIcons = {
    explain: '💡',
    compare: '⚖️',
    show_process: '🔄',
    show_structure: '🏗️',
    derive: '📝',
    calculate: '🔢',
    visualize: '👁️',
    cause_effect: '➡️',
    timeline: '📅',
    relationship: '🔗',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="absolute top-3 right-3 flex items-center gap-2 px-3 py-1.5 bg-white/90 backdrop-blur-sm rounded-full shadow-sm text-xs font-medium text-gray-600"
    >
      <span>{intentIcons[metadata.intent] || '✨'}</span>
      <span>{metadata.concept}</span>
      <span className="text-gray-300">|</span>
      <span className="text-gray-400">{metadata.style?.replace('_', ' ')}</span>
    </motion.div>
  );
};

// ============================================
// MAIN COMPONENT
// ============================================

const NetraEngineV4 = ({
  // Input
  question = null,
  userLevel = 'intermediate',
  language = 'en',

  // Display
  width = 800,
  height = 600,
  showMetadata = true,
  showTeaching = true,

  // Callbacks
  onGenerated = null,
  onError = null,
  onStepChange = null,

  // Style
  className = '',
  style = {},
}) => {
  // State
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('analyzing');
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [teachingMode, setTeachingMode] = useState(false);

  // Refs
  const lastQuestionRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Generate visual when question changes
  useEffect(() => {
    if (!question) return;

    // Prevent duplicate requests
    if (lastQuestionRef.current === question && result) {
      return;
    }
    lastQuestionRef.current = question;

    // Abort previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    const generate = async () => {
      setLoading(true);
      setError(null);
      setLoadingStage('analyzing');

      try {
        console.log('🔮 [NetraV4] Generating visual for:', question);

        // Simulate stage progression for UX
        setTimeout(() => setLoadingStage('strategizing'), 1000);
        setTimeout(() => setLoadingStage('generating'), 2500);
        setTimeout(() => setLoadingStage('teaching'), 5000);

        const response = await generateVisual({
          question,
          user_level: userLevel,
          language,
        });

        if (response.success) {
          console.log('✅ [NetraV4] Visual generated:', response.metadata?.concept);
          setResult(response);
          onGenerated?.(response);
        } else {
          throw new Error(response.error || 'Generation failed');
        }
      } catch (err) {
        if (err.name === 'AbortError') return;
        console.error('❌ [NetraV4] Error:', err);
        setError(err.message);
        onError?.(err);
      } finally {
        setLoading(false);
      }
    };

    generate();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [question, userLevel, language]);

  // Retry handler
  const handleRetry = useCallback(() => {
    lastQuestionRef.current = null;
    setError(null);
    setResult(null);
  }, []);

  // Toggle teaching mode
  const toggleTeaching = useCallback(() => {
    setTeachingMode((prev) => !prev);
  }, []);

  // Render content
  const renderContent = () => {
    if (loading) {
      return <LoadingState stage={loadingStage} />;
    }

    if (error) {
      return <ErrorState error={error} onRetry={handleRetry} />;
    }

    if (!result?.visual) {
      return <EmptyState />;
    }

    return (
      <>
        {/* Main image */}
        <ImageRenderer
          visual={result.visual}
          onError={setError}
        />

        {/* Teaching overlay */}
        {showTeaching && result.teaching && teachingMode && (
          <TeachingOverlay
            teaching={result.teaching}
            onStepChange={onStepChange}
            onClose={() => setTeachingMode(false)}
          />
        )}

        {/* Metadata badge */}
        {showMetadata && <MetadataBadge metadata={result.metadata} />}

        {/* Teaching toggle button */}
        {showTeaching && result.teaching && !teachingMode && (
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1 }}
            onClick={toggleTeaching}
            className="absolute bottom-4 right-4 px-4 py-2 bg-blue-500 text-white rounded-lg shadow-lg hover:bg-blue-600 transition-colors font-medium flex items-center gap-2"
          >
            <span>📚</span>
            <span>Start Learning</span>
          </motion.button>
        )}
      </>
    );
  };

  return (
    <div
      className={`netra-engine-v4 relative overflow-hidden rounded-xl bg-gray-50 ${className}`}
      style={{
        width,
        height,
        ...style,
      }}
    >
      <AnimatePresence mode="wait">
        {renderContent()}
      </AnimatePresence>
    </div>
  );
};

export default NetraEngineV4;
export { NetraEngineV4 };

