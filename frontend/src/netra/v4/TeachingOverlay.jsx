/**
 * 🔮 NETRA v4.0 - Teaching Overlay Component
 * ==========================================
 * 
 * Interactive overlay that transforms a static image into
 * a guided learning experience.
 * 
 * Features:
 * - Clickable hotspots with descriptions
 * - Step-by-step teaching flow
 * - Annotations and labels
 * - Progress tracking
 * - Narration display
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================
// HOTSPOT COMPONENT
// ============================================

const Hotspot = ({ hotspot, isActive, onClick }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <motion.div
      className="absolute cursor-pointer"
      style={{
        left: `${hotspot.x_percent}%`,
        top: `${hotspot.y_percent}%`,
        width: `${hotspot.width_percent}%`,
        height: `${hotspot.height_percent}%`,
        transform: 'translate(-50%, -50%)',
      }}
      onClick={() => onClick(hotspot)}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Hotspot indicator */}
      <motion.div
        className={`w-full h-full rounded-lg border-2 transition-colors ${
          isActive
            ? 'border-blue-500 bg-blue-500/20'
            : 'border-blue-300/50 bg-blue-500/10 hover:border-blue-400 hover:bg-blue-500/20'
        }`}
        animate={isActive ? { scale: [1, 1.05, 1] } : {}}
        transition={{ duration: 1, repeat: isActive ? Infinity : 0 }}
      />

      {/* Pulse effect for active */}
      {isActive && (
        <motion.div
          className="absolute inset-0 rounded-lg border-2 border-blue-500"
          animate={{ scale: [1, 1.3], opacity: [0.5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}

      {/* Label */}
      <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
        <span className="px-2 py-0.5 bg-gray-800 text-white text-xs rounded-full">
          {hotspot.label}
        </span>
      </div>

      {/* Tooltip */}
      <AnimatePresence>
        {showTooltip && !isActive && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 z-50"
          >
            <div className="px-3 py-2 bg-gray-900 text-white text-sm rounded-lg shadow-lg max-w-xs">
              {hotspot.description}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// ============================================
// ANNOTATION COMPONENT
// ============================================

const Annotation = ({ annotation, visible }) => {
  const styleClasses = {
    label: 'bg-gray-800 text-white',
    formula: 'bg-blue-600 text-white font-mono',
    callout: 'bg-yellow-400 text-gray-900',
    note: 'bg-green-500 text-white',
  };

  const sizeClasses = {
    small: 'text-xs px-2 py-1',
    medium: 'text-sm px-3 py-1.5',
    large: 'text-base px-4 py-2',
  };

  if (!visible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      className="absolute pointer-events-none"
      style={{
        left: `${annotation.x_percent}%`,
        top: `${annotation.y_percent}%`,
        transform: 'translate(-50%, -50%)',
      }}
    >
      <div
        className={`rounded-lg shadow-md ${styleClasses[annotation.style] || styleClasses.label} ${sizeClasses[annotation.font_size] || sizeClasses.medium}`}
      >
        {annotation.text}
      </div>
    </motion.div>
  );
};

// ============================================
// NARRATION BAR
// ============================================

const NarrationBar = ({ step, totalSteps, narration, onPrev, onNext, onClose }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: 20 }}
    className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-gray-900/95 to-gray-900/80 backdrop-blur-sm text-white p-4"
  >
    {/* Progress */}
    <div className="flex items-center gap-2 mb-3">
      {Array.from({ length: totalSteps }).map((_, i) => (
        <div
          key={i}
          className={`h-1 flex-1 rounded-full transition-colors ${
            i < step ? 'bg-blue-500' : i === step ? 'bg-blue-400' : 'bg-gray-600'
          }`}
        />
      ))}
    </div>

    {/* Content */}
    <div className="flex items-start gap-4">
      {/* Step indicator */}
      <div className="flex-shrink-0 w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center font-bold">
        {step + 1}
      </div>

      {/* Narration text */}
      <div className="flex-1 min-w-0">
        <div className="text-sm text-gray-300 mb-1">
          Step {step + 1} of {totalSteps}
        </div>
        <div className="text-base leading-relaxed">
          {narration}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <button
          onClick={onPrev}
          disabled={step === 0}
          className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          ←
        </button>
        <button
          onClick={onNext}
          disabled={step === totalSteps - 1}
          className="p-2 rounded-lg bg-blue-500 hover:bg-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          →
        </button>
        <button
          onClick={onClose}
          className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors ml-2"
        >
          ✕
        </button>
      </div>
    </div>
  </motion.div>
);

// ============================================
// MAIN TEACHING OVERLAY
// ============================================

const TeachingOverlay = ({ teaching, onStepChange, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [activeHotspot, setActiveHotspot] = useState(null);

  const steps = teaching?.steps || [];
  const hotspots = teaching?.hotspots || [];
  const annotations = teaching?.annotations || [];

  // Get current step data
  const step = steps[currentStep];
  const focusHotspotIds = step?.focus_hotspots || [];

  // Auto-advance timer
  useEffect(() => {
    if (!step?.duration_ms) return;

    const timer = setTimeout(() => {
      if (currentStep < steps.length - 1) {
        setCurrentStep((prev) => prev + 1);
      }
    }, step.duration_ms);

    return () => clearTimeout(timer);
  }, [currentStep, step]);

  // Notify parent of step change
  useEffect(() => {
    onStepChange?.(currentStep, step);
  }, [currentStep, step, onStepChange]);

  // Navigation handlers
  const handlePrev = useCallback(() => {
    setCurrentStep((prev) => Math.max(0, prev - 1));
  }, []);

  const handleNext = useCallback(() => {
    setCurrentStep((prev) => Math.min(steps.length - 1, prev + 1));
  }, [steps.length]);

  const handleHotspotClick = useCallback((hotspot) => {
    setActiveHotspot(hotspot.id === activeHotspot ? null : hotspot.id);
  }, [activeHotspot]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowLeft') handlePrev();
      if (e.key === 'ArrowRight') handleNext();
      if (e.key === 'Escape') onClose?.();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlePrev, handleNext, onClose]);

  return (
    <div className="absolute inset-0">
      {/* Semi-transparent overlay */}
      <div className="absolute inset-0 bg-black/30" />

      {/* Hotspots */}
      {hotspots.map((hotspot) => (
        <Hotspot
          key={hotspot.id}
          hotspot={hotspot}
          isActive={focusHotspotIds.includes(hotspot.id) || activeHotspot === hotspot.id}
          onClick={handleHotspotClick}
        />
      ))}

      {/* Annotations */}
      <AnimatePresence>
        {annotations.map((annotation) => (
          <Annotation
            key={annotation.id}
            annotation={annotation}
            visible={
              annotation.show_at_step === undefined ||
              annotation.show_at_step === null ||
              annotation.show_at_step <= currentStep + 1
            }
          />
        ))}
      </AnimatePresence>

      {/* Narration bar */}
      {step && (
        <NarrationBar
          step={currentStep}
          totalSteps={steps.length}
          narration={step.narration}
          onPrev={handlePrev}
          onNext={handleNext}
          onClose={onClose}
        />
      )}

      {/* Title */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="absolute top-4 left-4 right-4"
      >
        <h2 className="text-xl font-bold text-white drop-shadow-lg">
          {teaching.title}
        </h2>
        <p className="text-sm text-white/80 mt-1">
          {teaching.summary}
        </p>
      </motion.div>
    </div>
  );
};

export default TeachingOverlay;
export { TeachingOverlay, Hotspot, Annotation };

