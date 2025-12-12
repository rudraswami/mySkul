/**
 * Interactive Controls Component (SketchSense V5.0)
 * ==================================================
 * 
 * Bottom Control Deck for visual simulations.
 * Renders sliders, toggles, selectors with real-time updates.
 * 
 * Features:
 * - Sketch-style typography (Patrick Hand font)
 * - Purple track sliders with orange thumbs
 * - Glassmorphic control deck
 * - Hinglish labels for Indian students
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sliders, ToggleLeft, ToggleRight, Play, RotateCcw, Sparkles } from 'lucide-react';

// Sketch font style
const fontSketchStyle = {
  fontFamily: "'Patrick Hand', 'Comic Sans MS', 'Segoe Print', cursive",
  letterSpacing: '0.02em',
};

// SketchSense color palette
const SKETCH_COLORS = {
  purple: '#7c3aed',
  purpleLight: '#a78bfa',
  orange: '#f97316',
  orangeLight: '#fdba74',
  yellow: '#fde047',
  gridColor: '#cbd5e1',
};

export default function InteractiveControls({
  controls,
  values,
  onChange,
  showHinglish = true
}) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!controls) return null;

  const hasControls = 
    (controls.sliders && controls.sliders.length > 0) ||
    (controls.toggles && controls.toggles.length > 0) ||
    (controls.selectors && controls.selectors.length > 0) ||
    (controls.buttons && controls.buttons.length > 0);

  if (!hasControls) return null;

  return (
    <motion.div
      className="rounded-t-2xl overflow-hidden"
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(12px)',
        borderTop: `2px solid ${SKETCH_COLORS.gridColor}`,
        boxShadow: '0 -4px 20px rgba(0,0,0,0.08)',
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
    >
      {/* Header - Sketch Style */}
      <div
        className="px-4 py-3 flex items-center justify-between cursor-pointer"
        style={{
          background: `linear-gradient(135deg, ${SKETCH_COLORS.purpleLight}30 0%, ${SKETCH_COLORS.orangeLight}20 100%)`,
          borderBottom: `1px dashed ${SKETCH_COLORS.gridColor}`,
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5" style={{ color: SKETCH_COLORS.purple }} />
          <span style={{ ...fontSketchStyle, fontWeight: '600', color: '#374151' }}>
            🎛️ Controls
          </span>
          {showHinglish && (
            <span 
              className="text-sm px-2 py-0.5 rounded-full"
              style={{ 
                ...fontSketchStyle,
                backgroundColor: SKETCH_COLORS.yellow,
                color: '#92400e',
              }}
            >
              Experiment Karo!
            </span>
          )}
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
          style={{ color: SKETCH_COLORS.purple }}
        >
          ▼
        </motion.div>
      </div>

      {/* Controls Body - Control Deck Layout */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="p-4"
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '24px',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Sliders - Sketch Style with Purple Track & Orange Thumb */}
            {controls.sliders && controls.sliders.map((slider) => {
              const currentValue = values[slider.id] !== undefined ? values[slider.id] : slider.default;
              const percentage = ((currentValue - slider.min) / (slider.max - slider.min)) * 100;
              
              return (
                <div key={slider.id} className="flex-1 min-w-[200px] max-w-[300px] space-y-2">
                  <div className="flex items-center justify-between">
                    <label 
                      className="text-sm"
                      style={{ ...fontSketchStyle, fontWeight: '500', color: '#374151' }}
                    >
                      {showHinglish && slider.label_hinglish ? slider.label_hinglish : slider.label}
                    </label>
                    <span 
                      className="text-lg font-bold"
                      style={{ ...fontSketchStyle, color: SKETCH_COLORS.purple }}
                    >
                      {currentValue}
                      <span className="text-sm text-gray-500 ml-1">{slider.unit}</span>
                    </span>
                  </div>
                  
                  {/* Custom Slider - Purple Track, Orange Thumb */}
                  <div className="relative">
                    <input
                      type="range"
                      min={slider.min}
                      max={slider.max}
                      step={slider.step || 1}
                      value={currentValue}
                      onChange={(e) => onChange(slider.id, parseFloat(e.target.value))}
                      className="w-full h-3 rounded-full appearance-none cursor-pointer"
                      style={{
                        background: `linear-gradient(to right, ${SKETCH_COLORS.purple} 0%, ${SKETCH_COLORS.purple} ${percentage}%, ${SKETCH_COLORS.gridColor} ${percentage}%, ${SKETCH_COLORS.gridColor} 100%)`,
                        outline: 'none',
                      }}
                    />
                    {/* Custom styles injected */}
                    <style>{`
                      input[type="range"]::-webkit-slider-thumb {
                        -webkit-appearance: none;
                        width: 20px;
                        height: 20px;
                        border-radius: 50%;
                        background: ${SKETCH_COLORS.orange};
                        border: 3px solid white;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                        cursor: pointer;
                        transition: transform 0.15s ease;
                      }
                      input[type="range"]::-webkit-slider-thumb:hover {
                        transform: scale(1.15);
                      }
                      input[type="range"]::-moz-range-thumb {
                        width: 20px;
                        height: 20px;
                        border-radius: 50%;
                        background: ${SKETCH_COLORS.orange};
                        border: 3px solid white;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                        cursor: pointer;
                      }
                    `}</style>
                  </div>
                  
                  <div 
                    className="flex justify-between text-xs"
                    style={{ ...fontSketchStyle, color: '#9CA3AF' }}
                  >
                    <span>{slider.min}{slider.unit}</span>
                    <span>{slider.max}{slider.unit}</span>
                  </div>
                </div>
              );
            })}

            {/* Selectors/Dropdowns - Sketch Style */}
            {controls.selectors && controls.selectors.map((selector) => (
              <div key={selector.id} className="flex-1 min-w-[150px] max-w-[200px] space-y-2">
                <label 
                  className="text-sm"
                  style={{ ...fontSketchStyle, fontWeight: '500', color: '#374151' }}
                >
                  {showHinglish && selector.label_hinglish ? selector.label_hinglish : selector.label}
                </label>
                
                <select
                  value={values[selector.id] || selector.default}
                  onChange={(e) => onChange(selector.id, e.target.value)}
                  className="w-full px-3 py-2 rounded-lg focus:outline-none text-sm bg-white"
                  style={{
                    ...fontSketchStyle,
                    border: `2px solid ${SKETCH_COLORS.gridColor}`,
                    fontWeight: '500',
                  }}
                >
                  {selector.options.map((option) => (
                    <option
                      key={typeof option === 'object' ? option.value : option}
                      value={typeof option === 'object' ? option.value : option}
                    >
                      {typeof option === 'object' ? option.label : option}
                    </option>
                  ))}
                </select>
              </div>
            ))}

            {/* Toggles - Sketch Style */}
            {controls.toggles && controls.toggles.map((toggle) => {
              const isOn = values[toggle.id] !== undefined ? values[toggle.id] : toggle.default;
              return (
                <div key={toggle.id} className="flex items-center gap-3">
                  <label 
                    className="text-sm"
                    style={{ ...fontSketchStyle, fontWeight: '500', color: '#374151' }}
                  >
                    {showHinglish && toggle.label_hinglish ? toggle.label_hinglish : toggle.label}
                  </label>
                  
                  <button
                    onClick={() => onChange(toggle.id, !isOn)}
                    className="relative inline-flex h-7 w-12 items-center rounded-full transition-colors"
                    style={{
                      backgroundColor: isOn ? SKETCH_COLORS.purple : SKETCH_COLORS.gridColor,
                    }}
                  >
                    <motion.span
                      className="inline-block h-5 w-5 transform rounded-full shadow-md"
                      style={{
                        backgroundColor: isOn ? SKETCH_COLORS.orange : 'white',
                      }}
                      animate={{ x: isOn ? 26 : 4 }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  </button>
                </div>
              );
            })}

            {/* Buttons - Sketch Style */}
            {controls.buttons && controls.buttons.map((button) => (
              <button
                key={button.id}
                onClick={() => onChange(button.id, true)}
                className="px-5 py-2 rounded-lg shadow-md transition-all duration-200 transform hover:scale-105 active:scale-95"
                style={{
                  ...fontSketchStyle,
                  background: `linear-gradient(135deg, ${SKETCH_COLORS.purple} 0%, ${SKETCH_COLORS.purpleLight} 100%)`,
                  color: 'white',
                  fontWeight: '600',
                  border: 'none',
                }}
              >
                <Sparkles className="w-4 h-4 inline mr-1" />
                {showHinglish && button.label_hinglish ? button.label_hinglish : button.label}
              </button>
            ))}

            {/* Hint Text - Sketch Style */}
            <div 
              className="w-full pt-3 mt-2"
              style={{ borderTop: `1px dashed ${SKETCH_COLORS.gridColor}` }}
            >
              <p 
                className="text-xs text-center"
                style={{ ...fontSketchStyle, color: '#9CA3AF' }}
              >
                ✏️ {showHinglish ? 'Slider ghumao aur changes dekho!' : 'Adjust controls to see changes!'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </motion.div>
  );
}

