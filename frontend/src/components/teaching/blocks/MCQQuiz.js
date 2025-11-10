import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function MCQQuiz({ question, options = [], correct = 0, explanation }) {
  const [sel, setSel] = useState(null);
  const isAnswered = sel !== null;
  const isCorrect = isAnswered && sel === correct;

  return (
    <div className="bg-white rounded-xl border-2 border-emerald-200 p-4">
      <div className="text-sm font-semibold text-emerald-700 mb-2">Quick Check</div>
      <p className="font-medium text-gray-900 mb-2">{question}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {options.map((op, i) => (
          <button
            key={i}
            onClick={() => setSel(i)}
            className={`text-left px-3 py-2 rounded-lg border transition-all ${
              isAnswered
                ? i === correct
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
                  : i === sel
                  ? 'bg-red-50 border-red-300 text-red-900'
                  : 'bg-white border-gray-300'
                : 'bg-white border-gray-300 hover:bg-gray-50'
            }`}
          >
            {op}
          </button>
        ))}
      </div>
      <AnimatePresence>
        {isAnswered && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.98 }}
            className={`mt-3 text-sm rounded-lg p-3 ${isCorrect ? 'bg-emerald-50 text-emerald-900 border border-emerald-200' : 'bg-red-50 text-red-900 border border-red-200'}`}
          >
            <div className="flex items-center gap-2">
              <span>{isCorrect ? '🎉' : '🤔'}</span>
              <span>{isCorrect ? 'Correct!' : 'Not quite.'} {explanation}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
