import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check } from 'lucide-react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * FormulaCard - Styled card for displaying mathematical formulas with KaTeX
 * AI Tutor 2.1 micro-lesson component
 */
const FormulaCard = ({ formulas, title = 'Key Formula' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = (formula) => {
    navigator.clipboard.writeText(formula);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!formulas || formulas.length === 0) return null;

  // Clean formula for KaTeX (remove $$ delimiters if present)
  const cleanFormula = (formula) => {
    return formula.replace(/^\$\$|\$\$$/g, '').replace(/^\$|\$$/g, '').trim();
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="p-8 rounded-2xl bg-gradient-to-br from-violet-100 via-purple-50 to-pink-50 border-2 border-violet-300 shadow-lg hover:shadow-2xl transition-all"
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 mt-1">
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center shadow-md">
            <span className="text-3xl">🧮</span>
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold text-gray-900 font-poppins flex items-center">
              {title}
              <span className="ml-2 text-2xl">📐</span>
            </h3>
            <button
              onClick={() => handleCopy(typeof formulas === 'string' ? formulas : formulas[0])}
              className="p-3 hover:bg-white rounded-xl transition-all hover:scale-110"
              title="Copy formula"
            >
              {copied ? (
                <Check className="w-5 h-5 text-green-600" />
              ) : (
                <Copy className="w-5 h-5 text-violet-600" />
              )}
            </button>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-inner border-2 border-violet-100">
            {typeof formulas === 'string' ? (
              <div className="text-center">
                <BlockMath math={cleanFormula(formulas)} />
              </div>
            ) : (
              <div className="space-y-4">
                {formulas.map((formula, index) => (
                  <div key={index} className="text-center">
                    <BlockMath math={cleanFormula(formula)} />
                  </div>
                ))}
              </div>
            )}
          </div>
          <p className="text-xs text-violet-700 mt-3 text-center font-medium">
            💡 Tip: Click the copy icon to save this formula!
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default FormulaCard;