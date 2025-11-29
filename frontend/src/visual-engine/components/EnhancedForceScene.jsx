/**
 * Enhanced Force Visual Scene - NEXT LEVEL
 * 
 * Features:
 * - Interactive quiz after watching
 * - Exam tips overlay
 * - Voice narration ready
 * - Shareable moments
 * - Related concepts
 * - Common mistakes
 * - Speed controls
 * - Dark mode support
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  RotateCcw, ChevronLeft, ChevronRight, Maximize2, X, 
  Volume2, VolumeX, Share2, BookOpen, Zap, Award, 
  HelpCircle, CheckCircle, XCircle, Lightbulb, Target,
  Play, Pause, FastForward, Clock, Star, MessageCircle
} from 'lucide-react';

const EnhancedForceScene = ({ 
  onClose, 
  embedded = true,
  autoPlay = true,
  darkMode = false,
  onXPEarned,
  onShare,
}) => {
  // Scene state
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [ballPosition, setBallPosition] = useState({ x: 180, y: 200 });
  const [showForceArrow, setShowForceArrow] = useState(false);
  const [professorGesture, setProfessorGesture] = useState('ready');
  const [showFormula, setShowFormula] = useState(false);
  const [highlightedItem, setHighlightedItem] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Enhanced features state
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizAnswer, setQuizAnswer] = useState(null);
  const [showExamTip, setShowExamTip] = useState(false);
  const [showMistakes, setShowMistakes] = useState(false);
  const [showRelated, setShowRelated] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [xpEarned, setXpEarned] = useState(0);
  const [interactionCount, setInteractionCount] = useState(0);
  const [showShareMenu, setShowShareMenu] = useState(false);
  const [showAskDoubt, setShowAskDoubt] = useState(false);
  
  const animationRef = useRef(null);
  const totalSteps = 3;

  // Track interactions for XP
  const trackInteraction = (type) => {
    setInteractionCount(prev => prev + 1);
    
    // Award XP for interactions
    const xpMap = {
      'tap_object': 5,
      'watch_step': 10,
      'complete_quiz': 25,
      'view_exam_tip': 15,
      'share': 20,
    };
    
    const earned = xpMap[type] || 5;
    setXpEarned(prev => prev + earned);
    onXPEarned?.(earned);
  };

  // Animation logic (same as before)
  useEffect(() => {
    if (!isPlaying) return;

    const runStep = async () => {
      trackInteraction('watch_step');
      
      switch (currentStep) {
        case 0:
          setProfessorGesture('pointing');
          await delay(800 / playbackSpeed);
          setShowForceArrow(true);
          break;
        case 1:
          setProfessorGesture('throwing');
          await delay(300 / playbackSpeed);
          animateBall();
          break;
        case 2:
          setProfessorGesture('explaining');
          setShowFormula(true);
          // Show quiz after completing all steps
          await delay(2000 / playbackSpeed);
          setShowQuiz(true);
          break;
      }
    };

    runStep();
  }, [currentStep, isPlaying, playbackSpeed]);

  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const animateBall = () => {
    let startX = 180;
    let startY = 200;
    let time = 0;
    
    const animate = () => {
      time += 0.05 * playbackSpeed;
      if (time > 1.5) {
        setBallPosition({ x: 520, y: 240 });
        return;
      }
      
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
    setCurrentStep(0);
    setBallPosition({ x: 180, y: 200 });
    setShowForceArrow(false);
    setProfessorGesture('ready');
    setShowFormula(false);
    setShowQuiz(false);
    setQuizAnswer(null);
    setIsPlaying(true);
    
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  };

  const handleQuizAnswer = (answer, isCorrect) => {
    setQuizAnswer({ answer, isCorrect });
    if (isCorrect) {
      trackInteraction('complete_quiz');
    }
  };

  const handleShare = () => {
    trackInteraction('share');
    setShowShareMenu(true);
    onShare?.();
  };

  const stepTitles = [
    "Professor applies force on ball",
    "Ball accelerates forward!",
    "F = m × a explains it all!"
  ];

  const bgClass = darkMode 
    ? 'bg-gradient-to-b from-gray-900 to-gray-800' 
    : 'bg-gradient-to-b from-blue-200 to-green-300';

  return (
    <motion.div
      className={`relative rounded-2xl overflow-hidden shadow-2xl ${isExpanded ? 'fixed inset-4 z-50' : ''}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {isExpanded && (
        <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />
      )}

      {/* Main Scene */}
      <div className={`relative ${bgClass}`} style={{ minHeight: embedded ? '380px' : '480px' }}>
        {/* SVG Scene */}
        <svg 
          viewBox="0 0 640 360" 
          className="w-full h-full"
          style={{ background: darkMode 
            ? 'linear-gradient(180deg, #1a1a2e 0%, #16213e 60%, #1f4037 60%, #0f2027 100%)' 
            : 'linear-gradient(180deg, #87CEEB 0%, #E0F7FA 60%, #7CB342 60%, #558B2F 100%)' 
          }}
        >
          <defs>
            <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={darkMode ? "#1a1a2e" : "#64B5F6"} />
              <stop offset="100%" stopColor={darkMode ? "#16213e" : "#E3F2FD"} />
            </linearGradient>
            <linearGradient id="grassGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={darkMode ? "#1f4037" : "#7CB342"} />
              <stop offset="100%" stopColor={darkMode ? "#0f2027" : "#558B2F"} />
            </linearGradient>
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
          
          {/* Sun/Moon */}
          {darkMode ? (
            <g>
              <circle cx="580" cy="50" r="30" fill="#F5F5F5" opacity="0.9" />
              <circle cx="570" cy="45" r="8" fill="#E0E0E0" opacity="0.5" />
              <circle cx="590" cy="55" r="5" fill="#E0E0E0" opacity="0.5" />
              {/* Stars */}
              {[...Array(15)].map((_, i) => (
                <circle key={i} cx={50 + i * 40} cy={30 + (i % 3) * 20} r="1.5" fill="white" opacity="0.8">
                  <animate attributeName="opacity" values="0.4;1;0.4" dur={`${1 + i * 0.2}s`} repeatCount="indefinite" />
                </circle>
              ))}
            </g>
          ) : (
            <g>
              <circle cx="580" cy="50" r="35" fill="#FFD54F" opacity="0.9">
                <animate attributeName="r" values="35;38;35" dur="3s" repeatCount="indefinite" />
              </circle>
              <circle cx="580" cy="50" r="25" fill="#FFEB3B" />
            </g>
          )}
          
          {/* Clouds */}
          <g opacity={darkMode ? "0.3" : "0.8"}>
            <ellipse cx="100" cy="60" rx="40" ry="20" fill="white" />
            <ellipse cx="130" cy="55" rx="35" ry="18" fill="white" />
            <ellipse cx="80" cy="55" rx="25" ry="15" fill="white" />
          </g>

          {/* Ground/Grass */}
          <rect x="0" y="220" width="640" height="140" fill="url(#grassGrad)" />
          
          {/* Cricket Pitch */}
          <rect x="100" y="250" width="440" height="80" rx="5" fill={darkMode ? "#3d3d3d" : "#D7CCC8"} />
          <line x1="150" y1="250" x2="150" y2="330" stroke="white" strokeWidth="2" opacity="0.5" />
          <line x1="490" y1="250" x2="490" y2="330" stroke="white" strokeWidth="2" opacity="0.5" />
          
          {/* Boundary */}
          <ellipse cx="320" cy="290" rx="280" ry="50" fill="none" stroke="white" strokeWidth="2" strokeDasharray="10 5" opacity="0.3" />

          {/* ============ PROFESSOR ============ */}
          <g 
            transform="translate(80, 180)"
            onClick={() => { handleObjectTap('professor'); trackInteraction('tap_object'); }}
            style={{ cursor: 'pointer' }}
          >
            {highlightedItem === 'professor' && (
              <circle cx="0" cy="30" r="60" fill="none" stroke="#FF9800" strokeWidth="3" opacity="0.6" filter="url(#glow)">
                <animate attributeName="r" values="55;65;55" dur="0.8s" repeatCount="indefinite" />
              </circle>
            )}
            
            <ellipse cx="0" cy="95" rx="30" ry="10" fill="rgba(0,0,0,0.2)" />
            <path d="M -25 25 L -30 90 L 30 90 L 25 25 Q 0 35 -25 25" fill="#1565C0" stroke="#0D47A1" strokeWidth="2" />
            <path d="M -12 25 L 0 40 L 12 25" fill="#1976D2" />
            <rect x="-18" y="90" width="14" height="40" fill="#37474F" rx="2" />
            <rect x="4" y="90" width="14" height="40" fill="#37474F" rx="2" />
            <ellipse cx="-11" cy="132" rx="12" ry="6" fill="#4E342E" />
            <ellipse cx="11" cy="132" rx="12" ry="6" fill="#4E342E" />
            
            <g transform={`rotate(${professorGesture === 'pointing' ? -60 : professorGesture === 'throwing' ? -80 : -10} -20 30)`}>
              <path d="M -25 30 L -55 50" stroke="#FFCCBC" strokeWidth="10" strokeLinecap="round" fill="none" />
              <circle cx="-58" cy="52" r="8" fill="#FFCCBC" />
              {professorGesture === 'pointing' && (
                <line x1="-58" y1="52" x2="-75" y2="42" stroke="#FFCCBC" strokeWidth="5" strokeLinecap="round" />
              )}
            </g>
            
            <g transform={`rotate(${professorGesture === 'throwing' ? 30 : 15} 20 30)`}>
              <path d="M 25 30 L 50 55" stroke="#FFCCBC" strokeWidth="10" strokeLinecap="round" fill="none" />
              <circle cx="52" cy="58" r="8" fill="#FFCCBC" />
            </g>
            
            <circle cx="0" cy="0" r="28" fill="#FFCCBC" stroke="#FFAB91" strokeWidth="2" />
            <path d="M -26 -10 Q -28 -32 -15 -35 Q 0 -40 15 -35 Q 28 -32 26 -10" fill="#212121" />
            <ellipse cx="-10" cy="-2" rx="4" ry="5" fill="#212121" />
            <ellipse cx="10" cy="-2" rx="4" ry="5" fill="#212121" />
            <circle cx="-9" cy="-3" r="1.5" fill="white" />
            <circle cx="11" cy="-3" r="1.5" fill="white" />
            <circle cx="-10" cy="-2" r="10" fill="none" stroke="#424242" strokeWidth="2" />
            <circle cx="10" cy="-2" r="10" fill="none" stroke="#424242" strokeWidth="2" />
            <path d="M -10 12 Q -5 15 0 12 Q 5 15 10 12" fill="#424242" />
            <path d="M -8 18 Q 0 25 8 18" fill="none" stroke="#5D4037" strokeWidth="2" />
            
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
            onClick={() => { handleObjectTap('ball'); trackInteraction('tap_object'); }}
            style={{ cursor: 'pointer' }}
          >
            {highlightedItem === 'ball' && (
              <circle cx="0" cy="0" r="30" fill="none" stroke="#FF9800" strokeWidth="3" opacity="0.8" filter="url(#glow)">
                <animate attributeName="r" values="25;35;25" dur="0.6s" repeatCount="indefinite" />
              </circle>
            )}
            
            <ellipse cx="5" cy="20" rx="15" ry="5" fill="rgba(0,0,0,0.3)" />
            <circle cx="0" cy="0" r="18" fill="#D32F2F" stroke="#8B0000" strokeWidth="2" />
            <path d="M -12 -12 Q 0 0 12 12" stroke="white" strokeWidth="2" fill="none" />
            <circle cx="-6" cy="-8" r="4" fill="white" opacity="0.4" />
            
            <g transform="translate(0, 35)">
              <rect x="-30" y="-10" width="60" height="20" rx="4" fill="#FFF9C4" stroke="#FFC107" strokeWidth="1" />
              <text x="0" y="4" textAnchor="middle" fontSize="10" fill="#5D4037" fontWeight="bold">m = 0.15 kg</text>
            </g>
            
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
              <line 
                x1={ballPosition.x + 25} 
                y1={ballPosition.y} 
                x2={ballPosition.x + 145} 
                y2={ballPosition.y}
                stroke="#FF5722"
                strokeWidth="8"
                strokeLinecap="round"
              >
                <animate attributeName="x2" from={ballPosition.x + 25} to={ballPosition.x + 145} dur="0.5s" fill="freeze" />
              </line>
              
              <polygon 
                points={`${ballPosition.x + 150},${ballPosition.y} ${ballPosition.x + 130},${ballPosition.y - 15} ${ballPosition.x + 130},${ballPosition.y + 15}`}
                fill="#FF5722"
              />
              
              <g transform={`translate(${ballPosition.x + 90}, ${ballPosition.y - 30})`}>
                <rect x="-35" y="-15" width="70" height="28" rx="5" fill="#FF5722" />
                <text x="0" y="4" textAnchor="middle" fontSize="14" fill="white" fontWeight="bold">F (बल)</text>
              </g>
            </g>
          )}

          {/* ============ STUMPS ============ */}
          <g transform="translate(540, 260)" onClick={() => trackInteraction('tap_object')} style={{ cursor: 'pointer' }}>
            <rect x="-18" y="0" width="6" height="60" fill="#8D6E63" rx="1" />
            <rect x="-3" y="0" width="6" height="60" fill="#8D6E63" rx="1" />
            <rect x="12" y="0" width="6" height="60" fill="#8D6E63" rx="1" />
            <rect x="-16" y="-5" width="14" height="4" fill="#FFC107" rx="1" />
            <rect x="2" y="-5" width="14" height="4" fill="#FFC107" rx="1" />
          </g>

          {/* ============ BAT ============ */}
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
            </g>
          )}

          {/* Acceleration indicator */}
          {currentStep >= 1 && (
            <g transform="translate(380, 230)">
              <rect x="-50" y="-15" width="100" height="28" rx="5" fill="#4CAF50" />
              <text x="0" y="5" textAnchor="middle" fontSize="12" fill="white" fontWeight="bold">a = F/m ↑</text>
            </g>
          )}
        </svg>

        {/* ============ TOP CONTROLS ============ */}
        <div className="absolute top-3 left-3 bg-white/95 rounded-xl px-4 py-2 shadow-lg">
          <div className="text-xl font-bold text-gray-800 font-mono">F = m × a</div>
          <div className="text-xs text-gray-500">Force = Mass × Acceleration</div>
        </div>

        <div className="absolute top-3 right-3 flex space-x-2 z-10">
          {/* XP Badge */}
          {xpEarned > 0 && (
            <motion.div 
              className="flex items-center space-x-1 bg-yellow-400 text-yellow-900 px-3 py-1.5 rounded-full font-bold text-sm"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            >
              <Zap className="w-4 h-4" />
              <span>+{xpEarned} XP</span>
            </motion.div>
          )}
          
          {/* Speed control */}
          <button
            onClick={() => setPlaybackSpeed(prev => prev === 2 ? 0.5 : prev + 0.5)}
            className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white transition-all"
            title={`Speed: ${playbackSpeed}x`}
          >
            <span className="text-xs font-bold text-gray-700">{playbackSpeed}x</span>
          </button>
          
          {/* Sound toggle */}
          <button
            onClick={() => setIsMuted(!isMuted)}
            className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white transition-all"
          >
            {isMuted ? <VolumeX className="w-5 h-5 text-gray-700" /> : <Volume2 className="w-5 h-5 text-gray-700" />}
          </button>
          
          <button onClick={handleReplay} className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white">
            <RotateCcw className="w-5 h-5 text-gray-700" />
          </button>
          
          <button onClick={handleShare} className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white">
            <Share2 className="w-5 h-5 text-gray-700" />
          </button>
          
          <button onClick={() => setIsExpanded(!isExpanded)} className="p-2 bg-white/90 rounded-full shadow-lg hover:bg-white">
            {isExpanded ? <X className="w-5 h-5 text-gray-700" /> : <Maximize2 className="w-5 h-5 text-gray-700" />}
          </button>
        </div>

        {/* ============ FLOATING ACTION BUTTONS ============ */}
        <div className="absolute bottom-32 right-3 flex flex-col space-y-2 z-10">
          {/* Exam Tip */}
          <motion.button
            onClick={() => { setShowExamTip(true); trackInteraction('view_exam_tip'); }}
            className="p-3 bg-purple-500 text-white rounded-full shadow-lg hover:bg-purple-600"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Exam Tip"
          >
            <Target className="w-5 h-5" />
          </motion.button>
          
          {/* Common Mistakes */}
          <motion.button
            onClick={() => setShowMistakes(true)}
            className="p-3 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Common Mistakes"
          >
            <Lightbulb className="w-5 h-5" />
          </motion.button>
          
          {/* Ask Doubt */}
          <motion.button
            onClick={() => setShowAskDoubt(true)}
            className="p-3 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Ask Doubt"
          >
            <MessageCircle className="w-5 h-5" />
          </motion.button>
        </div>
      </div>

      {/* ============ BOTTOM CONTROLS ============ */}
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
                className={`w-3 h-3 rounded-full transition-all ${step === currentStep ? 'bg-orange-500 scale-125' : step < currentStep ? 'bg-green-500' : 'bg-gray-600'}`}
                animate={step === currentStep ? { scale: [1, 1.3, 1] } : {}}
                transition={{ repeat: Infinity, duration: 1.5 }}
              />
            ))}
          </div>

          <button
            onClick={handleNextStep}
            disabled={currentStep >= totalSteps - 1}
            className={`p-3 rounded-full transition-all ${currentStep >= totalSteps - 1 ? 'bg-gray-700 text-gray-500' : 'bg-orange-500 text-white hover:bg-orange-600 shadow-lg'}`}
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>

        <p className="text-center text-white font-medium">
          Step {currentStep + 1}: {stepTitles[currentStep]}
        </p>
        
        {/* Related concepts */}
        <div className="flex items-center justify-center mt-3 space-x-2">
          <span className="text-gray-400 text-xs">Related:</span>
          {['Newton\'s Laws', 'Friction', 'Momentum'].map((topic) => (
            <button 
              key={topic}
              className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded-full hover:bg-gray-600 transition-all"
            >
              {topic}
            </button>
          ))}
        </div>
      </div>

      {/* ============ OVERLAYS ============ */}
      
      {/* Quiz Overlay */}
      <AnimatePresence>
        {showQuiz && !quizAnswer && (
          <QuizOverlay onAnswer={handleQuizAnswer} onClose={() => setShowQuiz(false)} />
        )}
      </AnimatePresence>

      {/* Quiz Result */}
      <AnimatePresence>
        {quizAnswer && (
          <QuizResult result={quizAnswer} onClose={() => { setQuizAnswer(null); setShowQuiz(false); }} />
        )}
      </AnimatePresence>

      {/* Exam Tip Overlay */}
      <AnimatePresence>
        {showExamTip && (
          <ExamTipOverlay onClose={() => setShowExamTip(false)} />
        )}
      </AnimatePresence>

      {/* Common Mistakes Overlay */}
      <AnimatePresence>
        {showMistakes && (
          <MistakesOverlay onClose={() => setShowMistakes(false)} />
        )}
      </AnimatePresence>

      {/* Share Menu */}
      <AnimatePresence>
        {showShareMenu && (
          <ShareMenu onClose={() => setShowShareMenu(false)} />
        )}
      </AnimatePresence>

      {/* Ask Doubt */}
      <AnimatePresence>
        {showAskDoubt && (
          <AskDoubtOverlay onClose={() => setShowAskDoubt(false)} />
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// ============ OVERLAY COMPONENTS ============

const QuizOverlay = ({ onAnswer, onClose }) => (
  <motion.div
    className="absolute inset-0 z-40 flex items-center justify-center bg-black/70 backdrop-blur-sm"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
  >
    <motion.div
      className="bg-white rounded-2xl p-6 max-w-sm mx-4 shadow-2xl"
      initial={{ scale: 0.8, y: 20 }}
      animate={{ scale: 1, y: 0 }}
      exit={{ scale: 0.8, y: 20 }}
    >
      <div className="flex items-center space-x-2 mb-4">
        <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
          <HelpCircle className="w-5 h-5 text-orange-600" />
        </div>
        <div>
          <h3 className="font-bold text-gray-800">Quick Quiz! 🎯</h3>
          <p className="text-xs text-gray-500">Test your understanding</p>
        </div>
      </div>

      <p className="text-gray-700 mb-4 font-medium">
        If mass is doubled but force stays same, what happens to acceleration?
      </p>

      <div className="space-y-2">
        <button 
          onClick={() => onAnswer('A', false)}
          className="w-full p-3 text-left rounded-lg border-2 border-gray-200 hover:border-orange-400 transition-all"
        >
          A) Doubles
        </button>
        <button 
          onClick={() => onAnswer('B', true)}
          className="w-full p-3 text-left rounded-lg border-2 border-gray-200 hover:border-orange-400 transition-all"
        >
          B) Becomes half ✓
        </button>
        <button 
          onClick={() => onAnswer('C', false)}
          className="w-full p-3 text-left rounded-lg border-2 border-gray-200 hover:border-orange-400 transition-all"
        >
          C) Stays same
        </button>
        <button 
          onClick={() => onAnswer('D', false)}
          className="w-full p-3 text-left rounded-lg border-2 border-gray-200 hover:border-orange-400 transition-all"
        >
          D) Becomes zero
        </button>
      </div>

      <button onClick={onClose} className="mt-4 text-gray-400 text-sm hover:text-gray-600">
        Skip for now →
      </button>
    </motion.div>
  </motion.div>
);

