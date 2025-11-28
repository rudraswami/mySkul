/**
 * LayeredVisual.jsx
 * Phase 1.2: Multi-layer reveal system
 * 
 * 4 Layers:
 * Layer 1: Basic Scene (concept understanding)
 * Layer 2: Formula + Calculations
 * Layer 3: Deep Mechanics (forces, vectors, graphs)
 * Layer 4: Exam Mode (questions inside scene)
 */

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Layers, Eye, Calculator, Compass, GraduationCap, 
  Lock, Unlock, ChevronRight, Sparkles, Trophy
} from 'lucide-react';

// Layer definitions
const LAYER_CONFIG = {
  basic: {
    id: 'basic',
    name: 'Basic',
    icon: Eye,
    color: 'blue',
    description: 'Understand the concept',
    unlockCondition: null, // Always unlocked
  },
  formula: {
    id: 'formula',
    name: 'Formula',
    icon: Calculator,
    color: 'green',
    description: 'See the math',
    unlockCondition: 'view_basic', // Unlock after viewing basic
  },
  mechanics: {
    id: 'mechanics',
    name: 'Deep Dive',
    icon: Compass,
    color: 'purple',
    description: 'Vectors & graphs',
    unlockCondition: 'interact_formula', // Unlock after interacting with formula
  },
  exam: {
    id: 'exam',
    name: 'Exam Mode',
    icon: GraduationCap,
    color: 'orange',
    description: 'Test yourself',
    unlockCondition: 'complete_mechanics', // Unlock after completing mechanics
  },
};

