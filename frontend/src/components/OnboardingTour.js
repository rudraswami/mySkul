/**
 * Onboarding Tour Component
 * 3-step introduction for first-time users
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowRight, Check } from 'lucide-react';

export default function OnboardingTour({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if user has seen onboarding
    const hasSeenOnboarding = localStorage.getItem('dhruv_ai_onboarding_complete');
    if (!hasSeenOnboarding) {
      setTimeout(() => setIsVisible(true), 500);
    }
  }, []);

  const steps = [
    {
      title: "Meet Your AI Team",
      description: "Your AI Mentor 🤝 explains concepts intuitively with cricket metaphors and real examples. Your AI Professor 🎓 verifies everything academically with step-by-step logic.",
      icon: "🤝🎓",
      gradient: "from-green-500 to-purple-500"
    },
    {
      title: "Ask Anything - We Detect the Subject",
      description: "Just ask your question naturally! We automatically detect whether it's Math, Physics, Chemistry, or Biology. No need to select subjects manually!",
      icon: "🧠",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      title: "Earn XP, Unlock Badges, Compete!",
      description: "Every question you ask earns XP. Build your streak 🔥, level up ⭐, and climb the leaderboard. Make learning a fun game!",
      icon: "🏆",
      gradient: "from-orange-500 to-yellow-500"
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    localStorage.setItem('dhruv_ai_onboarding_complete', 'true');
    setIsVisible(false);
    if (onComplete) onComplete();
  };

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={handleSkip}
        />

        {/* Onboarding Card */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="relative bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden"
        >
          {/* Skip button */}
          <button
            onClick={handleSkip}
            className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full transition-colors z-10"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>

          {/* Gradient header */}
          <div className={`bg-gradient-to-br ${steps[currentStep].gradient} p-8 text-center`}>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1, rotate: [0, 10, -10, 0] }}
              transition={{ duration: 0.5 }}
              className="text-7xl mb-4"
            >
              {steps[currentStep].icon}
            </motion.div>
            <h2 className="text-2xl font-extrabold text-white drop-shadow-lg">
              {steps[currentStep].title}
            </h2>
          </div>

          {/* Content */}
          <div className="p-8">
            <p className="text-gray-700 text-lg leading-relaxed mb-8 text-center">
              {steps[currentStep].description}
            </p>

            {/* Progress dots */}
            <div className="flex items-center justify-center gap-2 mb-6">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`h-2 rounded-full transition-all ${
                    index === currentStep
                      ? 'w-8 bg-purple-600'
                      : index < currentStep
                      ? 'w-2 bg-green-600'
                      : 'w-2 bg-gray-300'
                  }`}
                />
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between gap-4">
              <button
                onClick={handleSkip}
                className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
              >
                Skip tour
              </button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleNext}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl flex items-center gap-2 shadow-lg transition-all font-semibold"
              >
                {currentStep < steps.length - 1 ? (
                  <>
                    Next
                    <ArrowRight className="w-4 h-4" />
                  </>
                ) : (
                  <>
                    Get Started
                    <Check className="w-4 h-4" />
                  </>
                )}
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}