const QuizResult = ({ result, onClose }) => (
  <motion.div
    className="absolute inset-0 z-40 flex items-center justify-center bg-black/70 backdrop-blur-sm"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    onClick={onClose}
  >
    <motion.div
      className={`rounded-2xl p-8 max-w-sm mx-4 shadow-2xl text-center ${result.isCorrect ? 'bg-green-500' : 'bg-red-500'}`}
      initial={{ scale: 0.5 }}
      animate={{ scale: 1 }}
      exit={{ scale: 0.5 }}
    >
      {result.isCorrect ? (
        <>
          <CheckCircle className="w-16 h-16 text-white mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-white mb-2">Correct! 🎉</h3>
          <p className="text-white/90 mb-4">a = F/m, so if m doubles, a halves!</p>
          <div className="bg-white/20 rounded-lg p-3">
            <p className="text-white font-bold">+25 XP earned!</p>
          </div>
        </>
      ) : (
        <>
          <XCircle className="w-16 h-16 text-white mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-white mb-2">Not quite!</h3>
          <p className="text-white/90 mb-4">Remember: a = F/m<br/>If m ↑ and F same → a ↓</p>
          <button className="bg-white/20 text-white px-4 py-2 rounded-lg">Try Again</button>
        </>
      )}
    </motion.div>
  </motion.div>
);

