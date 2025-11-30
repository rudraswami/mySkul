/**
 * 🚀 CONFIG-DRIVEN SKETCH ENGINE V4.0
 * ====================================
 * 
 * THE ULTIMATE VISUAL ENGINE
 * 
 * This component can render ANY STEM concept using:
 * - 8 template types (race, process, cycle, graph, structure, cause-effect, scale, timeline)
 * - 15+ reusable primitives
 * - Backend configuration for 170+ concepts
 * - Progressive animation system
 * - Indian context & memory hooks
 * 
 * Architecture:
 * Backend sends blueprint → Frontend renders dynamically
 * 
 * No more hardcoding! Every concept uses the template system.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';

// Import all templates
import {
  RaceTemplate,
  ProcessTemplate,
  CycleTemplate,
  GraphTemplate,
  StructureTemplate,
  CauseEffectTemplate,
  ScaleTemplate,
  TimelineTemplate,
  TEMPLATE_TYPES,
} from '../templates';

// Import primitives
import { COLORS, SUBJECT_THEMES } from '../primitives';

// Template mapping
const TEMPLATE_MAP = {
  [TEMPLATE_TYPES.RACE]: RaceTemplate,
  [TEMPLATE_TYPES.PROCESS]: ProcessTemplate,
  [TEMPLATE_TYPES.CYCLE]: CycleTemplate,
  [TEMPLATE_TYPES.GRAPH]: GraphTemplate,
  [TEMPLATE_TYPES.STRUCTURE]: StructureTemplate,
  [TEMPLATE_TYPES.CAUSE_EFFECT]: CauseEffectTemplate,
  [TEMPLATE_TYPES.SCALE]: ScaleTemplate,
  [TEMPLATE_TYPES.TIMELINE]: TimelineTemplate,
  // Aliases for flexibility
  'race_comparison': RaceTemplate,
  'process_flow': ProcessTemplate,
  'cycle': CycleTemplate,
  'graph_relationship': GraphTemplate,
  'structure_anatomy': StructureTemplate,
  'cause_effect': CauseEffectTemplate,
  'scale_spectrum': ScaleTemplate,
  'sequence_timeline': TimelineTemplate,
};

// Fallback configs for common concepts
const FALLBACK_CONFIGS = {
  velocity: {
    template: 'race_comparison',
    subject: 'physics',
    title: 'Velocity Race',
    title_hindi: 'वेग दौड़',
    config: {
      object_a: { type: 'auto_rickshaw', label: 'FAST', color: '#FF9933', speed: 20 },
      object_b: { type: 'auto_rickshaw', label: 'SLOW', color: '#3B82F6', speed: 10 },
      track_length: 100,
      formula: 'v = d / t',
      memory_hook: 'More distance in same time = More velocity! 🚀',
    },
  },
  force: {
    template: 'race_comparison',
    subject: 'physics',
    title: 'Force & Acceleration',
    title_hindi: 'बल और त्वरण',
    config: {
      object_a: { type: 'ball', label: 'LIGHT (1kg)', color: '#10B981', speed: 20 },
      object_b: { type: 'ball', label: 'HEAVY (5kg)', color: '#EF4444', speed: 5 },
      track_length: 100,
      formula: 'F = ma',
      memory_hook: 'Same force, less mass = More acceleration! 🏏',
    },
  },
  photosynthesis: {
    template: 'process_flow',
    subject: 'biology',
    title: 'Photosynthesis',
    title_hindi: 'प्रकाश संश्लेषण',
    config: {
      inputs: [
        { name: 'Sunlight', emoji: '☀️', color: '#FCD34D' },
        { name: 'Water', emoji: '💧', color: '#3B82F6' },
        { name: 'CO₂', emoji: '💨', color: '#6B7280' },
      ],
      process: { name: 'Chloroplast', emoji: '🌿', color: '#22C55E' },
      outputs: [
        { name: 'Glucose', emoji: '🍬', color: '#F59E0B' },
        { name: 'Oxygen', emoji: '💨', color: '#06B6D4' },
      ],
      formula: '6CO₂ + 6H₂O + Light → C₆H₁₂O₆ + 6O₂',
      memory_hook: 'Plants are food factories! ☀️ + 💧 + 💨 = 🍬 + O₂',
    },
  },
  cell: {
    template: 'structure_anatomy',
    subject: 'biology',
    title: 'Cell Structure',
    title_hindi: 'कोशिका संरचना',
    config: {
      components: [
        { name: 'Nucleus', x: 0, y: 0, size: 40, color: '#8B5CF6', emoji: '🟣', description: 'Control center' },
        { name: 'Mitochondria', x: -60, y: -30, size: 22, color: '#EF4444', emoji: '🔴', description: 'Powerhouse' },
        { name: 'Ribosome', x: 50, y: 40, size: 15, color: '#3B82F6', emoji: '🔵', description: 'Protein maker' },
        { name: 'ER', x: 40, y: -40, size: 25, color: '#10B981', emoji: '🟢', description: 'Transport' },
      ],
      memory_hook: 'Each part has a special job! 🏭',
    },
  },
  ph_scale: {
    template: 'scale_spectrum',
    subject: 'chemistry',
    title: 'pH Scale',
    title_hindi: 'pH स्केल',
    config: {
      min: 0,
      max: 14,
      current_value: 7,
      markers: [
        { value: 0, label: 'Strong Acid', emoji: '🍋', color: '#EF4444' },
        { value: 7, label: 'Neutral', emoji: '💧', color: '#10B981' },
        { value: 14, label: 'Strong Base', emoji: '🧼', color: '#3B82F6' },
      ],
      memory_hook: 'pH 7 is neutral, below = acid, above = base! 📏',
    },
  },
  water_cycle: {
    template: 'cycle',
    subject: 'biology',
    title: 'Water Cycle',
    title_hindi: 'जल चक्र',
    config: {
      steps: [
        { name: 'Evaporation', emoji: '☀️', color: '#F59E0B', description: 'Water → Vapor' },
        { name: 'Condensation', emoji: '☁️', color: '#6B7280', description: 'Vapor → Clouds' },
        { name: 'Precipitation', emoji: '🌧️', color: '#3B82F6', description: 'Rain/Snow' },
        { name: 'Collection', emoji: '🌊', color: '#06B6D4', description: 'Rivers/Oceans' },
      ],
      center_label: 'WATER',
      memory_hook: 'Round and round the water goes! 💧',
    },
  },
};

const ConfigDrivenSketch = ({
  blueprint = null, // Full blueprint from backend
  concept = 'velocity', // Fallback concept name
  subject = 'physics',
  question = '',
  onComplete,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const totalSteps = 5;

  // Determine configuration
  const getConfig = useCallback(() => {
    // Priority 1: Use blueprint from backend
    if (blueprint && blueprint.template) {
      return blueprint;
    }
    
    // Priority 2: Use fallback config for known concepts
    const conceptKey = concept?.toLowerCase().replace(/\s+/g, '_');
    if (FALLBACK_CONFIGS[conceptKey]) {
      return FALLBACK_CONFIGS[conceptKey];
    }
    
    // Priority 3: Default velocity race
    return FALLBACK_CONFIGS.velocity;
  }, [blueprint, concept]);

  const config = getConfig();
  const templateType = config.template || 'race_comparison';
  const TemplateComponent = TEMPLATE_MAP[templateType] || RaceTemplate;
  const theme = SUBJECT_THEMES[config.subject || subject] || SUBJECT_THEMES.physics;

  // Auto-advance steps
  useEffect(() => {
    if (!isPlaying || currentStep >= totalSteps) return;
    
    const durations = [1500, 2500, 3000, 2500, 2000];
    const timer = setTimeout(() => {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }, durations[currentStep] || 2000);
    
    return () => clearTimeout(timer);
  }, [currentStep, isPlaying, totalSteps]);

  // Handle replay
  const handleReplay = useCallback(() => {
    setCurrentStep(0);
    setIsPlaying(true);
  }, []);

  // Get title with Hindi
  const title = config.title || concept;
  const titleHindi = config.title_hindi || '';

  return (
    <div className="config-driven-sketch rounded-2xl overflow-hidden shadow-2xl border-2" style={{ borderColor: theme.primary }}>
      {/* Header */}
      <div 
        className="px-5 py-3 flex items-center justify-between"
        style={{ background: `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})` }}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">🎬</span>
          <div>
            <span className="font-bold text-white text-lg">Watch & Learn</span>
            {titleHindi && (
              <span className="ml-2 text-white/80 text-sm">({titleHindi})</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-white/30 backdrop-blur-sm px-4 py-1.5 rounded-full text-white text-sm font-bold capitalize">
            {config.subject || subject}
          </span>
          <button
            onClick={handleReplay}
            className="p-2 bg-white/30 rounded-full hover:bg-white/50 transition-all"
            title="Replay"
          >
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Main Canvas */}
      <svg
        viewBox="0 0 500 420"
        className="w-full"
        style={{ 
          minHeight: '420px',
          background: `linear-gradient(180deg, ${theme.background || COLORS.paper} 0%, #FEF3C7 100%)`
        }}
      >
        {/* Background grid */}
        <defs>
          <pattern id="sketchPaper" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke={COLORS.paperLines} strokeWidth="0.5" opacity="0.5"/>
          </pattern>
        </defs>
        <rect width="500" height="420" fill="url(#sketchPaper)"/>
        
        {/* Dynamic Template */}
        <TemplateComponent 
          config={config.config || {}} 
          step={currentStep}
          subject={config.subject || subject}
        />
      </svg>

      {/* Footer */}
      <div 
        className="px-5 py-2.5 flex items-center justify-between border-t"
        style={{ 
          background: `linear-gradient(90deg, ${theme.background}, white)`,
          borderColor: theme.primary + '40'
        }}
      >
        <div className="flex items-center gap-2">
          {currentStep >= totalSteps ? (
            <motion.div 
              initial={{ scale: 0 }} 
              animate={{ scale: 1 }} 
              className="flex items-center gap-2"
              style={{ color: theme.primary }}
            >
              <span className="text-lg">✅</span>
              <span className="font-medium text-sm">Complete!</span>
            </motion.div>
          ) : (
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: theme.primary }} />
              <span className="text-sm" style={{ color: theme.primary }}>Playing...</span>
            </div>
          )}
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleReplay}
          className="px-4 py-1.5 text-white text-sm font-medium rounded-full transition-all flex items-center gap-1.5 shadow-md"
          style={{ backgroundColor: theme.primary }}
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Replay
        </motion.button>
      </div>
    </div>
  );
};

export default ConfigDrivenSketch;