const LayeredVisual = ({
  children,
  concept,
  onLayerChange,
  onInteraction,
  gamificationEnabled = true,
  initialLayer = 'basic',
  showLayerNav = true,
}) => {
  const [activeLayer, setActiveLayer] = useState(initialLayer);
  const [unlockedLayers, setUnlockedLayers] = useState(['basic']);
  const [layerProgress, setLayerProgress] = useState({
    basic: { viewed: false, interactions: 0 },
    formula: { viewed: false, interactions: 0 },
    mechanics: { viewed: false, interactions: 0 },
    exam: { viewed: false, interactions: 0, score: 0 },
  });
  const [showUnlockAnimation, setShowUnlockAnimation] = useState(null);

  // Check if layer is unlocked
  const isLayerUnlocked = useCallback((layerId) => {
    return unlockedLayers.includes(layerId);
  }, [unlockedLayers]);

  // Unlock a layer with animation
  const unlockLayer = useCallback((layerId) => {
    if (!unlockedLayers.includes(layerId)) {
      setUnlockedLayers(prev => [...prev, layerId]);
      setShowUnlockAnimation(layerId);
      setTimeout(() => setShowUnlockAnimation(null), 2000);
      
      // Gamification callback
      if (gamificationEnabled) {
        onInteraction?.({
          type: 'layer_unlock',
          layer: layerId,
          xp: 10,
        });
      }
    }
  }, [unlockedLayers, gamificationEnabled, onInteraction]);

  // Handle layer change
  const handleLayerChange = useCallback((layerId) => {
    if (!isLayerUnlocked(layerId)) {
      // Show locked message
      return;
    }
    
    setActiveLayer(layerId);
    
    // Update progress
    setLayerProgress(prev => ({
      ...prev,
      [layerId]: { ...prev[layerId], viewed: true },
    }));
    
    // Check for unlocks
    if (layerId === 'basic' && !unlockedLayers.includes('formula')) {
      setTimeout(() => unlockLayer('formula'), 1500);
    }
    
    onLayerChange?.(layerId);
  }, [isLayerUnlocked, unlockedLayers, unlockLayer, onLayerChange]);

  // Handle interaction within a layer
  const handleInteraction = useCallback((interactionData) => {
    setLayerProgress(prev => ({
      ...prev,
      [activeLayer]: {
        ...prev[activeLayer],
        interactions: prev[activeLayer].interactions + 1,
      },
    }));

    // Check for unlocks based on interactions
    if (activeLayer === 'formula' && layerProgress.formula.interactions >= 2) {
      unlockLayer('mechanics');
    }
    if (activeLayer === 'mechanics' && layerProgress.mechanics.interactions >= 3) {
      unlockLayer('exam');
    }

    onInteraction?.(interactionData);
  }, [activeLayer, layerProgress, unlockLayer, onInteraction]);

  // Get color classes for a layer
  const getLayerColors = (layerId) => {
    const colors = {
      basic: {
        bg: 'bg-blue-500',
        bgLight: 'bg-blue-100 dark:bg-blue-900/30',
        text: 'text-blue-600 dark:text-blue-400',
        border: 'border-blue-500',
      },
      formula: {
        bg: 'bg-green-500',
        bgLight: 'bg-green-100 dark:bg-green-900/30',
        text: 'text-green-600 dark:text-green-400',
        border: 'border-green-500',
      },
      mechanics: {
        bg: 'bg-purple-500',
        bgLight: 'bg-purple-100 dark:bg-purple-900/30',
        text: 'text-purple-600 dark:text-purple-400',
        border: 'border-purple-500',
      },
      exam: {
        bg: 'bg-orange-500',
        bgLight: 'bg-orange-100 dark:bg-orange-900/30',
        text: 'text-orange-600 dark:text-orange-400',
        border: 'border-orange-500',
      },
    };
    return colors[layerId] || colors.basic;
  };

  return (
    <div className="relative">
      {/* Layer Navigation */}
      {showLayerNav && (
        <div className="mb-3">
          {/* Desktop: Horizontal tabs */}
          <div className="hidden sm:flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-xl">
            {Object.values(LAYER_CONFIG).map((layer, idx) => {
              const Icon = layer.icon;
              const isActive = activeLayer === layer.id;
              const isUnlocked = isLayerUnlocked(layer.id);
              const colors = getLayerColors(layer.id);
              
              return (
                <React.Fragment key={layer.id}>
                  <motion.button
                    onClick={() => handleLayerChange(layer.id)}
                    disabled={!isUnlocked}
                    className={`relative flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                      isActive
                        ? `${colors.bg} text-white shadow-lg`
                        : isUnlocked
                          ? `${colors.bgLight} ${colors.text} hover:opacity-80`
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                    }`}
                    whileHover={isUnlocked ? { scale: 1.02 } : {}}
                    whileTap={isUnlocked ? { scale: 0.98 } : {}}
                  >
                    {isUnlocked ? (
                      <Icon className="w-4 h-4" />
                    ) : (
                      <Lock className="w-4 h-4" />
                    )}
                    <span>{layer.name}</span>
                    
                    {/* Progress indicator */}
                    {isUnlocked && layerProgress[layer.id]?.viewed && (
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white dark:border-gray-800" />
                    )}
                    
                    {/* Unlock animation */}
                    {showUnlockAnimation === layer.id && (
                      <motion.div
                        className="absolute inset-0 rounded-lg"
                        initial={{ boxShadow: '0 0 0 0 rgba(34, 197, 94, 0.7)' }}
                        animate={{ boxShadow: '0 0 0 10px rgba(34, 197, 94, 0)' }}
                        transition={{ duration: 0.5, repeat: 2 }}
                      />
                    )}
                  </motion.button>
                  
                  {idx < Object.values(LAYER_CONFIG).length - 1 && (
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  )}
                </React.Fragment>
              );
            })}
          </div>
          
          {/* Mobile: Compact selector */}
          <div className="sm:hidden">
            <div className="flex items-center justify-between p-2 bg-gray-100 dark:bg-gray-800 rounded-xl">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-gray-500" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Layer: {LAYER_CONFIG[activeLayer].name}
                </span>
              </div>
              <div className="flex gap-1">
                {Object.values(LAYER_CONFIG).map((layer) => {
                  const isActive = activeLayer === layer.id;
                  const isUnlocked = isLayerUnlocked(layer.id);
                  const colors = getLayerColors(layer.id);
                  
                  return (
                    <button
                      key={layer.id}
                      onClick={() => handleLayerChange(layer.id)}
                      disabled={!isUnlocked}
                      className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        isActive
                          ? `${colors.bg} text-white`
                          : isUnlocked
                            ? `${colors.bgLight} ${colors.text}`
                            : 'bg-gray-200 dark:bg-gray-700 text-gray-400'
                      }`}
                    >
                      {isUnlocked ? (
                        <layer.icon className="w-4 h-4" />
                      ) : (
                        <Lock className="w-3 h-3" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Layer Content */}
      <div className="relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeLayer}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            {/* Pass layer info to children */}
            {React.Children.map(children, child => {
              if (React.isValidElement(child)) {
                return React.cloneElement(child, {
                  activeLayer,
                  onInteraction: handleInteraction,
                  layerProgress: layerProgress[activeLayer],
                });
              }
              return child;
            })}
          </motion.div>
        </AnimatePresence>

        {/* Layer Overlay based on active layer */}
        <LayerOverlay 
          activeLayer={activeLayer} 
          concept={concept}
          onInteraction={handleInteraction}
        />
      </div>

      {/* Unlock Celebration */}
      <AnimatePresence>
        {showUnlockAnimation && (
          <motion.div
            className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-2xl border-2 border-green-500"
              initial={{ scale: 0.5, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.5, y: -50 }}
            >
              <div className="flex items-center gap-3">
                <motion.div
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ repeat: Infinity, duration: 0.5 }}
                >
                  <Unlock className="w-8 h-8 text-green-500" />
                </motion.div>
                <div>
                  <p className="font-bold text-gray-800 dark:text-white">
                    🎉 Layer Unlocked!
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {LAYER_CONFIG[showUnlockAnimation]?.name} is now available
                  </p>
                </div>
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 1 }}
                >
                  <Sparkles className="w-6 h-6 text-yellow-500" />
                </motion.div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress Bar */}
      {gamificationEnabled && (
        <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
              Visual Mastery
            </span>
            <span className="text-xs font-bold text-purple-600 dark:text-purple-400">
              {unlockedLayers.length}/{Object.keys(LAYER_CONFIG).length} Layers
            </span>
          </div>
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-orange-500"
              initial={{ width: 0 }}
              animate={{ width: `${(unlockedLayers.length / Object.keys(LAYER_CONFIG).length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          {unlockedLayers.length === Object.keys(LAYER_CONFIG).length && (
            <motion.div
              className="mt-2 flex items-center gap-2 text-sm text-green-600 dark:text-green-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <Trophy className="w-4 h-4" />
              <span>All layers unlocked! +50 XP bonus</span>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
};

// Layer-specific overlays
const LayerOverlay = ({ activeLayer, concept, onInteraction }) => {
  if (activeLayer === 'basic') return null;
  
  return (
    <AnimatePresence>
      {activeLayer === 'formula' && (
        <FormulaOverlay concept={concept} onInteraction={onInteraction} />
      )}
      {activeLayer === 'mechanics' && (
        <MechanicsOverlay concept={concept} onInteraction={onInteraction} />
      )}
      {activeLayer === 'exam' && (
        <ExamOverlay concept={concept} onInteraction={onInteraction} />
      )}
    </AnimatePresence>
  );
};

// Formula Layer Overlay
const FormulaOverlay = ({ concept, onInteraction }) => {
  const formulas = {
    force: { main: 'F = m × a', derived: ['a = F/m', 'm = F/a'], unit: 'Newton (N)' },
    motion: { main: 'v = u + at', derived: ['s = ut + ½at²', 'v² = u² + 2as'], unit: 'm/s' },
    gravity: { main: 'F = Gm₁m₂/r²', derived: ['g = GM/R²', 'W = mg'], unit: 'N or m/s²' },
    momentum: { main: 'p = mv', derived: ['Δp = FΔt', 'p₁ + p₂ = p₁\' + p₂\''], unit: 'kg·m/s' },
    energy: { main: 'E = ½mv²', derived: ['PE = mgh', 'W = Fd'], unit: 'Joule (J)' },
  };
  
  const data = formulas[concept?.toLowerCase()] || formulas.force;
  
  return (
    <motion.div
      className="absolute top-2 right-2 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-green-200 dark:border-green-800 max-w-xs"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
    >
      <div className="flex items-center gap-2 mb-3">
        <Calculator className="w-5 h-5 text-green-600" />
        <span className="font-bold text-green-700 dark:text-green-300">Formulas</span>
      </div>
      
      <div 
        className="text-2xl font-bold text-center py-3 bg-green-50 dark:bg-green-900/30 rounded-lg mb-3 cursor-pointer hover:bg-green-100 dark:hover:bg-green-900/50 transition-colors"
        onClick={() => onInteraction?.({ type: 'formula_tap', formula: data.main })}
      >
        {data.main}
      </div>
      
      <div className="space-y-1">
        <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Derived:</p>
        {data.derived.map((f, i) => (
          <div 
            key={i} 
            className="text-sm text-gray-700 dark:text-gray-300 pl-2 border-l-2 border-green-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 rounded-r px-2 py-1"
            onClick={() => onInteraction?.({ type: 'formula_tap', formula: f })}
          >
            {f}
          </div>
        ))}
      </div>
      
      <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          SI Unit: <span className="font-medium text-gray-700 dark:text-gray-300">{data.unit}</span>
        </p>
      </div>
    </motion.div>
  );
};

// Mechanics Layer Overlay
const MechanicsOverlay = ({ concept, onInteraction }) => {
  const [showVectors, setShowVectors] = useState(true);
  const [showGraph, setShowGraph] = useState(false);
  
  return (
    <motion.div
      className="absolute bottom-2 left-2 right-2 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-purple-200 dark:border-purple-800"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Compass className="w-5 h-5 text-purple-600" />
          <span className="font-bold text-purple-700 dark:text-purple-300">Deep Mechanics</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setShowVectors(!showVectors); onInteraction?.({ type: 'toggle_vectors' }); }}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              showVectors 
                ? 'bg-purple-500 text-white' 
                : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
            }`}
          >
            Vectors
          </button>
          <button
            onClick={() => { setShowGraph(!showGraph); onInteraction?.({ type: 'toggle_graph' }); }}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              showGraph 
                ? 'bg-purple-500 text-white' 
                : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
            }`}
          >
            Graph
          </button>
        </div>
      </div>
      
      {showGraph && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3"
        >
          <svg viewBox="0 0 200 100" className="w-full h-24">
            {/* Axes */}
            <line x1="20" y1="80" x2="180" y2="80" stroke="#666" strokeWidth="1" />
            <line x1="20" y1="80" x2="20" y2="10" stroke="#666" strokeWidth="1" />
            
            {/* Labels */}
            <text x="100" y="95" textAnchor="middle" fontSize="10" fill="#666">Time (s)</text>
            <text x="10" y="45" textAnchor="middle" fontSize="10" fill="#666" transform="rotate(-90, 10, 45)">Value</text>
            
            {/* Curve */}
            <motion.path
              d="M 20 70 Q 60 60 100 40 T 180 20"
              fill="none"
              stroke="#8B5CF6"
              strokeWidth="2"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1 }}
            />
          </svg>
        </motion.div>
      )}
    </motion.div>
  );
};

// Exam Layer Overlay
const ExamOverlay = ({ concept, onInteraction }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  
  const questions = {
    force: [
      {
        q: "If F = 10N and m = 2kg, what is acceleration?",
        options: ["2 m/s²", "5 m/s²", "20 m/s²", "0.2 m/s²"],
        correct: 1,
        explanation: "a = F/m = 10/2 = 5 m/s²"
      },
      {
        q: "Which increases acceleration more?",
        options: ["Increasing mass", "Increasing force", "Both equally", "Neither"],
        correct: 1,
        explanation: "a = F/m, so increasing F increases a"
      }
    ],
    motion: [
      {
        q: "If v = 20m/s and t = 4s, what is distance?",
        options: ["5m", "24m", "80m", "16m"],
        correct: 2,
        explanation: "d = v × t = 20 × 4 = 80m"
      }
    ],
  };
  
  const conceptQuestions = questions[concept?.toLowerCase()] || questions.force;
  const currentQ = conceptQuestions[currentQuestion];
  
  const handleAnswer = (idx) => {
    setSelectedAnswer(idx);
    setShowResult(true);
    onInteraction?.({ 
      type: 'exam_answer', 
      correct: idx === currentQ.correct,
      question: currentQuestion 
    });
  };
  
  return (
    <motion.div
      className="absolute inset-4 bg-white/98 dark:bg-gray-800/98 backdrop-blur-sm rounded-xl p-4 shadow-lg border-2 border-orange-300 dark:border-orange-700"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-orange-600" />
          <span className="font-bold text-orange-700 dark:text-orange-300">Exam Mode</span>
        </div>
        <span className="text-sm text-gray-500">
          Q{currentQuestion + 1}/{conceptQuestions.length}
        </span>
      </div>
      
      <p className="text-gray-800 dark:text-gray-200 font-medium mb-4">
        {currentQ.q}
      </p>
      
      <div className="space-y-2">
        {currentQ.options.map((option, idx) => (
          <button
            key={idx}
            onClick={() => !showResult && handleAnswer(idx)}
            disabled={showResult}
            className={`w-full p-3 text-left rounded-lg border-2 transition-all ${
              showResult
                ? idx === currentQ.correct
                  ? 'bg-green-100 dark:bg-green-900/30 border-green-500 text-green-700 dark:text-green-300'
                  : idx === selectedAnswer
                    ? 'bg-red-100 dark:bg-red-900/30 border-red-500 text-red-700 dark:text-red-300'
                    : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-500'
                : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 hover:border-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20'
            }`}
          >
            <span className="font-medium mr-2">{String.fromCharCode(65 + idx)}.</span>
            {option}
          </button>
        ))}
      </div>
      
      {showResult && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-4 p-3 rounded-lg ${
            selectedAnswer === currentQ.correct
              ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
              : 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800'
          }`}
        >
          <p className="text-sm">
            {selectedAnswer === currentQ.correct ? '✅ Correct!' : '❌ Not quite!'}{' '}
            <span className="text-gray-600 dark:text-gray-400">{currentQ.explanation}</span>
          </p>
          
          {currentQuestion < conceptQuestions.length - 1 && (
            <button
              onClick={() => {
                setCurrentQuestion(prev => prev + 1);
                setSelectedAnswer(null);
                setShowResult(false);
              }}
              className="mt-2 px-4 py-2 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600"
            >
              Next Question →
            </button>
          )}
        </motion.div>
      )}
    </motion.div>
  );
};

export { LAYER_CONFIG };
export default LayeredVisual;



