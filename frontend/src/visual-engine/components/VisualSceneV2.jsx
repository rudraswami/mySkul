/**
 * VisualScene V2 - Auto-playing, Interactive Visual Teaching Component
 * 
 * Key improvements:
 * - Auto-plays without requiring Play button
 * - Objects never disappear (persistent registry)
 * - Proper step-based timeline
 * - Smooth animations with animation library
 * - Touch interactions (tap, long-press, swipe)
 * - Replay button inside scene
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RotateCcw, ChevronLeft, ChevronRight, Pause, Play, Volume2, VolumeX } from 'lucide-react';

// Core engines
import { sceneRegistry } from '../core/SceneObjectRegistry';
import { timelineEngine } from '../core/TimelineEngine';
import { interactionEngine } from '../core/InteractionEngine';
import { animations } from '../core/AnimationLibrary';

// Sub-components
import SceneBackground from './scene/SceneBackground';
import SceneProps from './scene/SceneProps';
import SceneProfessor from './scene/SceneProfessor';
import SceneLabels from './scene/SceneLabels';
import SceneVectors from './scene/SceneVectors';
import FormulaOverlay from './scene/FormulaOverlay';

const VisualSceneV2 = ({
  toon,
  autoPlay = true,
  showControls = true,
  onComplete,
  onInteraction,
  className = '',
}) => {
  // Scene state
  const [isInitialized, setIsInitialized] = useState(false);
  const [objects, setObjects] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showFormula, setShowFormula] = useState(false);
  const [formulaData, setFormulaData] = useState(null);
  const [highlightedObject, setHighlightedObject] = useState(null);
  
  const containerRef = useRef(null);
  const viewportRef = useRef({ width: 640, height: 360 });

  // Initialize scene from TOON
  useEffect(() => {
    if (!toon) return;

    // Clear previous scene
    sceneRegistry.clear();
    interactionEngine.clear();

    // Register all objects from TOON
    initializeScene(toon);

    // Set up timeline
    if (toon.steps) {
      timelineEngine.init(toon.steps);
    }

    // Set up interactions
    setupInteractions(toon);

    // Subscribe to registry changes
    const unsubscribe = sceneRegistry.subscribe((newObjects) => {
      setObjects([...newObjects]);
    });

    // Subscribe to timeline events
    const unsubStep = timelineEngine.on('stepChange', ({ step }) => {
      setCurrentStep(step);
    });

    const unsubPlay = timelineEngine.on('play', () => setIsPlaying(true));
    const unsubPause = timelineEngine.on('pause', () => setIsPlaying(false));
    const unsubStop = timelineEngine.on('stop', () => {
      setIsPlaying(false);
      setCurrentStep(0);
    });

    // Subscribe to interaction events
    const unsubFormula = interactionEngine.on('showFormula', ({ objectId }) => {
      const obj = sceneRegistry.get(objectId);
      setFormulaData(obj || toon.formula);
      setShowFormula(true);
    });

    const unsubHighlight = interactionEngine.on('tap', ({ objectId }) => {
      if (objectId) {
        setHighlightedObject(objectId);
        setTimeout(() => setHighlightedObject(null), 1500);
        onInteraction?.('tap', { objectId });
      }
    });

    setIsInitialized(true);

    // Auto-play after short delay
    if (autoPlay) {
      const timer = setTimeout(() => {
        timelineEngine.play();
        runStepAnimations(0);
      }, 800);
      return () => {
        clearTimeout(timer);
        unsubscribe();
        unsubStep();
        unsubPlay();
        unsubPause();
        unsubStop();
        unsubFormula();
        unsubHighlight();
      };
    }

    return () => {
      unsubscribe();
      unsubStep();
      unsubPlay();
      unsubPause();
      unsubStop();
      unsubFormula();
      unsubHighlight();
    };
  }, [toon, autoPlay, onInteraction]);

  /**
   * Initialize scene objects from TOON
   */
  const initializeScene = useCallback((toon) => {
    // Register background
    sceneRegistry.register('background', {
      type: 'background',
      scene: toon.scene || 'classroom',
      visible: true,
    });

    // Register actors (professor, etc.)
    toon.actors?.forEach((actor, i) => {
      sceneRegistry.register(actor.id || `actor_${i}`, {
        type: 'actor',
        actorType: actor.type || 'professor',
        ...actor,
        x: (actor.position?.x || 0.1) * 100,
        y: (actor.position?.y || 0.5) * 100,
        visible: true,
        gesture: actor.initialState || 'standing',
        initialState: {
          x: (actor.position?.x || 0.1) * 100,
          y: (actor.position?.y || 0.5) * 100,
          gesture: actor.initialState || 'standing',
        },
      });
    });

    // Register props
    toon.props?.forEach((prop, i) => {
      sceneRegistry.register(prop.id || `prop_${i}`, {
        type: 'prop',
        propType: prop.type,
        ...prop,
        x: (prop.position?.x || 0.5) * 100,
        y: (prop.position?.y || 0.5) * 100,
        visible: true,
        initialState: {
          x: (prop.position?.x || 0.5) * 100,
          y: (prop.position?.y || 0.5) * 100,
          opacity: 1,
        },
      });
    });

    // Register labels (initially hidden, shown on steps)
    toon.labels?.forEach((label, i) => {
      sceneRegistry.register(label.id || `label_${i}`, {
        type: 'label',
        ...label,
        visible: label.showOn === 'always',
        opacity: label.showOn === 'always' ? 1 : 0,
      });
    });

    // Register animations as vector objects
    toon.animations?.filter(a => a.type === 'vector_grow' || a.id?.includes('force') || a.id?.includes('arrow')).forEach((anim, i) => {
      sceneRegistry.register(anim.id || `vector_${i}`, {
        type: 'vector',
        direction: anim.direction || 'right',
        magnitude: 0,
        visible: false,
        opacity: 0,
      });
    });
  }, []);

  /**
   * Set up interactions from TOON
   */
  const setupInteractions = useCallback((toon) => {
    // Register object-specific interactions
    toon.interactions?.forEach(interaction => {
      if (interaction.onTap) {
        interactionEngine.register(interaction.target || interaction.onTap, {
          onTap: interaction.action,
        });
      }
      if (interaction.onLongPress) {
        interactionEngine.register(interaction.target || interaction.onLongPress, {
          onLongPress: interaction.action,
        });
      }
    });

    // Global swipe for step navigation
    interactionEngine.registerGlobal({
      onSwipe: 'next_step',
    });
  }, []);

  /**
   * Run animations for a specific step
   */
  const runStepAnimations = useCallback(async (stepIndex) => {
    const step = timelineEngine.getStep(stepIndex);
    if (!step) return;

    // Run animations for this step
    for (const animId of step.animations) {
      const animConfig = toon?.animations?.find(a => a.id === animId);
      if (animConfig) {
        await runAnimation(animConfig);
      }
    }

    // Show labels for this step
    step.labels?.forEach(labelId => {
      animations.fadeIn(labelId, { duration: 400 });
    });
  }, [toon]);

  /**
   * Run a single animation
   */
  const runAnimation = useCallback(async (animConfig) => {
    const { id, target, type } = animConfig;

    switch (type) {
      case 'throw':
      case 'projectile':
      case 'curve_forward':
        await animations.projectile(target, {
          force: animConfig.force || 'medium',
          angle: animConfig.angle || -15,
          duration: animConfig.duration || 1500,
        });
        break;

      case 'vector_grow':
      case 'force_arrow':
        await animations.forceArrowGrow(id || target, {
          direction: animConfig.direction,
          magnitude: animConfig.magnitude || 100,
          duration: (animConfig.duration || 0.8) * 1000,
        });
        break;

      case 'rotate':
      case 'rotate_forward':
        await animations.rotate(target, {
          angle: animConfig.angle || 90,
          duration: animConfig.duration || 600,
        });
        break;

      case 'gesture':
        await animations.professorGesture(target, animConfig.params?.gesture || 'point');
        break;

      case 'pulse':
        await animations.pulse(target, { duration: 800 });
        break;

      case 'fadeIn':
        await animations.fadeIn(target, { duration: 400 });
        break;

      default:
        console.log(`Unknown animation type: ${type}`);
    }
  }, []);

  /**
   * Handle step navigation
   */
  const handleNextStep = useCallback(() => {
    const hasNext = timelineEngine.nextStep();
    if (hasNext) {
      runStepAnimations(timelineEngine.currentStepIndex);
    }
  }, [runStepAnimations]);

  const handlePrevStep = useCallback(() => {
    timelineEngine.prevStep();
  }, []);

  /**
   * Handle replay
   */
  const handleReplay = useCallback(() => {
    sceneRegistry.reset();
    timelineEngine.stop();
    setCurrentStep(0);
    
    setTimeout(() => {
      timelineEngine.play();
      runStepAnimations(0);
    }, 300);
  }, [runStepAnimations]);

  /**
   * Handle touch events
   */
  const handleTouchStart = useCallback((e, objectId = null) => {
    interactionEngine.handleStart(e.nativeEvent, objectId);
  }, []);

  const handleTouchMove = useCallback((e) => {
    interactionEngine.handleMove(e.nativeEvent);
  }, []);

  const handleTouchEnd = useCallback((e) => {
    interactionEngine.handleEnd(e.nativeEvent);
  }, []);

  /**
   * Handle click on object
   */
  const handleObjectClick = useCallback((objectId) => {
    interactionEngine.handleTap(objectId);
    onInteraction?.('tap', { objectId });
  }, [onInteraction]);

  // Categorize objects by type
  const categorizedObjects = useMemo(() => {
    const result = {
      background: null,
      actors: [],
      props: [],
      labels: [],
      vectors: [],
    };

    objects.forEach(obj => {
      switch (obj.type) {
        case 'background':
          result.background = obj;
          break;
        case 'actor':
          result.actors.push(obj);
          break;
        case 'prop':
          result.props.push(obj);
          break;
        case 'label':
          result.labels.push(obj);
          break;
        case 'vector':
          result.vectors.push(obj);
          break;
      }
    });

    return result;
  }, [objects]);

  const totalSteps = toon?.steps?.length || 1;

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center h-64 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          className="w-10 h-10 border-3 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <motion.div
      ref={containerRef}
      className={`visual-scene-v2 relative rounded-2xl overflow-hidden shadow-2xl bg-white ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      onMouseDown={(e) => handleTouchStart(e)}
      onMouseMove={handleTouchMove}
      onMouseUp={handleTouchEnd}
    >
      {/* Header with topic and analogy */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-gradient-to-b from-black/70 via-black/40 to-transparent p-4 pb-8">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-white font-bold text-lg drop-shadow-lg">
              {toon?.topic || 'Visual Explanation'}
            </h3>
            {toon?.analogy && (
              <p className="text-white/90 text-sm mt-1 drop-shadow">
                💡 {toon.analogy}
              </p>
            )}
          </div>
          
          {/* Formula badge */}
          {toon?.formula && (
            <div className="bg-white/95 rounded-lg px-3 py-2 shadow-lg ml-3">
              <div className="text-lg font-bold text-gray-800">{toon.formula.main}</div>
              <div className="text-xs text-gray-500">{toon.formula.meaning}</div>
            </div>
          )}
        </div>
      </div>

      {/* Main SVG Scene */}
      <svg
        viewBox="0 0 100 60"
        className="w-full h-auto"
        style={{ minHeight: '300px', maxHeight: '450px' }}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Background */}
        <SceneBackground 
          scene={categorizedObjects.background?.scene || toon?.scene || 'classroom'} 
        />

        {/* Props */}
        <SceneProps
          props={categorizedObjects.props}
          highlightedId={highlightedObject}
          onPropClick={handleObjectClick}
        />

        {/* Professor/Actors */}
        {categorizedObjects.actors.map(actor => (
          <SceneProfessor
            key={actor.id}
            {...actor}
            onClick={() => handleObjectClick(actor.id)}
          />
        ))}

        {/* Vectors/Arrows */}
        <SceneVectors vectors={categorizedObjects.vectors} />

        {/* Labels */}
        <SceneLabels
          labels={categorizedObjects.labels}
          onLabelClick={handleObjectClick}
        />
      </svg>

      {/* Step Controls - Bottom */}
      {showControls && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 pt-8">
          <div className="flex items-center justify-between max-w-md mx-auto">
            {/* Prev Step */}
            <button
              onClick={handlePrevStep}
              disabled={currentStep === 0}
              className={`p-2 rounded-full transition-all ${
                currentStep === 0 
                  ? 'bg-white/20 text-white/40' 
                  : 'bg-white/30 text-white hover:bg-white/40'
              }`}
            >
              <ChevronLeft className="w-6 h-6" />
            </button>

            {/* Step Indicator */}
            <div className="flex items-center space-x-2">
              {[...Array(totalSteps)].map((_, i) => (
                <motion.div
                  key={i}
                  className={`w-2.5 h-2.5 rounded-full transition-all ${
                    i === currentStep 
                      ? 'bg-orange-500 scale-125' 
                      : i < currentStep 
                        ? 'bg-green-500' 
                        : 'bg-white/40'
                  }`}
                  animate={i === currentStep ? { scale: [1, 1.3, 1] } : {}}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                />
              ))}
            </div>

            {/* Next Step */}
            <button
              onClick={handleNextStep}
              disabled={currentStep >= totalSteps - 1}
              className={`p-2 rounded-full transition-all ${
                currentStep >= totalSteps - 1 
                  ? 'bg-white/20 text-white/40' 
                  : 'bg-orange-500 text-white hover:bg-orange-600 shadow-lg'
              }`}
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          </div>

          {/* Step description */}
          <div className="text-center mt-3">
            <p className="text-white/90 text-sm font-medium">
              Step {currentStep + 1}: {toon?.steps?.[currentStep]?.title || `Step ${currentStep + 1}`}
            </p>
          </div>
        </div>
      )}

      {/* Replay Button - Floating */}
      <motion.button
        onClick={handleReplay}
        className="absolute top-20 right-4 z-30 p-2 bg-white/90 rounded-full shadow-lg hover:bg-white transition-all"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        title="Replay Animation"
      >
        <RotateCcw className="w-5 h-5 text-gray-700" />
      </motion.button>

      {/* Formula Overlay */}
      <AnimatePresence>
        {showFormula && (
          <FormulaOverlay
            formula={formulaData || toon?.formula}
            onClose={() => setShowFormula(false)}
          />
        )}
      </AnimatePresence>

      {/* Interaction hints */}
      <div className="absolute bottom-24 left-0 right-0 text-center pointer-events-none">
        <motion.p
          className="text-white/60 text-xs"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
        >
          👆 Tap objects • 📱 Long-press for formula • 👉 Swipe for steps
        </motion.p>
      </div>
    </motion.div>
  );
};

export default VisualSceneV2;


