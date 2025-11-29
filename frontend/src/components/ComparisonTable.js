/**
 * Comparison Table Component
 * Shows side-by-side comparison for "difference between" questions
 * ENHANCED: Now renders LaTeX math formulas beautifully!
 */
import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight } from 'lucide-react';
import { InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * Render text with inline LaTeX math support
 * Handles: \(...\), $...$, and **bold** formatting
 */
const renderMathText = (text) => {
  if (!text) return null;
  
  const parts = [];
  let key = 0;
  
  // Combined pattern for LaTeX and bold
  // Order: \(...\) first, then $...$, then **bold**
  const patterns = [
    { regex: /\\\((.+?)\\\)/g, type: 'math' },      // \(...\) - LaTeX inline
    { regex: /\$([^\$\n]+)\$/g, type: 'math' },     // $...$ - LaTeX inline
    { regex: /\*\*(.+?)\*\*/g, type: 'bold' },      // **bold**
  ];
  
  // Find all matches
  const matches = [];
  patterns.forEach(({ regex, type }) => {
    let match;
    const r = new RegExp(regex.source, 'g');
    while ((match = r.exec(text)) !== null) {
      matches.push({
        start: match.index,
        end: match.index + match[0].length,
        content: match[1],
        type
      });
    }
  });
  
  // Sort by position
  matches.sort((a, b) => a.start - b.start);
  
  // Remove overlapping matches
  const filtered = [];
  let lastEnd = 0;
  matches.forEach(m => {
    if (m.start >= lastEnd) {
      filtered.push(m);
      lastEnd = m.end;
    }
  });
  
  // Build result
  let pos = 0;
  filtered.forEach(m => {
    // Text before match
    if (m.start > pos) {
      parts.push(<span key={key++}>{text.slice(pos, m.start)}</span>);
    }
    
    // Render match
    if (m.type === 'math') {
      try {
        parts.push(
          <InlineMath key={key++} math={m.content.trim()} />
        );
      } catch (e) {
        // Fallback for invalid LaTeX
        parts.push(
          <code key={key++} className="bg-purple-100 dark:bg-purple-900/30 px-1.5 py-0.5 rounded text-sm font-mono text-purple-700 dark:text-purple-300">
            {m.content}
          </code>
        );
      }
    } else if (m.type === 'bold') {
      parts.push(<strong key={key++} className="font-bold text-gray-900">{m.content}</strong>);
    }
    
    pos = m.end;
  });
  
  // Remaining text
  if (pos < text.length) {
    parts.push(<span key={key++}>{text.slice(pos)}</span>);
  }
  
  return parts.length > 0 ? parts : text;
};

export default function ComparisonTable({ comparisonData }) {
  const { title, left, right, summary, example, exam_tip } = comparisonData;

  return (
    <div className="space-y-6">
      {/* Title */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-2xl font-bold text-purple-900">{title}</h2>
        <p className="text-gray-600 mt-2">{comparisonData.greeting || 'Here\'s a clear comparison!'}</p>
      </motion.div>

      {/* Two Column Comparison Table */}
      <div className="grid md:grid-cols-2 gap-5">
        {/* Left Column */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-6 border-2 border-blue-300 shadow-md"
        >
          <div className="flex items-center gap-3 mb-5">
            <span className="text-4xl">{left.icon || '📘'}</span>
            <h3 className="text-xl font-bold text-blue-900">{left.name}</h3>
          </div>
          
          <div className="space-y-3">
            {left.points.map((point, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + idx * 0.1 }}
                className="flex items-start gap-3"
              >
                <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" />
                <p 
                  className="text-gray-900 leading-relaxed"
                  style={{ fontSize: '17px', lineHeight: '1.8' }}
                >
                  {renderMathText(point)}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Right Column */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border-2 border-green-300 shadow-md"
        >
          <div className="flex items-center gap-3 mb-5">
            <span className="text-4xl">{right.icon || '📗'}</span>
            <h3 className="text-xl font-bold text-green-900">{right.name}</h3>
          </div>
          
          <div className="space-y-3">
            {right.points.map((point, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + idx * 0.1 }}
                className="flex items-start gap-3"
              >
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-1" />
                <p 
                  className="text-gray-900 leading-relaxed"
                  style={{ fontSize: '17px', lineHeight: '1.8' }}
                >
                  {renderMathText(point)}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Summary */}
      {summary && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl p-5 border-l-4 border-yellow-400"
        >
          <p 
            className="text-gray-900 font-semibold text-center"
            style={{ fontSize: '18px', lineHeight: '1.8' }}
          >
            {renderMathText(summary)}
          </p>
        </motion.div>
      )}

      {/* Example */}
      {example && example.scenario && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white rounded-xl p-6 border-2 border-gray-200"
        >
          <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2" style={{ fontSize: '17px' }}>
            💡 Example
          </h4>
          <p className="text-gray-800 mb-3" style={{ fontSize: '17px', lineHeight: '1.8' }}>
            <strong>Scenario:</strong> {example.scenario}
          </p>
          <div className="grid md:grid-cols-2 gap-4 mt-4">
            <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-400">
              <p className="font-semibold text-blue-900 mb-2">Permutations:</p>
              <p className="text-gray-800" style={{ fontSize: '16px' }}>{example.permutation_result}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-400">
              <p className="font-semibold text-green-900 mb-2">Combinations:</p>
              <p className="text-gray-800" style={{ fontSize: '16px' }}>{example.combination_result}</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Exam Tip */}
      {exam_tip && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-gradient-to-r from-red-50 to-pink-50 rounded-xl p-5 border-2 border-red-200"
        >
          <p 
            className="text-gray-900 font-semibold"
            style={{ fontSize: '17px', lineHeight: '1.8' }}
          >
            {renderMathText(exam_tip)}
          </p>
        </motion.div>
      )}
    </div>
  );
}



