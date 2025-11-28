/**
 * TryYourselfMode.jsx
 * Phase 7: Interactive challenges with XP rewards
 * 
 * Features:
 * - Observation prompts
 * - Interactive challenges
 * - Answer validation
 * - XP rewards integration
 * - Hint system
 * - Progress tracking
 */

import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Target, Lightbulb, CheckCircle, XCircle, 
  HelpCircle, Award, Zap, ChevronRight,
  RotateCcw, Sparkles, Trophy
} from 'lucide-react';

// Challenge types
const CHALLENGE_TYPES = {
  OBSERVATION: 'observation',
  PREDICTION: 'prediction',
  CALCULATION: 'calculation',
  COMPARISON: 'comparison',
  APPLICATION: 'application',
};

// Challenge data for different concepts
const CONCEPT_CHALLENGES = {
  force: [
    {
      type: CHALLENGE_TYPES.OBSERVATION,
      prompt: "Set force = 0. What happens to the ball?",
      prompt_hi: "Force = 0 करो। गेंद को क्या होता है?",
      instruction: "Observe and answer!",
      options: [
        { id: 'a', text: "Ball stops immediately", correct: false },
        { id: 'b', text: "Ball continues moving (if already moving)", correct: true },
        { id: 'c', text: "Ball accelerates", correct: false },
        { id: 'd', text: "Ball reverses direction", correct: false },
      ],
      explanation: "Newton's First Law: An object in motion stays in motion unless acted upon by a force!",
      explanation_hi: "न्यूटन का पहला नियम: गतिशील वस्तु गतिशील रहती है जब तक बल न लगे!",
      xp: 10,
      hint: "Think about Newton's First Law of Motion",
    },
    {
      type: CHALLENGE_TYPES.PREDICTION,
      prompt: "If you double the mass, what happens to acceleration?",
      prompt_hi: "अगर mass दोगुना करो, acceleration को क्या होगा?",
      instruction: "Use F = ma to predict!",
      options: [
        { id: 'a', text: "Doubles", correct: false },
        { id: 'b', text: "Halves", correct: true },
        { id: 'c', text: "Stays same", correct: false },
        { id: 'd', text: "Becomes zero", correct: false },
      ],
      explanation: "a = F/m. If m doubles, a becomes half (with same force)!",
      explanation_hi: "a = F/m। अगर m दोगुना, तो a आधा हो जाता है!",
      xp: 15,
      hint: "Rearrange F = ma to find acceleration",
    },
    {
      type: CHALLENGE_TYPES.CALCULATION,
      prompt: "F = 20N, m = 4kg. Find acceleration.",
      prompt_hi: "F = 20N, m = 4kg। Acceleration निकालो।",
      instruction: "Calculate using F = ma",
      options: [
        { id: 'a', text: "80 m/s²", correct: false },
        { id: 'b', text: "5 m/s²", correct: true },
        { id: 'c', text: "16 m/s²", correct: false },
        { id: 'd', text: "0.2 m/s²", correct: false },
      ],
      explanation: "a = F/m = 20/4 = 5 m/s²",
      explanation_hi: "a = F/m = 20/4 = 5 m/s²",
      xp: 20,
      hint: "a = F ÷ m",
    },
  ],
  
  motion: [
    {
      type: CHALLENGE_TYPES.OBSERVATION,
      prompt: "Increase velocity. What happens to distance covered?",
      prompt_hi: "Velocity बढ़ाओ। Distance को क्या होता है?",
      instruction: "Observe the simulation!",
      options: [
        { id: 'a', text: "Decreases", correct: false },
        { id: 'b', text: "Increases", correct: true },
        { id: 'c', text: "Stays same", correct: false },
        { id: 'd', text: "Becomes zero", correct: false },
      ],
      explanation: "Distance = Velocity × Time. More velocity = more distance!",
      explanation_hi: "Distance = Velocity × Time। ज़्यादा velocity = ज़्यादा distance!",
      xp: 10,
      hint: "Think about the formula d = v × t",
    },
    {
      type: CHALLENGE_TYPES.CALCULATION,
      prompt: "v = 15 m/s, t = 4s. Find distance.",
      prompt_hi: "v = 15 m/s, t = 4s। Distance निकालो।",
      instruction: "Use d = v × t",
      options: [
        { id: 'a', text: "60 m", correct: true },
        { id: 'b', text: "19 m", correct: false },
        { id: 'c', text: "3.75 m", correct: false },
        { id: 'd', text: "11 m", correct: false },
      ],
      explanation: "d = v × t = 15 × 4 = 60 m",
      xp: 15,
      hint: "Multiply velocity by time",
    },
  ],
  
  gravity: [
    {
      type: CHALLENGE_TYPES.PREDICTION,
      prompt: "Drop a feather and a ball in vacuum. Which falls faster?",
      prompt_hi: "Vacuum में पंख और गेंद गिराओ। कौन तेज़ गिरेगा?",
      instruction: "Think about gravity!",
      options: [
        { id: 'a', text: "Ball (heavier)", correct: false },
        { id: 'b', text: "Feather (lighter)", correct: false },
        { id: 'c', text: "Both fall at same rate", correct: true },
        { id: 'd', text: "Neither falls", correct: false },
      ],
      explanation: "In vacuum, all objects fall at the same rate regardless of mass! g = 9.8 m/s² for all.",
      explanation_hi: "Vacuum में सब एक ही speed से गिरते हैं! g = 9.8 m/s² सबके लिए।",
      xp: 15,
      hint: "Galileo's famous experiment from Pisa tower!",
    },
  ],
  
  photosynthesis: [
    {
      type: CHALLENGE_TYPES.OBSERVATION,
      prompt: "Increase light intensity. What happens to oxygen production?",
      prompt_hi: "Light बढ़ाओ। Oxygen production को क्या होता है?",
      instruction: "Watch the bubbles!",
      options: [
        { id: 'a', text: "Decreases", correct: false },
        { id: 'b', text: "Increases (up to a point)", correct: true },
        { id: 'c', text: "No change", correct: false },
        { id: 'd', text: "Stops completely", correct: false },
      ],
      explanation: "More light = more photosynthesis = more O₂! But only up to saturation point.",
      explanation_hi: "ज़्यादा light = ज़्यादा photosynthesis = ज़्यादा O₂! पर एक limit तक।",
      xp: 15,
      hint: "Light is a reactant in photosynthesis",
    },
  ],
  
  quadratic: [
    {
      type: CHALLENGE_TYPES.PREDICTION,
      prompt: "If a > 0, which way does the parabola open?",
      prompt_hi: "अगर a > 0, parabola किस तरफ खुलेगा?",
      instruction: "Change 'a' and observe!",
      options: [
        { id: 'a', text: "Upward (∪)", correct: true },
        { id: 'b', text: "Downward (∩)", correct: false },
        { id: 'c', text: "Sideways", correct: false },
        { id: 'd', text: "No curve", correct: false },
      ],
      explanation: "When a > 0, parabola opens upward. When a < 0, it opens downward!",
      explanation_hi: "जब a > 0, parabola ऊपर खुलता है। जब a < 0, नीचे खुलता है!",
      xp: 10,
      hint: "The sign of 'a' determines the direction",
    },
  ],
};

