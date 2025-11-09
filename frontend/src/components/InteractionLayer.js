/**
 * Interaction Layer Component
 * Handles all student interactions within the teaching visual
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, X, HelpCircle, Lightbulb, Target, Zap } from 'lucide-react';

export default function InteractionLayer({ interaction, onResponse, stage }) {
  const [selectedOption, setSelectedOption] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [dragPosition, setDragPosition] = useState({ x: 0, y: 0 });
  const [sliderValue, setSliderValue] = useState(50);
  const [isCorrect, setIsCorrect] = useState(null);
  const [hint, setHint] = useState(null);

  // Handle different interaction types
  const renderInteraction = () => {
    switch (interaction.type) {
      case 'tap_to_continue':
        return <TapToContinue onTap={handleResponse} />;

      case 'quiz':
        return (
          <QuizInteraction
            question={interaction.question}
            options={interaction.options}
            correct={interaction.correct}
            onSelect={handleQuizResponse}
            showFeedback={showFeedback}
            isCorrect={isCorrect}
          />
        );

      case 'drag':
        return (
          <DragInteraction
            items={interaction.items}
            targets={interaction.targets}
            onComplete={handleDragComplete}
          />
        );

      case 'slider':
        return (
          <SliderInteraction
            min={interaction.min || 0}
            max={interaction.max || 100}
            step={interaction.step || 1}
            value={sliderValue}
            onChange={setSliderValue}
            onConfirm={() => handleResponse({ value: sliderValue })}
            label={interaction.label}
          />
        );

      case 'predict':
        return (
          <PredictionInteraction
            prompt={interaction.prompt}
            options={interaction.options}
            onPredict={handlePrediction}
          />
        );

      default:
        return <TapToContinue onTap={handleResponse} />;
    }
  };

  const handleResponse = (response = {}) => {
    onResponse({
      type: interaction.type,
      response,
      timestamp: Date.now(),
      stage
    });
  };

  const handleQuizResponse = (optionIndex) => {
    setSelectedOption(optionIndex);
    const correct = optionIndex === interaction.correct;
    setIsCorrect(correct);
    setShowFeedback(true);

    // Auto-continue after feedback
    setTimeout(() => {
      handleResponse({
        selected: optionIndex,
        correct,
        option: interaction.options[optionIndex]
      });
    }, 2000);
  };

  const handleDragComplete = (connections) => {
    const correct = validateDragConnections(connections, interaction.correctMapping);
    setIsCorrect(correct);
    setShowFeedback(true);

    setTimeout(() => {
      handleResponse({
        connections,
        correct
      });
    }, 1500);
  };

  const handlePrediction = (prediction) => {
    handleResponse({
      prediction,
      actual: interaction.actual
    });
  };

  const validateDragConnections = (connections, correctMapping) => {
    return Object.keys(connections).every(key =>
      connections[key] === correctMapping[key]
    );
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="interaction-container bg-white rounded-2xl shadow-2xl p-6 max-w-2xl w-full mx-4"
      >
        {/* Interaction Header */}
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
            <Zap className="w-5 h-5 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            Your Turn!
          </h3>
        </div>

        {/* Render appropriate interaction */}
        {renderInteraction()}

        {/* Hint System */}
        {interaction.hint && !showFeedback && (
          <button
            onClick={() => setHint(interaction.hint)}
            className="mt-4 text-sm text-purple-600 hover:text-purple-700 flex items-center gap-1"
          >
            <HelpCircle className="w-4 h-4" />
            Need a hint?
          </button>
        )}

        {hint && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
          >
            <div className="flex items-start gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-yellow-900">{hint}</p>
            </div>
          </motion.div>
        )}

        {/* Feedback Display */}
        {showFeedback && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mt-4 p-4 rounded-lg ${
              isCorrect
                ? 'bg-green-50 border border-green-200'
                : 'bg-red-50 border border-red-200'
            }`}
          >
            <div className="flex items-start gap-2">
              {isCorrect ? (
                <>
                  <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-green-900">Perfect!</p>
                    <p className="text-sm text-green-700 mt-1">
                      {interaction.successMessage || "You got it right! Let's continue."}
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <X className="w-5 h-5 text-red-600 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-red-900">Not quite!</p>
                    <p className="text-sm text-red-700 mt-1">
                      {interaction.errorMessage || "Let's see the correct answer and learn from it."}
                    </p>
                  </div>
                </>
              )}
            </div>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

// ============================================================================
// INTERACTION COMPONENTS
// ============================================================================

function TapToContinue({ onTap }) {
  return (
    <div className="text-center py-8">
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onTap}
        className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
      >
        Continue →
      </motion.button>
      <p className="text-sm text-gray-500 mt-3">Tap to continue to the next step</p>
    </div>
  );
}

function QuizInteraction({ question, options, correct, onSelect, showFeedback, isCorrect }) {
  const [selected, setSelected] = useState(null);

  const handleSelect = (index) => {
    if (showFeedback) return;
    setSelected(index);
    onSelect(index);
  };

  return (
    <div>
      <h4 className="text-lg font-medium text-gray-900 mb-4">{question}</h4>
      <div className="space-y-2">
        {options.map((option, index) => {
          const isSelected = selected === index;
          const isCorrectOption = index === correct;
          const showCorrect = showFeedback && isCorrectOption;
          const showIncorrect = showFeedback && isSelected && !isCorrectOption;

          return (
            <motion.button
              key={index}
              whileHover={!showFeedback ? { scale: 1.02 } : {}}
              whileTap={!showFeedback ? { scale: 0.98 } : {}}
              onClick={() => handleSelect(index)}
              disabled={showFeedback}
              className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                showCorrect
                  ? 'border-green-500 bg-green-50'
                  : showIncorrect
                  ? 'border-red-500 bg-red-50'
                  : isSelected
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-200 hover:border-purple-400 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`${
                  showCorrect ? 'text-green-900' :
                  showIncorrect ? 'text-red-900' :
                  'text-gray-900'
                }`}>
                  {option}
                </span>
                {showCorrect && <Check className="w-5 h-5 text-green-600" />}
                {showIncorrect && <X className="w-5 h-5 text-red-600" />}
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}

function DragInteraction({ items, targets, onComplete }) {
  const [connections, setConnections] = useState({});
  const [draggedItem, setDraggedItem] = useState(null);
  const [hoveredTarget, setHoveredTarget] = useState(null);

  const handleDragStart = (item) => {
    setDraggedItem(item);
  };

  const handleDragEnd = () => {
    if (hoveredTarget && draggedItem) {
      const newConnections = {
        ...connections,
        [draggedItem.id]: hoveredTarget.id
      };
      setConnections(newConnections);

      // Check if all items are connected
      if (Object.keys(newConnections).length === items.length) {
        onComplete(newConnections);
      }
    }
    setDraggedItem(null);
    setHoveredTarget(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (target) => {
    setHoveredTarget(target);
  };

  return (
    <div className="drag-interaction">
      <p className="text-sm text-gray-600 mb-4">Drag items to their correct positions:</p>

      <div className="flex justify-between gap-8">
        {/* Items */}
        <div className="flex-1">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Items</h5>
          <div className="space-y-2">
            {items.map(item => (
              <div
                key={item.id}
                draggable
                onDragStart={() => handleDragStart(item)}
                onDragEnd={handleDragEnd}
                className={`p-3 bg-purple-100 rounded-lg cursor-move transition-all ${
                  connections[item.id] ? 'opacity-50' : 'hover:bg-purple-200'
                }`}
              >
                {item.label}
              </div>
            ))}
          </div>
        </div>

        {/* Targets */}
        <div className="flex-1">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Targets</h5>
          <div className="space-y-2">
            {targets.map(target => (
              <div
                key={target.id}
                onDragOver={handleDragOver}
                onDrop={() => handleDrop(target)}
                onDragEnter={() => setHoveredTarget(target)}
                onDragLeave={() => setHoveredTarget(null)}
                className={`p-3 border-2 border-dashed rounded-lg transition-all ${
                  hoveredTarget?.id === target.id
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-300 bg-gray-50'
                }`}
              >
                {target.label}
                {Object.entries(connections).map(([itemId, targetId]) =>
                  targetId === target.id && (
                    <div key={itemId} className="mt-2 p-2 bg-purple-200 rounded text-sm">
                      {items.find(i => i.id === itemId)?.label}
                    </div>
                  )
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function SliderInteraction({ min, max, step, value, onChange, onConfirm, label }) {
  return (
    <div className="slider-interaction">
      <p className="text-sm text-gray-600 mb-4">{label || "Adjust the slider:"}</p>

      <div className="space-y-4">
        <div className="relative">
          <input
            type="range"
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            style={{
              background: `linear-gradient(to right, #9333ea 0%, #9333ea ${
                ((value - min) / (max - min)) * 100
              }%, #e5e7eb ${((value - min) / (max - min)) * 100}%, #e5e7eb 100%)`
            }}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>{min}</span>
            <span className="font-bold text-purple-600">{value}</span>
            <span>{max}</span>
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onConfirm}
          className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
        >
          Confirm Selection
        </motion.button>
      </div>
    </div>
  );
}

function PredictionInteraction({ prompt, options, onPredict }) {
  const [selected, setSelected] = useState(null);

  const handlePredict = () => {
    if (selected !== null) {
      onPredict(options[selected]);
    }
  };

  return (
    <div className="prediction-interaction">
      <div className="flex items-start gap-2 mb-4">
        <Target className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="font-medium text-gray-900">Make a Prediction</h4>
          <p className="text-sm text-gray-600 mt-1">{prompt}</p>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        {options.map((option, index) => (
          <motion.button
            key={index}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setSelected(index)}
            className={`w-full p-3 text-left rounded-lg border-2 transition-all ${
              selected === index
                ? 'border-purple-600 bg-purple-50'
                : 'border-gray-200 hover:border-purple-400'
            }`}
          >
            {option}
          </motion.button>
        ))}
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handlePredict}
        disabled={selected === null}
        className={`w-full px-6 py-3 rounded-lg font-medium transition-all ${
          selected !== null
            ? 'bg-purple-600 text-white hover:bg-purple-700'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }`}
      >
        Submit Prediction
      </motion.button>
    </div>
  );
}