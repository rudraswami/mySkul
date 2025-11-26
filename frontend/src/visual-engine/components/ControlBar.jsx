/**
 * ControlBar - Animation playback controls
 * Play, Pause, Restart, Step navigation
 */

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  ChevronLeft, 
  ChevronRight,
  Maximize2
} from 'lucide-react';

const ControlBar = ({
  isPlaying,
  onPlay,
  onPause,
  onRestart,
  onNextStep,
  onPrevStep,
  hasSteps,
  currentStep,
  totalSteps,
  onFullscreen,
}) => {
  return (
    <motion.div
      className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <div className="flex items-center justify-between max-w-md mx-auto">
        {/* Step navigation (left) */}
        {hasSteps ? (
          <div className="flex items-center gap-2">
            <ControlButton
              onClick={onPrevStep}
              disabled={currentStep === 0}
              title="Previous Step"
            >
              <ChevronLeft className="w-5 h-5" />
            </ControlButton>
            
            <span className="text-white text-sm font-medium px-3">
              Step {currentStep + 1} / {totalSteps}
            </span>
            
            <ControlButton
              onClick={onNextStep}
              disabled={currentStep >= totalSteps - 1}
              title="Next Step"
            >
              <ChevronRight className="w-5 h-5" />
            </ControlButton>
          </div>
        ) : (
          <div /> // Spacer
        )}

        {/* Playback controls (center) */}
        <div className="flex items-center gap-3">
          <ControlButton onClick={onRestart} title="Restart">
            <RotateCcw className="w-5 h-5" />
          </ControlButton>
          
          <ControlButton
            onClick={isPlaying ? onPause : onPlay}
            primary
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? (
              <Pause className="w-6 h-6" />
            ) : (
              <Play className="w-6 h-6 ml-0.5" />
            )}
          </ControlButton>
        </div>

        {/* Fullscreen (right) */}
        <div className="flex items-center gap-2">
          {onFullscreen && (
            <ControlButton onClick={onFullscreen} title="Fullscreen">
              <Maximize2 className="w-5 h-5" />
            </ControlButton>
          )}
        </div>
      </div>

      {/* Progress bar */}
      {hasSteps && (
        <div className="mt-3 max-w-md mx-auto">
          <div className="h-1 bg-white/20 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-orange-400 to-orange-600"
              initial={{ width: 0 }}
              animate={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      )}
    </motion.div>
  );
};

const ControlButton = ({ 
  children, 
  onClick, 
  disabled, 
  primary, 
  title 
}) => (
  <motion.button
    onClick={onClick}
    disabled={disabled}
    title={title}
    className={`
      flex items-center justify-center rounded-full transition-all
      ${primary 
        ? 'w-14 h-14 bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-lg shadow-orange-500/30' 
        : 'w-10 h-10 bg-white/10 text-white hover:bg-white/20'
      }
      ${disabled ? 'opacity-40 cursor-not-allowed' : 'hover:scale-105'}
    `}
    whileTap={{ scale: 0.95 }}
  >
    {children}
  </motion.button>
);

export default ControlBar;