// Default challenges for unknown concepts
const DEFAULT_CHALLENGES = [
  {
    type: CHALLENGE_TYPES.OBSERVATION,
    prompt: "Observe the visual and note what changes",
    prompt_hi: "Visual देखो और बदलाव नोट करो",
    instruction: "Interact with the sliders!",
    options: [
      { id: 'a', text: "Values increase", correct: true },
      { id: 'b', text: "Values decrease", correct: false },
      { id: 'c', text: "No change", correct: false },
      { id: 'd', text: "Random changes", correct: false },
    ],
    explanation: "Great observation! Keep experimenting.",
    xp: 5,
  },
];

const TryYourselfMode = ({
  concept,
  onComplete,
  onXPEarned,
  currentValues = {},
  onValueChange,
  showHinglish = true,
  gamificationEnabled = true,
}) => {
  const [currentChallengeIndex, setCurrentChallengeIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [totalXP, setTotalXP] = useState(0);
  const [completedChallenges, setCompletedChallenges] = useState([]);
  const [streak, setStreak] = useState(0);

  // Get challenges for current concept
  const challenges = CONCEPT_CHALLENGES[concept?.toLowerCase()] || DEFAULT_CHALLENGES;
  const currentChallenge = challenges[currentChallengeIndex];

  // Handle answer selection
  const handleAnswer = useCallback((optionId) => {
    if (showResult) return;
    
    setSelectedAnswer(optionId);
    setShowResult(true);
    
    const isCorrect = currentChallenge.options.find(o => o.id === optionId)?.correct;
    
    if (isCorrect) {
      const xpEarned = currentChallenge.xp * (streak >= 3 ? 1.5 : 1); // Streak bonus
      setTotalXP(prev => prev + xpEarned);
      setStreak(prev => prev + 1);
      setCompletedChallenges(prev => [...prev, currentChallengeIndex]);
      
      if (gamificationEnabled) {
        onXPEarned?.({
          amount: xpEarned,
          reason: 'challenge_correct',
          streak: streak + 1,
        });
      }
    } else {
      setStreak(0);
    }
  }, [currentChallenge, showResult, streak, gamificationEnabled, onXPEarned, currentChallengeIndex]);

  // Move to next challenge
  const nextChallenge = useCallback(() => {
    if (currentChallengeIndex < challenges.length - 1) {
      setCurrentChallengeIndex(prev => prev + 1);
      setSelectedAnswer(null);
      setShowResult(false);
      setShowHint(false);
    } else {
      // All challenges completed
      onComplete?.({
        totalXP,
        completed: completedChallenges.length,
        total: challenges.length,
        accuracy: (completedChallenges.length / challenges.length) * 100,
      });
    }
  }, [currentChallengeIndex, challenges.length, totalXP, completedChallenges, onComplete]);

  // Reset current challenge
  const resetChallenge = useCallback(() => {
    setSelectedAnswer(null);
    setShowResult(false);
    setShowHint(false);
  }, []);

  // Get option style based on state
  const getOptionStyle = (option) => {
    if (!showResult) {
      return selectedAnswer === option.id
        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
        : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/20';
    }
    
    if (option.correct) {
      return 'border-green-500 bg-green-50 dark:bg-green-900/30';
    }
    
    if (selectedAnswer === option.id && !option.correct) {
      return 'border-red-500 bg-red-50 dark:bg-red-900/30';
    }
    
    return 'border-gray-200 dark:border-gray-700 opacity-50';
  };

  return (
    <motion.div
      className="bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-800 dark:to-gray-900 rounded-xl border-2 border-orange-200 dark:border-orange-800 overflow-hidden"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-orange-100 to-yellow-100 dark:from-orange-900/30 dark:to-yellow-900/30 border-b border-orange-200 dark:border-orange-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-orange-600 dark:text-orange-400" />
            <h3 className="font-bold text-orange-800 dark:text-orange-200">
              🎯 Try Yourself!
            </h3>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Streak indicator */}
            {streak > 0 && (
              <motion.div
                className="flex items-center gap-1 px-2 py-1 bg-orange-500 text-white rounded-full text-xs font-bold"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
              >
                <Zap className="w-3 h-3" />
                {streak} streak!
              </motion.div>
            )}
            
            {/* XP counter */}
            {gamificationEnabled && (
              <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <span className="text-sm font-bold text-purple-700 dark:text-purple-300">
                  {totalXP} XP
                </span>
              </div>
            )}
            
            {/* Progress */}
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {currentChallengeIndex + 1}/{challenges.length}
            </span>
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="mt-2 h-1.5 bg-orange-200 dark:bg-orange-900 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-orange-500"
            initial={{ width: 0 }}
            animate={{ width: `${((currentChallengeIndex + (showResult ? 1 : 0)) / challenges.length) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Challenge Content */}
      <div className="p-4">
        {/* Challenge Type Badge */}
        <div className="flex items-center gap-2 mb-3">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
            currentChallenge.type === CHALLENGE_TYPES.OBSERVATION ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' :
            currentChallenge.type === CHALLENGE_TYPES.PREDICTION ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' :
            currentChallenge.type === CHALLENGE_TYPES.CALCULATION ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
            'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
          }`}>
            {currentChallenge.type.charAt(0).toUpperCase() + currentChallenge.type.slice(1)}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            +{currentChallenge.xp} XP
          </span>
        </div>

        {/* Question */}
        <div className="mb-4">
          <p className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            {currentChallenge.prompt}
          </p>
          {showHinglish && currentChallenge.prompt_hi && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {currentChallenge.prompt_hi}
            </p>
          )}
          <p className="text-sm text-orange-600 dark:text-orange-400 mt-2 flex items-center gap-1">
            <Lightbulb className="w-4 h-4" />
            {currentChallenge.instruction}
          </p>
        </div>

        {/* Options */}
        <div className="space-y-2 mb-4">
          {currentChallenge.options.map((option, idx) => (
            <motion.button
              key={option.id}
              onClick={() => handleAnswer(option.id)}
              disabled={showResult}
              className={`w-full p-3 text-left rounded-lg border-2 transition-all ${getOptionStyle(option)}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              whileHover={!showResult ? { scale: 1.01 } : {}}
              whileTap={!showResult ? { scale: 0.99 } : {}}
            >
              <div className="flex items-center gap-3">
                <span className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold ${
                  showResult && option.correct ? 'bg-green-500 text-white' :
                  showResult && selectedAnswer === option.id && !option.correct ? 'bg-red-500 text-white' :
                  selectedAnswer === option.id ? 'bg-indigo-500 text-white' :
                  'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                }`}>
                  {showResult && option.correct ? <CheckCircle className="w-4 h-4" /> :
                   showResult && selectedAnswer === option.id && !option.correct ? <XCircle className="w-4 h-4" /> :
                   option.id.toUpperCase()}
                </span>
                <span className={`flex-1 ${
                  showResult && option.correct ? 'text-green-700 dark:text-green-300 font-medium' :
                  showResult && selectedAnswer === option.id && !option.correct ? 'text-red-700 dark:text-red-300' :
                  'text-gray-700 dark:text-gray-300'
                }`}>
                  {option.text}
                </span>
              </div>
            </motion.button>
          ))}
        </div>

        {/* Hint Button */}
        {!showResult && currentChallenge.hint && (
          <button
            onClick={() => setShowHint(!showHint)}
            className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 hover:text-orange-600 dark:hover:text-orange-400 transition-colors"
          >
            <HelpCircle className="w-4 h-4" />
            {showHint ? 'Hide Hint' : 'Need a Hint?'}
          </button>
        )}

        {/* Hint Display */}
        <AnimatePresence>
          {showHint && !showResult && (
            <motion.div
              className="mt-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                💡 <strong>Hint:</strong> {currentChallenge.hint}
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Result Display */}
        <AnimatePresence>
          {showResult && (
            <motion.div
              className={`mt-4 p-4 rounded-lg border ${
                currentChallenge.options.find(o => o.id === selectedAnswer)?.correct
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                  : 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800'
              }`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-start gap-3">
                {currentChallenge.options.find(o => o.id === selectedAnswer)?.correct ? (
                  <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                    <Trophy className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </div>
                ) : (
                  <div className="w-10 h-10 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                    <Lightbulb className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                  </div>
                )}
                <div className="flex-1">
                  <p className={`font-bold ${
                    currentChallenge.options.find(o => o.id === selectedAnswer)?.correct
                      ? 'text-green-700 dark:text-green-300'
                      : 'text-orange-700 dark:text-orange-300'
                  }`}>
                    {currentChallenge.options.find(o => o.id === selectedAnswer)?.correct
                      ? '🎉 Correct! Well done!'
                      : '❌ Not quite! Keep learning!'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {currentChallenge.explanation}
                  </p>
                  {showHinglish && currentChallenge.explanation_hi && (
                    <p className="text-sm text-gray-500 dark:text-gray-500 mt-1 italic">
                      {currentChallenge.explanation_hi}
                    </p>
                  )}
                  
                  {/* XP Earned */}
                  {currentChallenge.options.find(o => o.id === selectedAnswer)?.correct && gamificationEnabled && (
                    <motion.div
                      className="mt-2 flex items-center gap-2"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                    >
                      <Award className="w-4 h-4 text-purple-500" />
                      <span className="text-sm font-bold text-purple-600 dark:text-purple-400">
                        +{currentChallenge.xp * (streak >= 3 ? 1.5 : 1)} XP earned!
                        {streak >= 3 && ' (Streak bonus!)'}
                      </span>
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action Buttons */}
        <div className="mt-4 flex gap-2">
          {showResult ? (
            <motion.button
              onClick={nextChallenge}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {currentChallengeIndex < challenges.length - 1 ? (
                <>
                  Next Challenge
                  <ChevronRight className="w-5 h-5" />
                </>
              ) : (
                <>
                  <Trophy className="w-5 h-5" />
                  Complete!
                </>
              )}
            </motion.button>
          ) : (
            <button
              onClick={resetChallenge}
              className="px-4 py-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 flex items-center gap-1"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default TryYourselfMode;