const ExamTipOverlay = ({ onClose }) => (
  <motion.div
    className="absolute inset-0 z-40 flex items-center justify-center bg-black/70 backdrop-blur-sm"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    onClick={onClose}
  >
    <motion.div
      className="bg-gradient-to-br from-purple-600 to-indigo-700 rounded-2xl p-6 max-w-sm mx-4 shadow-2xl"
      initial={{ scale: 0.8, y: 20 }}
      animate={{ scale: 1, y: 0 }}
      exit={{ scale: 0.8, y: 20 }}
      onClick={e => e.stopPropagation()}
    >
      <div className="flex items-center space-x-2 mb-4">
        <Target className="w-8 h-8 text-yellow-400" />
        <h3 className="text-xl font-bold text-white">Exam Tips 🎯</h3>
      </div>

      <div className="space-y-3 text-white">
        <div className="bg-white/20 rounded-lg p-3">
          <p className="font-bold text-yellow-300">JEE Mains 2023</p>
          <p className="text-sm">Q15: Force-mass problems - 4 marks</p>
        </div>
        
        <div className="bg-white/20 rounded-lg p-3">
          <p className="font-bold text-yellow-300">NEET 2023</p>
          <p className="text-sm">Newton's 2nd law - 8 marks total</p>
        </div>
        
        <div className="bg-white/10 rounded-lg p-3 border border-yellow-400/50">
          <p className="text-yellow-300 font-bold text-sm">💡 Pro Tip</p>
          <p className="text-sm">Always check units! F in N, m in kg, a in m/s²</p>
        </div>
      </div>

      <button 
        onClick={onClose}
        className="mt-4 w-full bg-white text-purple-700 py-2 rounded-lg font-bold hover:bg-gray-100"
      >
        Got it! +15 XP
      </button>
    </motion.div>
  </motion.div>
);

