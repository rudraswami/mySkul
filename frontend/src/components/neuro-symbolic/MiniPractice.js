/**
 * Mini Practice Component
 * MCQ question with hint
 */
import React, { useState } from 'react';
import { CheckCircle, XCircle, Lightbulb } from 'lucide-react';

export default function MiniPractice({ practice }) {
  const [selectedOption, setSelectedOption] = useState(null);
  const [showHint, setShowHint] = useState(false);

  if (!practice) return null;

  const { question, options, hint, question_type } = practice;

  const handleOptionSelect = (index) => {
    setSelectedOption(index);
  };

  return (
    <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-xl border border-green-200 p-6 my-4">
      <div className="flex items-center space-x-2 mb-4">
        <span className="text-2xl">🎯</span>
        <h3 className="font-semibold text-gray-900">Mini Practice</h3>
      </div>

      {/* Question */}
      <div className="bg-white rounded-lg p-4 mb-4 border border-green-100">
        <p className="text-gray-900 font-medium leading-relaxed">
          {question}
        </p>
      </div>

      {/* Options (for MCQ) */}
      {question_type === 'mcq' && options && options.length > 0 && (
        <div className="space-y-2 mb-4">
          {options.map((option, index) => {
            const letters = ['A', 'B', 'C', 'D'];
            const isSelected = selectedOption === index;
            
            return (
              <button
                key={index}
                onClick={() => handleOptionSelect(index)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  isSelected
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-green-300 bg-white'
                }`}
              >
                <div className="flex items-center">
                  <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold mr-3 ${
                    isSelected
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {letters[index]}
                  </span>
                  <span className="text-gray-700">
                    {option}
                  </span>
                  {isSelected && (
                    <CheckCircle className="ml-auto h-5 w-5 text-green-500" />
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Fill in blank or short answer */}
      {question_type !== 'mcq' && (
        <textarea
          className="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none resize-none"
          rows="3"
          placeholder="Type your answer here..."
        />
      )}

      {/* Hint toggle */}
      <div className="mt-4">
        <button
          onClick={() => setShowHint(!showHint)}
          className="flex items-center space-x-2 text-sm text-green-700 hover:text-green-800 font-medium"
        >
          <Lightbulb className="h-4 w-4" />
          <span>{showHint ? 'Hide Hint' : 'Show Hint'}</span>
        </button>

        {showHint && hint && (
          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-900 leading-relaxed">
              💡 {hint}
            </p>
          </div>
        )}
      </div>

      <div className="mt-4 text-xs text-gray-500 italic">
        Try this yourself! Don't peek at the answer too quickly.
      </div>
    </div>
  );
}
