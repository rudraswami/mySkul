/**
 * Cinematic Force Visual Scene
 * 
 * Philosophy: The visual should be SO GOOD it explains itself
 * - No clutter, no extra buttons
 * - Immersive, cinematic experience
 * - Motion trails, particle effects
 * - Students will screenshot and share this naturally
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RotateCcw, Maximize2, X } from 'lucide-react';

const CinematicForceScene = ({ 
  onClose, 
  embedded = true,
  autoPlay = true,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [ballPosition, setBallPosition] = useState({ x: 200, y: 180 });
  const [ballTrail, setBallTrail] = useState([]);
  const [showForceArrow, setShowForceArrow] = useState(false);
  const [forceArrowLength, setForceArrowLength] = useState(0);
  const [professorArm, setProfessorArm] = useState(0);
  const [showFormula, setShowFormula] = useState(false);
  const [particles, setParticles] = useState([]);
  const [impactEffect, setImpactEffect] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [cameraX, setCameraX] = useState(0);
  
  const animationRef = useRef(null);
  const totalSteps = 3;

  // Cinematic auto-play sequence
  useEffect(() => {
    if (currentStep === 0) {
      // Step 1: Professor winds up, force arrow grows
      animateProfessorWindup();
    } else if (currentStep === 1) {
      // Step 2: Ball flies with trail, particles burst
      animateBallFlight();
    } else if (currentStep === 2) {
      // Step 3: Formula reveals cinematically
      animateFormulaReveal();
    }
  }, [currentStep]);

  // Auto-advance steps
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentStep < 2) {
        setCurrentStep(prev => prev + 1);
      }
    }, currentStep === 0 ? 2500 : currentStep === 1 ? 3000 : 5000);
    
    return () => clearTimeout(timer);
  }, [currentStep]);

  const animateProfessorWindup = async () => {
    // Arm winds back
    for (let i = 0; i <= 60; i++) {
      await delay(15);
      setProfessorArm(-i);
    }
    
    // Force arrow grows
    setShowForceArrow(true);
    for (let i = 0; i <= 100; i++) {
      await delay(10);
      setForceArrowLength(i);
    }
    
    // Create anticipation particles
    createParticles(200, 180, 5, '#FF9800');
  };

  const animateBallFlight = async () => {
    // Professor throws
    for (let i = -60; i <= 30; i += 5) {
      await delay(20);
      setProfessorArm(i);
    }
    
    // Ball trajectory with trail
    let startX = 200;
    let startY = 180;
    let time = 0;
    const trail = [];
    
    const animate = () => {
      time += 0.04;
      
      if (time > 1.8) {
        setBallPosition({ x: 520, y: 220 });
        setImpactEffect(true);
        createParticles(520, 220, 15, '#D32F2F');
        setTimeout(() => setImpactEffect(false), 500);
        return;
      }
      
      // Smooth projectile motion
      const x = startX + 200 * time;
      const y = startY - 100 * Math.sin(time * Math.PI * 0.5) + 30 * time;
      
      // Add to trail
      trail.push({ x, y, opacity: 1 - time * 0.5 });
      if (trail.length > 15) trail.shift();
      setBallTrail([...trail]);
      
      setBallPosition({ x, y });
      
      // Camera follows ball slightly
      setCameraX(-time * 20);
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
  };

  const animateFormulaReveal = async () => {
    // Zoom out slightly for formula
    setZoomLevel(0.95);
    await delay(300);
    setShowFormula(true);
    
    // Particles celebrate
    createParticles(320, 100, 20, '#4CAF50');
  };

  const createParticles = (x, y, count, color) => {
    const newParticles = [];
    for (let i = 0; i < count; i++) {
      newParticles.push({
        id: Date.now() + i,
        x,
        y,
        vx: (Math.random() - 0.5) * 8,
        vy: (Math.random() - 0.5) * 8 - 3,
        color,
        size: Math.random() * 6 + 2,
        life: 1,
      });
    }
    setParticles(prev => [...prev, ...newParticles]);
    
    // Animate particles
    const animateParticles = () => {
      setParticles(prev => {
        const updated = prev.map(p => ({
          ...p,
          x: p.x + p.vx,
          y: p.y + p.vy,
          vy: p.vy + 0.3, // gravity
          life: p.life - 0.02,
        })).filter(p => p.life > 0);
        
        if (updated.length > 0) {
          requestAnimationFrame(animateParticles);
        }
        return updated;
      });
    };
    requestAnimationFrame(animateParticles);
  };

  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const handleReplay = () => {
    setCurrentStep(0);
    setBallPosition({ x: 200, y: 180 });
    setBallTrail([]);
    setShowForceArrow(false);
    setForceArrowLength(0);
    setProfessorArm(0);
    setShowFormula(false);
    setParticles([]);
    setImpactEffect(false);
    setZoomLevel(1);
    setCameraX(0);
    
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  };

  const stepTitles = [
    "Professor winds up... Force builds!",
    "RELEASE! Ball accelerates →",
    "F = m × a — The magic equation!"
  ];

  return (
    <motion.div
      className={`relative rounded-2xl overflow-hidden shadow-2xl ${isExpanded ? 'fixed inset-4 z-50' : ''}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {isExpanded && (
        <div className="fixed inset-0 bg-black/90 -z-10" onClick={() => setIsExpanded(false)} />
      )}

      {/* Main Scene - CLEAN, NO CLUTTER */}
      <motion.div 
        className="relative overflow-hidden"
        style={{ minHeight: embedded ? '400px' : '500px' }}
        animate={{ scale: zoomLevel }}
        transition={{ duration: 0.5 }}
      >
        <motion.svg 
          viewBox="0 0 640 380" 
          className="w-full h-full"
          animate={{ x: cameraX }}
          transition={{ type: 'spring', stiffness: 50 }}
        >
          <defs>
            {/* Beautiful gradients */}
            <linearGradient id="skyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#4FC3F7" />
              <stop offset="50%" stopColor="#81D4FA" />
              <stop offset="100%" stopColor="#E1F5FE" />
            </linearGradient>
            
            <linearGradient id="grassGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#66BB6A" />
              <stop offset="100%" stopColor="#388E3C" />
            </linearGradient>
            
            <linearGradient id="pitchGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#EFEBE9" />
              <stop offset="100%" stopColor="#D7CCC8" />
            </linearGradient>
            
            <linearGradient id="forceArrowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#FF5722" />
              <stop offset="100%" stopColor="#FF9800" />
            </linearGradient>
            
            {/* Glow effects */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="8" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>

            {/* Motion blur for ball */}
            <filter id="motionBlur" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="3 0" />
            </filter>
          </defs>

          {/* === SKY === */}
          <rect x="0" y="0" width="700" height="240" fill="url(#skyGradient)" />
          
          {/* Sun with rays */}
          <g transform="translate(560, 60)">
            {/* Sun rays */}
            {[...Array(12)].map((_, i) => (
              <line 
                key={i}
                x1="0" y1="0" 
                x2={Math.cos(i * 30 * Math.PI / 180) * 60} 
                y2={Math.sin(i * 30 * Math.PI / 180) * 60}
                stroke="#FFD54F" 
                strokeWidth="3" 
                opacity="0.4"
              >
                <animate 
                  attributeName="opacity" 
                  values="0.2;0.5;0.2" 
                  dur={`${2 + i * 0.1}s`} 
                  repeatCount="indefinite" 
                />
              </line>
            ))}
            <circle cx="0" cy="0" r="40" fill="#FFD54F" filter="url(#softGlow)" />
            <circle cx="0" cy="0" r="32" fill="#FFEB3B" />
            <circle cx="-8" cy="-8" r="10" fill="#FFF9C4" opacity="0.6" />
          </g>
          
          {/* Animated clouds */}
          <g opacity="0.9">
            <ellipse cx="120" cy="70" rx="50" ry="25" fill="white">
              <animate attributeName="cx" values="120;130;120" dur="8s" repeatCount="indefinite" />
            </ellipse>
            <ellipse cx="160" cy="65" rx="40" ry="20" fill="white">
              <animate attributeName="cx" values="160;170;160" dur="8s" repeatCount="indefinite" />
            </ellipse>
            <ellipse cx="90" cy="65" rx="30" ry="18" fill="white">
              <animate attributeName="cx" values="90;100;90" dur="8s" repeatCount="indefinite" />
            </ellipse>
          </g>
          
          <g opacity="0.7">
            <ellipse cx="380" cy="50" rx="60" ry="28" fill="white">
              <animate attributeName="cx" values="380;395;380" dur="10s" repeatCount="indefinite" />
            </ellipse>
            <ellipse cx="430" cy="45" rx="45" ry="22" fill="white">
              <animate attributeName="cx" values="430;445;430" dur="10s" repeatCount="indefinite" />
            </ellipse>
          </g>

          {/* === GROUND === */}
          <rect x="0" y="240" width="700" height="150" fill="url(#grassGradient)" />
          
          {/* Grass blades animation */}
          {[...Array(25)].map((_, i) => (
            <path 
              key={i}
              d={`M ${i * 28 + 10} 380 Q ${i * 28 + 15} ${360 + Math.sin(i) * 5} ${i * 28 + 20} 380`}
              stroke="#81C784" 
              strokeWidth="3" 
              fill="none"
            >
              <animate 
                attributeName="d" 
                values={`M ${i * 28 + 10} 380 Q ${i * 28 + 15} 360 ${i * 28 + 20} 380;M ${i * 28 + 10} 380 Q ${i * 28 + 18} 358 ${i * 28 + 20} 380;M ${i * 28 + 10} 380 Q ${i * 28 + 15} 360 ${i * 28 + 20} 380`}
                dur={`${2 + i * 0.1}s`}
                repeatCount="indefinite"
              />
            </path>
          ))}
          
          {/* Cricket Pitch - Premium look */}
          <rect x="80" y="260" width="480" height="100" rx="8" fill="url(#pitchGradient)" />
          <rect x="85" y="265" width="470" height="90" rx="6" fill="#E8E0DB" opacity="0.5" />
          
          {/* Pitch markings */}
          <line x1="150" y1="260" x2="150" y2="360" stroke="white" strokeWidth="3" opacity="0.6" />
          <line x1="490" y1="260" x2="490" y2="360" stroke="white" strokeWidth="3" opacity="0.6" />
          
          {/* Elegant boundary */}
          <ellipse cx="320" cy="310" rx="300" ry="55" fill="none" stroke="white" strokeWidth="2" strokeDasharray="15 10" opacity="0.3" />

          {/* === PROFESSOR (Cinematic) === */}
          <g transform="translate(100, 180)">
            {/* Dynamic shadow */}
            <ellipse cx="0" cy="110" rx={35 + Math.abs(professorArm) * 0.1} ry="12" fill="rgba(0,0,0,0.15)" />
            
            {/* Body with slight lean */}
            <g transform={`rotate(${professorArm * 0.1} 0 50)`}>
              {/* Kurta */}
              <path d="M -28 30 L -35 100 L 35 100 L 28 30 Q 0 42 -28 30" fill="#1565C0" stroke="#0D47A1" strokeWidth="2" />
              <path d="M -15 30 L 0 48 L 15 30" fill="#1976D2" />
              
              {/* Legs */}
              <rect x="-20" y="100" width="16" height="45" fill="#37474F" rx="3" />
              <rect x="4" y="100" width="16" height="45" fill="#37474F" rx="3" />
              
              {/* Shoes */}
              <ellipse cx="-12" cy="148" rx="14" ry="7" fill="#4E342E" />
              <ellipse cx="12" cy="148" rx="14" ry="7" fill="#4E342E" />
            </g>
            
            {/* Throwing arm - DYNAMIC */}
            <g transform={`rotate(${professorArm} -20 35)`}>
              <path d="M -28 35 L -65 55" stroke="#FFCCBC" strokeWidth="12" strokeLinecap="round" />
              <circle cx="-68" cy="57" r="10" fill="#FFCCBC" />
              {/* Fist detail */}
              <circle cx="-72" cy="55" r="5" fill="#FFB899" />
            </g>
            
            {/* Other arm */}
            <path d="M 28 40 L 50 70" stroke="#FFCCBC" strokeWidth="12" strokeLinecap="round" />
            <circle cx="52" cy="72" r="10" fill="#FFCCBC" />
            
            {/* Head */}
            <circle cx="0" cy="0" r="32" fill="#FFCCBC" stroke="#FFAB91" strokeWidth="2" />
            
            {/* Hair */}
            <path d="M -30 -12 Q -32 -38 -18 -42 Q 0 -48 18 -42 Q 32 -38 30 -12" fill="#1a1a1a" />
            
            {/* Expressive eyes based on step */}
            <g>
              <ellipse cx="-12" cy="-2" rx={currentStep === 1 ? 6 : 5} ry={currentStep === 1 ? 7 : 6} fill="#212121" />
              <ellipse cx="12" cy="-2" rx={currentStep === 1 ? 6 : 5} ry={currentStep === 1 ? 7 : 6} fill="#212121" />
              <circle cx="-10" cy="-4" r="2" fill="white" />
              <circle cx="14" cy="-4" r="2" fill="white" />
            </g>
            
            {/* Glasses */}
            <circle cx="-12" cy="-2" r="12" fill="none" stroke="#333" strokeWidth="2.5" />
            <circle cx="12" cy="-2" r="12" fill="none" stroke="#333" strokeWidth="2.5" />
            <line x1="0" y1="-2" x2="0" y2="-2" stroke="#333" strokeWidth="2.5" />
            <line x1="24" y1="-5" x2="32" y2="-10" stroke="#333" strokeWidth="2.5" />
            <line x1="-24" y1="-5" x2="-32" y2="-10" stroke="#333" strokeWidth="2.5" />
            
            {/* Mustache */}
            <path d="M -12 12 Q -6 16 0 12 Q 6 16 12 12" fill="#333" />
            
            {/* Smile - changes with step */}
            <path 
              d={currentStep === 2 ? "M -10 22 Q 0 35 10 22" : "M -8 20 Q 0 28 8 20"} 
              fill="none" 
              stroke="#5D4037" 
              strokeWidth="2.5" 
            />
          </g>

          {/* === BALL TRAIL (Motion effect) === */}
          {ballTrail.map((point, i) => (
            <circle 
              key={i}
              cx={point.x} 
              cy={point.y} 
              r={8 - i * 0.4}
              fill="#D32F2F"
              opacity={point.opacity * 0.6}
            />
          ))}

          {/* === CRICKET BALL === */}
          <g transform={`translate(${ballPosition.x}, ${ballPosition.y})`}>
            {/* Ball shadow */}
            <ellipse cx="8" cy="25" rx="18" ry="6" fill="rgba(0,0,0,0.2)" />
            
            {/* Ball glow when moving */}
            {currentStep === 1 && (
              <circle cx="0" cy="0" r="28" fill="#FF5722" opacity="0.3" filter="url(#softGlow)">
                <animate attributeName="r" values="25;35;25" dur="0.3s" repeatCount="indefinite" />
              </circle>
            )}
            
            {/* Main ball */}
            <circle cx="0" cy="0" r="22" fill="#D32F2F" stroke="#8B0000" strokeWidth="2" />
            
            {/* Ball texture */}
            <path d="M -14 -14 Q 0 0 14 14" stroke="white" strokeWidth="2.5" fill="none" />
            <path d="M -16 -10 Q 0 5 16 10" stroke="white" strokeWidth="1.5" fill="none" strokeDasharray="4 3" />
            
            {/* Shine */}
            <circle cx="-7" cy="-10" r="6" fill="white" opacity="0.4" />
            <circle cx="-4" cy="-6" r="3" fill="white" opacity="0.6" />
            
            {/* Rotation effect when flying */}
            {currentStep === 1 && (
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0"
                to="360"
                dur="0.2s"
                repeatCount="indefinite"
                additive="sum"
              />
            )}
          </g>

          {/* === FORCE ARROW (Cinematic grow) === */}
          {showForceArrow && (
            <g transform={`translate(${ballPosition.x + 30}, ${ballPosition.y})`}>
              {/* Arrow glow */}
              <line 
                x1="0" y1="0" 
                x2={forceArrowLength * 1.5} y2="0"
                stroke="#FF9800"
                strokeWidth="18"
                strokeLinecap="round"
                opacity="0.4"
                filter="url(#softGlow)"
              />
              
              {/* Main arrow */}
              <line 
                x1="0" y1="0" 
                x2={forceArrowLength * 1.5} y2="0"
                stroke="url(#forceArrowGrad)"
                strokeWidth="10"
                strokeLinecap="round"
              />
              
              {/* Arrow head */}
              {forceArrowLength > 50 && (
                <polygon 
                  points={`${forceArrowLength * 1.5 + 5},0 ${forceArrowLength * 1.5 - 15},-15 ${forceArrowLength * 1.5 - 15},15`}
                  fill="#FF5722"
                />
              )}
              
              {/* Force label */}
              {forceArrowLength > 80 && (
                <g transform={`translate(${forceArrowLength * 0.75}, -35)`}>
                  <rect x="-35" y="-18" width="70" height="36" rx="8" fill="#FF5722" filter="url(#glow)" />
                  <text x="0" y="6" textAnchor="middle" fontSize="18" fill="white" fontWeight="bold">F →</text>
                </g>
              )}
            </g>
          )}

          {/* === IMPACT EFFECT === */}
          {impactEffect && (
            <g transform={`translate(${ballPosition.x}, ${ballPosition.y})`}>
              {[...Array(3)].map((_, i) => (
                <circle 
                  key={i}
                  cx="0" cy="0" 
                  r="20"
                  fill="none" 
                  stroke="#FF5722" 
                  strokeWidth="4"
                  opacity="0.8"
                >
                  <animate attributeName="r" from="20" to={80 + i * 20} dur="0.5s" fill="freeze" />
                  <animate attributeName="opacity" from="0.8" to="0" dur="0.5s" fill="freeze" />
                </circle>
              ))}
            </g>
          )}

          {/* === STUMPS === */}
          <g transform="translate(550, 270)">
            <rect x="-20" y="0" width="8" height="70" fill="#8D6E63" rx="2" />
            <rect x="-4" y="0" width="8" height="70" fill="#8D6E63" rx="2" />
            <rect x="12" y="0" width="8" height="70" fill="#8D6E63" rx="2" />
            {/* Bails with shine */}
            <rect x="-18" y="-6" width="16" height="5" fill="#FFC107" rx="2">
              <animate attributeName="fill" values="#FFC107;#FFD54F;#FFC107" dur="2s" repeatCount="indefinite" />
            </rect>
            <rect x="2" y="-6" width="16" height="5" fill="#FFC107" rx="2">
              <animate attributeName="fill" values="#FFC107;#FFD54F;#FFC107" dur="2s" repeatCount="indefinite" begin="0.5s" />
            </rect>
          </g>

          {/* === BAT === */}
          <g transform="translate(470, 290) rotate(-25)">
            <rect x="-6" y="-55" width="12" height="28" fill="#5D4037" rx="3" />
            <rect x="-14" y="-27" width="28" height="70" fill="#EFEBE9" rx="4" stroke="#A1887F" strokeWidth="1" />
            {/* Bat grain lines */}
            <line x1="-8" y1="-20" x2="-8" y2="35" stroke="#D7CCC8" strokeWidth="1" />
            <line x1="0" y1="-20" x2="0" y2="35" stroke="#D7CCC8" strokeWidth="1" />
            <line x1="8" y1="-20" x2="8" y2="35" stroke="#D7CCC8" strokeWidth="1" />
          </g>

          {/* === PARTICLES === */}
          {particles.map(p => (
            <circle 
              key={p.id}
              cx={p.x} 
              cy={p.y} 
              r={p.size * p.life}
              fill={p.color}
              opacity={p.life}
            />
          ))}

          {/* === FORMULA (Cinematic Reveal) === */}
          <AnimatePresence>
            {showFormula && (
              <motion.g
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, type: 'spring' }}
              >
                {/* Backdrop blur effect */}
                <rect x="170" y="40" width="300" height="130" rx="20" fill="white" opacity="0.95" filter="url(#softGlow)" />
                <rect x="175" y="45" width="290" height="120" rx="18" fill="#FFF8E1" />
                
                {/* Main formula */}
                <text x="320" y="95" textAnchor="middle" fontSize="48" fill="#E65100" fontWeight="bold" fontFamily="Georgia, serif">
                  F = m × a
                </text>
                
                {/* Subtitle */}
                <text x="320" y="125" textAnchor="middle" fontSize="14" fill="#5D4037">
                  Force = Mass × Acceleration
                </text>
                <text x="320" y="148" textAnchor="middle" fontSize="13" fill="#8D6E63">
                  बल = द्रव्यमान × त्वरण
                </text>
                
                {/* Decorative elements */}
                <circle cx="185" cy="105" r="8" fill="#FF9800" opacity="0.3" />
                <circle cx="455" cy="105" r="8" fill="#FF9800" opacity="0.3" />
              </motion.g>
            )}
          </AnimatePresence>

          {/* === MASS LABEL (follows ball) === */}
          <g transform={`translate(${ballPosition.x}, ${ballPosition.y + 40})`}>
            <rect x="-40" y="0" width="80" height="26" rx="6" fill="white" stroke="#FFC107" strokeWidth="2" opacity="0.95" />
            <text x="0" y="18" textAnchor="middle" fontSize="13" fill="#5D4037" fontWeight="bold">m = 0.15 kg</text>
          </g>

        </motion.svg>

        {/* === MINIMAL UI === */}
        
        {/* Formula badge - top left */}
        <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-xl px-5 py-3 shadow-lg border border-gray-100">
          <div className="text-2xl font-bold text-gray-800 font-serif tracking-wide">F = m × a</div>
          <div className="text-xs text-gray-500 mt-0.5">Newton's Second Law</div>
        </div>

        {/* Minimal controls - top right */}
        <div className="absolute top-4 right-4 flex space-x-2">
          <motion.button 
            onClick={handleReplay}
            className="p-2.5 bg-white/90 backdrop-blur-sm rounded-full shadow-lg hover:bg-white transition-all"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <RotateCcw className="w-5 h-5 text-gray-700" />
          </motion.button>
          <motion.button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2.5 bg-white/90 backdrop-blur-sm rounded-full shadow-lg hover:bg-white transition-all"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            {isExpanded ? <X className="w-5 h-5 text-gray-700" /> : <Maximize2 className="w-5 h-5 text-gray-700" />}
          </motion.button>
        </div>
      </motion.div>

      {/* === ELEGANT BOTTOM BAR === */}
      <div className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 px-6 py-4">
        <div className="flex items-center justify-between max-w-lg mx-auto">
          {/* Step dots */}
          <div className="flex items-center space-x-4">
            {[0, 1, 2].map((step) => (
              <motion.div
                key={step}
                className={`transition-all ${
                  step === currentStep 
                    ? 'w-8 h-3 bg-orange-500 rounded-full' 
                    : step < currentStep 
                      ? 'w-3 h-3 bg-green-500 rounded-full' 
                      : 'w-3 h-3 bg-gray-600 rounded-full'
                }`}
                animate={step === currentStep ? { scale: [1, 1.1, 1] } : {}}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
            ))}
          </div>
        </div>

        {/* Step description */}
        <motion.p 
          className="text-center text-white font-medium mt-3 text-lg"
          key={currentStep}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {stepTitles[currentStep]}
        </motion.p>
      </div>
    </motion.div>
  );
};

export default CinematicForceScene;









