/**
 * Motion Visual Scene - Indian Street Scene
 * Auto-rickshaw demonstrating motion concepts
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { RotateCcw, ChevronLeft, ChevronRight, Maximize2, X } from 'lucide-react';

const MotionVisualScene = ({ 
  onClose, 
  embedded = true,
  autoPlay = true,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [autoPosition, setAutoPosition] = useState(100);
  const [isMoving, setIsMoving] = useState(false);
  const [showVelocityArrow, setShowVelocityArrow] = useState(false);
  const [showDistanceMarker, setShowDistanceMarker] = useState(false);
  const [showFormula, setShowFormula] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [wheelRotation, setWheelRotation] = useState(0);
  
  const animationRef = useRef(null);
  const totalSteps = 3;

  // Auto-play animation
  useEffect(() => {
    if (currentStep === 0) {
      setShowDistanceMarker(true);
    } else if (currentStep === 1) {
      setIsMoving(true);
      animateAuto();
    } else if (currentStep === 2) {
      setShowFormula(true);
      setShowVelocityArrow(true);
    }
  }, [currentStep]);

  const animateAuto = () => {
    let pos = 100;
    let rotation = 0;
    
    const animate = () => {
      pos += 3;
      rotation += 15;
      
      if (pos >= 450) {
        setAutoPosition(450);
        setWheelRotation(rotation);
        setIsMoving(false);
        return;
      }
      
      setAutoPosition(pos);
      setWheelRotation(rotation);
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
    setAutoPosition(100);
    setIsMoving(false);
    setShowVelocityArrow(false);
    setShowDistanceMarker(false);
    setShowFormula(false);
    setWheelRotation(0);
  };

  const stepTitles = [
    "Auto at starting position (A)",
    "Auto travels distance (d)",
    "Velocity = Distance ÷ Time"
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

      {/* Scene */}
      <div className="relative" style={{ minHeight: '350px' }}>
        <svg viewBox="0 0 640 360" className="w-full h-full">
          <defs>
            <linearGradient id="sky2" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#81D4FA" />
              <stop offset="100%" stopColor="#E1F5FE" />
            </linearGradient>
            <linearGradient id="road" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#424242" />
              <stop offset="100%" stopColor="#212121" />
            </linearGradient>
            <filter id="shadow2">
              <feDropShadow dx="2" dy="4" stdDeviation="3" floodOpacity="0.3"/>
            </filter>
          </defs>

          {/* Sky */}
          <rect x="0" y="0" width="640" height="200" fill="url(#sky2)" />
          
          {/* Sun */}
          <circle cx="550" cy="60" r="40" fill="#FFD54F" opacity="0.8" />
          <circle cx="550" cy="60" r="30" fill="#FFEB3B" />
          
          {/* Buildings */}
          <rect x="20" y="80" width="80" height="120" fill="#90A4AE" />
          <rect x="30" y="95" width="20" height="25" fill="#64B5F6" opacity="0.8" />
          <rect x="60" y="95" width="20" height="25" fill="#64B5F6" opacity="0.8" />
          <rect x="30" y="130" width="20" height="25" fill="#64B5F6" opacity="0.8" />
          <rect x="60" y="130" width="20" height="25" fill="#64B5F6" opacity="0.8" />
          
          <rect x="520" y="60" width="100" height="140" fill="#78909C" />
          <rect x="535" y="80" width="25" height="30" fill="#64B5F6" opacity="0.8" />
          <rect x="575" y="80" width="25" height="30" fill="#64B5F6" opacity="0.8" />
          <rect x="535" y="120" width="25" height="30" fill="#64B5F6" opacity="0.8" />
          <rect x="575" y="120" width="25" height="30" fill="#64B5F6" opacity="0.8" />
          
          {/* Sidewalk */}
          <rect x="0" y="195" width="640" height="25" fill="#BDBDBD" />
          
          {/* Road */}
          <rect x="0" y="220" width="640" height="100" fill="url(#road)" />
          
          {/* Road markings */}
          {[80, 200, 320, 440, 560].map(x => (
            <rect key={x} x={x} y="265" width="50" height="8" fill="#FFC107" rx="2" />
          ))}
          
          {/* Divider line */}
          <line x1="0" y1="270" x2="640" y2="270" stroke="#FFC107" strokeWidth="3" strokeDasharray="20 15" />
          
          {/* Grass at bottom */}
          <rect x="0" y="320" width="640" height="40" fill="#7CB342" />

          {/* Distance markers */}
          {showDistanceMarker && (
            <g>
              {/* Point A */}
              <circle cx="100" cy="340" r="15" fill="#2196F3" />
              <text x="100" y="345" textAnchor="middle" fontSize="14" fill="white" fontWeight="bold">A</text>
              
              {/* Point B */}
              <circle cx="450" cy="340" r="15" fill="#4CAF50" />
              <text x="450" y="345" textAnchor="middle" fontSize="14" fill="white" fontWeight="bold">B</text>
              
              {/* Distance line */}
              <line x1="115" y1="340" x2="435" y2="340" stroke="#FF5722" strokeWidth="3" strokeDasharray="10 5">
                <animate attributeName="stroke-dashoffset" from="0" to="-15" dur="0.5s" repeatCount="indefinite" />
              </line>
              
              {/* Distance label */}
              <g transform="translate(275, 340)">
                <rect x="-45" y="-28" width="90" height="24" rx="5" fill="#FF5722" />
                <text x="0" y="-12" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">d = 100m</text>
              </g>
            </g>
          )}

          {/* ============ AUTO RICKSHAW ============ */}
          <g transform={`translate(${autoPosition}, 240)`} filter="url(#shadow2)">
            {/* Shadow */}
            <ellipse cx="0" cy="55" rx="45" ry="10" fill="rgba(0,0,0,0.3)" />
            
            {/* Body */}
            <path d="M -40 0 L -40 -35 L -30 -50 L 35 -50 L 45 -35 L 45 0 Z" fill="#4CAF50" stroke="#2E7D32" strokeWidth="2" />
            
            {/* Roof */}
            <path d="M -35 -50 L -30 -65 L 30 -65 L 35 -50" fill="#FDD835" stroke="#F9A825" strokeWidth="2" />
            
            {/* Front window */}
            <rect x="-35" y="-45" width="25" height="20" rx="3" fill="#81D4FA" stroke="#0288D1" strokeWidth="1" />
            
            {/* Passenger area */}
            <rect x="-5" y="-45" width="45" height="25" rx="3" fill="#81D4FA" stroke="#0288D1" strokeWidth="1" />
            
            {/* Headlight */}
            <circle cx="-42" cy="-20" r="6" fill="#FFEB3B" stroke="#FFC107" strokeWidth="1">
              {isMoving && (
                <animate attributeName="fill" values="#FFEB3B;#FFF59D;#FFEB3B" dur="0.3s" repeatCount="indefinite" />
              )}
            </circle>
            
            {/* Front wheel */}
            <g transform={`rotate(${wheelRotation} -30 8)`}>
              <circle cx="-30" cy="8" r="18" fill="#37474F" stroke="#263238" strokeWidth="3" />
              <circle cx="-30" cy="8" r="8" fill="#78909C" />
              <line x1="-30" y1="-5" x2="-30" y2="21" stroke="#546E7A" strokeWidth="2" />
              <line x1="-43" y1="8" x2="-17" y2="8" stroke="#546E7A" strokeWidth="2" />
            </g>
            
            {/* Rear wheel */}
            <g transform={`rotate(${wheelRotation} 30 8)`}>
              <circle cx="30" cy="8" r="18" fill="#37474F" stroke="#263238" strokeWidth="3" />
              <circle cx="30" cy="8" r="8" fill="#78909C" />
              <line x1="30" y1="-5" x2="30" y2="21" stroke="#546E7A" strokeWidth="2" />
              <line x1="17" y1="8" x2="43" y2="8" stroke="#546E7A" strokeWidth="2" />
            </g>
            
            {/* Auto text */}
            <text x="15" y="-55" textAnchor="middle" fontSize="10" fill="#1B5E20" fontWeight="bold">AUTO</text>
            
            {/* Exhaust smoke when moving */}
            {isMoving && (
              <g>
                <circle cx="-55" cy="-5" r="5" fill="#9E9E9E" opacity="0.5">
                  <animate attributeName="cx" from="-55" to="-80" dur="0.8s" repeatCount="indefinite" />
                  <animate attributeName="opacity" from="0.5" to="0" dur="0.8s" repeatCount="indefinite" />
                  <animate attributeName="r" from="5" to="12" dur="0.8s" repeatCount="indefinite" />
                </circle>
                <circle cx="-60" cy="-8" r="4" fill="#BDBDBD" opacity="0.4">
                  <animate attributeName="cx" from="-60" to="-90" dur="1s" repeatCount="indefinite" />
                  <animate attributeName="opacity" from="0.4" to="0" dur="1s" repeatCount="indefinite" />
                  <animate attributeName="r" from="4" to="10" dur="1s" repeatCount="indefinite" />
                </circle>
              </g>
            )}
          </g>

          {/* Velocity Arrow */}
          {showVelocityArrow && (
            <g transform={`translate(${autoPosition + 60}, 230)`}>
              <line x1="0" y1="0" x2="80" y2="0" stroke="#2196F3" strokeWidth="6" strokeLinecap="round">
                <animate attributeName="x2" from="0" to="80" dur="0.5s" fill="freeze" />
              </line>
              <polygon points="80,0 65,-10 65,10" fill="#2196F3" />
              
              {/* Label */}
              <g transform="translate(40, -25)">
                <rect x="-35" y="-12" width="70" height="24" rx="5" fill="#2196F3" />
                <text x="0" y="4" textAnchor="middle" fontSize="11" fill="white" fontWeight="bold">v = 10 m/s</text>
              </g>
            </g>
          )}

          {/* Formula Card */}
          {showFormula && (
            <g transform="translate(320, 100)">
              <rect x="-120" y="-60" width="240" height="110" rx="12" fill="white" stroke="#2196F3" strokeWidth="3" filter="url(#shadow2)" />
              <rect x="-115" y="-55" width="230" height="100" rx="10" fill="#E3F2FD" />
              
              <text x="0" y="-20" textAnchor="middle" fontSize="32" fill="#1565C0" fontWeight="bold" fontFamily="monospace">
                v = d / t
              </text>
              <text x="0" y="10" textAnchor="middle" fontSize="13" fill="#424242">
                Velocity = Distance ÷ Time
              </text>
              <text x="0" y="32" textAnchor="middle" fontSize="12" fill="#757575">
                वेग = दूरी ÷ समय
              </text>
              
              {/* Animated border */}
              <rect x="-120" y="-60" width="240" height="110" rx="12" fill="none" stroke="#2196F3" strokeWidth="2" strokeDasharray="15 8">
                <animate attributeName="stroke-dashoffset" from="0" to="46" dur="1.5s" repeatCount="indefinite" />
              </rect>
            </g>
          )}

          {/* Time indicator */}
          {currentStep >= 1 && (
            <g transform="translate(550, 280)">
              <rect x="-40" y="-20" width="80" height="35" rx="5" fill="#FF9800" />
              <text x="0" y="-2" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">⏱ t = 10s</text>
              <text x="0" y="12" textAnchor="middle" fontSize="9" fill="white">समय</text>
            </g>
          )}
          
          {/* Traffic Signal */}
          <g transform="translate(150, 150)">
            <rect x="-3" y="0" width="6" height="50" fill="#424242" />
            <rect x="-15" y="-40" width="30" height="45" rx="3" fill="#37474F" />
            <circle cx="0" cy="-28" r="8" fill={currentStep === 0 ? "#EF5350" : "#4A4A4A"} />
            <circle cx="0" cy="-10" r="8" fill={currentStep === 1 ? "#FFC107" : "#4A4A4A"} />
            <circle cx="0" cy="8" r="8" fill={currentStep >= 1 ? "#4CAF50" : "#4A4A4A"} />
          </g>
        </svg>

        {/* Top Controls */}
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
          <div className="text-xl font-bold text-blue-700 font-mono">v = d / t</div>
          <div className="text-xs text-gray-500">Velocity = Distance / Time</div>
        </div>
      </div>

      {/* Controls */}
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
                className={`w-3 h-3 rounded-full ${step === currentStep ? 'bg-blue-500 scale-125' : step < currentStep ? 'bg-green-500' : 'bg-gray-600'}`}
                animate={step === currentStep ? { scale: [1, 1.3, 1] } : {}}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
            ))}
          </div>

          <button
            onClick={handleNextStep}
            disabled={currentStep >= totalSteps - 1}
            className={`p-3 rounded-full transition-all ${currentStep >= totalSteps - 1 ? 'bg-gray-700 text-gray-500' : 'bg-blue-500 text-white hover:bg-blue-600 shadow-lg'}`}
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

export default MotionVisualScene;


