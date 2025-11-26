/**
 * Force Visual Scene - Complete Working Implementation
 * A visually rich, animated scene that actually SHOWS things!
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RotateCcw, ChevronLeft, ChevronRight, Volume2, X, Maximize2 } from 'lucide-react';

const ForceVisualScene = ({ 
  onClose, 
  embedded = true,
  autoPlay = true,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [ballPosition, setBallPosition] = useState({ x: 180, y: 200 });
  const [showForceArrow, setShowForceArrow] = useState(false);
  const [professorGesture, setProfessorGesture] = useState('ready');
  const [showFormula, setShowFormula] = useState(false);
  const [highlightedItem, setHighlightedItem] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  
  const animationRef = useRef(null);
  const totalSteps = 3;

  // Auto-play animation sequence
  useEffect(() => {
    if (!isPlaying) return;

    const runStep = async () => {
      switch (currentStep) {
        case 0:
          // Step 1: Professor points, show force arrow
          setProfessorGesture('pointing');
          await delay(800);
          setShowForceArrow(true);
          break;
        case 1:
          // Step 2: Ball moves with force
          setProfessorGesture('throwing');
          await delay(300);
          animateBall();
          break;
        case 2:
          // Step 3: Show formula
          setProfessorGesture('explaining');
          setShowFormula(true);
          break;
      }
    };

    runStep();
  }, [currentStep, isPlaying]);

  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const animateBall = () => {
    let startX = 180;
    let startY = 200;
    let time = 0;
    
    const animate = () => {
      time += 0.05;
      if (time > 1.5) {
        setBallPosition({ x: 520, y: 240 });
        return;
      }
      
      // Projectile motion
      const x = startX + 250 * time;
      const y = startY - 80 * time + 40 * time * time;
      setBallPosition({ x, y });
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
  };

  const handleNextStep = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleReplay = () => {
    // Reset everything
    setCurrentStep(0);
    setBallPosition({ x: 180, y: 200 });
    setShowForceArrow(false);
    setProfessorGesture('ready');
    setShowFormula(false);
    setIsPlaying(true);
    
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  };

  const handleObjectTap = (objectId) => {
    setHighlightedItem(objectId);
    setTimeout(() => setHighlightedItem(null), 1500);
  };

  const stepTitles = [
    "Professor applies force on ball",
    "Ball accelerates forward!",
    "F = m × a explains it all!"
  ];

  const SceneContent = () => (
    <svg 
      viewBox="0 0 640 360" 
      className="w-full h-full"
      style={{ background: 'linear-gradient(180deg, #87CEEB 0%, #E0F7FA 60%, #7CB342 60%, #558B2F 100%)' }}
    >
      <defs>
        {/* Gradients */}
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#64B5F6" />
          <stop offset="100%" stopColor="#E3F2FD" />
        </linearGradient>
        <linearGradient id="grassGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#7CB342" />
          <stop offset="100%" stopColor="#558B2F" />
        </linearGradient>
        <linearGradient id="pitchGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#D7CCC8" />
          <stop offset="100%" stopColor="#BCAAA4" />
        </linearGradient>
        
        {/* Glow filter */}
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {/* Sky */}
      <rect x="0" y="0" width="640" height="220" fill="url(#skyGrad)" />
      
      {/* Sun */}
      <circle cx="580" cy="50" r="35" fill="#FFD54F" opacity="0.9">
        <animate attributeName="r" values="35;38;35" dur="3s" repeatCount="indefinite" />
      </circle>
      <circle cx="580" cy="50" r="25" fill="#FFEB3B" />
      
      {/* Clouds */}
      <g opacity="0.8">
        <ellipse cx="100" cy="60" rx="40" ry="20" fill="white" />
        <ellipse cx="130" cy="55" rx="35" ry="18" fill="white" />
        <ellipse cx="80" cy="55" rx="25" ry="15" fill="white" />
      </g>
      <g opacity="0.7">
        <ellipse cx="400" cy="40" rx="50" ry="22" fill="white" />
        <ellipse cx="440" cy="35" rx="40" ry="18" fill="white" />
      </g>

      {/* Ground/Grass */}
      <rect x="0" y="220" width="640" height="140" fill="url(#grassGrad)" />
      
      {/* Cricket Pitch */}
      <rect x="100" y="250" width="440" height="80" rx="5" fill="url(#pitchGrad)" />
      <line x1="150" y1="250" x2="150" y2="330" stroke="white" strokeWidth="2" />
      <line x1="490" y1="250" x2="490" y2="330" stroke="white" strokeWidth="2" />
      
      {/* Boundary Line */}
      <ellipse cx="320" cy="290" rx="280" ry="50" fill="none" stroke="white" strokeWidth="2" strokeDasharray="10 5" opacity="0.5" />

      {/* ============ PROFESSOR ============ */}
      <g 
        transform="translate(80, 180)"
        onClick={() => handleObjectTap('professor')}
        style={{ cursor: 'pointer' }}
      >
        {/* Highlight glow */}
        {highlightedItem === 'professor' && (
          <circle cx="0" cy="30" r="60" fill="none" stroke="#FF9800" strokeWidth="3" opacity="0.6" filter="url(#glow)">
            <animate attributeName="r" values="55;65;55" dur="0.8s" repeatCount="indefinite" />
          </circle>
        )}
        
        {/* Shadow */}
        <ellipse cx="0" cy="95" rx="30" ry="10" fill="rgba(0,0,0,0.2)" />
        
        {/* Body - Blue Kurta */}
        <path d="M -25 25 L -30 90 L 30 90 L 25 25 Q 0 35 -25 25" fill="#1565C0" stroke="#0D47A1" strokeWidth="2" />
        
        {/* Collar */}
        <path d="M -12 25 L 0 40 L 12 25" fill="#1976D2" />
        
        {/* Legs */}
        <rect x="-18" y="90" width="14" height="40" fill="#37474F" rx="2" />
        <rect x="4" y="90" width="14" height="40" fill="#37474F" rx="2" />
        
        {/* Shoes */}
        <ellipse cx="-11" cy="132" rx="12" ry="6" fill="#4E342E" />
        <ellipse cx="11" cy="132" rx="12" ry="6" fill="#4E342E" />
        
        {/* Left Arm - Animated based on gesture */}
        <g transform={`rotate(${professorGesture === 'pointing' ? -60 : professorGesture === 'throwing' ? -80 : -10} -20 30)`}>
          <path d="M -25 30 L -55 50" stroke="#FFCCBC" strokeWidth="10" strokeLinecap="round" fill="none" />
          <circle cx="-58" cy="52" r="8" fill="#FFCCBC" />
          {/* Pointing finger */}
          {professorGesture === 'pointing' && (
            <line x1="-58" y1="52" x2="-75" y2="42" stroke="#FFCCBC" strokeWidth="5" strokeLinecap="round" />
          )}
        </g>
        
        {/* Right Arm */}
        <g transform={`rotate(${professorGesture === 'throwing' ? 30 : 15} 20 30)`}>
          <path d="M 25 30 L 50 55" stroke="#FFCCBC" strokeWidth="10" strokeLinecap="round" fill="none" />
          <circle cx="52" cy="58" r="8" fill="#FFCCBC" />
        </g>
        
        {/* Head */}
        <circle cx="0" cy="0" r="28" fill="#FFCCBC" stroke="#FFAB91" strokeWidth="2" />
        
        {/* Hair */}
        <path d="M -26 -10 Q -28 -32 -15 -35 Q 0 -40 15 -35 Q 28 -32 26 -10" fill="#212121" />
        
        {/* Eyes */}
        <ellipse cx="-10" cy="-2" rx="4" ry="5" fill="#212121" />
        <ellipse cx="10" cy="-2" rx="4" ry="5" fill="#212121" />
        <circle cx="-9" cy="-3" r="1.5" fill="white" />
        <circle cx="11" cy="-3" r="1.5" fill="white" />
        
        {/* Eyebrows */}
        <path d="M -15 -10 Q -10 -14 -5 -10" fill="none" stroke="#424242" strokeWidth="2" />
        <path d="M 5 -10 Q 10 -14 15 -10" fill="none" stroke="#424242" strokeWidth="2" />
        
        {/* Glasses */}
        <circle cx="-10" cy="-2" r="10" fill="none" stroke="#424242" strokeWidth="2" />
        <circle cx="10" cy="-2" r="10" fill="none" stroke="#424242" strokeWidth="2" />
        <line x1="0" y1="-2" x2="-0" y2="-2" stroke="#424242" strokeWidth="2" />
        <line x1="20" y1="-4" x2="28" y2="-8" stroke="#424242" strokeWidth="2" />
        <line x1="-20" y1="-4" x2="-28" y2="-8" stroke="#424242" strokeWidth="2" />
        
        {/* Nose */}
        <path d="M 0 2 L 3 10 L -3 10" fill="#FFAB91" />
        
        {/* Mustache */}
        <path d="M -10 12 Q -5 15 0 12 Q 5 15 10 12" fill="#424242" />
        
        {/* Mouth - Smiling */}
        <path d="M -8 18 Q 0 25 8 18" fill="none" stroke="#5D4037" strokeWidth="2" />
        
        {/* Speech Bubble */}
        {currentStep === 0 && (
          <g>
            <path d="M 45 -40 L 55 -60 L 150 -60 L 150 -20 L 55 -20 L 45 -40 L 52 -30" fill="white" stroke="#E0E0E0" strokeWidth="2" />
            <text x="100" y="-45" textAnchor="middle" fontSize="12" fill="#333" fontWeight="bold">Force lagao!</text>
            <text x="100" y="-28" textAnchor="middle" fontSize="10" fill="#666">बल लगाओ!</text>
          </g>
        )}
      </g>

      {/* ============ CRICKET BALL ============ */}
      <g 
        transform={`translate(${ballPosition.x}, ${ballPosition.y})`}
        onClick={() => handleObjectTap('ball')}
        style={{ cursor: 'pointer' }}
      >
        {/* Highlight */}
        {highlightedItem === 'ball' && (
          <circle cx="0" cy="0" r="30" fill="none" stroke="#FF9800" strokeWidth="3" opacity="0.8" filter="url(#glow)">
            <animate attributeName="r" values="25;35;25" dur="0.6s" repeatCount="indefinite" />
          </circle>
        )}
        
        {/* Ball shadow */}
        <ellipse cx="5" cy="20" rx="15" ry="5" fill="rgba(0,0,0,0.3)" />
        
        {/* Ball */}
        <circle cx="0" cy="0" r="18" fill="#D32F2F" stroke="#8B0000" strokeWidth="2" />
        
        {/* Ball seam */}
        <path d="M -12 -12 Q 0 0 12 12" stroke="white" strokeWidth="2" fill="none" />
        <path d="M -14 -8 Q 0 5 14 8" stroke="white" strokeWidth="1" fill="none" strokeDasharray="3 2" />
        
        {/* Shine */}
        <circle cx="-6" cy="-8" r="4" fill="white" opacity="0.4" />
        
        {/* Mass label */}
        <g transform="translate(0, 35)">
          <rect x="-30" y="-10" width="60" height="20" rx="4" fill="#FFF9C4" stroke="#FFC107" strokeWidth="1" />
          <text x="0" y="4" textAnchor="middle" fontSize="10" fill="#5D4037" fontWeight="bold">m = 0.15 kg</text>
        </g>
        
        {/* Ball spinning animation when moving */}
        {currentStep === 1 && (
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0"
            to="360"
            dur="0.3s"
            repeatCount="indefinite"
            additive="sum"
          />
        )}
      </g>

      {/* ============ FORCE ARROW ============ */}
      {showForceArrow && (
        <g>
          {/* Arrow shaft */}
          <line 
            x1={ballPosition.x + 25} 
            y1={ballPosition.y} 
            x2={ballPosition.x + 25 + (currentStep >= 1 ? 120 : 0)} 
            y2={ballPosition.y}
            stroke="#FF5722"
            strokeWidth="8"
            strokeLinecap="round"
          >
            <animate 
              attributeName="x2" 
              from={ballPosition.x + 25} 
              to={ballPosition.x + 145} 
              dur="0.5s" 
              fill="freeze"
            />
          </line>
          
          {/* Arrow head */}
          <polygon 
            points={`${ballPosition.x + 150},${ballPosition.y} ${ballPosition.x + 130},${ballPosition.y - 15} ${ballPosition.x + 130},${ballPosition.y + 15}`}
            fill="#FF5722"
          >
            <animate attributeName="opacity" from="0" to="1" dur="0.5s" fill="freeze" />
          </polygon>
          
          {/* Force label */}
          <g transform={`translate(${ballPosition.x + 90}, ${ballPosition.y - 30})`}>
            <rect x="-35" y="-15" width="70" height="28" rx="5" fill="#FF5722" />
            <text x="0" y="4" textAnchor="middle" fontSize="14" fill="white" fontWeight="bold">F (बल)</text>
          </g>
          
          {/* Glow effect */}
          <line 
            x1={ballPosition.x + 25} 
            y1={ballPosition.y} 
            x2={ballPosition.x + 145} 
            y2={ballPosition.y}
            stroke="#FF5722"
            strokeWidth="15"
            strokeLinecap="round"
            opacity="0.3"
            filter="url(#glow)"
          >
            <animate attributeName="opacity" values="0.3;0.5;0.3" dur="1s" repeatCount="indefinite" />
          </line>
        </g>
      )}

      {/* ============ STUMPS ============ */}
      <g transform="translate(540, 260)" onClick={() => handleObjectTap('stumps')} style={{ cursor: 'pointer' }}>
        {/* Highlight */}
        {highlightedItem === 'stumps' && (
          <circle cx="0" cy="20" r="40" fill="none" stroke="#FF9800" strokeWidth="3" opacity="0.6" filter="url(#glow)" />
        )}
        
        {/* Stumps */}
        <rect x="-18" y="0" width="6" height="60" fill="#8D6E63" rx="1" />
        <rect x="-3" y="0" width="6" height="60" fill="#8D6E63" rx="1" />
        <rect x="12" y="0" width="6" height="60" fill="#8D6E63" rx="1" />
        
        {/* Bails */}
        <rect x="-16" y="-5" width="14" height="4" fill="#FFC107" rx="1" />
        <rect x="2" y="-5" width="14" height="4" fill="#FFC107" rx="1" />
      </g>

      {/* ============ BAT (optional decoration) ============ */}
      <g transform="translate(460, 280) rotate(-20)">
        <rect x="-5" y="-50" width="10" height="25" fill="#5D4037" rx="2" />
        <rect x="-12" y="-25" width="24" height="60" fill="#D7CCC8" rx="3" stroke="#8D6E63" strokeWidth="1" />
      </g>

      {/* ============ FORMULA CARD ============ */}
      {showFormula && (
        <g transform="translate(320, 80)">
          <rect x="-100" y="-50" width="200" height="100" rx="10" fill="white" stroke="#FF9800" strokeWidth="3" filter="url(#glow)" />
          <rect x="-95" y="-45" width="190" height="90" rx="8" fill="#FFF8E1" />
          
          <text x="0" y="-15" textAnchor="middle" fontSize="28" fill="#E65100" fontWeight="bold" fontFamily="monospace">
            F = m × a
          </text>
          <text x="0" y="15" textAnchor="middle" fontSize="12" fill="#5D4037">
            Force = Mass × Acceleration
          </text>
          <text x="0" y="35" textAnchor="middle" fontSize="11" fill="#8D6E63">
            बल = द्रव्यमान × त्वरण
          </text>
          
          {/* Animated border */}
          <rect x="-100" y="-50" width="200" height="100" rx="10" fill="none" stroke="#FF9800" strokeWidth="2" strokeDasharray="10 5">
            <animate attributeName="stroke-dashoffset" from="0" to="30" dur="1s" repeatCount="indefinite" />
          </rect>
        </g>
      )}

      {/* ============ ACCELERATION INDICATOR ============ */}
      {currentStep >= 1 && (
        <g transform="translate(380, 230)">
          <rect x="-50" y="-15" width="100" height="28" rx="5" fill="#4CAF50" />
          <text x="0" y="5" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">
            a = F/m ↑
          </text>
        </g>
      )}
    </svg>
  );

  return (
    <motion.div
      className={`relative rounded-2xl overflow-hidden shadow-2xl ${isExpanded ? 'fixed inset-4 z-50' : ''}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Backdrop for expanded */}
      {isExpanded && (
        <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />
      )}

      {/* Scene Container */}
      <div className="relative bg-gradient-to-b from-blue-200 to-green-300" style={{ minHeight: embedded ? '350px' : '450px' }}>
        <SceneContent />
        
        {/* Top Controls */}
        <div className="absolute top-3 right-3 flex space-x-2 z-10">
          <button
            onClick={handleReplay}
            className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white transition-all"
            title="Replay"
          >
            <RotateCcw className="w-5 h-5 text-gray-700" />
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white transition-all"
            title={isExpanded ? "Minimize" : "Fullscreen"}
          >
            {isExpanded ? <X className="w-5 h-5 text-gray-700" /> : <Maximize2 className="w-5 h-5 text-gray-700" />}
          </button>
        </div>

        {/* Formula Badge - Top Right */}
        <div className="absolute top-3 left-3 bg-white/95 rounded-xl px-4 py-2 shadow-lg">
          <div className="text-xl font-bold text-gray-800 font-mono">F = m × a</div>
          <div className="text-xs text-gray-500">Force = Mass × Acceleration</div>
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="bg-gradient-to-t from-gray-900 to-gray-800 p-4">
        {/* Step navigation */}
        <div className="flex items-center justify-between max-w-md mx-auto mb-3">
          <button
            onClick={handlePrevStep}
            disabled={currentStep === 0}
            className={`p-3 rounded-full transition-all ${
              currentStep === 0 ? 'bg-gray-700 text-gray-500' : 'bg-gray-600 text-white hover:bg-gray-500'
            }`}
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          {/* Step dots */}
          <div className="flex items-center space-x-3">
            {[0, 1, 2].map((step) => (
              <motion.div
                key={step}
                className={`w-3 h-3 rounded-full transition-all ${
                  step === currentStep ? 'bg-orange-500 scale-125' : step < currentStep ? 'bg-green-500' : 'bg-gray-600'
                }`}
                animate={step === currentStep ? { scale: [1, 1.3, 1] } : {}}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
            ))}
          </div>

          <button
            onClick={handleNextStep}
            disabled={currentStep >= totalSteps - 1}
            className={`p-3 rounded-full transition-all ${
              currentStep >= totalSteps - 1 ? 'bg-gray-700 text-gray-500' : 'bg-orange-500 text-white hover:bg-orange-600 shadow-lg'
            }`}
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>

        {/* Step title */}
        <p className="text-center text-white font-medium">
          Step {currentStep + 1}: {stepTitles[currentStep]}
        </p>
      </div>
    </motion.div>
  );
};

export default ForceVisualScene;


