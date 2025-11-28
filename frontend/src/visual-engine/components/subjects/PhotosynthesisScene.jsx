/**
 * PhotosynthesisScene.jsx
 * Phase 8: Interactive photosynthesis visualization
 * 
 * Features:
 * - Light intensity control
 * - CO2/O2 flow animation
 * - Chloroplast detail view
 * - Step-by-step process
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Droplets, Wind, ChevronDown, ChevronUp, Maximize2, RotateCcw, Leaf } from 'lucide-react';

const PhotosynthesisScene = ({ embedded = true }) => {
  // State
  const [lightIntensity, setLightIntensity] = useState(70);
  const [co2Level, setCo2Level] = useState(50);
  const [showControls, setShowControls] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [showDetail, setShowDetail] = useState(false);
  
  // Animation refs
  const [bubbles, setBubbles] = useState([]);
  const animationRef = useRef(null);

  // Calculate oxygen production rate
  const oxygenRate = Math.min(lightIntensity, co2Level) / 10;

  // Generate oxygen bubbles
  useEffect(() => {
    const interval = setInterval(() => {
      if (oxygenRate > 2) {
        setBubbles(prev => {
          const newBubbles = [...prev];
          // Add new bubble
          newBubbles.push({
            id: Date.now(),
            x: 280 + Math.random() * 20,
            y: 140,
            size: 3 + Math.random() * 4,
          });
          // Remove old bubbles
          return newBubbles.filter(b => b.y > 20).slice(-15);
        });
      }
    }, 500 / oxygenRate);

    return () => clearInterval(interval);
  }, [oxygenRate]);

  // Animate bubbles rising
  useEffect(() => {
    const animate = () => {
      setBubbles(prev => prev.map(b => ({
        ...b,
        y: b.y - 1.5,
        x: b.x + (Math.random() - 0.5) * 2,
      })));
      animationRef.current = requestAnimationFrame(animate);
    };
    animationRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationRef.current);
  }, []);

  // Process steps
  const steps = [
    { title: "Light Absorption", description: "Chlorophyll absorbs sunlight", icon: "☀️" },
    { title: "Water Split", description: "H₂O → H⁺ + O₂", icon: "💧" },
    { title: "CO₂ Fixation", description: "CO₂ enters through stomata", icon: "🌬️" },
    { title: "Glucose Made", description: "C₆H₁₂O₆ is produced!", icon: "🍬" },
  ];

  return (
    <motion.div
      className={`rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-white ${isExpanded ? 'fixed inset-8 z-50' : ''}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {isExpanded && <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />}

      {/* Scene */}
      <div className="relative bg-gradient-to-b from-sky-300 via-sky-200 to-green-100" style={{ height: isExpanded ? '60vh' : '300px' }}>
        <svg viewBox="0 0 400 220" className="w-full h-full">
          <defs>
            {/* Sun gradient */}
            <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#FFEB3B" />
              <stop offset="50%" stopColor="#FFC107" />
              <stop offset="100%" stopColor="#FF9800" stopOpacity="0" />
            </radialGradient>
            
            {/* Leaf gradient */}
            <linearGradient id="leafGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#66BB6A" />
              <stop offset="100%" stopColor="#2E7D32" />
            </linearGradient>
            
            {/* Chloroplast gradient */}
            <linearGradient id="chloroplastGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#81C784" />
              <stop offset="100%" stopColor="#4CAF50" />
            </linearGradient>
          </defs>

          {/* Sky background */}
          <rect x="0" y="0" width="400" height="120" fill="url(#sky)" />

          {/* Sun */}
          <motion.g
            animate={{ 
              scale: [1, 1.05, 1],
              opacity: lightIntensity / 100 
            }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <circle cx="350" cy="40" r="35" fill="url(#sunGlow)" />
            <circle cx="350" cy="40" r="22" fill="#FFD54F" />
            
            {/* Sun rays */}
            {[...Array(8)].map((_, i) => (
              <motion.line
                key={i}
                x1={350 + 28 * Math.cos(i * Math.PI / 4)}
                y1={40 + 28 * Math.sin(i * Math.PI / 4)}
                x2={350 + 45 * Math.cos(i * Math.PI / 4)}
                y2={40 + 45 * Math.sin(i * Math.PI / 4)}
                stroke="#FFC107"
                strokeWidth="3"
                strokeLinecap="round"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 1, delay: i * 0.1 }}
              />
            ))}
          </motion.g>

          {/* Light rays hitting leaf */}
          {lightIntensity > 20 && (
            <g opacity={lightIntensity / 150}>
              {[...Array(5)].map((_, i) => (
                <motion.line
                  key={i}
                  x1={320 - i * 15}
                  y1={60 + i * 10}
                  x2={200 + i * 10}
                  y2={100 + i * 5}
                  stroke="#FFD54F"
                  strokeWidth="2"
                  strokeDasharray="10 5"
                  animate={{ strokeDashoffset: [-15, 0] }}
                  transition={{ repeat: Infinity, duration: 0.5 }}
                />
              ))}
            </g>
          )}

          {/* Ground */}
          <rect x="0" y="180" width="400" height="40" fill="#8D6E63" />
          <ellipse cx="200" cy="180" rx="150" ry="15" fill="#6D4C41" />

          {/* Plant stem */}
          <rect x="195" y="140" width="10" height="50" fill="#5D4037" rx="2" />

          {/* Main leaf */}
          <motion.g
            animate={{ rotate: [0, 2, 0, -2, 0] }}
            transition={{ repeat: Infinity, duration: 4 }}
            style={{ transformOrigin: '200px 140px' }}
          >
            <path
              d="M 120 100 Q 200 60 280 100 Q 260 140 200 145 Q 140 140 120 100"
              fill="url(#leafGradient)"
              stroke="#2E7D32"
              strokeWidth="2"
            />
            
            {/* Leaf veins */}
            <path d="M 200 145 L 200 80" stroke="#43A047" strokeWidth="2" />
            <path d="M 200 100 L 160 85" stroke="#43A047" strokeWidth="1.5" />
            <path d="M 200 100 L 240 85" stroke="#43A047" strokeWidth="1.5" />
            <path d="M 200 120 L 150 100" stroke="#43A047" strokeWidth="1" />
            <path d="M 200 120 L 250 100" stroke="#43A047" strokeWidth="1" />

            {/* Chloroplasts */}
            {[
              { x: 160, y: 95 }, { x: 180, y: 85 }, { x: 220, y: 85 }, { x: 240, y: 95 },
              { x: 170, y: 110 }, { x: 200, y: 105 }, { x: 230, y: 110 },
            ].map((pos, i) => (
              <motion.ellipse
                key={i}
                cx={pos.x}
                cy={pos.y}
                rx="10"
                ry="6"
                fill="url(#chloroplastGradient)"
                stroke="#388E3C"
                strokeWidth="1"
                animate={lightIntensity > 30 ? { 
                  fill: ['#81C784', '#4CAF50', '#81C784'],
                } : {}}
                transition={{ repeat: Infinity, duration: 1, delay: i * 0.2 }}
              />
            ))}

            {/* Stomata */}
            <g>
              <ellipse cx="180" cy="130" rx="6" ry="3" fill="#1B5E20" />
              <ellipse cx="220" cy="130" rx="6" ry="3" fill="#1B5E20" />
              
              {/* CO2 entering */}
              {co2Level > 20 && (
                <>
                  <motion.text
                    x="170"
                    y="145"
                    fontSize="8"
                    fill="#666"
                    animate={{ y: [145, 130], opacity: [1, 0] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  >
                    CO₂
                  </motion.text>
                  <motion.text
                    x="210"
                    y="145"
                    fontSize="8"
                    fill="#666"
                    animate={{ y: [145, 130], opacity: [1, 0] }}
                    transition={{ repeat: Infinity, duration: 2, delay: 0.5 }}
                  >
                    CO₂
                  </motion.text>
                </>
              )}
            </g>
          </motion.g>

          {/* Oxygen bubbles */}
          {bubbles.map((bubble) => (
            <motion.g key={bubble.id}>
              <circle
                cx={bubble.x}
                cy={bubble.y}
                r={bubble.size}
                fill="rgba(33, 150, 243, 0.4)"
                stroke="#2196F3"
                strokeWidth="1"
              />
              <text
                x={bubble.x}
                y={bubble.y + 2}
                fontSize="5"
                fill="#1565C0"
                textAnchor="middle"
              >
                O₂
              </text>
            </motion.g>
          ))}

          {/* Water uptake arrows */}
          <motion.g
            animate={{ y: [0, -5, 0] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          >
            <path d="M 200 190 L 200 170" stroke="#2196F3" strokeWidth="2" markerEnd="url(#arrow)" />
            <text x="210" y="185" fontSize="8" fill="#1565C0">H₂O</text>
          </motion.g>

          {/* Roots */}
          <g>
            <path d="M 200 190 Q 180 200 170 210" stroke="#5D4037" strokeWidth="4" fill="none" />
            <path d="M 200 190 Q 220 200 230 210" stroke="#5D4037" strokeWidth="4" fill="none" />
            <path d="M 200 190 L 200 215" stroke="#5D4037" strokeWidth="4" />
          </g>

          {/* Glucose indicator */}
          {lightIntensity > 40 && co2Level > 30 && (
            <motion.g
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 }}
            >
              <rect x="80" y="90" width="50" height="20" rx="4" fill="white" stroke="#FFC107" strokeWidth="2" />
              <text x="105" y="104" fontSize="9" fill="#F57F17" textAnchor="middle" fontWeight="bold">
                C₆H₁₂O₆
              </text>
            </motion.g>
          )}
        </svg>

        {/* Formula overlay */}
        <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow">
          <p className="text-xs font-bold text-green-700">Photosynthesis</p>
          <p className="text-xs text-gray-600 font-mono">
            6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂
          </p>
        </div>

        {/* O2 production rate */}
        <div className="absolute top-2 right-12 bg-blue-100/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow">
          <p className="text-xs text-blue-700">O₂ Production</p>
          <p className="text-lg font-bold text-blue-600">{oxygenRate.toFixed(1)} 💨</p>
        </div>

        {/* Controls */}
        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="absolute top-2 right-2 p-1.5 bg-white/80 rounded-lg hover:bg-white"
        >
          <Maximize2 className="w-4 h-4 text-gray-600" />
        </button>

        {/* Step indicator */}
        <div className="absolute bottom-2 left-2 right-2 flex gap-1">
          {steps.map((step, i) => (
            <button
              key={i}
              onClick={() => setCurrentStep(i)}
              className={`flex-1 py-1 px-2 rounded text-xs font-medium transition-colors ${
                currentStep === i
                  ? 'bg-green-500 text-white'
                  : 'bg-white/80 text-gray-600 hover:bg-white'
              }`}
            >
              {step.icon}
            </button>
          ))}
        </div>
      </div>

      {/* Step description */}
      <div className="px-4 py-2 bg-green-50 border-b border-green-200">
        <p className="text-sm font-bold text-green-700">
          Step {currentStep + 1}: {steps[currentStep].title}
        </p>
        <p className="text-xs text-green-600">{steps[currentStep].description}</p>
      </div>

      {/* Controls Panel */}
      <div className="bg-gray-50 border-t border-gray-100">
        <button 
          onClick={() => setShowControls(!showControls)}
          className="w-full py-1.5 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-sm"
        >
          {showControls ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          <span className="ml-1">{showControls ? 'Hide' : 'Show'} Controls</span>
        </button>

        {showControls && (
          <div className="px-4 pb-4 space-y-4">
            {/* Light intensity */}
            <div>
              <div className="flex justify-between items-center text-sm mb-1">
                <span className="flex items-center gap-1 text-gray-600">
                  <Sun className="w-4 h-4 text-yellow-500" />
                  Light Intensity
                </span>
                <span className="font-bold text-yellow-600">{lightIntensity}%</span>
              </div>
              <input
                type="range"
                min="0" max="100" value={lightIntensity}
                onChange={(e) => setLightIntensity(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-yellow-500"
              />
            </div>

            {/* CO2 level */}
            <div>
              <div className="flex justify-between items-center text-sm mb-1">
                <span className="flex items-center gap-1 text-gray-600">
                  <Wind className="w-4 h-4 text-gray-500" />
                  CO₂ Level
                </span>
                <span className="font-bold text-gray-600">{co2Level}%</span>
              </div>
              <input
                type="range"
                min="0" max="100" value={co2Level}
                onChange={(e) => setCo2Level(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-500"
              />
            </div>

            {/* Info cards */}
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 bg-green-50 rounded-lg border border-green-200">
                <p className="text-xs text-green-600">Glucose Made</p>
                <p className="text-sm font-bold text-green-700">
                  {(oxygenRate * 0.5).toFixed(1)} units
                </p>
              </div>
              <div className="p-2 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-xs text-blue-600">O₂ Released</p>
                <p className="text-sm font-bold text-blue-700">
                  {oxygenRate.toFixed(1)} bubbles/s
                </p>
              </div>
            </div>

            {/* Limiting factor */}
            <div className="p-2 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-xs text-yellow-700 flex items-center gap-1">
                ⚠️ Limiting Factor: 
                <span className="font-bold">
                  {lightIntensity < co2Level ? 'Light' : 'CO₂'}
                </span>
              </p>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default PhotosynthesisScene;



