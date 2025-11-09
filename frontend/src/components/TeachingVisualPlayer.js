/**
 * Teaching Visual Player Component
 * Renders animated, interactive teaching visuals with mentor-style narration
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';
import { Play, Pause, RotateCcw, Volume2, VolumeX, ChevronRight } from 'lucide-react';

// Import animation engine
import AnimationEngine from '../engines/AnimationEngine';
import InteractionLayer from './InteractionLayer';

export default function TeachingVisualPlayer({ visualData, onComplete, onInteraction }) {
  // State management
  const [currentStage, setCurrentStage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showInteraction, setShowInteraction] = useState(false);
  const [userResponse, setUserResponse] = useState(null);
  const [animationSpeed, setAnimationSpeed] = useState(1);

  // Refs
  const canvasRef = useRef(null);
  const engineRef = useRef(null);
  const progressInterval = useRef(null);
  const startTimeRef = useRef(null);

  // Animation controls
  const controls = useAnimation();

  // Initialize animation engine
  useEffect(() => {
    if (!visualData || !canvasRef.current) return;

    // Create animation engine instance
    engineRef.current = new AnimationEngine(canvasRef.current, {
      width: 800,
      height: 450,
      responsive: true,
      fps: 60,
      renderer: 'svg' // Can be 'canvas' or 'webgl' for performance
    });

    // Load visual data
    engineRef.current.loadVisual(visualData);

    // Set up event listeners
    engineRef.current.on('stageComplete', handleStageComplete);
    engineRef.current.on('interactionRequired', handleInteractionRequired);
    engineRef.current.on('animationComplete', handleAnimationComplete);

    return () => {
      if (engineRef.current) {
        engineRef.current.destroy();
      }
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    };
  }, [visualData]);

  // Handle stage progression
  const handleStageComplete = useCallback((stageIndex) => {
    if (stageIndex < visualData.stages.length - 1) {
      // Check if next stage has interaction
      const nextStage = visualData.stages[stageIndex + 1];
      if (nextStage.interactions && nextStage.interactions.length > 0) {
        setShowInteraction(true);
        setIsPlaying(false);
      } else {
        // Auto-progress to next stage
        setTimeout(() => {
          setCurrentStage(stageIndex + 1);
        }, 500); // Brief pause between stages
      }
    }
  }, [visualData]);

  // Handle interaction requirements
  const handleInteractionRequired = useCallback((interaction) => {
    setShowInteraction(true);
    setIsPlaying(false);

    if (onInteraction) {
      onInteraction(interaction);
    }
  }, [onInteraction]);

  // Handle animation complete
  const handleAnimationComplete = useCallback(() => {
    setIsPlaying(false);
    setProgress(100);

    if (onComplete) {
      onComplete({
        completed: true,
        userResponses: userResponse,
        totalDuration: visualData.total_duration_ms
      });
    }
  }, [onComplete, userResponse, visualData]);

  // Play/Pause control
  const togglePlayPause = useCallback(() => {
    if (!engineRef.current) return;

    if (isPlaying) {
      engineRef.current.pause();
      clearInterval(progressInterval.current);
    } else {
      engineRef.current.play();
      startProgressTracking();
    }

    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  // Start progress tracking
  const startProgressTracking = useCallback(() => {
    if (!visualData) return;

    startTimeRef.current = Date.now() - (progress * visualData.total_duration_ms / 100);

    progressInterval.current = setInterval(() => {
      const elapsed = Date.now() - startTimeRef.current;
      const newProgress = Math.min(100, (elapsed / visualData.total_duration_ms) * 100);
      setProgress(newProgress);

      if (newProgress >= 100) {
        clearInterval(progressInterval.current);
      }
    }, 100);
  }, [progress, visualData]);

  // Restart animation
  const restart = useCallback(() => {
    if (!engineRef.current) return;

    setCurrentStage(0);
    setProgress(0);
    setUserResponse(null);
    engineRef.current.restart();
    setIsPlaying(false);
  }, []);

  // Skip to next stage
  const skipToNext = useCallback(() => {
    if (currentStage < visualData.stages.length - 1) {
      setCurrentStage(currentStage + 1);
      engineRef.current.skipToStage(currentStage + 1);
    }
  }, [currentStage, visualData]);

  // Handle interaction response
  const handleInteractionResponse = useCallback((response) => {
    setUserResponse(prev => ({
      ...prev,
      [`stage_${currentStage}`]: response
    }));

    setShowInteraction(false);

    // Continue to next stage
    if (currentStage < visualData.stages.length - 1) {
      setCurrentStage(currentStage + 1);
      setIsPlaying(true);
      engineRef.current.continueFromInteraction(response);
    }
  }, [currentStage, visualData]);

  // Render loading state
  if (!visualData) {
    return (
      <div className="flex items-center justify-center h-96 bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Preparing your visual lesson...</p>
        </div>
      </div>
    );
  }

  const currentStageData = visualData.stages[currentStage];

  return (
    <div className="teaching-visual-player bg-white rounded-2xl shadow-xl overflow-hidden">
      {/* Canvas Container */}
      <div className="relative bg-gradient-to-br from-purple-50 to-blue-50">
        {/* SVG/Canvas Render Area */}
        <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full"
            style={{ background: 'transparent' }}
          />

          {/* Interaction Overlay */}
          <AnimatePresence>
            {showInteraction && currentStageData.interactions && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-10"
              >
                <InteractionLayer
                  interaction={currentStageData.interactions[0]}
                  onResponse={handleInteractionResponse}
                  stage={currentStage}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Stage Indicator */}
          <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-1.5 shadow-md">
            <span className="text-xs font-medium text-gray-600">
              Stage {currentStage + 1} of {visualData.stages.length}
            </span>
          </div>

          {/* Emphasis Indicator */}
          {currentStageData.emphasis && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="absolute bottom-4 left-4 right-4 bg-yellow-100/90 backdrop-blur-sm border border-yellow-300 rounded-lg p-3 shadow-md"
            >
              <div className="flex items-start gap-2">
                <span className="text-yellow-600 text-lg">💡</span>
                <p className="text-sm font-medium text-yellow-900">
                  {currentStageData.emphasis}
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Narration Bar */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4">
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <span className="text-xl">👨‍🏫</span>
            </div>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium leading-relaxed">
              {currentStageData.narration}
            </p>
          </div>
          <button
            onClick={() => setIsMuted(!isMuted)}
            className="flex-shrink-0 p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-gray-100 h-1 relative">
        <motion.div
          className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-600 to-indigo-600"
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3 }}
        />
        {/* Stage markers */}
        {visualData.stages.map((_, index) => {
          const position = (index / (visualData.stages.length - 1)) * 100;
          return (
            <div
              key={index}
              className={`absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-white border-2 ${
                index <= currentStage ? 'border-purple-600' : 'border-gray-300'
              }`}
              style={{ left: `${position}%`, transform: 'translateX(-50%) translateY(-50%)' }}
            />
          );
        })}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center gap-2">
          {/* Play/Pause */}
          <button
            onClick={togglePlayPause}
            className="p-3 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition-colors shadow-lg"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>

          {/* Restart */}
          <button
            onClick={restart}
            className="p-2 bg-white text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <RotateCcw className="w-5 h-5" />
          </button>

          {/* Skip */}
          {currentStage < visualData.stages.length - 1 && (
            <button
              onClick={skipToNext}
              className="p-2 bg-white text-gray-700 rounded-lg hover:bg-gray-100 transition-colors flex items-center gap-1"
            >
              <span className="text-sm">Skip</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Speed Control */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Speed:</span>
          <div className="flex items-center gap-1">
            {[0.5, 1, 1.5, 2].map((speed) => (
              <button
                key={speed}
                onClick={() => {
                  setAnimationSpeed(speed);
                  if (engineRef.current) {
                    engineRef.current.setSpeed(speed);
                  }
                }}
                className={`px-2 py-1 text-sm rounded ${
                  animationSpeed === speed
                    ? 'bg-purple-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                } transition-colors`}
              >
                {speed}x
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Debug Info (Development Only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="p-2 bg-gray-900 text-green-400 font-mono text-xs">
          <div>Stage: {currentStage + 1}/{visualData.stages.length}</div>
          <div>Progress: {progress.toFixed(1)}%</div>
          <div>Pattern: {visualData.metadata?.pattern}</div>
          <div>Complexity: {visualData.metadata?.complexity}</div>
        </div>
      )}
    </div>
  );
}