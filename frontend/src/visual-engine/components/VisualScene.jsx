/**
 * VisualScene - Main Interactive Visual Teaching Component
 * 
 * This is the primary component that renders animated, interactive
 * teaching scenes based on TOON instructions.
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TOONParser } from '../core/TOONParser';
import { AnimationTimeline } from '../core/AnimationTimeline';
import SceneRenderer from './SceneRenderer';
import ControlBar from './ControlBar';
import StepIndicator from './StepIndicator';

// Create parser instance once
const toonParser = new TOONParser();

const VisualScene = ({
  toon,
  concept,
  context = {},
  language = 'hinglish',
  autoPlay = true,
  showControls = true,
  onInteraction,
  onComplete,
  className = '',
}) => {
  // Parse TOON to scene config
  const [sceneConfig, setSceneConfig] = useState(null);
  const [animState, setAnimState] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [showFormula, setShowFormula] = useState(false);
  const [activeLabel, setActiveLabel] = useState(null);
  
  const timelineRef = useRef(new AnimationTimeline());
  const containerRef = useRef(null);

  // Initialize scene from TOON
  useEffect(() => {
    let config;
    
    if (toon) {
      config = toonParser.parse(toon);
    } else if (concept) {
      // Auto-generate TOON from concept name
      const generatedToon = generateTOONFromConcept(concept, context);
      config = toonParser.parse(generatedToon);
    }

    if (config) {
      setSceneConfig(config);
      timelineRef.current.init(config);
      
      // Set up timeline listeners
      timelineRef.current.on('tick', (state) => {
        setAnimState(state);
      });
      
      timelineRef.current.on('step', (step) => {
        setCurrentStep(step);
      });

      if (autoPlay) {
        setTimeout(() => timelineRef.current.play(), 500);
      }
    }

    return () => {
      timelineRef.current.stop();
    };
  }, [toon, concept, context, autoPlay]);

  // Control handlers
  const handlePlay = useCallback(() => {
    setIsPlaying(true);
    timelineRef.current.play();
  }, []);

  const handlePause = useCallback(() => {
    setIsPlaying(false);
    timelineRef.current.pause();
  }, []);

  const handleRestart = useCallback(() => {
    timelineRef.current.stop();
    setCurrentStep(0);
    setTimeout(() => {
      timelineRef.current.play();
      setIsPlaying(true);
    }, 100);
  }, []);

  const handleNextStep = useCallback(() => {
    timelineRef.current.nextStep();
  }, []);

  const handlePrevStep = useCallback(() => {
    timelineRef.current.prevStep();
  }, []);

  // Interaction handlers
  const handleTap = useCallback((targetId, position) => {
    const interaction = sceneConfig?.interactions?.find(
      i => i.target === targetId && i.type === 'tap'
    );

    if (interaction) {
      switch (interaction.action) {
        case 'animate':
          // Trigger animation for this target
          const anim = sceneConfig.animations.find(
            a => a.target === targetId && a.trigger === 'tap'
          );
          if (anim) {
            timelineRef.current.triggerAnimation(anim.id);
          }
          break;
        case 'showFormula':
          setShowFormula(true);
          break;
        case 'nextStep':
          handleNextStep();
          break;
        case 'explain':
          setActiveLabel(targetId);
          break;
      }
    }

    onInteraction?.('tap', { targetId, position });
  }, [sceneConfig, onInteraction, handleNextStep]);

  const handleLongPress = useCallback((targetId) => {
    setShowFormula(true);
    setActiveLabel(targetId);
    onInteraction?.('longPress', { targetId });
  }, [onInteraction]);

  const handleSwipe = useCallback((direction) => {
    if (direction === 'left') {
      handleNextStep();
    } else if (direction === 'right') {
      handlePrevStep();
    }
    onInteraction?.('swipe', { direction });
  }, [handleNextStep, handlePrevStep, onInteraction]);

  if (!sceneConfig) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-100 rounded-xl">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500" />
      </div>
    );
  }

  return (
    <motion.div
      ref={containerRef}
      className={`visual-scene-container relative rounded-2xl overflow-hidden shadow-2xl ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Scene Header */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-gradient-to-b from-black/60 to-transparent p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-bold text-lg">
              {sceneConfig.topic}
            </h3>
            {sceneConfig.analogy && (
              <p className="text-white/80 text-sm mt-1">
                💡 {sceneConfig.analogy}
              </p>
            )}
          </div>
          
          {/* Step Indicator */}
          {sceneConfig.steps?.length > 1 && (
            <StepIndicator
              currentStep={currentStep}
              totalSteps={sceneConfig.steps.length}
              stepTitles={sceneConfig.steps.map(s => s.title)}
            />
          )}
        </div>
      </div>

      {/* Main Scene Renderer */}
      <SceneRenderer
        config={sceneConfig}
        animState={animState}
        timeline={timelineRef.current}
        language={language}
        onTap={handleTap}
        onLongPress={handleLongPress}
        onSwipe={handleSwipe}
        activeLabel={activeLabel}
        showFormula={showFormula}
      />

      {/* Formula Overlay */}
      <AnimatePresence>
        {showFormula && (
          <motion.div
            className="absolute inset-0 z-30 flex items-center justify-center bg-black/70"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowFormula(false)}
          >
            <motion.div
              className="bg-white rounded-2xl p-8 max-w-md mx-4 shadow-2xl"
              initial={{ scale: 0.8, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.8, y: 20 }}
              onClick={e => e.stopPropagation()}
            >
              <FormulaCard config={sceneConfig} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Control Bar */}
      {showControls && (
        <ControlBar
          isPlaying={isPlaying}
          onPlay={handlePlay}
          onPause={handlePause}
          onRestart={handleRestart}
          onNextStep={handleNextStep}
          onPrevStep={handlePrevStep}
          hasSteps={sceneConfig.steps?.length > 1}
          currentStep={currentStep}
          totalSteps={sceneConfig.steps?.length || 1}
        />
      )}

      {/* Tap Hint */}
      {!animState && (
        <motion.div
          className="absolute bottom-20 left-0 right-0 text-center text-white/80 text-sm"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          👆 Tap anywhere to interact • Long press for formula
        </motion.div>
      )}
    </motion.div>
  );
};

