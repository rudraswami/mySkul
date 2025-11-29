/**
 * Mathematics - Pythagorean Theorem Scene
 * Interactive right triangle with squares
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Maximize2, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react';

const MathPythagorasScene = ({ embedded = true }) => {
  const [sideA, setSideA] = useState(3);
  const [sideB, setSideB] = useState(4);
  const [showSquares, setShowSquares] = useState(true);
  const [showControls, setShowControls] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const sideC = Math.sqrt(sideA * sideA + sideB * sideB);
  const scale = 25; // pixels per unit

  // Animate the proof
  const animateProof = () => {
    setIsAnimating(true);
    setShowSquares(false);
    setTimeout(() => setShowSquares(true), 500);
    setTimeout(() => setIsAnimating(false), 1500);
  };

  return (
    <motion.div
      className={`rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-white ${isExpanded ? 'fixed inset-8 z-50' : ''}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {isExpanded && <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />}

      {/* Scene */}
      <div className="relative bg-gradient-to-br from-blue-50 to-indigo-100" style={{ height: isExpanded ? '60vh' : '260px' }}>
        <svg viewBox="0 0 400 220" className="w-full h-full">
          <defs>
            <pattern id="grid" width="25" height="25" patternUnits="userSpaceOnUse">
              <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#ddd" strokeWidth="0.5" />
            </pattern>
          </defs>

          {/* Grid background */}
          <rect width="400" height="220" fill="url(#grid)" />

          {/* Triangle positioned */}
          <g transform="translate(80, 180)">
            {/* Triangle */}
            <polygon
              points={`0,0 ${sideA * scale},0 ${sideA * scale},${-sideB * scale}`}
              fill="rgba(66, 165, 245, 0.3)"
              stroke="#1976D2"
              strokeWidth="3"
            />

            {/* Right angle marker */}
            <rect x={sideA * scale - 10} y={-10} width="10" height="10" fill="none" stroke="#1976D2" strokeWidth="1.5" />

            {/* Side labels */}
            <text x={sideA * scale / 2} y="20" textAnchor="middle" fontSize="14" fill="#1565C0" fontWeight="bold">
              a = {sideA}
            </text>
            <text x={sideA * scale + 15} y={-sideB * scale / 2} textAnchor="start" fontSize="14" fill="#1565C0" fontWeight="bold">
              b = {sideB}
            </text>
            <text x={sideA * scale / 2 - 20} y={-sideB * scale / 2 - 10} textAnchor="middle" fontSize="14" fill="#D32F2F" fontWeight="bold" transform={`rotate(-${Math.atan(sideB/sideA) * 180 / Math.PI} ${sideA * scale / 2} ${-sideB * scale / 2})`}>
              c = {sideC.toFixed(2)}
            </text>

            {/* Squares on sides (when shown) */}
            {showSquares && (
              <>
                {/* Square on side a */}
                <motion.rect
                  x="0" y="0"
                  width={sideA * scale}
                  height={sideA * scale}
                  fill="rgba(76, 175, 80, 0.4)"
                  stroke="#4CAF50"
                  strokeWidth="2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2 }}
                />
                <text x={sideA * scale / 2} y={sideA * scale / 2 + 5} textAnchor="middle" fontSize="12" fill="#2E7D32" fontWeight="bold">
                  a² = {sideA * sideA}
                </text>

                {/* Square on side b */}
                <motion.rect
                  x={sideA * scale}
                  y={-sideB * scale}
                  width={sideB * scale}
                  height={sideB * scale}
                  fill="rgba(255, 152, 0, 0.4)"
                  stroke="#FF9800"
                  strokeWidth="2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.4 }}
                />
                <text x={sideA * scale + sideB * scale / 2} y={-sideB * scale / 2 + 5} textAnchor="middle" fontSize="12" fill="#E65100" fontWeight="bold">
                  b² = {sideB * sideB}
                </text>

                {/* Square on hypotenuse (c) - simplified visualization */}
                <motion.g
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                >
                  <rect
                    x="-10"
                    y={-sideB * scale - sideC * scale - 10}
                    width={sideC * scale}
                    height={sideC * scale}
                    fill="rgba(233, 30, 99, 0.3)"
                    stroke="#E91E63"
                    strokeWidth="2"
                    transform={`rotate(${Math.atan(sideB/sideA) * 180 / Math.PI})`}
                  />
                </motion.g>
              </>
            )}
          </g>

          {/* Formula */}
          <g transform="translate(300, 40)">
            <rect x="-50" y="-25" width="100" height="50" rx="8" fill="white" stroke="#1976D2" strokeWidth="2" />
            <text x="0" y="8" textAnchor="middle" fontSize="18" fill="#1565C0" fontWeight="bold">
              a² + b² = c²
            </text>
          </g>

          {/* Calculation */}
          <g transform="translate(300, 110)">
            <rect x="-70" y="-35" width="140" height="70" rx="8" fill="rgba(255,255,255,0.9)" />
            <text x="0" y="-15" textAnchor="middle" fontSize="12" fill="#666">
              {sideA}² + {sideB}² = {sideC.toFixed(2)}²
            </text>
            <text x="0" y="5" textAnchor="middle" fontSize="12" fill="#666">
              {sideA * sideA} + {sideB * sideB} = {(sideC * sideC).toFixed(1)}
            </text>
            <text x="0" y="25" textAnchor="middle" fontSize="14" fill="#4CAF50" fontWeight="bold">
              ✓ {sideA * sideA + sideB * sideB} = {sideA * sideA + sideB * sideB}
            </text>
          </g>
        </svg>

        {/* Top UI */}
        <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-1.5">
          <div className="text-lg font-bold text-gray-800">Pythagoras Theorem</div>
        </div>

        <div className="absolute top-2 right-2 flex space-x-1.5">
          <button onClick={animateProof} className="p-1.5 bg-white/90 rounded-lg hover:bg-white">
            <RotateCcw className="w-4 h-4 text-gray-600" />
          </button>
          <button onClick={() => setIsExpanded(!isExpanded)} className="p-1.5 bg-white/90 rounded-lg hover:bg-white">
            <Maximize2 className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-gray-50 border-t border-gray-100">
        <button 
          onClick={() => setShowControls(!showControls)}
          className="w-full py-1.5 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-sm"
        >
          {showControls ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          <span className="ml-1">{showControls ? 'Hide' : 'Show'} Controls</span>
        </button>

        {showControls && (
          <div className="px-4 pb-3 space-y-2">
            <div className="flex items-center justify-center py-2 bg-white rounded-lg border border-gray-100">
              <span className="text-green-600 font-bold">{sideA}²</span>
              <span className="text-gray-400 mx-2">+</span>
              <span className="text-orange-500 font-bold">{sideB}²</span>
              <span className="text-gray-400 mx-2">=</span>
              <span className="text-pink-600 font-bold text-lg">{sideC.toFixed(2)}²</span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Side a</span>
                  <span className="font-medium text-green-600">{sideA}</span>
                </div>
                <input
                  type="range" min="1" max="6" value={sideA}
                  onChange={(e) => setSideA(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg cursor-pointer accent-green-500"
                />
              </div>
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Side b</span>
                  <span className="font-medium text-orange-500">{sideB}</span>
                </div>
                <input
                  type="range" min="1" max="6" value={sideB}
                  onChange={(e) => setSideB(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg cursor-pointer accent-orange-500"
                />
              </div>
            </div>

            <div className="flex justify-center">
              <label className="flex items-center space-x-2 text-sm text-gray-600">
                <input
                  type="checkbox"
                  checked={showSquares}
                  onChange={(e) => setShowSquares(e.target.checked)}
                  className="rounded accent-blue-500"
                />
                <span>Show squares on sides</span>
              </label>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default MathPythagorasScene;