const MistakesOverlay = ({ onClose }) => (
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
      <div className="flex items-center space-x-2 mb-4">
        <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
          <Lightbulb className="w-5 h-5 text-red-600" />
        </div>
        <h3 className="font-bold text-gray-800">Common Mistakes ⚠️</h3>
      </div>

      <div className="space-y-3">
        <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded-r-lg">
          <p className="text-red-800 font-medium text-sm">❌ Forgetting Force is a VECTOR</p>
          <p className="text-red-600 text-xs">Direction matters! F⃗ not just F</p>
        </div>
        
        <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded-r-lg">
          <p className="text-red-800 font-medium text-sm">❌ Confusing mass and weight</p>
          <p className="text-red-600 text-xs">Weight = mg, Mass ≠ Weight</p>
        </div>
        
        <div className="bg-green-50 border-l-4 border-green-500 p-3 rounded-r-lg">
          <p className="text-green-800 font-medium text-sm">✓ Remember: a = F_net / m</p>
          <p className="text-green-600 text-xs">Use NET force, not individual forces!</p>
        </div>
      </div>

      <button 
        onClick={onClose}
        className="mt-4 w-full bg-gray-800 text-white py-2 rounded-lg font-bold hover:bg-gray-700"
      >
        I'll remember! 💪
      </button>
    </motion.div>
  </motion.div>
);

