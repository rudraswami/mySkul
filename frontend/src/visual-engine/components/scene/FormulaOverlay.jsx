/**
 * Formula Overlay Component
 * Shows detailed formula breakdown when long-pressing objects
 */

import React from 'react';
import { motion } from 'framer-motion';
import { X, BookOpen } from 'lucide-react';

const FormulaOverlay = ({ formula, onClose }) => {
  if (!formula) return null;

  const { main, meaning, breakdown, example } = typeof formula === 'object' 
    ? formula 
    : { main: formula, meaning: '', breakdown: [], example: '' };

  return (
    <motion.div
      className="absolute inset-0 z-40 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="bg-white rounded-2xl p-6 max-w-sm mx-4 shadow-2xl"
        initial={{ scale: 0.8, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.8, y: 20 }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-orange-600" />
            </div>
            <span className="font-bold text-gray-800">Formula</span>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Main Formula */}
        <div className="text-center py-6 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl mb-4">
          <div className="text-4xl font-bold text-gray-800 mb-2 font-mono">
            {main || 'F = m × a'}
          </div>
          {meaning && (
            <p className="text-gray-600 text-sm">{meaning}</p>
          )}
        </div>

        {/* Breakdown */}
        {breakdown && breakdown.length > 0 && (
          <div className="space-y-3 mb-4">
            <h4 className="font-semibold text-gray-700 text-sm uppercase">Breakdown</h4>
            {breakdown.map((item, i) => (
              <div key={i} className="flex items-center space-x-3 bg-gray-50 p-3 rounded-lg">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-700">
                  {item.symbol}
                </div>
                <div>
                  <div className="font-semibold text-gray-800">{item.name}</div>
                  <div className="text-xs text-gray-500">{item.unit}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Example */}
        {example && (
          <div className="bg-green-50 border-l-4 border-green-500 p-3 rounded-r-lg">
            <p className="text-green-800 text-sm font-medium">Example:</p>
            <p className="text-green-700 text-sm">{example}</p>
          </div>
        )}

        {/* Close hint */}
        <p className="text-center text-gray-400 text-xs mt-4">
          Tap anywhere to close
        </p>
      </motion.div>
    </motion.div>
  );
};

export default FormulaOverlay;









