/**
 * Interactive Controls Component
 * Renders sliders, toggles, selectors with real-time updates
 * Includes Hinglish labels for Indian students
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sliders, ToggleLeft, ToggleRight, Play, RotateCcw } from 'lucide-react';

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
      className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl border-2 border-purple-200 overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
    >
      {/* Header */}
      <div
        className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-3 flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5" />
          <span className="font-semibold">Interactive Controls</span>
          {showHinglish && <span className="text-sm opacity-90">(Experiment Karo!)</span>}
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          ▼
        </motion.div>
      </div>

      {/* Controls Body */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="p-4 space-y-4"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Sliders */}
            {controls.sliders && controls.sliders.map((slider) => (
              <div key={slider.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">
                    {showHinglish && slider.label_hinglish ? slider.label_hinglish : slider.label}
                  </label>
                  <span className="text-lg font-bold text-purple-600">
                    {values[slider.id] !== undefined ? values[slider.id] : slider.default}
                    <span className="text-sm text-gray-500 ml-1">{slider.unit}</span>
                  </span>
                </div>
                
                <input
                  type="range"
                  min={slider.min}
                  max={slider.max}
                  step={slider.step || 1}
                  value={values[slider.id] !== undefined ? values[slider.id] : slider.default}
                  onChange={(e) => onChange(slider.id, parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-purple"
                  style={{
                    background: `linear-gradient(to right, #a78bfa 0%, #a78bfa ${((values[slider.id] || slider.default) - slider.min) / (slider.max - slider.min) * 100}%, #e5e7eb ${((values[slider.id] || slider.default) - slider.min) / (slider.max - slider.min) * 100}%, #e5e7eb 100%)`
                  }}
                />
                
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{slider.min}{slider.unit}</span>
                  <span>{slider.max}{slider.unit}</span>
                </div>
              </div>
            ))}

            {/* Selectors/Dropdowns */}
            {controls.selectors && controls.selectors.map((selector) => (
              <div key={selector.id} className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  {showHinglish && selector.label_hinglish ? selector.label_hinglish : selector.label}
                </label>
                
                <select
                  value={values[selector.id] || selector.default}
                  onChange={(e) => onChange(selector.id, e.target.value)}
                  className="w-full px-3 py-2 border-2 border-purple-200 rounded-lg focus:border-purple-500 focus:outline-none text-sm font-medium bg-white"
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

            {/* Toggles */}
            {controls.toggles && controls.toggles.map((toggle) => (
              <div key={toggle.id} className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">
                  {showHinglish && toggle.label_hinglish ? toggle.label_hinglish : toggle.label}
                </label>
                
                <button
                  onClick={() => onChange(toggle.id, !(values[toggle.id] || toggle.default))}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    (values[toggle.id] !== undefined ? values[toggle.id] : toggle.default)
                      ? 'bg-purple-600'
                      : 'bg-gray-300'
                  }`}
                >
                  <motion.span
                    className="inline-block h-4 w-4 transform rounded-full bg-white shadow-lg"
                    animate={{
                      x: (values[toggle.id] !== undefined ? values[toggle.id] : toggle.default) ? 24 : 4
                    }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                </button>
              </div>
            ))}

            {/* Buttons */}
            {controls.buttons && controls.buttons.map((button) => (
              <button
                key={button.id}
                onClick={() => onChange(button.id, true)}
                className="w-full px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-lg shadow-md transition-all duration-200 transform hover:scale-105 active:scale-95"
              >
                {showHinglish && button.label_hinglish ? button.label_hinglish : button.label}
              </button>
            ))}

            {/* Hint Text */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500 italic text-center">
                💡 {showHinglish ? 'Slider ghumao aur changes dekho!' : 'Adjust controls to see changes!'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </motion.div>
  );
}

