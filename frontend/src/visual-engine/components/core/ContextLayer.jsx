/**
 * ContextLayer.jsx
 * Phase 1.1: Adds meaning and relevance to visuals
 * 
 * Shows:
 * - Why this matters (real-life relevance)
 * - Exam POV (importance for exams)
 * - Quick facts
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, BookOpen, Lightbulb, ChevronDown, ChevronUp, Target, Sparkles } from 'lucide-react';

// Context data for all concepts
const CONTEXT_DATA = {
  // ============ PHYSICS ============
  force: {
    realLife: [
      "Every time you throw a ball, push a door, or ride a bike - you're applying force!",
      "Cricket bowlers use force to make the ball swing and bounce",
      "Car brakes use friction force to stop the vehicle"
    ],
    examPOV: {
      frequency: "2-3 questions every year",
      boards: ["JEE Main", "JEE Advanced", "NEET", "CBSE Class 11"],
      marks: "4-8 marks",
      tip: "Always draw Free Body Diagrams (FBD) first!"
    },
    quickFacts: [
      "Force is a vector quantity (has direction)",
      "SI unit: Newton (N)",
      "1 Newton = force needed to accelerate 1kg by 1m/s²"
    ],
    hinglishTip: "Force = Push ya Pull jo cheez ko hilata hai! 💪"
  },
  
  motion: {
    realLife: [
      "Auto rickshaw ki speed, train ka acceleration - sab motion hai!",
      "Athletes use motion principles to run faster",
      "GPS calculates your car's velocity using motion equations"
    ],
    examPOV: {
      frequency: "3-4 questions every year",
      boards: ["JEE Main", "NEET", "CBSE Class 9, 11"],
      marks: "6-10 marks",
      tip: "Learn all 3 equations of motion by heart!"
    },
    quickFacts: [
      "Distance is scalar, Displacement is vector",
      "Speed = Distance/Time, Velocity = Displacement/Time",
      "Acceleration can be positive (speeding up) or negative (slowing down)"
    ],
    hinglishTip: "Gadi kitni fast? Speed. Kidhar ja rahi? Velocity! 🚗"
  },
  
  gravity: {
    realLife: [
      "Aam ka ped se girna - Newton ne yahi dekha tha!",
      "Satellites orbit Earth because of gravity",
      "Tides in the ocean are caused by Moon's gravity"
    ],
    examPOV: {
      frequency: "2-3 questions every year",
      boards: ["JEE Main", "JEE Advanced", "NEET"],
      marks: "4-8 marks",
      tip: "Remember: g = 9.8 m/s² on Earth's surface"
    },
    quickFacts: [
      "Gravity is always attractive",
      "Weight changes with location, mass doesn't",
      "g decreases as you go up from Earth's surface"
    ],
    hinglishTip: "Gravity = Zameen tumhe khichti hai! 🌍"
  },
  
  momentum: {
    realLife: [
      "Cricket ball hitting the bat - momentum transfer!",
      "Why trucks are harder to stop than bikes",
      "Rocket propulsion uses conservation of momentum"
    ],
    examPOV: {
      frequency: "2-3 questions every year",
      boards: ["JEE Main", "NEET", "CBSE Class 9, 11"],
      marks: "4-6 marks",
      tip: "In collisions, total momentum is always conserved!"
    },
    quickFacts: [
      "Momentum = mass × velocity",
      "SI unit: kg·m/s",
      "Impulse = Change in momentum"
    ],
    hinglishTip: "Heavy truck + fast speed = bahut momentum = mushkil rokna! 🚛"
  },
  
  friction: {
    realLife: [
      "Walking is possible because of friction!",
      "Car tyres grip the road using friction",
      "Matchstick lights due to friction heat"
    ],
    examPOV: {
      frequency: "1-2 questions every year",
      boards: ["JEE Main", "CBSE Class 11"],
      marks: "4-6 marks",
      tip: "Static friction > Kinetic friction always!"
    },
    quickFacts: [
      "Friction opposes relative motion",
      "f = μN (friction = coefficient × normal force)",
      "Smooth surfaces have low μ, rough surfaces have high μ"
    ],
    hinglishTip: "Friction = Zameen tumhe slide hone se rokti hai! 🛞"
  },
  
  energy: {
    realLife: [
      "Food gives you energy to study and play",
      "Solar panels convert light energy to electrical energy",
      "Roller coasters convert PE to KE and back"
    ],
    examPOV: {
      frequency: "3-4 questions every year",
      boards: ["JEE Main", "JEE Advanced", "NEET", "CBSE"],
      marks: "6-10 marks",
      tip: "Energy is always conserved - it just changes form!"
    },
    quickFacts: [
      "KE = ½mv², PE = mgh",
      "SI unit: Joule (J)",
      "Work done = Energy transferred"
    ],
    hinglishTip: "Energy kabhi khatam nahi hoti, bas form badal jaati hai! ⚡"
  },
  
  // ============ CHEMISTRY ============
  atom: {
    realLife: [
      "Everything around you is made of atoms!",
      "Your phone screen uses silicon atoms",
      "Gold jewelry - just gold atoms arranged beautifully"
    ],
    examPOV: {
      frequency: "2-3 questions every year",
      boards: ["JEE Main", "NEET", "CBSE Class 9, 11"],
      marks: "4-6 marks",
      tip: "Remember: Atomic number = Protons = Electrons (in neutral atom)"
    },
    quickFacts: [
      "Atom = Nucleus (protons + neutrons) + Electrons",
      "Protons are positive, Electrons are negative",
      "Most of atom is empty space!"
    ],
    hinglishTip: "Atom = Sabse chhota building block! ⚛️"
  },
  
  photosynthesis: {
    realLife: [
      "Plants make food using sunlight - that's why they're green!",
      "Oxygen we breathe comes from photosynthesis",
      "Farmers know: more sunlight = better crop growth"
    ],
    examPOV: {
      frequency: "2-3 questions every year",
      boards: ["NEET", "CBSE Class 10, 11"],
      marks: "4-6 marks",
      tip: "Remember the equation: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂"
    },
    quickFacts: [
      "Happens in chloroplasts (contain chlorophyll)",
      "Light reaction in thylakoids, Dark reaction in stroma",
      "Produces glucose and oxygen"
    ],
    hinglishTip: "Plants ka khana banana = Photosynthesis! 🌱☀️"
  },
  
  cell: {
    realLife: [
      "Your body has 37 trillion cells!",
      "Skin cells replace themselves every 2-3 weeks",
      "Red blood cells carry oxygen to all parts"
    ],
    examPOV: {
      frequency: "3-4 questions every year",
      boards: ["NEET", "CBSE Class 9, 11"],
      marks: "6-8 marks",
      tip: "Know the difference between plant and animal cells!"
    },
    quickFacts: [
      "Cell = Basic unit of life",
      "Plant cells have cell wall, animal cells don't",
      "Mitochondria = Powerhouse of the cell"
    ],
    hinglishTip: "Cell = Body ki sabse chhoti factory! 🔬"
  },
  
  // ============ MATHEMATICS ============
  quadratic: {
    realLife: [
      "Projectile motion follows quadratic path",
      "Bridge arches are parabolic (quadratic curves)",
      "Profit/loss calculations in business"
    ],
    examPOV: {
      frequency: "2-3 questions every year",
      boards: ["JEE Main", "CBSE Class 10, 11"],
      marks: "4-8 marks",
      tip: "Discriminant (b²-4ac) tells you about roots!"
    },
    quickFacts: [
      "Standard form: ax² + bx + c = 0",
      "Quadratic formula: x = (-b ± √(b²-4ac))/2a",
      "Graph is always a parabola"
    ],
    hinglishTip: "Quadratic = x² wala equation! 📈"
  },
  
  pythagoras: {
    realLife: [
      "Construction workers use it to make right angles",
      "TV screen size is measured using Pythagoras",
      "GPS uses it to calculate distances"
    ],
    examPOV: {
      frequency: "1-2 questions every year",
      boards: ["CBSE Class 10", "JEE Main"],
      marks: "2-4 marks",
      tip: "Works ONLY for right-angled triangles!"
    },
    quickFacts: [
      "a² + b² = c² (c is hypotenuse)",
      "Common triplets: 3-4-5, 5-12-13, 8-15-17",
      "Hypotenuse is always the longest side"
    ],
    hinglishTip: "Right angle triangle mein: Lambi side² = Baaki dono² ka sum! 📐"
  },
  
  integral: {
    realLife: [
      "Calculate area under any curve",
      "Find total distance from velocity graph",
      "Physics uses integrals everywhere!"
    ],
    examPOV: {
      frequency: "4-5 questions every year",
      boards: ["JEE Main", "JEE Advanced", "CBSE Class 12"],
      marks: "8-12 marks",
      tip: "Practice substitution and by-parts methods!"
    },
    quickFacts: [
      "Integration is reverse of differentiation",
      "∫xⁿdx = xⁿ⁺¹/(n+1) + C",
      "Definite integral gives exact area"
    ],
    hinglishTip: "Integral = Area nikalo curve ke neeche! ∫"
  },
  
  derivative: {
    realLife: [
      "Speed is derivative of distance",
      "Rate of change in stock prices",
      "Slope of a curve at any point"
    ],
    examPOV: {
      frequency: "3-4 questions every year",
      boards: ["JEE Main", "JEE Advanced", "CBSE Class 11, 12"],
      marks: "6-10 marks",
      tip: "Master chain rule and product rule!"
    },
    quickFacts: [
      "Derivative = Rate of change",
      "d/dx(xⁿ) = nxⁿ⁻¹",
      "Derivative of constant = 0"
    ],
    hinglishTip: "Derivative = Kitna fast badal raha hai! 📈"
  }
};

// Default context for unknown concepts
const DEFAULT_CONTEXT = {
  realLife: [
    "This concept is used in many real-world applications",
    "Understanding this helps in competitive exams",
    "Scientists and engineers use this daily"
  ],
  examPOV: {
    frequency: "Varies by exam",
    boards: ["JEE", "NEET", "CBSE"],
    marks: "2-6 marks",
    tip: "Practice problems regularly!"
  },
  quickFacts: [
    "Fundamental concept in this subject",
    "Build strong basics first",
    "Connect with related topics"
  ],
  hinglishTip: "Basics strong karo, sab easy lagega! 💪"
};

const ContextLayer = ({ 
  concept, 
  subject,
  position = 'top', // 'top' | 'bottom' | 'side'
  collapsed = false,
  onToggle,
  showExamPOV = true,
  showRealLife = true,
  showQuickFacts = true
}) => {
  const [isExpanded, setIsExpanded] = useState(!collapsed);
  const [activeTab, setActiveTab] = useState('realLife');
  
  // Get context data for the concept
  const contextData = CONTEXT_DATA[concept?.toLowerCase()] || DEFAULT_CONTEXT;
  
  const tabs = [
    { id: 'realLife', label: 'Real Life', icon: Globe, show: showRealLife },
    { id: 'examPOV', label: 'Exam POV', icon: Target, show: showExamPOV },
    { id: 'quickFacts', label: 'Quick Facts', icon: Lightbulb, show: showQuickFacts },
  ].filter(tab => tab.show);

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
    onToggle?.(!isExpanded);
  };

  return (
    <motion.div
      className={`bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-800 dark:via-gray-800 dark:to-gray-800 rounded-xl border border-purple-200 dark:border-purple-800 overflow-hidden ${position === 'side' ? 'w-72' : 'w-full'}`}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <button
        onClick={handleToggle}
        className="w-full px-4 py-3 flex items-center justify-between bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-900/30 dark:to-indigo-900/30 hover:from-purple-200 hover:to-indigo-200 dark:hover:from-purple-900/50 dark:hover:to-indigo-900/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <span className="font-semibold text-purple-800 dark:text-purple-200">
            Why This Matters
          </span>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </motion.div>
      </button>

      {/* Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Tabs */}
            <div className="flex border-b border-purple-200 dark:border-purple-800">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 px-3 py-2 flex items-center justify-center gap-1.5 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'text-purple-700 dark:text-purple-300 bg-white dark:bg-gray-700 border-b-2 border-purple-500'
                      : 'text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="p-4">
              <AnimatePresence mode="wait">
                {activeTab === 'realLife' && (
                  <motion.div
                    key="realLife"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    className="space-y-2"
                  >
                    {contextData.realLife.map((item, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300"
                      >
                        <span className="text-green-500 mt-0.5">✓</span>
                        <span>{item}</span>
                      </motion.div>
                    ))}
                    
                    {/* Hinglish Tip */}
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                      className="mt-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800"
                    >
                      <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                        💡 {contextData.hinglishTip}
                      </p>
                    </motion.div>
                  </motion.div>
                )}

                {activeTab === 'examPOV' && (
                  <motion.div
                    key="examPOV"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    className="space-y-3"
                  >
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">Frequency</p>
                        <p className="text-sm font-bold text-blue-800 dark:text-blue-200">{contextData.examPOV.frequency}</p>
                      </div>
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <p className="text-xs text-green-600 dark:text-green-400 font-medium">Marks</p>
                        <p className="text-sm font-bold text-green-800 dark:text-green-200">{contextData.examPOV.marks}</p>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <p className="text-xs text-purple-600 dark:text-purple-400 font-medium mb-1">Important For</p>
                      <div className="flex flex-wrap gap-1">
                        {contextData.examPOV.boards.map((board, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 bg-purple-100 dark:bg-purple-800 text-purple-700 dark:text-purple-200 text-xs rounded-full"
                          >
                            {board}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border-l-4 border-orange-500">
                      <p className="text-xs text-orange-600 dark:text-orange-400 font-medium">🎯 Pro Tip</p>
                      <p className="text-sm text-orange-800 dark:text-orange-200">{contextData.examPOV.tip}</p>
                    </div>
                  </motion.div>
                )}

                {activeTab === 'quickFacts' && (
                  <motion.div
                    key="quickFacts"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    className="space-y-2"
                  >
                    {contextData.quickFacts.map((fact, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="flex items-start gap-2 p-2 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                      >
                        <span className="w-6 h-6 flex items-center justify-center bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full text-xs font-bold">
                          {idx + 1}
                        </span>
                        <span className="text-sm text-gray-700 dark:text-gray-300 flex-1">{fact}</span>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Export context data for use in other components
export { CONTEXT_DATA, DEFAULT_CONTEXT };
export default ContextLayer;



