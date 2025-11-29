/**
 * StepIndicator - Visual step progress indicator
 * Shows current step in the animation sequence
 */

import React from 'react';
import { motion } from 'framer-motion';

const StepIndicator = ({ currentStep, totalSteps, stepTitles = [] }) => {
  return (
    <div className="flex items-center gap-2">
      {[...Array(totalSteps)].map((_, index) => {
        const isActive = index === currentStep;
        const isCompleted = index < currentStep;
        const title = stepTitles[index] || `Step ${index + 1}`;

        return (
          <motion.div
            key={index}
            className="relative group"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: index * 0.1 }}
          >
            {/* Step dot */}
            <motion.div
              className={`
                w-3 h-3 rounded-full transition-all duration-300
                ${isActive 
                  ? 'bg-orange-500 ring-4 ring-orange-500/30' 
                  : isCompleted 
                    ? 'bg-green-500' 
                    : 'bg-white/30'
                }
              `}
              animate={{
                scale: isActive ? [1, 1.2, 1] : 1,
              }}
              transition={{
                repeat: isActive ? Infinity : 0,
                duration: 1.5,
              }}
            />

            {/* Connector line */}
            {index < totalSteps - 1 && (
              <div 
                className={`
                  absolute top-1/2 left-3 w-4 h-0.5 -translate-y-1/2
                  ${isCompleted ? 'bg-green-500' : 'bg-white/20'}
                `}
              />
            )}

            {/* Tooltip */}
            <div className="
              absolute -bottom-8 left-1/2 -translate-x-1/2 
              opacity-0 group-hover:opacity-100 transition-opacity
              pointer-events-none z-50
            ">
              <div className="bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                {title}
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

/**
 * Vertical Step List - For larger displays
 */
export const StepList = ({ steps, currentStep, onStepClick }) => {
  return (
    <div className="space-y-2">
      {steps.map((step, index) => {
        const isActive = index === currentStep;
        const isCompleted = index < currentStep;

        return (
          <motion.button
            key={step.id || index}
            onClick={() => onStepClick?.(index)}
            className={`
              w-full text-left p-3 rounded-lg transition-all
              ${isActive 
                ? 'bg-orange-500 text-white' 
                : isCompleted 
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }
            `}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center gap-3">
              {/* Step number */}
              <div className={`
                w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold
                ${isActive 
                  ? 'bg-white text-orange-500' 
                  : isCompleted 
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-300 text-gray-600'
                }
              `}>
                {isCompleted ? '✓' : index + 1}
              </div>

              {/* Step info */}
              <div className="flex-1">
                <div className="font-semibold text-sm">{step.title}</div>
                {step.description && (
                  <div className={`text-xs ${isActive ? 'text-white/80' : 'text-gray-500'}`}>
                    {step.description}
                  </div>
                )}
              </div>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
};

export default StepIndicator;









