import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { CheckCircle, Circle, Loader2, Sparkles, Zap } from 'lucide-react';

const GENERATION_STEPS = [
  {
    id: 1,
    label: 'Analyzing Requirements',
    description: 'Understanding your syllabus & difficulty level',
    duration: 2000,
    icon: '🎯',
    color: 'text-blue-600'
  },
  {
    id: 2,
    label: 'Selecting Questions',
    description: 'Curating verified questions from our database',
    duration: 3000,
    icon: '📚',
    color: 'text-purple-600'
  },
  {
    id: 3,
    label: 'Structuring Test',
    description: 'Organizing questions by subject and difficulty',
    duration: 2500,
    icon: '⚡',
    color: 'text-yellow-600'
  },
  {
    id: 4,
    label: 'Finalizing Paper',
    description: 'Validating test quality and preparing your exam',
    duration: 2000,
    icon: '✨',
    color: 'text-green-600'
  }
];

const MOTIVATIONAL_MESSAGES = [
  "Building your personalized test… stay focused! 💪",
  "Your hard work today will pay off tomorrow 🎓",
  "Every practice test brings you closer to success 🚀",
  "Great students practice consistently 📈",
  "You're investing in your future right now ⭐",
  "Quality questions being selected for you 🎯"
];

export default function TestGenerationProgress({ onComplete, onStartTest, config, testData }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [motivationalMessage, setMotivationalMessage] = useState(MOTIVATIONAL_MESSAGES[0]);
  const [progress, setProgress] = useState(0);
  const [showSuccessState, setShowSuccessState] = useState(false);

  useEffect(() => {
    // Rotate motivational messages
    const messageInterval = setInterval(() => {
      const randomMessage = MOTIVATIONAL_MESSAGES[Math.floor(Math.random() * MOTIVATIONAL_MESSAGES.length)];
      setMotivationalMessage(randomMessage);
    }, 3000);

    return () => clearInterval(messageInterval);
  }, []);

  useEffect(() => {
    // Progress through steps automatically
    if (currentStep < GENERATION_STEPS.length) {
      const step = GENERATION_STEPS[currentStep];
      
      // Start progress animation for current step
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) return 100;
          return prev + (100 / (step.duration / 100));
        });
      }, 100);

      // Move to next step after duration
      const stepTimeout = setTimeout(() => {
        setCompletedSteps(prev => new Set([...prev, currentStep]));
        setProgress(0);
        setCurrentStep(prev => prev + 1);
      }, step.duration);

      return () => {
        clearInterval(progressInterval);
        clearTimeout(stepTimeout);
      };
    } else if (currentStep === GENERATION_STEPS.length && !showSuccessState) {
      // All animation steps complete - wait for test data
      // Check if test data is ready
      if (testData) {
        // Test is ready! Show success state
        const successTimeout = setTimeout(() => {
          setShowSuccessState(true);
        }, 500);
        return () => clearTimeout(successTimeout);
      }
      // If test data not ready yet, keep waiting (polling will happen via testData prop change)
    }
  }, [currentStep, testData, showSuccessState]);

  const totalProgress = ((currentStep + (progress / 100)) / GENERATION_STEPS.length) * 100;

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-900/95 via-purple-900/95 to-indigo-900/95 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${5 + Math.random() * 10}s`
            }}
          >
            <Sparkles className="w-4 h-4 text-blue-300 opacity-30" />
          </div>
        ))}
      </div>

      <Card className="max-w-2xl w-full bg-white/95 backdrop-blur-md border-0 shadow-2xl relative overflow-hidden">
        {/* Top gradient accent */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>

        <CardContent className="p-8 md:p-12">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mb-4 animate-pulse">
              <Zap className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-2">
              Generating Your Test
            </h2>
            <p className="text-gray-600">
              {config?.subjects?.join(', ') || 'Your custom test'} • {config?.numQuestions || 25} Questions
            </p>
          </div>

          {/* Overall Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Overall Progress</span>
              <span className="font-semibold">{Math.round(totalProgress)}%</span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-300 ease-out"
                style={{ width: `${totalProgress}%` }}
              >
                <div className="h-full w-full animate-shimmer bg-gradient-to-r from-transparent via-white/40 to-transparent"></div>
              </div>
            </div>
          </div>

          {/* Step Timeline */}
          <div className="space-y-4 mb-8">
            {GENERATION_STEPS.map((step, index) => {
              const isCompleted = completedSteps.has(index);
              const isCurrent = index === currentStep;
              const isPending = index > currentStep;

              return (
                <div
                  key={step.id}
                  className={`flex items-start gap-4 transition-all duration-500 ${
                    isCurrent ? 'scale-105' : ''
                  }`}
                >
                  {/* Step Icon/Indicator */}
                  <div className="flex-shrink-0 relative">
                    {isCompleted ? (
                      <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-6 h-6 text-white" />
                      </div>
                    ) : isCurrent ? (
                      <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center animate-pulse">
                        <Loader2 className="w-6 h-6 text-white animate-spin" />
                      </div>
                    ) : (
                      <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                        <Circle className="w-6 h-6 text-gray-400" />
                      </div>
                    )}
                    
                    {/* Vertical line connector */}
                    {index < GENERATION_STEPS.length - 1 && (
                      <div
                        className={`absolute left-1/2 top-10 w-0.5 h-8 -ml-px transition-colors duration-500 ${
                          isCompleted ? 'bg-green-500' : 'bg-gray-200'
                        }`}
                      />
                    )}
                  </div>

                  {/* Step Content */}
                  <div className="flex-1 pt-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-2xl">{step.icon}</span>
                      <h3 className={`font-semibold transition-colors ${
                        isCompleted ? 'text-green-600' :
                        isCurrent ? 'text-blue-600' :
                        'text-gray-400'
                      }`}>
                        {step.label}
                      </h3>
                    </div>
                    <p className={`text-sm transition-colors ${
                      isCurrent ? 'text-gray-700' : 'text-gray-500'
                    }`}>
                      {step.description}
                    </p>
                    
                    {/* Current step progress bar */}
                    {isCurrent && (
                      <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 transition-all duration-100"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Motivational Message */}
          <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
            <p className="text-gray-700 font-medium animate-fade-in">
              {motivationalMessage}
            </p>
          </div>

          {/* Pro tip */}
          <div className="mt-6 flex items-start gap-2 text-sm text-gray-600 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
            <Sparkles className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
            <p>
              <strong>Pro Tip:</strong> While your test is generating, take a deep breath and prepare your study space for optimal focus!
            </p>
          </div>
        </CardContent>
      </Card>

      <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px) translateX(0px);
            opacity: 0.3;
          }
          50% {
            transform: translateY(-20px) translateX(10px);
            opacity: 0.6;
          }
        }

        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-float {
          animation: float linear infinite;
        }

        .animate-shimmer {
          animation: shimmer 2s infinite;
        }

        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}