/**
 * Formula Card Component
 */
const FormulaCard = ({ config }) => {
  const formulas = {
    force: { main: 'F = m × a', meaning: 'Force = Mass × Acceleration', unit: 'Newton (N)' },
    motion: { main: 'v = u + at', meaning: 'Final velocity = Initial + (accel × time)', unit: 'm/s' },
    gravity: { main: 'F = G(m₁m₂)/r²', meaning: 'Gravitational Force', unit: 'Newton (N)' },
  };

  const formula = formulas[config.id] || formulas['force'];

  return (
    <div className="text-center">
      <div className="text-4xl font-bold text-purple-600 mb-4">
        {formula.main}
      </div>
      <div className="text-gray-600 mb-2">{formula.meaning}</div>
      <div className="text-sm text-gray-400">Unit: {formula.unit}</div>
      <div className="mt-6 p-4 bg-yellow-50 rounded-lg text-left">
        <div className="text-sm font-semibold text-yellow-800 mb-2">💡 याद रखो:</div>
        <div className="text-sm text-yellow-700">
          {config.analogy || 'Force causes acceleration in objects'}
        </div>
      </div>
    </div>
  );
};

/**
 * Generate TOON from concept name
 */
const generateTOONFromConcept = (concept, context = {}) => {
  const templates = {
    force: require('../templates/force.toon').forceTOON,
    motion: require('../templates/motion.toon').motionTOON,
    gravity: require('../templates/gravity.toon').gravityTOON,
  };

  const template = templates[concept.toLowerCase()];
  
  if (template) {
    // Apply context modifications
    return {
      ...template,
      language: context.language || 'hinglish',
      region: context.region || 'north',
    };
  }

  // Default generic template
  return {
    topic: concept,
    scene: 'classroom',
    actors: [{ id: 'professor', type: 'professor', role: 'demonstrator' }],
    props: [],
    animations: [],
    labels: [{ text: `Explaining: ${concept}` }],
  };
};

export default VisualScene;