const ShareMenu = ({ onClose }) => (
  <motion.div
    className="absolute inset-0 z-40 flex items-end justify-center bg-black/50"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    onClick={onClose}
  >
    <motion.div
      className="bg-white rounded-t-3xl p-6 w-full max-w-md"
      initial={{ y: 200 }}
      animate={{ y: 0 }}
      exit={{ y: 200 }}
      onClick={e => e.stopPropagation()}
    >
      <div className="w-12 h-1 bg-gray-300 rounded-full mx-auto mb-4" />
      <h3 className="font-bold text-gray-800 text-center mb-4">Share this visual 📤</h3>
      
      <div className="grid grid-cols-4 gap-4">
        <button className="flex flex-col items-center space-y-1">
          <div className="w-14 h-14 rounded-full bg-green-500 flex items-center justify-center">
            <span className="text-white text-2xl">📱</span>
          </div>
          <span className="text-xs text-gray-600">WhatsApp</span>
        </button>
        <button className="flex flex-col items-center space-y-1">
          <div className="w-14 h-14 rounded-full bg-blue-500 flex items-center justify-center">
            <span className="text-white text-2xl">📘</span>
          </div>
          <span className="text-xs text-gray-600">Facebook</span>
        </button>
        <button className="flex flex-col items-center space-y-1">
          <div className="w-14 h-14 rounded-full bg-pink-500 flex items-center justify-center">
            <span className="text-white text-2xl">📸</span>
          </div>
          <span className="text-xs text-gray-600">Instagram</span>
        </button>
        <button className="flex flex-col items-center space-y-1">
          <div className="w-14 h-14 rounded-full bg-gray-200 flex items-center justify-center">
            <span className="text-2xl">📋</span>
          </div>
          <span className="text-xs text-gray-600">Copy Link</span>
        </button>
      </div>
      
      <div className="mt-4 p-3 bg-green-50 rounded-lg text-center">
        <p className="text-green-700 text-sm">🎁 Share & earn 20 XP!</p>
      </div>
    </motion.div>
  </motion.div>
);

const AskDoubtOverlay = ({ onClose }) => (
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
      <div className="flex items-center space-x-2 mb-4">
        <MessageCircle className="w-8 h-8 text-blue-500" />
        <h3 className="font-bold text-gray-800">Ask a Doubt 🤔</h3>
      </div>

      <textarea 
        className="w-full p-3 border-2 border-gray-200 rounded-lg resize-none focus:border-blue-400 focus:outline-none"
        rows="3"
        placeholder="Type your question about Force..."
      />

      <div className="mt-3 flex flex-wrap gap-2">
        <button className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full">Why F=ma?</button>
        <button className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full">Unit of Force?</button>
        <button className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full">Real examples?</button>
      </div>

      <button className="mt-4 w-full bg-blue-500 text-white py-3 rounded-lg font-bold hover:bg-blue-600">
        Ask AI Mentor
      </button>
    </motion.div>
  </motion.div>
);

// Helper function
const handleObjectTap = (id) => {
  console.log('Tapped:', id);
};

export default EnhancedForceScene;









