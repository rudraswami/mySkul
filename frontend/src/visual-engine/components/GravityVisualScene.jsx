/**
 * Gravity Visual Scene - Village Mango Tree Scene
 * Demonstrates gravity with falling mango (Newton's Apple Indian Style!)
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { RotateCcw, ChevronLeft, ChevronRight, Maximize2, X } from 'lucide-react';

const GravityVisualScene = ({ 
  onClose, 
  embedded = true,
  autoPlay = true,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [mangoY, setMangoY] = useState(80);
  const [isFalling, setIsFalling] = useState(false);
  const [showGravityArrow, setShowGravityArrow] = useState(false);
  const [showFormula, setShowFormula] = useState(false);
  const [professorSpeech, setProfessorSpeech] = useState("देखो!");
  const [isExpanded, setIsExpanded] = useState(false);
  const [showImpact, setShowImpact] = useState(false);
  
  const animationRef = useRef(null);
  const totalSteps = 3;

  useEffect(() => {
    if (currentStep === 0) {
      setShowGravityArrow(true);
      setProfessorSpeech("Gravity खींचती है!");
    } else if (currentStep === 1) {
      setIsFalling(true);
      animateMango();
      setProfessorSpeech("गिर रहा है!");
    } else if (currentStep === 2) {
      setShowFormula(true);
      setProfessorSpeech("F = mg");
    }
  }, [currentStep]);

  const animateMango = () => {
    let y = 80;
    let velocity = 0;
    const gravity = 0.8;
    
    const animate = () => {
      velocity += gravity;
      y += velocity;
      
      if (y >= 280) {
        setMangoY(280);
        setIsFalling(false);
        setShowImpact(true);
        setTimeout(() => setShowImpact(false), 500);
        return;
      }
      
      setMangoY(y);
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
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    setCurrentStep(0);
    setMangoY(80);
    setIsFalling(false);
    setShowGravityArrow(false);
    setShowFormula(false);
    setShowImpact(false);
  };

  const stepTitles = [
    "Mango hangs on tree - Gravity pulls down",
    "Mango falls! (g = 9.8 m/s²)",
    "Formula: F = m × g"
  ];

  return (
    <motion.div
      className={`relative rounded-2xl overflow-hidden shadow-2xl ${isExpanded ? 'fixed inset-4 z-50' : ''}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {isExpanded && (
        <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />
      )}

      <div className="relative" style={{ minHeight: '350px' }}>
        <svg viewBox="0 0 640 360" className="w-full h-full">
          <defs>
            <linearGradient id="skyGrad3" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#64B5F6" />
              <stop offset="100%" stopColor="#E3F2FD" />
            </linearGradient>
            <linearGradient id="hillGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#81C784" />
              <stop offset="100%" stopColor="#4CAF50" />
            </linearGradient>
            <filter id="glow3">
              <feGaussianBlur stdDeviation="4" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Sky */}
          <rect x="0" y="0" width="640" height="240" fill="url(#skyGrad3)" />
          
          {/* Sun */}
          <circle cx="80" cy="60" r="45" fill="#FFD54F" opacity="0.9">
            <animate attributeName="r" values="45;48;45" dur="3s" repeatCount="indefinite" />
          </circle>
          <circle cx="80" cy="60" r="35" fill="#FFEB3B" />
          
          {/* Clouds */}
          <g opacity="0.8">
            <ellipse cx="200" cy="50" rx="50" ry="25" fill="white" />
            <ellipse cx="240" cy="45" rx="40" ry="20" fill="white" />
            <ellipse cx="170" cy="45" rx="30" ry="18" fill="white" />
          </g>
          <g opacity="0.7">
            <ellipse cx="500" cy="70" rx="60" ry="28" fill="white" />
            <ellipse cx="550" cy="65" rx="45" ry="22" fill="white" />
          </g>

          {/* Hills */}
          <ellipse cx="100" cy="240" rx="150" ry="60" fill="#81C784" />
          <ellipse cx="500" cy="240" rx="200" ry="80" fill="url(#hillGrad)" />

          {/* Ground */}
          <rect x="0" y="240" width="640" height="120" fill="#558B2F" />
          
          {/* Grass details */}
          {[...Array(20)].map((_, i) => (
            <path key={i} d={`M ${i * 32 + 10} 320 Q ${i * 32 + 15} 305 ${i * 32 + 20} 320`} stroke="#7CB342" strokeWidth="2" fill="none" />
          ))}

          {/* ============ MANGO TREE ============ */}
          <g transform="translate(420, 100)">
            {/* Trunk */}
            <rect x="-20" y="50" width="40" height="180" fill="#5D4037" />
            <rect x="-15" y="50" width="30" height="180" fill="#6D4C41" />
            
            {/* Branches */}
            <path d="M 0 80 Q -80 60 -120 90" stroke="#5D4037" strokeWidth="15" fill="none" />
            <path d="M 0 100 Q 70 70 100 100" stroke="#5D4037" strokeWidth="12" fill="none" />
            <path d="M 0 60 Q -40 30 -60 50" stroke="#5D4037" strokeWidth="10" fill="none" />
            
            {/* Leaves (canopy) */}
            <ellipse cx="0" cy="0" rx="100" ry="60" fill="#4CAF50" />
            <ellipse cx="-80" cy="30" rx="60" ry="40" fill="#66BB6A" />
            <ellipse cx="80" cy="20" rx="55" ry="38" fill="#43A047" />
            <ellipse cx="0" cy="-30" rx="70" ry="45" fill="#81C784" />
            <ellipse cx="-50" cy="-20" rx="50" ry="35" fill="#4CAF50" />
            <ellipse cx="50" cy="-10" rx="45" ry="32" fill="#66BB6A" />
            
            {/* Other mangoes on tree */}
            <ellipse cx="-70" cy="20" rx="8" ry="12" fill="#FF9800" stroke="#E65100" strokeWidth="1" />
            <ellipse cx="60" cy="10" rx="7" ry="10" fill="#FFC107" stroke="#FF8F00" strokeWidth="1" />
            <ellipse cx="-30" cy="-10" rx="8" ry="11" fill="#FF9800" stroke="#E65100" strokeWidth="1" />
          </g>

          {/* ============ FALLING MANGO ============ */}
          <g transform={`translate(380, ${mangoY})`}>
            {/* Mango shadow on ground */}
            {mangoY > 250 && (
              <ellipse cx="40" cy={310 - mangoY} rx={15 + (mangoY - 250) / 5} ry={5 + (mangoY - 250) / 10} fill="rgba(0,0,0,0.2)" />
            )}
            
            {/* Mango */}
            <ellipse cx="0" cy="0" rx="15" ry="22" fill="#FF9800" stroke="#E65100" strokeWidth="2" />
            <ellipse cx="0" cy="0" rx="12" ry="18" fill="#FFA726" />
            
            {/* Stem */}
            <path d="M 0 -22 Q 5 -30 3 -35" stroke="#5D4037" strokeWidth="3" fill="none" />
            <ellipse cx="8" cy="-32" rx="10" ry="6" fill="#66BB6A" transform="rotate(30 8 -32)" />
            
            {/* Shine */}
            <ellipse cx="-5" cy="-8" rx="4" ry="6" fill="white" opacity="0.3" />
            
            {/* Mass label */}
            <g transform="translate(30, 0)">
              <rect x="0" y="-12" width="70" height="24" rx="4" fill="#FFF9C4" stroke="#FFC107" strokeWidth="1" />
              <text x="35" y="4" textAnchor="middle" fontSize="10" fill="#5D4037" fontWeight="bold">m = 0.2 kg</text>
            </g>
            
            {/* Motion blur when falling */}
            {isFalling && (
              <g opacity="0.3">
                <ellipse cx="0" cy="-30" rx="12" ry="15" fill="#FF9800" />
                <ellipse cx="0" cy="-50" rx="10" ry="12" fill="#FF9800" />
              </g>
            )}
          </g>

          {/* Impact effect */}
          {showImpact && (
            <g transform="translate(380, 300)">
              <circle cx="0" cy="0" r="30" fill="none" stroke="#8D6E63" strokeWidth="3" opacity="0.8">
                <animate attributeName="r" from="10" to="50" dur="0.5s" />
                <animate attributeName="opacity" from="1" to="0" dur="0.5s" />
              </circle>
              <text x="0" y="5" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#E65100">THUD!</text>
            </g>
          )}

          {/* Gravity Arrow */}
          {showGravityArrow && mangoY < 200 && (
            <g transform={`translate(380, ${mangoY + 40})`}>
              <line x1="0" y1="0" x2="0" y2="60" stroke="#E91E63" strokeWidth="6" strokeLinecap="round">
                <animate attributeName="y2" values="40;70;40" dur="1s" repeatCount="indefinite" />
              </line>
              <polygon points="0,70 -10,50 10,50" fill="#E91E63">
                <animate attributeName="points" values="0,60 -10,40 10,40;0,80 -10,60 10,60;0,60 -10,40 10,40" dur="1s" repeatCount="indefinite" />
              </polygon>
              
              {/* Label */}
              <g transform="translate(30, 30)">
                <rect x="0" y="-12" width="60" height="24" rx="4" fill="#E91E63" />
                <text x="30" y="4" textAnchor="middle" fontSize="11" fill="white" fontWeight="bold">g ↓</text>
              </g>
            </g>
          )}

          {/* ============ PROFESSOR ============ */}
          <g transform="translate(100, 200)">
            {/* Shadow */}
            <ellipse cx="0" cy="95" rx="35" ry="12" fill="rgba(0,0,0,0.2)" />
            
            {/* Body - Dhoti/Kurta */}
            <path d="M -25 25 L -30 90 L 30 90 L 25 25 Q 0 35 -25 25" fill="#FFF8E1" stroke="#FFE082" strokeWidth="2" />
            
            {/* Legs */}
            <rect x="-15" y="90" width="12" height="35" fill="#FFE082" rx="2" />
            <rect x="3" y="90" width="12" height="35" fill="#FFE082" rx="2" />
            
            {/* Sandals */}
            <ellipse cx="-9" cy="128" rx="12" ry="5" fill="#8D6E63" />
            <ellipse cx="9" cy="128" rx="12" ry="5" fill="#8D6E63" />
            
            {/* Arm pointing up */}
            <g transform="rotate(-70 -20 30)">
              <path d="M -25 30 L -55 50" stroke="#FFCCBC" strokeWidth="10" strokeLinecap="round" />
              <circle cx="-58" cy="52" r="8" fill="#FFCCBC" />
              <line x1="-58" y1="52" x2="-70" y2="42" stroke="#FFCCBC" strokeWidth="5" strokeLinecap="round" />
            </g>
            
            {/* Right arm */}
            <path d="M 25 35 L 45 60" stroke="#FFCCBC" strokeWidth="10" strokeLinecap="round" />
            <circle cx="48" cy="62" r="8" fill="#FFCCBC" />
            
            {/* Head */}
            <circle cx="0" cy="0" r="28" fill="#FFCCBC" stroke="#FFAB91" strokeWidth="2" />
            
            {/* Turban */}
            <path d="M -28 -5 Q -30 -35 0 -40 Q 30 -35 28 -5" fill="#FF5722" />
            <path d="M -25 -8 Q -28 -30 0 -35 Q 28 -30 25 -8" fill="#FF7043" />
            
            {/* Eyes */}
            <ellipse cx="-10" cy="-2" rx="4" ry="5" fill="#212121" />
            <ellipse cx="10" cy="-2" rx="4" ry="5" fill="#212121" />
            <circle cx="-9" cy="-3" r="1.5" fill="white" />
            <circle cx="11" cy="-3" r="1.5" fill="white" />
            
            {/* Nose */}
            <path d="M 0 2 L 3 10 L -3 10" fill="#FFAB91" />
            
            {/* Beard */}
            <path d="M -15 15 Q -20 30 0 35 Q 20 30 15 15" fill="#9E9E9E" />
            
            {/* Mouth */}
            <path d="M -6 18 Q 0 22 6 18" fill="none" stroke="#5D4037" strokeWidth="2" />
            
            {/* Speech bubble */}
            <g>
              <path d="M 40 -50 L 50 -70 L 160 -70 L 160 -25 L 50 -25 L 40 -50 L 48 -38" fill="white" stroke="#E0E0E0" strokeWidth="2" />
              <text x="105" y="-52" textAnchor="middle" fontSize="11" fill="#333" fontWeight="bold">{professorSpeech}</text>
              <text x="105" y="-35" textAnchor="middle" fontSize="9" fill="#666">Newton का सेब!</text>
            </g>
          </g>

          {/* Formula Card */}
          {showFormula && (
            <g transform="translate(320, 80)">
              <rect x="-110" y="-55" width="220" height="100" rx="12" fill="white" stroke="#E91E63" strokeWidth="3" filter="url(#glow3)" />
              <rect x="-105" y="-50" width="210" height="90" rx="10" fill="#FCE4EC" />
              
              <text x="0" y="-15" textAnchor="middle" fontSize="30" fill="#C2185B" fontWeight="bold" fontFamily="monospace">
                F = m × g
              </text>
              <text x="0" y="12" textAnchor="middle" fontSize="12" fill="#424242">
                Weight = Mass × Gravity
              </text>
              <text x="0" y="32" textAnchor="middle" fontSize="11" fill="#757575">
                भार = द्रव्यमान × गुरुत्व
              </text>
            </g>
          )}

          {/* g value indicator */}
          {currentStep >= 1 && (
            <g transform="translate(550, 150)">
              <rect x="-45" y="-25" width="90" height="45" rx="8" fill="#9C27B0" />
              <text x="0" y="-5" textAnchor="middle" fontSize="14" fill="white" fontWeight="bold">g = 9.8</text>
              <text x="0" y="12" textAnchor="middle" fontSize="10" fill="white">m/s²</text>
            </g>
          )}

          {/* Earth indicator at bottom */}
          <g transform="translate(320, 345)">
            <ellipse cx="0" cy="0" rx="200" ry="20" fill="#4CAF50" stroke="#2E7D32" strokeWidth="2" />
            <text x="0" y="5" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">🌍 Earth pulls everything!</text>
          </g>
        </svg>

        {/* Controls */}
        <div className="absolute top-3 right-3 flex space-x-2 z-10">
          <button onClick={handleReplay} className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white">
            <RotateCcw className="w-5 h-5 text-gray-700" />
          </button>
          <button onClick={() => setIsExpanded(!isExpanded)} className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white">
            {isExpanded ? <X className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
          </button>
        </div>

        {/* Formula Badge */}
        <div className="absolute top-3 left-3 bg-white/95 rounded-xl px-4 py-2 shadow-lg">
          <div className="text-xl font-bold text-pink-700 font-mono">F = mg</div>
          <div className="text-xs text-gray-500">Weight = Mass × Gravity</div>
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="bg-gradient-to-t from-gray-900 to-gray-800 p-4">
        <div className="flex items-center justify-between max-w-md mx-auto mb-3">
          <button
            onClick={handlePrevStep}
            disabled={currentStep === 0}
            className={`p-3 rounded-full transition-all ${currentStep === 0 ? 'bg-gray-700 text-gray-500' : 'bg-gray-600 text-white hover:bg-gray-500'}`}
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          <div className="flex items-center space-x-3">
            {[0, 1, 2].map((step) => (
              <motion.div
                key={step}
                className={`w-3 h-3 rounded-full ${step === currentStep ? 'bg-pink-500 scale-125' : step < currentStep ? 'bg-green-500' : 'bg-gray-600'}`}
                animate={step === currentStep ? { scale: [1, 1.3, 1] } : {}}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
            ))}
          </div>

          <button
            onClick={handleNextStep}
            disabled={currentStep >= totalSteps - 1}
            className={`p-3 rounded-full transition-all ${currentStep >= totalSteps - 1 ? 'bg-gray-700 text-gray-500' : 'bg-pink-500 text-white hover:bg-pink-600 shadow-lg'}`}
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>

        <p className="text-center text-white font-medium">
          Step {currentStep + 1}: {stepTitles[currentStep]}
        </p>
      </div>
    </motion.div>
  );
};

export default GravityVisualScene;







